// จัดรายการฉบับย้อนหลังเป็นกลุ่มตามวัน (ฟังก์ชันบริสุทธิ์) ใช้ป้ายวันที่ของ TMD ตรงๆ
// รายวัน: "ประจำวันที่ 16 พฤศจิกายน 2569 17.00 น." -> วัน "16 พฤศจิกายน 2569", รอบ "17.00 น."
import type { IssueListItem } from "@/lib/forecast-rows";

export type HistoryEntry = { issueId: string; label: string };
export type HistoryGroup = { day: string; entries: HistoryEntry[] };

const LABEL = /^(?:ประจำวันที่|ฉบับวันที่)\s+(\d{1,2}\s+\S+\s+\d{4})(?:\s+(?:รอบ\s+)?(\d{1,2}\.\d{2})\s*น\.)?/;

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
