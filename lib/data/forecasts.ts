import "server-only";

import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

import { neon } from "@neondatabase/serverless";
import { cacheLife, cacheTag } from "next/cache";

import type { ShippingIssue, WarningNotice, WeeklySummary } from "@/lib/contract/documents";
import { type DocType, type Issue } from "@/lib/contract/issue";
import type { LoadedDocType } from "@/lib/contract/stored";
import {
  parseIssuePayload,
  parseShippingPayload,
  parseWarningPayload,
  parseWeeklyPayload,
  toListItem,
  type IssueListItem,
} from "@/lib/forecast-rows";
import { bangkokMonthKey } from "@/lib/format/thai";
import { countByMonth, type MonthCount } from "@/lib/history";
import { toWarningListItem, toWarningListItemFromRow, type WarningListItem } from "@/lib/warnings";

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

type Dated = { issue_id: string; issued_at: string };

async function readProcessed<T extends Dated>(docType: LoadedDocType, parse: (payload: unknown) => T): Promise<T[]> {
  // FORECAST_DATA_DIR ใช้กับเทสต์ e2e (ข้อมูลว่าง/เสีย) ค่าเริ่มต้น data/processed
  const root = process.env.FORECAST_DATA_DIR ?? path.join(process.cwd(), "data", "processed");
  const dir = path.join(/*turbopackIgnore: true*/ root, docType);
  // ใช้เฉพาะบนเครื่อง/เทสต์ (เว็บจริงอ่าน Neon) จึงไม่ให้ Turbopack ลากทั้งโปรเจกต์เข้าไปในชุดที่ deploy
  let names: string[];
  try {
    names = await readdir(/*turbopackIgnore: true*/ dir);
  } catch (err) {
    // ไม่มีโฟลเดอร์ของชนิดนี้ = ยังไม่มีข้อมูล (หน้าแสดงสถานะว่าง) ข้อผิดพลาดอื่นส่งต่อให้หน้าข้อผิดพลาด
    if ((err as NodeJS.ErrnoException).code === "ENOENT") return [];
    throw err;
  }
  const files = names.filter((f) => f.endsWith(".json"));
  const docs = await Promise.all(
    files.map(async (f) => parse(await readFile(path.join(/*turbopackIgnore: true*/ dir, f), "utf-8"))),
  );
  // เวลาเท่ากัน: รหัสมากก่อนแบบตัวเลข (ประกาศ 2569_99 ก่อน 2569_100) ให้ตรงกับคิวรี Neon และ lib/warnings.ts
  return docs.sort(
    (a, b) =>
      Date.parse(b.issued_at) - Date.parse(a.issued_at) ||
      b.issue_id.localeCompare(a.issue_id, "en", { numeric: true }),
  );
}

/** ฉบับล่าสุดของชนิดนั้น (ไม่มีข้อมูล = null) */
export async function getLatestIssue(docType: DocType): Promise<Issue | null> {
  "use cache";
  cacheTag(FORECASTS_TAG);
  cacheLife("hours");
  const sql = db();
  if (!sql) return (await readProcessed(docType, parseIssuePayload))[0] ?? null;
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
  if (!sql) return (await readProcessed(docType, parseIssuePayload)).find((i) => i.issue_id === issueId) ?? null;
  const rows = await sql`
    select payload from forecast_issue
    where doc_type = ${docType} and issue_id = ${issueId}`;
  return rows.length ? parseIssuePayload(rows[0].payload) : null;
}

// แถวรายการจากไฟล์: ตรวจเต็มตามชนิดก่อน (ไฟล์เสียต้องไม่ขึ้นในรายการ) แล้วเหลือแค่ฟิลด์ของรายการ
function toListRow(docType: LoadedDocType, payload: unknown) {
  const doc =
    docType === "shipping"
      ? parseShippingPayload(payload)
      : docType === "warning"
        ? parseWarningPayload(payload)
        : docType === "weekly"
          ? parseWeeklyPayload(payload)
          : parseIssuePayload(payload);
  return { issue_id: doc.issue_id, doc_type: doc.doc_type, issued_at: doc.issued_at, source_label: doc.source_label };
}

/** พยากรณ์เดินเรือฉบับล่าสุด (ไม่มีข้อมูล = null) */
export async function getLatestShippingIssue(): Promise<ShippingIssue | null> {
  "use cache";
  cacheTag(FORECASTS_TAG);
  cacheLife("hours");
  const sql = db();
  if (!sql) return (await readProcessed("shipping", parseShippingPayload))[0] ?? null;
  const rows = await sql`
    select payload from forecast_issue
    where doc_type = 'shipping'
    order by issued_at desc
    limit 1`;
  return rows.length ? parseShippingPayload(rows[0].payload) : null;
}

/** พยากรณ์เดินเรือฉบับที่ระบุ (ไม่พบ = null) */
export async function getShippingIssue(issueId: string): Promise<ShippingIssue | null> {
  "use cache";
  cacheTag(FORECASTS_TAG);
  cacheLife("hours");
  const sql = db();
  if (!sql) {
    return (await readProcessed("shipping", parseShippingPayload)).find((i) => i.issue_id === issueId) ?? null;
  }
  const rows = await sql`
    select payload from forecast_issue
    where doc_type = 'shipping' and issue_id = ${issueId}`;
  return rows.length ? parseShippingPayload(rows[0].payload) : null;
}

/** ประกาศเตือนภัยฉบับล่าสุด (ไม่มีข้อมูล = null) */
export async function getLatestWarning(): Promise<WarningNotice | null> {
  "use cache";
  cacheTag(FORECASTS_TAG);
  cacheLife("hours");
  const sql = db();
  if (!sql) return (await readProcessed("warning", parseWarningPayload))[0] ?? null;
  const rows = await sql`
    select payload from forecast_issue
    where doc_type = 'warning'
    order by issued_at desc, split_part(issue_id, '_', 1)::int desc, split_part(issue_id, '_', 2)::int desc
    limit 1`;
  return rows.length ? parseWarningPayload(rows[0].payload) : null;
}

/** ประกาศเตือนภัยฉบับที่ระบุ (ไม่พบ = null) */
export async function getWarning(issueId: string): Promise<WarningNotice | null> {
  "use cache";
  cacheTag(FORECASTS_TAG);
  cacheLife("hours");
  const sql = db();
  if (!sql) return (await readProcessed("warning", parseWarningPayload)).find((i) => i.issue_id === issueId) ?? null;
  const rows = await sql`
    select payload from forecast_issue
    where doc_type = 'warning' and issue_id = ${issueId}`;
  return rows.length ? parseWarningPayload(rows[0].payload) : null;
}

/**
 * รายการประกาศเตือนภัยทุกฉบับที่มีในระบบ (ไม่จำกัด 7 วันเหมือนพยากรณ์: ชุดประกาศยาวหลายวัน และหน้านี้มีย้อนหลัง)
 * ใหม่สุดก่อน คืนเฉพาะฟิลด์ที่รายการใช้ (หน้าจัดชุด/เดือนเองด้วย lib/warnings.ts)
 */
export async function listWarnings(): Promise<WarningListItem[]> {
  "use cache";
  cacheTag(FORECASTS_TAG);
  cacheLife("hours");
  const sql = db();
  if (!sql) {
    return (await readProcessed("warning", parseWarningPayload)).map(toWarningListItem);
  }
  const rows = await sql`
    select issue_id, issued_at,
      payload->>'title' as title,
      (payload->>'series_no')::int as series_no,
      payload->>'notice_no' as notice_no,
      payload->'effect'->>'text' as effect_text,
      payload->>'next_issue_at' as next_issue_at
    from forecast_issue
    where doc_type = 'warning'
    order by issued_at desc, split_part(issue_id, '_', 1)::int desc, split_part(issue_id, '_', 2)::int desc`;
  return rows.map(toWarningListItemFromRow);
}

/** สรุปรายสัปดาห์ฉบับล่าสุด (ไม่มีข้อมูล = null) */
export async function getLatestWeekly(): Promise<WeeklySummary | null> {
  "use cache";
  cacheTag(FORECASTS_TAG);
  cacheLife("hours");
  const sql = db();
  if (!sql) return (await readProcessed("weekly", parseWeeklyPayload))[0] ?? null;
  const rows = await sql`
    select payload from forecast_issue
    where doc_type = 'weekly'
    order by issued_at desc, issue_id desc
    limit 1`;
  return rows.length ? parseWeeklyPayload(rows[0].payload) : null;
}

/** สรุปรายสัปดาห์ฉบับที่ระบุ (ไม่พบ = null) */
export async function getWeekly(issueId: string): Promise<WeeklySummary | null> {
  "use cache";
  cacheTag(FORECASTS_TAG);
  cacheLife("hours");
  const sql = db();
  if (!sql) return (await readProcessed("weekly", parseWeeklyPayload)).find((i) => i.issue_id === issueId) ?? null;
  const rows = await sql`
    select payload from forecast_issue
    where doc_type = 'weekly' and issue_id = ${issueId}`;
  return rows.length ? parseWeeklyPayload(rows[0].payload) : null;
}

/** เดือนที่มีฉบับของชนิดนั้น พร้อมจำนวน ใหม่สุดก่อน (เดือนตามเวลาไทย; ใช้กับตัวเลือกรอบแบบรายเดือน 11.6) */
export async function listIssueMonths(docType: LoadedDocType): Promise<MonthCount[]> {
  "use cache";
  cacheTag(FORECASTS_TAG);
  cacheLife("hours");
  const sql = db();
  if (!sql) {
    const rows = await readProcessed(docType, (p) => toListRow(docType, p));
    return countByMonth(rows.map((r) => ({ issuedAt: r.issued_at })));
  }
  const rows = await sql`
    select to_char(issued_at at time zone 'Asia/Bangkok', 'YYYY-MM') as month, count(*)::int as n
    from forecast_issue
    where doc_type = ${docType}
    group by 1
    order by 1 desc`;
  return rows.map((r) => ({ month: String(r.month), count: Number(r.n) }));
}

/** รายการฉบับของชนิดนั้นในเดือนที่ระบุ (คีย์ "YYYY-MM") ใหม่สุดก่อน */
export async function listIssuesInMonth(docType: LoadedDocType, month: string): Promise<IssueListItem[]> {
  "use cache";
  cacheTag(FORECASTS_TAG);
  cacheLife("hours");
  const sql = db();
  if (!sql) {
    const rows = await readProcessed(docType, (p) => toListRow(docType, p));
    return rows.filter((r) => bangkokMonthKey(r.issued_at) === month).map(toListItem);
  }
  const rows = await sql`
    select issue_id, doc_type, issued_at, source_label from forecast_issue
    where doc_type = ${docType}
      and to_char(issued_at at time zone 'Asia/Bangkok', 'YYYY-MM') = ${month}
    order by issued_at desc, issue_id desc`;
  return rows.map(toListItem);
}
