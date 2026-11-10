import { existsSync, readdirSync, readFileSync } from "node:fs";
import path from "node:path";

import { describe, expect, it } from "vitest";
import type { z } from "zod";

import {
  RESULT_KINDS,
  SEA_AREA_KEYS,
  SEA_AREA_LABELS_TH,
  TRACE_MAX_BYTES,
  TRACE_MAX_ITEMS,
  TRACE_STEP_IDS,
  effectPeriodSchema,
  genericDocumentSchema,
  genericSectionSchema,
  genericUnitSchema,
  glossaryEntrySchema,
  quotedAdviceSchema,
  seaAreaSchema,
  seaPartSchema,
  shippingIssueSchema,
  tableCellSchema,
  traceSchema,
  traceStepSchema,
  warningNoticeSchema,
  weeklyRegionSchema,
  weeklySummarySchema,
} from "@/lib/contract/documents";
import { storedDocumentSchema } from "@/lib/contract/stored";
import { ERROR_MESSAGES_TH, summarizeOkSchema, summarizeResponseSchema } from "@/lib/contract/summarize";

const ROOT = path.resolve(import.meta.dirname, "../..");
const defs = JSON.parse(readFileSync(path.join(ROOT, "lib/contract/summarize-response.schema.json"), "utf-8")).$defs;
const contractPy = readFileSync(path.join(ROOT, "src/tmd_plain/contract.py"), "utf-8");

function fixture(name: string): Record<string, unknown> {
  return JSON.parse(readFileSync(path.join(ROOT, "tests/fixtures/contract", name), "utf-8"));
}

function shapeKeys(schema: z.ZodType): string[] {
  // schema ที่มี refine ยังเก็บ shape ไว้ใน def.in / def.schema ตามชนิด
  const inner = (schema as unknown as { def: { in?: { shape: object }; shape?: object } }).def;
  const shape = inner.shape ?? inner.in?.shape ?? (schema as unknown as { shape: object }).shape;
  return Object.keys(shape).sort();
}

describe("Zod v2 ตรงกับ JSON Schema ที่ส่งออกจาก Pydantic", () => {
  const pairs = [
    ["ShippingIssue", shippingIssueSchema],
    ["SeaArea", seaAreaSchema],
    ["SeaPart", seaPartSchema],
    ["QuotedAdvice", quotedAdviceSchema],
    ["WarningNotice", warningNoticeSchema],
    ["EffectPeriod", effectPeriodSchema],
    ["WeeklySummary", weeklySummarySchema],
    ["WeeklyRegion", weeklyRegionSchema],
    ["TableCell", tableCellSchema],
    ["GenericDocument", genericDocumentSchema],
    ["GenericSection", genericSectionSchema],
    ["GenericUnit", genericUnitSchema],
    ["GlossaryEntry", glossaryEntrySchema],
    ["Trace", traceSchema],
    ["TraceStep", traceStepSchema],
  ] as const;

  it.each(pairs)("%s มีชื่อฟิลด์เดียวกัน", (name, schema) => {
    expect(shapeKeys(schema)).toEqual(Object.keys(defs[name].properties).sort());
  });

  it("ค่าคงที่ตรงกับ Python", () => {
    expect([...SEA_AREA_KEYS]).toEqual(defs.ShippingIssue.properties.areas.propertyNames.enum);
    expect([...TRACE_STEP_IDS]).toEqual(defs.TraceStep.properties.id.enum);
    const kinds = Object.keys(defs)
      .filter((k) => /^Summarize\w+Ok$/.test(k))
      .map((k) => defs[k].properties.kind.const);
    expect(kinds.sort()).toEqual([...RESULT_KINDS].sort());
    expect(contractPy).toContain(`TRACE_MAX_BYTES = 256 * 1024`);
    expect(TRACE_MAX_BYTES).toBe(256 * 1024);
    expect(contractPy).toContain(`TRACE_MAX_ITEMS = ${TRACE_MAX_ITEMS}`);
    for (const key of SEA_AREA_KEYS) {
      expect(contractPy).toContain(`"${key}": "${SEA_AREA_LABELS_TH[key]}"`);
    }
  });
});

describe("ไฟล์ตัวอย่างผ่านสัญญา v2", () => {
  it.each([
    ["shipping-example.json", shippingIssueSchema],
    ["warning-example.json", warningNoticeSchema],
    ["weekly-example.json", weeklySummarySchema],
  ] as const)("%s", (name, schema) => {
    expect(() => schema.parse(fixture(name))).not.toThrow();
  });

  it("คำตอบ generic พร้อม trace", () => {
    const res = summarizeResponseSchema.parse(fixture("summarize-v2-generic-example.json"));
    expect(res.ok && res.kind === "generic" && res.trace?.steps.length).toBe(6);
  });

  it("คำตอบ issue ไม่มี trace ได้ null", () => {
    const res = summarizeOkSchema.parse({ ok: true, kind: "issue", document: fixture("issue-daily-example.json") });
    expect(res.trace).toBeNull();
  });

  it("ข้อผิดพลาดใช้รูปเดิม", () => {
    const err = { ok: false, error: { code: "extract_failed", message_th: ERROR_MESSAGES_TH.extract_failed } };
    expect(summarizeResponseSchema.safeParse(err).success).toBe(true);
  });
});

describe("กฎตรวจของสัญญา v2", () => {
  it("kind ต้องตรงกับชนิดของ document", () => {
    const bad = { ok: true, kind: "shipping", document: fixture("issue-daily-example.json") };
    expect(summarizeOkSchema.safeParse(bad).success).toBe(false);
  });

  it("รูปคำตอบ v1 ไม่ผ่าน v2", () => {
    expect(summarizeResponseSchema.safeParse({ ok: true, issue: fixture("issue-daily-example.json") }).success).toBe(
      false,
    );
  });

  it("พยากรณ์เดินเรือต้องครบ 4 พื้นที่และชื่อตรงต้นฉบับ", () => {
    const doc = fixture("shipping-example.json") as { areas: Record<string, { name_th: string }> };
    const renamed = structuredClone(doc);
    renamed.areas.gulf_of_thailand.name_th = "อ่าวไทย";
    expect(shippingIssueSchema.safeParse(renamed).success).toBe(false);
    const missing = structuredClone(doc);
    delete missing.areas.ca_mau_cape;
    expect(shippingIssueSchema.safeParse(missing).success).toBe(false);
  });

  it("เลขประกาศต้องตรงกับ issue_id", () => {
    expect(warningNoticeSchema.safeParse({ ...fixture("warning-example.json"), notice_no: "314/2569" }).success).toBe(
      false,
    );
  });

  it("not_tmd_like ต้องสอดคล้องกับ tmd_like", () => {
    const doc = (fixture("summarize-v2-generic-example.json") as { document: Record<string, unknown> }).document;
    expect(genericDocumentSchema.safeParse({ ...doc, tmd_like: false }).success).toBe(false);
    expect(genericDocumentSchema.safeParse({ ...doc, tmd_like: false, warnings: ["not_tmd_like"] }).success).toBe(true);
  });

  it("trace จำกัดจำนวนชิ้นและขนาด", () => {
    const step = (id: string, n: number, item = "ก") => ({
      id,
      title_th: "x",
      status: "done",
      data: { tokens: Array(n).fill(item) },
    });
    expect(traceSchema.safeParse({ steps: [step("tokenize", TRACE_MAX_ITEMS)] }).success).toBe(true);
    expect(traceSchema.safeParse({ steps: [step("tokenize", TRACE_MAX_ITEMS + 1)] }).success).toBe(false);
    const big = "ก".repeat(1000);
    const huge = [step("tokenize", TRACE_MAX_ITEMS, big), step("filter_tokens", TRACE_MAX_ITEMS, big)];
    expect(traceSchema.safeParse({ steps: huge }).success).toBe(false);
    expect(traceSchema.safeParse({ steps: [step("clean", 1), step("clean", 1)] }).success).toBe(false);
  });
});

describe("ไฟล์พยากรณ์เดินเรือจริงใน data/processed (11.1)", () => {
  const dir = path.join(ROOT, "data/processed/shipping");
  const files = existsSync(dir) ? readdirSync(dir).filter((f) => f.endsWith(".json")) : [];

  it("มีไฟล์จากทุกฉบับที่เก็บ (100 ฉบับ)", () => {
    expect(files).toHaveLength(100);
  });

  it.each(files)("%s ผ่าน ShippingIssue และสคีมารวมตาม doc_type", (name) => {
    const data = JSON.parse(readFileSync(path.join(dir, name), "utf-8"));
    const doc = shippingIssueSchema.parse(data);
    expect(`${doc.issue_id}.json`).toBe(name);
    expect(storedDocumentSchema.parse(data).doc_type).toBe("shipping");
  });

  it("สคีมารวมเลือกตาม doc_type: ไฟล์รายวันไม่ผ่านเป็นเดินเรือ", () => {
    const daily = fixture("issue-daily-example.json");
    expect(storedDocumentSchema.parse(daily).doc_type).toBe("daily");
    expect(storedDocumentSchema.safeParse({ ...daily, doc_type: "shipping" }).success).toBe(false);
  });
});

describe("ไฟล์สรุปรายสัปดาห์จริงใน data/processed (11.5)", () => {
  const dir = path.join(ROOT, "data/processed/weekly");
  const files = existsSync(dir) ? readdirSync(dir).filter((f) => f.endsWith(".json")) : [];

  it("มีไฟล์จากทุกฉบับที่เก็บ (100 ฉบับ)", () => {
    expect(files).toHaveLength(100);
  });

  it.each(files)("%s ผ่าน WeeklySummary และสคีมารวมตาม doc_type", (name) => {
    const data = JSON.parse(readFileSync(path.join(dir, name), "utf-8"));
    const doc = weeklySummarySchema.parse(data);
    expect(`${doc.issue_id}.json`).toBe(name);
    expect(storedDocumentSchema.parse(data).doc_type).toBe("weekly");
    expect(Object.keys(doc.regions)).toHaveLength(7);
  });
});
