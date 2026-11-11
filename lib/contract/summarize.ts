// คำตอบของ POST /api/summarize ฝั่งเว็บ (Zod, สัญญา v2 ADR 0017) ให้ตรงกับ lib/contract/summarize-response.schema.json
// ข้อความภาษาไทยต้องเหมือน ERROR_MESSAGES_TH ใน src/tmd_plain/contract.py (summarize.test.ts ตรวจ)
import { z } from "zod";

import {
  genericDocumentSchema,
  shippingIssueSchema,
  traceSchema,
  warningNoticeSchema,
  weeklySummarySchema,
} from "@/lib/contract/documents";
import { issueSchema } from "@/lib/contract/issue";

export const ERROR_CODES = ["unsupported_document", "too_large", "extract_failed", "empty_file"] as const;
export const errorCodeSchema = z.enum(ERROR_CODES);
export type ErrorCode = z.infer<typeof errorCodeSchema>;

export const ERROR_MESSAGES_TH: Record<ErrorCode, string> = {
  unsupported_document: "ไฟล์นี้ไม่ใช่ PDF กรุณาเลือกไฟล์ PDF จากเว็บไซต์กรมอุตุนิยมวิทยา",
  too_large: "ไฟล์ใหญ่เกิน 4 MB กรุณาเลือกไฟล์พยากรณ์ฉบับเดียว",
  extract_failed: "อ่านหรือสรุปข้อความในไฟล์ไม่สำเร็จ ไฟล์อาจเป็นภาพสแกนที่ไม่มีข้อความหรือไฟล์เสีย กรุณาลองไฟล์อื่น",
  empty_file: "ไฟล์ว่างเปล่า กรุณาเลือกไฟล์ใหม่",
};

export const errorDetailSchema = z.strictObject({
  code: errorCodeSchema,
  message_th: z.string().min(1),
});

function ok<K extends string, D extends z.ZodType>(kind: K, document: D) {
  return z.strictObject({
    ok: z.literal(true),
    kind: z.literal(kind),
    document,
    trace: traceSchema.nullable().default(null),
  });
}

// แยกชนิดด้วย kind (Python: SummarizeOk = Annotated[..., discriminator="kind"])
export const summarizeOkSchema = z.discriminatedUnion("kind", [
  ok("issue", issueSchema),
  ok("shipping", shippingIssueSchema),
  ok("warning", warningNoticeSchema),
  ok("weekly", weeklySummarySchema),
  ok("generic", genericDocumentSchema),
]);
export const summarizeErrorSchema = z.strictObject({ ok: z.literal(false), error: errorDetailSchema });
export const summarizeResponseSchema = z.union([summarizeOkSchema, summarizeErrorSchema]);

export type SummarizeOk = z.infer<typeof summarizeOkSchema>;
export type SummarizeResponse = z.infer<typeof summarizeResponseSchema>;
