// import แบบสัมพัทธ์ (.ts) เพราะ scripts/load-to-neon.mts รันด้วย node ตรงๆ ไม่รู้จัก @/
// เอกสารที่เก็บใน data/processed และตาราง forecast_issue แยกชนิดด้วย doc_type (สัญญา v2 หัวข้อ v2.8)
// ชนิดที่เว็บอ่านจากฐานข้อมูลแล้วเท่านั้น: ประกาศเตือนภัยเพิ่มใน 11.4, สรุปรายสัปดาห์ใน 11.5 (เกษตร/คาดหมายเพิ่มเมื่อแผน 12 ทำ)
import { z } from "zod";

import { shippingIssueSchema, warningNoticeSchema, weeklySummarySchema } from "./documents.ts";
import { issueSchema } from "./issue.ts";

export const LOADED_DOC_TYPES = ["daily", "sevenday", "shipping", "warning", "weekly"] as const;
export type LoadedDocType = (typeof LOADED_DOC_TYPES)[number];

export const storedDocumentSchema = z.discriminatedUnion("doc_type", [
  issueSchema,
  shippingIssueSchema,
  warningNoticeSchema,
  weeklySummarySchema,
]);
export type StoredDocument = z.infer<typeof storedDocumentSchema>;
