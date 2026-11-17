// จัดรายการฉบับย้อนหลังเป็นกลุ่มตามวัน (ฟังก์ชันบริสุทธิ์) ใช้ป้ายวันที่ของ TMD ตรงๆ
// รายวัน: "ประจำวันที่ 16 พฤศจิกายน 2569 17.00 น." -> วัน "16 พฤศจิกายน 2569", รอบ "17.00 น."
// เดินเรือ: "ออกประกาศ 16 พฤศจิกายน 2569 13:00 น." -> วัน "16 พฤศจิกายน 2569", รอบ "13:00 น." (คงรูปเวลาของต้นฉบับ)
import type { IssueListItem } from "@/lib/forecast-rows";
import { bangkokMonthKey } from "@/lib/format/thai";

export type HistoryEntry = { issueId: string; label: string };
export type HistoryGroup = { day: string; entries: HistoryEntry[] };

const LABEL = /^(?:ประจำวันที่|ฉบับวันที่|ออกประกาศ)\s+(\d{1,2}\s+\S+\s+\d{4})(?:\s+(?:รอบ\s+)?(\d{1,2}[.:]\d{2})\s*น\.)?/;

export function splitLabel(sourceLabel: string): { day: string; time: string | null } {
  const m = LABEL.exec(sourceLabel.trim());
  if (!m) return { day: sourceLabel, time: null };
  return { day: m[1], time: m[2] ? `${m[2]} น.` : null };
}

/** เรียงตามลำดับที่ได้รับ (ใหม่สุดก่อน) รวมรอบของวันเดียวกันไว้กลุ่มเดียว */
export function groupByDay(items: IssueListItem[]): HistoryGroup[] {
  const groups: HistoryGroup[] = [];
  for (const item of items) {
    const { day, time } = splitLabel(item.sourceLabel);
    const last = groups.at(-1);
    const entry = { issueId: item.issueId, label: time ?? day };
    if (last && last.day === day) last.entries.push(entry);
    else groups.push({ day, entries: [entry] });
  }
  return groups;
}

// ---- ตัวเลือกรอบแบบรายเดือน (11.6) ----

/** คีย์เดือน "YYYY-MM" (ปี ค.ศ. เวลาไทย) ที่ใช้ใน URL ?month= */
export const MONTH_KEY = /^\d{4}-(0[1-9]|1[0-2])$/;

export type MonthCount = { month: string; count: number };

/** อ่านค่า ?month= แบบไม่เชื่อค่า: รูปแบบผิด = null (ใช้เดือนของฉบับที่เลือก/เดือนล่าสุด) */
export function parseMonthParam(raw: string | string[] | undefined): string | null {
  return typeof raw === "string" && MONTH_KEY.test(raw) ? raw : null;
}

/** นับฉบับต่อเดือน ใหม่สุดก่อน (ใช้กับข้อมูลที่อ่านจากไฟล์; ฐานข้อมูลนับด้วย SQL แบบเดียวกัน) */
export function countByMonth(items: { issuedAt: string }[]): MonthCount[] {
  const counts = new Map<string, number>();
  for (const item of items) {
    const month = bangkokMonthKey(item.issuedAt);
    counts.set(month, (counts.get(month) ?? 0) + 1);
  }
  return [...counts].map(([month, count]) => ({ month, count })).sort((a, b) => (a.month < b.month ? 1 : -1));
}

/**
 * เดือนที่ต้องแสดง: เดือนที่ขอถ้ามีข้อมูล ไม่ก็เดือนของฉบับที่เลือก ไม่ก็เดือนล่าสุด (ไม่มีข้อมูลเลย = null)
 * months เรียงใหม่สุดก่อน
 */
export function resolveMonth(months: MonthCount[], requested: string | null, selectedIssuedAt: string | null): string | null {
  if (requested && months.some((m) => m.month === requested)) return requested;
  if (selectedIssuedAt) {
    const own = bangkokMonthKey(selectedIssuedAt);
    if (months.some((m) => m.month === own)) return own;
  }
  return months[0]?.month ?? null;
}

/** เดือนก่อนหน้า (เก่ากว่า) และถัดไป (ใหม่กว่า) ที่มีข้อมูล; ไม่มี = null */
export function neighborMonths(months: MonthCount[], current: string): { older: string | null; newer: string | null } {
  const i = months.findIndex((m) => m.month === current);
  if (i < 0) return { older: null, newer: null };
  return { older: months[i + 1]?.month ?? null, newer: months[i - 1]?.month ?? null };
}

// ---- สรุปรายสัปดาห์ (11.5): ป้ายของฉบับคือช่วงสัปดาห์ "24 สิงหาคม 2569 - 30 สิงหาคม 2569" ----

const WEEK_LABEL = /^(\d{1,2})\s+(\S+)\s+(\d{4})\s*-\s*(\d{1,2})\s+(\S+)\s+(\d{4})$/;
const MONTH_SHORT: Record<string, string> = {
  มกราคม: "ม.ค.",
  กุมภาพันธ์: "ก.พ.",
  มีนาคม: "มี.ค.",
  เมษายน: "เม.ย.",
  พฤษภาคม: "พ.ค.",
  มิถุนายน: "มิ.ย.",
  กรกฎาคม: "ก.ค.",
  สิงหาคม: "ส.ค.",
  กันยายน: "ก.ย.",
  ตุลาคม: "ต.ค.",
  พฤศจิกายน: "พ.ย.",
  ธันวาคม: "ธ.ค.",
};

/** "24 สิงหาคม 2569 - 30 สิงหาคม 2569" -> "24-30 ส.ค. 2569" (ข้ามเดือน "28 ก.ย. - 4 ต.ค. 2569"); ไม่ตรงรูป = ป้ายเดิม */
export function weekShortLabel(sourceLabel: string): string {
  const m = WEEK_LABEL.exec(sourceLabel.trim());
  if (!m) return sourceLabel;
  const [, d1, m1, y1, d2, m2, y2] = m;
  const a = MONTH_SHORT[m1] ?? m1;
  const b = MONTH_SHORT[m2] ?? m2;
  if (m1 === m2 && y1 === y2) return `${Number(d1)}-${Number(d2)} ${b} ${y2}`;
  return `${Number(d1)} ${a}${y1 === y2 ? "" : ` ${y1}`} - ${Number(d2)} ${b} ${y2}`;
}

/** สัปดาห์ของเดือนที่เลือกเป็นกลุ่มเดียว (หนึ่งฉบับ = หนึ่งสัปดาห์ ไม่แยกวัน) */
export function groupWeeks(items: IssueListItem[], heading: string): HistoryGroup[] {
  if (items.length === 0) return [];
  return [{ day: heading, entries: items.map((i) => ({ issueId: i.issueId, label: weekShortLabel(i.sourceLabel) })) }];
}
