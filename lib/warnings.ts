// ประกาศเตือนภัย (11.4): รายการย่อ + เชื่อมฉบับต่อเนื่องเป็นเรื่องเดียว + จัดกลุ่มตามเดือน (ฟังก์ชันบริสุทธิ์)
// กติกาเชื่อมชุดเหมือน src/tmd_plain/doctypes/warning/series.py ทุกข้อ (ADR 0018: ไม่เก็บชุดในสัญญา คำนวณจากรายการ)
// lib/warnings.test.ts เทียบผลกับข้อมูลจริง: 155 ฉบับ -> 13 ชุด ปิด 12 ชุด (ตรง docs/results/warning-check.md)
import { z } from "zod";

import type { WarningNotice } from "@/lib/contract/documents";
import { thaiMonthYear } from "@/lib/format/thai";

export type WarningListItem = {
  issueId: string;
  title: string;
  seriesNo: number;
  noticeNo: string;
  issuedAt: string;
  // ข้อความช่วงที่มีผลตามต้นฉบับ (ไม่มีบรรทัดนี้ในต้นฉบับ = null)
  effectText: string | null;
  // เวลาฉบับต่อไป; null = ฉบับสุดท้ายของเหตุการณ์ (ต้นฉบับใช้ประโยค "ฉบับสุดท้าย" แทนบรรทัดฉบับต่อไป)
  nextIssueAt: string | null;
};

export type WarningSeries = {
  // รหัสชุด = รหัสของฉบับแรกที่มีในข้อมูล
  id: string;
  // เก่าสุดก่อน
  notices: WarningListItem[];
  closed: boolean;
  // ชุดที่ฉบับแรกในข้อมูลไม่ใช่ฉบับที่ 1 = ฉบับก่อนหน้าไม่ได้เก็บไว้
  completeStart: boolean;
};

export type WarningMonthGroup = { month: string; series: WarningSeries[] };

// ฉบับถัดไปของชุดต้องออกห่างฉบับก่อนไม่เกินนี้ (เท่า MAX_GAP ใน series.py)
const MAX_GAP_MS = 48 * 60 * 60 * 1000;

export const WARNING_ID = /^\d{4}_\d+$/;

/** payload เต็ม -> รายการย่อ (ใช้ตอนอ่านจากไฟล์ data/processed) */
export function toWarningListItem(notice: WarningNotice): WarningListItem {
  return {
    issueId: notice.issue_id,
    title: notice.title,
    seriesNo: notice.series_no,
    noticeNo: notice.notice_no,
    issuedAt: notice.issued_at,
    effectText: notice.effect?.text ?? null,
    nextIssueAt: notice.next_issue_at,
  };
}

const listRowSchema = z.object({
  issue_id: z.string().regex(WARNING_ID),
  issued_at: z.union([z.date(), z.string()]),
  title: z.string().min(1),
  series_no: z.number().int().min(1),
  notice_no: z.string().regex(/^\d+\/\d{4}$/),
  effect_text: z.string().nullable(),
  next_issue_at: z.string().nullable(),
});

/** แถวจากคิวรี Neon (เลือกเฉพาะฟิลด์ที่รายการใช้) -> รายการย่อ; ไม่ผ่านสัญญาโยนข้อผิดพลาด */
export function toWarningListItemFromRow(row: unknown): WarningListItem {
  const r = listRowSchema.parse(row);
  return {
    issueId: r.issue_id,
    title: r.title,
    seriesNo: r.series_no,
    noticeNo: r.notice_no,
    issuedAt: r.issued_at instanceof Date ? r.issued_at.toISOString() : r.issued_at,
    effectText: r.effect_text,
    nextIssueAt: r.next_issue_at,
  };
}

function noticeNumber(item: WarningListItem): number {
  return Number(item.issueId.split("_")[1]);
}

// เรียงตามเวลาออก แล้วเลขประกาศ (เหมือน _order ใน series.py)
function byTime(a: WarningListItem, b: WarningListItem): number {
  return Date.parse(a.issuedAt) - Date.parse(b.issuedAt) || noticeNumber(a) - noticeNumber(b) || (a.issueId < b.issueId ? -1 : 1);
}

/**
 * จัดประกาศเป็นชุดตามเวลาออก: ฉบับที่ n ต่อจากชุดที่ฉบับล่าสุดเป็น n-1 และออกห่างกันไม่เกิน 48 ชม.
 * หลายชุดเข้าเงื่อนไข = เลือกชุดที่บอกเวลาฉบับต่อไปตรงกับเวลาฉบับนี้ แล้วชุดที่หัวเรื่องเหมือนกัน แล้วชุดที่ออกใกล้กว่า
 * ฉบับที่ 1 เริ่มชุดใหม่เสมอ · ฉบับสุดท้ายปิดชุด · ผลเรียงเก่าสุดก่อน
 */
export function linkSeries(items: WarningListItem[]): WarningSeries[] {
  const series: WarningSeries[] = [];
  for (const notice of [...items].sort(byTime)) {
    const issued = Date.parse(notice.issuedAt);
    const open = series.filter((s) => {
      const last = s.notices.at(-1)!;
      const gap = issued - Date.parse(last.issuedAt);
      return !s.closed && last.seriesNo === notice.seriesNo - 1 && gap >= 0 && gap <= MAX_GAP_MS;
    });
    let chosen: WarningSeries;
    if (notice.seriesNo === 1 || open.length === 0) {
      chosen = { id: notice.issueId, notices: [], closed: false, completeStart: notice.seriesNo === 1 };
      series.push(chosen);
    } else {
      // คีย์เทียบแบบ tuple: เท่ากันค่อยดูข้อถัดไป
      const rank = (s: WarningSeries) => {
        const last = s.notices.at(-1)!;
        return [
          last.nextIssueAt !== null && Date.parse(last.nextIssueAt) === issued ? 0 : 1,
          last.title === notice.title ? 0 : 1,
          issued - Date.parse(last.issuedAt),
        ];
      };
      chosen = open.reduce((best, s) => {
        const a = rank(s);
        const b = rank(best);
        for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return a[i] < b[i] ? s : best;
        return best;
      });
    }
    chosen.notices.push(notice);
    chosen.closed = notice.nextIssueAt === null;
  }
  return series;
}

/** ลิงก์หน้า /warnings (ไม่ระบุฉบับ = ฉบับล่าสุด) */
export function warningsHref(issueId: string | null): string {
  return issueId ? `/warnings?issue=${issueId}` : "/warnings";
}

/** อ่าน ?issue= แบบไม่เชื่อค่า: รูปแบบผิด = ใช้ฉบับล่าสุด */
export function parseWarningQuery(raw: Record<string, string | string[] | undefined>): { issue: string | null } {
  const issue = raw.issue;
  return { issue: typeof issue === "string" && WARNING_ID.test(issue) ? issue : null };
}

/** ช่วงฉบับของชุดที่ผู้อ่านเห็น เช่น "ฉบับที่ 1-13" หรือ "ฉบับที่ 7" */
export function seriesRangeLabel(s: WarningSeries): string {
  const first = s.notices[0].seriesNo;
  const last = s.notices.at(-1)!.seriesNo;
  return first === last ? `ฉบับที่ ${first}` : `ฉบับที่ ${first}-${last}`;
}

/** ชุดที่ฉบับนี้อยู่ (ไม่พบ = undefined) */
export function seriesOf(series: WarningSeries[], issueId: string): WarningSeries | undefined {
  return series.find((s) => s.notices.some((n) => n.issueId === issueId));
}

/** ชุดเรียงตามฉบับล่าสุดของชุด ใหม่สุดก่อน แล้วจัดกลุ่มตามเดือนของฉบับล่าสุด (เดือน พ.ศ. ตามที่ผู้อ่านเห็น) */
export function groupSeriesByMonth(series: WarningSeries[]): WarningMonthGroup[] {
  const sorted = [...series].sort((a, b) => byTime(b.notices.at(-1)!, a.notices.at(-1)!));
  const groups: WarningMonthGroup[] = [];
  for (const s of sorted) {
    const month = thaiMonthYear(s.notices.at(-1)!.issuedAt);
    const last = groups.at(-1);
    if (last && last.month === month) last.series.push(s);
    else groups.push({ month, series: [s] });
  }
  return groups;
}
