// ตรรกะของหน้า /demo (ฟังก์ชันบริสุทธิ์ ทดสอบได้): ตรวจไฟล์ก่อนส่ง และแปลงคำตอบของ /api/summarize
import { ERROR_MESSAGES_TH, type ErrorCode, type SummarizeOk, summarizeResponseSchema } from "@/lib/contract/summarize";

// เท่ากับ max_upload_bytes ใน src/tmd_plain/config.toml (upload.test.ts ตรวจ) ต่ำกว่าเพดาน body 4.5 MB ของ Vercel
export const MAX_UPLOAD_BYTES = 4 * 1024 * 1024;
// ขอภาพขั้นตอนทุกครั้ง (เปิดเป็นค่าเริ่มต้นตามแผน 10.4) ผลสรุปเหมือนกันทุกไบต์ทั้งเปิด/ปิด
export const SUMMARIZE_URL = "/api/summarize?trace=1";
export const NETWORK_MESSAGE_TH = "ติดต่อระบบสรุปไม่สำเร็จ กรุณาลองใหม่อีกครั้ง";
// ชนิดที่สัญญารองรับแต่หน้านี้ยังไม่มีหน้าแสดงผล (เดินเรือ/เตือนภัย/สรุปรายสัปดาห์ มาในแผน 11)
export const PENDING_KIND_MESSAGE_TH =
  "ระบบอ่านเอกสารนี้ได้แล้ว แต่หน้านี้ยังแสดงผลเอกสารชนิดนี้ไม่ได้ การแสดงผลจะเพิ่มในรุ่นถัดไป";

export type FileInfo = { name: string; size: number; type: string };

// ชนิดที่หน้านี้แสดงผลได้: ผลสรุปเต็มของรายวัน/7 วัน และโหมดทั่วไป
export type ShownResult = Extract<SummarizeOk, { kind: "issue" | "generic" }>;

export type UploadOutcome =
  | { kind: "ok"; result: ShownResult }
  | { kind: "error"; code: ErrorCode; message: string }
  | { kind: "network"; message: string }
  | { kind: "notice"; message: string };

/** ตรวจในเบราว์เซอร์ก่อนส่ง: ไม่ผ่านคืนรหัสตามสัญญา (ข้อความเดียวกับที่ฟังก์ชันตอบ) ผ่านคืน null */
export function checkFile(file: FileInfo): ErrorCode | null {
  if (file.size === 0) return "empty_file";
  if (file.size > MAX_UPLOAD_BYTES) return "too_large";
  const looksPdf = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
  return looksPdf ? null : "unsupported_document";
}

export function errorOutcome(code: ErrorCode): UploadOutcome {
  return { kind: "error", code, message: ERROR_MESSAGES_TH[code] };
}

/** คำตอบที่ไม่ผ่านสัญญา (เช่น หน้า 404/413 ของแพลตฟอร์มที่ไม่ใช่ JSON ของเรา) = ติดต่อระบบไม่สำเร็จ */
export function readResponse(body: unknown): UploadOutcome {
  const parsed = summarizeResponseSchema.safeParse(body);
  if (!parsed.success) return { kind: "network", message: NETWORK_MESSAGE_TH };
  if (parsed.data.ok) {
    const result = parsed.data;
    if (result.kind === "issue" || result.kind === "generic") return { kind: "ok", result };
    // ชนิดที่ยังไม่มีหน้าแสดงผล บอกตรงๆ ไม่ใช่ข้อผิดพลาด
    return { kind: "notice", message: PENDING_KIND_MESSAGE_TH };
  }
  return { kind: "error", code: parsed.data.error.code, message: parsed.data.error.message_th };
}

/** ขนาดไฟล์อ่านง่าย เช่น "312 KB", "4.2 MB" */
export function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
