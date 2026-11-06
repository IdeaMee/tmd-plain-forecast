import "server-only";

import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

import { neon } from "@neondatabase/serverless";
import { cacheLife, cacheTag } from "next/cache";

import { type DocType, type Issue } from "@/lib/contract/issue";
import { parseIssuePayload, toListItem, type IssueListItem } from "@/lib/forecast-rows";

// แท็กเดียวของข้อมูลพยากรณ์ สคริปต์โหลดสั่งล้างผ่าน /internal/revalidate
export const FORECASTS_TAG = "forecasts";

/**
 * แหล่งข้อมูล: Neon เมื่อตั้ง DATABASE_URL (เว็บจริง)
 * ไม่ตั้ง = อ่านไฟล์ใน data/processed/ (ผลของ scripts/run_pipeline.py) ใช้ตอนพัฒนาก่อนมี DB และในเทสต์ e2e
 */
function db() {
  const url = process.env.DATABASE_URL;
  return url ? neon(url) : null;
}

async function readProcessed(docType: DocType): Promise<Issue[]> {
  // FORECAST_DATA_DIR ใช้กับเทสต์ e2e (ข้อมูลว่าง/เสีย) ค่าเริ่มต้น data/processed
  const root = process.env.FORECAST_DATA_DIR ?? path.join(process.cwd(), "data", "processed");
  const dir = path.join(/*turbopackIgnore: true*/ root, docType);
  // ใช้เฉพาะบนเครื่อง/เทสต์ (เว็บจริงอ่าน Neon) จึงไม่ให้ Turbopack ลากทั้งโปรเจกต์เข้าไปในชุดที่ deploy
  const files = (await readdir(/*turbopackIgnore: true*/ dir)).filter((f) => f.endsWith(".json"));
  const issues = await Promise.all(
    files.map(async (f) =>
      parseIssuePayload(await readFile(path.join(/*turbopackIgnore: true*/ dir, f), "utf-8")),
    ),
  );
  return issues.sort((a, b) => Date.parse(b.issued_at) - Date.parse(a.issued_at));
}

/** ฉบับล่าสุดของชนิดนั้น (ไม่มีข้อมูล = null) */
export async function getLatestIssue(docType: DocType): Promise<Issue | null> {
  "use cache";
  cacheTag(FORECASTS_TAG);
  cacheLife("hours");
  const sql = db();
  if (!sql) return (await readProcessed(docType))[0] ?? null;
  const rows = await sql`
    select payload from forecast_issue
    where doc_type = ${docType}
    order by issued_at desc
    limit 1`;
  return rows.length ? parseIssuePayload(rows[0].payload) : null;
}

/** ฉบับที่ระบุ (ไม่พบ = null) */
export async function getIssue(docType: DocType, issueId: string): Promise<Issue | null> {
  "use cache";
  cacheTag(FORECASTS_TAG);
  cacheLife("hours");
  const sql = db();
  if (!sql) return (await readProcessed(docType)).find((i) => i.issue_id === issueId) ?? null;
  const rows = await sql`
    select payload from forecast_issue
    where doc_type = ${docType} and issue_id = ${issueId}`;
  return rows.length ? parseIssuePayload(rows[0].payload) : null;
}

/**
 * รายการฉบับย้อนหลัง days วันนับจากฉบับล่าสุดในฐานข้อมูล (ไม่ใช่จากวันนี้
 * เพราะชุดข้อมูลเป็นช่วงที่เก็บไว้แล้ว) ใหม่สุดก่อน
 */
export async function listRecentIssues(docType: DocType, days = 7): Promise<IssueListItem[]> {
  "use cache";
  cacheTag(FORECASTS_TAG);
  cacheLife("hours");
  const sql = db();
  if (!sql) {
    const issues = await readProcessed(docType);
    if (!issues.length) return [];
    const since = Date.parse(issues[0].issued_at) - days * 24 * 60 * 60 * 1000;
    return issues
      .filter((i) => Date.parse(i.issued_at) > since)
      .map((i) => toListItem({ ...i, doc_type: i.doc_type }));
  }
  const rows = await sql`
    select issue_id, doc_type, issued_at, source_label from forecast_issue
    where doc_type = ${docType}
      and issued_at > (select max(issued_at) from forecast_issue where doc_type = ${docType})
                      - make_interval(days => ${days})
    order by issued_at desc`;
  return rows.map(toListItem);
}
