// สัญญาข้อมูล v2 ฝั่งเว็บ (Zod, ADR 0017) เขียนมือให้ตรงกับ lib/contract/summarize-response.schema.json
// documents.test.ts ตรวจชื่อฟิลด์เทียบ JSON Schema และไฟล์ตัวอย่างใน tests/fixtures/contract
import { z } from "zod";

import { factValueSchema, regionKeySchema, summaryLineSchema } from "./issue.ts";

export const STORED_DOC_TYPES = ["daily", "sevenday", "shipping", "warning", "weekly"] as const;
export const RESULT_KINDS = ["issue", "shipping", "warning", "weekly", "generic"] as const;

export const SEA_AREA_KEYS = ["gulf_of_thailand", "andaman_malacca", "kota_bharu_singapore", "ca_mau_cape"] as const;
// ต้องเหมือน SEA_AREA_LABELS_TH ใน src/tmd_plain/contract.py (documents.test.ts ตรวจกับข้อความใน contract.py)
export const SEA_AREA_LABELS_TH: Record<(typeof SEA_AREA_KEYS)[number], string> = {
  gulf_of_thailand: "อ่าวไทยทั้งสองฝั่ง",
  andaman_malacca: "ทะเลอันดามันและช่องแคบมะละกา",
  kota_bharu_singapore: "เส้นทางเดินเรือโกตาบารูถึงสิงคโปร์",
  ca_mau_cape: "ปลายแหลมญวน",
};

export const TRACE_STEP_IDS = [
  "read_pdf",
  "clean",
  "detect_type",
  "segment",
  "units",
  "tokenize",
  "filter_tokens",
  "classify",
  "scope",
  "extract",
  "template",
  "verify",
  "result",
] as const;

// เพดาน trace (ข้อตัดสินใจ V4 ข) ต้องเท่ากับ TRACE_MAX_BYTES / TRACE_MAX_ITEMS ใน contract.py
export const TRACE_MAX_BYTES = 256 * 1024;
export const TRACE_MAX_ITEMS = 50;

export const seaAreaKeySchema = z.enum(SEA_AREA_KEYS);
export const unitLabelSchema = z.enum(["weather", "advice", "cause", "other"]);
const isoDateTime = z.iso.datetime({ offset: true });

function unique(items: readonly string[]): boolean {
  return new Set(items).size === items.length;
}

export const quotedAdviceSchema = z
  .strictObject({
    // คัดจากต้นฉบับตรงๆ ห้ามเขียนเอง
    text: z.string().min(1),
    regions: z.array(regionKeySchema).default([]),
    source_unit_id: z.string().min(1),
  })
  .refine((a) => unique(a.regions), { message: "regions มีค่าซ้ำ" });

export const seaPartSchema = z.strictObject({
  name_th: z.string().min(1),
  lines: z.array(summaryLineSchema).min(1),
});

export const seaAreaSchema = z
  .strictObject({
    name_th: z.string().min(1),
    lines: z.array(summaryLineSchema).default([]),
    parts: z.array(seaPartSchema).default([]),
  })
  .refine((a) => a.lines.length > 0 || a.parts.length > 0, { message: "พื้นที่ทะเลต้องมี lines หรือ parts" });

export const shippingIssueSchema = z
  .strictObject({
    issue_id: z.string().regex(/^\d{12}$/),
    doc_type: z.literal("shipping"),
    issued_at: isoDateTime,
    source_label: z.string().min(1),
    overview: z.array(summaryLineSchema).default([]),
    areas: z.record(seaAreaKeySchema, seaAreaSchema),
    advice: z.array(quotedAdviceSchema).default([]),
    pipeline_version: z.string().min(1),
  })
  .superRefine((doc, ctx) => {
    for (const key of SEA_AREA_KEYS) {
      if (doc.areas[key].name_th !== SEA_AREA_LABELS_TH[key]) {
        ctx.addIssue({ code: "custom", message: `ชื่อพื้นที่ ${key} ไม่ตรงต้นฉบับ` });
      }
    }
  });

export const effectPeriodSchema = z
  .strictObject({
    text: z.string().min(1),
    start: z.iso.date().nullable().default(null),
    end: z.iso.date().nullable().default(null),
  })
  .refine((e) => !e.start || !e.end || e.start <= e.end, { message: "start ต้องไม่หลัง end" });

export const warningNoticeSchema = z
  .strictObject({
    issue_id: z.string().regex(/^\d{4}_\d+$/),
    doc_type: z.literal("warning"),
    issued_at: isoDateTime,
    source_label: z.string().min(1),
    title: z.string().min(1),
    series_no: z.number().int().min(1),
    notice_no: z.string().regex(/^\d+\/\d{4}$/),
    // ไม่มีบรรทัดช่วงที่มีผลในต้นฉบับ = null (ADR 0018)
    effect: effectPeriodSchema.nullable().default(null),
    next_issue_at: isoDateTime.nullable().default(null),
    regions: z.array(regionKeySchema).default([]),
    provinces: z.array(z.string()).default([]),
    lines: z.array(summaryLineSchema).default([]),
    precautions: z.array(quotedAdviceSchema).default([]),
    pipeline_version: z.string().min(1),
  })
  .superRefine((doc, ctx) => {
    const [number, year] = doc.notice_no.split("/");
    if (doc.issue_id !== `${year}_${number}`) {
      ctx.addIssue({ code: "custom", message: "issue_id ต้องตรงกับ notice_no" });
    }
    if (doc.next_issue_at && Date.parse(doc.next_issue_at) <= Date.parse(doc.issued_at)) {
      ctx.addIssue({ code: "custom", message: "next_issue_at ต้องหลัง issued_at" });
    }
    if (!unique(doc.regions) || !unique(doc.provinces)) {
      ctx.addIssue({ code: "custom", message: "regions/provinces มีค่าซ้ำ" });
    }
  });

export const tableCellSchema = z.strictObject({
  text: z.string().min(1),
  facts: z.record(z.string(), factValueSchema).default({}),
});

export const weeklyRegionSchema = z.strictObject({
  lines: z.array(summaryLineSchema).default([]),
  rain_max: tableCellSchema.nullable().default(null),
  temp_max: tableCellSchema.nullable().default(null),
  temp_min: tableCellSchema.nullable().default(null),
});

export const weeklySummarySchema = z
  .strictObject({
    issue_id: z.string().regex(/^\d{12}$/),
    doc_type: z.literal("weekly"),
    issued_at: isoDateTime,
    source_label: z.string().min(1),
    week_start: z.iso.date(),
    week_end: z.iso.date(),
    overview: z.array(summaryLineSchema).default([]),
    regions: z.record(regionKeySchema, weeklyRegionSchema),
    pipeline_version: z.string().min(1),
  })
  .refine((doc) => doc.week_start <= doc.week_end, { message: "week_start ต้องไม่หลัง week_end" });

export const genericUnitSchema = z.strictObject({
  unit_id: z.string().min(1),
  text: z.string().min(1),
  label: unitLabelSchema,
  confidence: z.number().min(0).max(1),
  uncertain: z.boolean(),
  regions: z.array(regionKeySchema).default([]),
  provinces: z.array(z.string()).default([]),
  numbers: z.array(z.string()).default([]),
  dates: z.array(z.string()).default([]),
});

export const genericSectionSchema = z.strictObject({
  heading: z.string().nullable().default(null),
  units: z.array(genericUnitSchema).default([]),
});

export const glossaryEntrySchema = z.strictObject({
  term: z.string().min(1),
  explanation: z.string().min(1),
});

export const genericDocumentSchema = z
  .strictObject({
    title: z.string().nullable().default(null),
    tmd_like: z.boolean(),
    warnings: z.array(z.literal("not_tmd_like")).default([]),
    page_count: z.number().int().min(1),
    char_count: z.number().int().min(0),
    has_region_headings: z.boolean(),
    sections: z.array(genericSectionSchema).default([]),
    glossary: z.array(glossaryEntrySchema).default([]),
    truncated: z.boolean().default(false),
  })
  .superRefine((doc, ctx) => {
    if (doc.warnings.includes("not_tmd_like") === doc.tmd_like) {
      ctx.addIssue({ code: "custom", message: "warnings ต้องมี not_tmd_like เมื่อ tmd_like=false เท่านั้น" });
    }
    if (!unique(doc.sections.flatMap((s) => s.units.map((u) => u.unit_id)))) {
      ctx.addIssue({ code: "custom", message: "unit_id มีค่าซ้ำ" });
    }
  });

const traceValueSchema = z.union([
  z.string(),
  z.number(),
  z.boolean(),
  z.array(z.string()),
  z.array(z.number()),
  z.record(z.string(), z.number()),
]);

export const traceStepSchema = z
  .strictObject({
    id: z.enum(TRACE_STEP_IDS),
    title_th: z.string().min(1),
    status: z.enum(["done", "skipped", "failed"]),
    note_th: z.string().default(""),
    data: z.record(z.string(), traceValueSchema).default({}),
  })
  .refine(
    (step) =>
      Object.values(step.data).every(
        (v) => typeof v !== "object" || (Array.isArray(v) ? v : Object.keys(v)).length <= TRACE_MAX_ITEMS,
      ),
    { message: `trace รายการเกิน ${TRACE_MAX_ITEMS} ชิ้น` },
  );

export const traceSchema = z
  .strictObject({
    steps: z.array(traceStepSchema).default([]),
    truncated: z.boolean().default(false),
  })
  .refine((t) => unique(t.steps.map((s) => s.id)), { message: "step id ซ้ำ" })
  .refine((t) => new TextEncoder().encode(JSON.stringify(t)).length <= TRACE_MAX_BYTES, {
    message: `trace ใหญ่เกิน ${TRACE_MAX_BYTES} ไบต์`,
  });

export type SeaAreaKey = z.infer<typeof seaAreaKeySchema>;
export type QuotedAdvice = z.infer<typeof quotedAdviceSchema>;
export type ShippingIssue = z.infer<typeof shippingIssueSchema>;
export type WarningNotice = z.infer<typeof warningNoticeSchema>;
export type WeeklySummary = z.infer<typeof weeklySummarySchema>;
export type WeeklyRegion = z.infer<typeof weeklyRegionSchema>;
export type TableCell = z.infer<typeof tableCellSchema>;
export type GenericDocument = z.infer<typeof genericDocumentSchema>;
export type Trace = z.infer<typeof traceSchema>;
