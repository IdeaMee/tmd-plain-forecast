import { readdirSync, readFileSync, existsSync } from "node:fs";
import path from "node:path";

import { describe, expect, it } from "vitest";

import {
  adviceItemSchema,
  issueSchema,
  periodSchema,
  regionSummarySchema,
  summaryLineSchema,
} from "@/lib/contract/issue";

const ROOT = path.resolve(import.meta.dirname, "../..");
const jsonSchema = JSON.parse(readFileSync(path.join(ROOT, "lib/contract/issue.schema.json"), "utf-8"));

function readJson(file: string): unknown {
  return JSON.parse(readFileSync(file, "utf-8"));
}

// เฉพาะชนิดที่ใช้ Issue (รายวัน/7 วัน) ชนิดอื่นใน data/processed ตรวจใน documents.test.ts
function processedFiles(): string[] {
  const dir = path.join(ROOT, "data/processed");
  if (!existsSync(dir)) return [];
  return ["daily", "sevenday"]
    .filter((docType) => existsSync(path.join(dir, docType)))
    .flatMap((docType) => readdirSync(path.join(dir, docType)).map((f) => path.join(dir, docType, f)));
}

describe("Zod ตรงกับ JSON Schema ที่ส่งออกจาก Pydantic", () => {
  const pairs = [
    ["Issue", issueSchema],
    ["RegionSummary", regionSummarySchema],
    ["SummaryLine", summaryLineSchema],
    ["Period", periodSchema],
    ["AdviceItem", adviceItemSchema],
  ] as const;

  it.each(pairs)("%s มีชื่อฟิลด์เดียวกัน", (name, schema) => {
    const def = name === "Issue" ? jsonSchema : jsonSchema.$defs[name];
    // schema ที่มี refine ยังเก็บ shape ไว้ใน def.in / def.schema ตามชนิด
    const inner = (schema as unknown as { def: { in?: { shape: object }; shape?: object } }).def;
    const shape = inner.shape ?? inner.in?.shape ?? (schema as unknown as { shape: object }).shape;
    expect(Object.keys(shape).sort()).toEqual(Object.keys(def.properties).sort());
  });
});

describe("ไฟล์จริงผ่านสัญญา", () => {
  const files = processedFiles();

  // 11.6: ขึ้นเว็บทุกฉบับที่เก็บ (ปัจจุบัน 102 + 21) · ชุดแสดงผลเดิม 35 ฉบับต้องยังอยู่ครบ
  it("data/processed มีอย่างน้อย 35 ฉบับของชุดเดิม (รายวัน 28 + 7 วัน 7) และทุกฉบับผ่านสัญญา", () => {
    expect(files.length).toBeGreaterThanOrEqual(35);
  });

  it.each(files.map((f) => [path.relative(ROOT, f), f]))("%s", (_, file) => {
    const issue = issueSchema.parse(readJson(file));
    expect(path.basename(file, ".json")).toBe(issue.issue_id);
  });

  it.each(["issue-daily-example.json", "issue-sevenday-example.json"])("fixture %s", (name) => {
    expect(() => issueSchema.parse(readJson(path.join(ROOT, "tests/fixtures/contract", name)))).not.toThrow();
  });
});

describe("กฎตรวจของสัญญา", () => {
  const base = readJson(path.join(ROOT, "tests/fixtures/contract/issue-daily-example.json")) as Record<
    string,
    unknown
  >;

  it("ห้ามมีฟิลด์นอกสัญญา", () => {
    expect(issueSchema.safeParse({ ...base, extra: 1 }).success).toBe(false);
  });

  it("issued_at ต้องมีเขตเวลา", () => {
    expect(issueSchema.safeParse({ ...base, issued_at: "2026-11-16T17:00:00" }).success).toBe(false);
  });

  it("ข้อแนะนำทั่วไปต้องครบ 7 ภาค", () => {
    const item = { text: "ขอให้ประชาชน", scope: ["north"], general: true, source_unit_id: "d-1" };
    expect(adviceItemSchema.safeParse(item).success).toBe(false);
  });
});
