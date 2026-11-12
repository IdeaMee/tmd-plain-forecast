import "server-only";

import { modelReportSchema, type ModelReportId, type SentenceRoleReport } from "@/lib/contract/model-report";
import raw from "@/lib/generated/model-report.json";

// ชั้นข้อมูลของหน้า /model: ไฟล์ที่สคริปต์สร้าง (ไม่อ่าน DB) ตรวจด้วย Zod ครั้งเดียวตอนโหลดโมดูล
// ไฟล์ผิดรูป = throw ตอน build ไม่ส่งตัวเลขที่ไม่ผ่านสัญญาไปหน้าเว็บ
const report = modelReportSchema.parse(raw);

// sentence-role = ประโยคของรายวัน/7 วัน (หน้า /model) · warning-role = ท่อนของประกาศเตือนภัย (/model/warning, 11.3)
export function getModelReport(id: ModelReportId): SentenceRoleReport {
  const item = report.models.find((m) => m.id === id);
  if (!item) throw new Error(`model-report.json ไม่มีโมเดล ${id}`);
  return item;
}
