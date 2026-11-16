// แปลงแถวจากตาราง forecast_issue เป็นข้อมูลที่หน้าเว็บใช้ (ฟังก์ชันบริสุทธิ์ ทดสอบได้โดยไม่ต้องมี DB)
import { z } from "zod";

import {
  shippingIssueSchema,
  warningNoticeSchema,
  weeklySummarySchema,
  type ShippingIssue,
  type WarningNotice,
  type WeeklySummary,
} from "@/lib/contract/documents";
import { issueSchema, type Issue } from "@/lib/contract/issue";
import { LOADED_DOC_TYPES, type LoadedDocType } from "@/lib/contract/stored";

export type IssueListItem = {
  issueId: string;
  docType: LoadedDocType;
  issuedAt: string;
  sourceLabel: string;
};

/** payload (jsonb) -> Issue; ไม่ผ่านสัญญาโยนข้อผิดพลาด ไม่แสดงข้อมูลที่ตรวจไม่ผ่าน */
export function parseIssuePayload(payload: unknown): Issue {
  const value = typeof payload === "string" ? JSON.parse(payload) : payload;
  return issueSchema.parse(value);
}

/** payload ของพยากรณ์เดินเรือ (11.1) -> ShippingIssue; ไม่ผ่านสัญญาโยนข้อผิดพลาด */
export function parseShippingPayload(payload: unknown): ShippingIssue {
  const value = typeof payload === "string" ? JSON.parse(payload) : payload;
  return shippingIssueSchema.parse(value);
}

/** payload ของประกาศเตือนภัย (11.4) -> WarningNotice; ไม่ผ่านสัญญาโยนข้อผิดพลาด */
export function parseWarningPayload(payload: unknown): WarningNotice {
  const value = typeof payload === "string" ? JSON.parse(payload) : payload;
  return warningNoticeSchema.parse(value);
}

/** payload ของสรุปรายสัปดาห์ (11.5) -> WeeklySummary; ไม่ผ่านสัญญาโยนข้อผิดพลาด */
export function parseWeeklyPayload(payload: unknown): WeeklySummary {
  const value = typeof payload === "string" ? JSON.parse(payload) : payload;
  return weeklySummarySchema.parse(value);
}

const listRowSchema = z.object({
  issue_id: z.string(),
  doc_type: z.enum(LOADED_DOC_TYPES),
  issued_at: z.union([z.date(), z.string()]),
  source_label: z.string().min(1),
});

export function toListItem(row: unknown): IssueListItem {
  const r = listRowSchema.parse(row);
  const issuedAt = r.issued_at instanceof Date ? r.issued_at.toISOString() : r.issued_at;
  return { issueId: r.issue_id, docType: r.doc_type, issuedAt, sourceLabel: r.source_label };
}
