// สรุปรายสัปดาห์ (11.5): อ่าน query ของ /summaries แบบไม่เชื่อค่า + สร้างลิงก์ (ฟังก์ชันบริสุทธิ์)
import type { RegionKey } from "@/lib/contract/issue";
import { parseMonthParam } from "@/lib/history";

// รหัสฉบับ = รหัสรอบของหน้าเว็บ TMD DDMMYYYYHHMM
export const WEEKLY_ID = /^\d{12}$/;

export type SummariesQuery = { issue: string | null; month: string | null; region: RegionKey | null };

export function summariesHref({ issue, month, region }: SummariesQuery): string {
  const params = new URLSearchParams();
  if (issue) params.set("issue", issue);
  if (month) params.set("month", month);
  if (region) params.set("region", region);
  const query = params.toString();
  return query ? `/summaries?${query}` : "/summaries";
}

/** ค่าที่ไม่รู้จักหรือรูปแบบผิดใช้ค่าเริ่มต้น (ฉบับล่าสุด เดือนของฉบับ ทุกภาค) */
export function parseSummariesQuery(
  raw: Record<string, string | string[] | undefined>,
  isRegion: (v: unknown) => v is RegionKey,
): SummariesQuery {
  const issue = typeof raw.issue === "string" && WEEKLY_ID.test(raw.issue) ? raw.issue : null;
  const region = isRegion(raw.region) ? raw.region : null;
  return { issue, month: parseMonthParam(raw.month), region };
}

const CELL_LEAD = /^(\d+(?:\.\d+)?\s*(?:มม\.|[º°]\s*ซ\.))\s*(.*)$/;

/** ช่องตาราง "61.5 มม. ที่ อ.แม่สอด ..." -> ค่านำ "61.5 มม." กับส่วนที่เหลือ (ต่อกันได้ข้อความเดิมคำต่อคำ); ไม่ตรงรูป = null */
export function splitCellLead(text: string): { lead: string; rest: string } | null {
  const m = CELL_LEAD.exec(text);
  return m ? { lead: m[1], rest: m[2] } : null;
}

