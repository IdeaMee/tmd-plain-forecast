// แปลงแถวจากตาราง forecast_issue เป็นข้อมูลที่หน้าเว็บใช้ (ฟังก์ชันบริสุทธิ์ ทดสอบได้โดยไม่ต้องมี DB)
import { z } from "zod";

import { docTypeSchema, issueSchema, type DocType, type Issue } from "@/lib/contract/issue";

export type IssueListItem = {
  issueId: string;
  docType: DocType;
  issuedAt: string;
  sourceLabel: string;
};

/** payload (jsonb) -> Issue; ไม่ผ่านสัญญาโยนข้อผิดพลาด ไม่แสดงข้อมูลที่ตรวจไม่ผ่าน */
export function parseIssuePayload(payload: unknown): Issue {
  const value = typeof payload === "string" ? JSON.parse(payload) : payload;
  return issueSchema.parse(value);
}

const listRowSchema = z.object({
  issue_id: z.string(),
  doc_type: docTypeSchema,
  issued_at: z.union([z.date(), z.string()]),
  source_label: z.string().min(1),
});

export function toListItem(row: unknown): IssueListItem {
  const r = listRowSchema.parse(row);
  const issuedAt = r.issued_at instanceof Date ? r.issued_at.toISOString() : r.issued_at;
  return { issueId: r.issue_id, docType: r.doc_type, issuedAt, sourceLabel: r.source_label };
}
