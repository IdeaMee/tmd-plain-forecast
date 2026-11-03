// จัดรูปข้อความไทย (ฟังก์ชันบริสุทธิ์): วันที่ พ.ศ. เวลาไทย ชื่อภาค ชื่อชนิดบรรทัด
import { REGION_KEYS, type LineKind, type RegionKey } from "@/lib/contract/issue";

const MONTHS = [
  "มกราคม",
  "กุมภาพันธ์",
  "มีนาคม",
  "เมษายน",
  "พฤษภาคม",
  "มิถุนายน",
  "กรกฎาคม",
  "สิงหาคม",
  "กันยายน",
  "ตุลาคม",
  "พฤศจิกายน",
  "ธันวาคม",
];
const MONTHS_SHORT = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];

export const REGION_LABELS: Record<RegionKey, string> = {
  north: "ภาคเหนือ",
  northeast: "ภาคตะวันออกเฉียงเหนือ",
  central: "ภาคกลาง",
  east: "ภาคตะวันออก",
  south_east_coast: "ภาคใต้ฝั่งตะวันออก",
  south_west_coast: "ภาคใต้ฝั่งตะวันตก",
  bangkok_vicinity: "กรุงเทพมหานครและปริมณฑล",
};

export const LINE_KIND_LABELS: Record<LineKind, string> = {
  rain: "ฝน",
  temperature: "อุณหภูมิ",
  wind: "ลม",
  wave: "คลื่น",
  fog: "หมอก",
  other: "ท้องฟ้า",
};

export function isRegionKey(value: unknown): value is RegionKey {
  return typeof value === "string" && (REGION_KEYS as readonly string[]).includes(value);
}

// เวลาไทย (UTC+7 ไม่มีเวลาออมแสง) คำนวณเองเพื่อให้ผลเท่ากันทุกเครื่อง
function bangkokParts(iso: string) {
  const d = new Date(new Date(iso).getTime() + 7 * 60 * 60 * 1000);
  return {
    day: d.getUTCDate(),
    month: d.getUTCMonth(),
    year: d.getUTCFullYear() + 543,
    hour: d.getUTCHours(),
    minute: d.getUTCMinutes(),
  };
}

/** เดือนปีสากลตามเวลาไทยของเวลาออกฉบับ "2026-11-16T18:00:00+07:00" -> "2026-11" (คีย์เดือนของตัวเลือกรอบ) */
export function bangkokMonthKey(iso: string): string {
  const p = bangkokParts(iso);
  return `${p.year - 543}-${String(p.month + 1).padStart(2, "0")}`;
}

/** คีย์เดือน "2026-11" -> "พฤศจิกายน 2569" (ไม่ใช่คีย์ที่ถูกต้อง = ส่งคืนตามเดิม) */
export function thaiMonthOfKey(key: string): string {
  const m = /^(\d{4})-(0[1-9]|1[0-2])$/.exec(key);
  return m ? `${MONTHS[Number(m[2]) - 1]} ${Number(m[1]) + 543}` : key;
}

/** "2026-11-16T18:00:00+07:00" -> "16 พฤศจิกายน 2569" */
export function thaiDate(iso: string): string {
  const p = bangkokParts(iso);
  return `${p.day} ${MONTHS[p.month]} ${p.year}`;
}

/** "2026-11-16T18:00:00+07:00" -> "พฤศจิกายน 2569" */
export function thaiMonthYear(iso: string): string {
  const p = bangkokParts(iso);
  return `${MONTHS[p.month]} ${p.year}`;
}

/** "2026-11-16T18:00:00+07:00" -> "16 พ.ย. 2569 18.00 น." */
export function thaiDateTimeShort(iso: string): string {
  const p = bangkokParts(iso);
  const hh = String(p.hour).padStart(2, "0");
  const mm = String(p.minute).padStart(2, "0");
  return `${p.day} ${MONTHS_SHORT[p.month]} ${p.year} ${hh}.${mm} น.`;
}

/** ช่วงวันของฉบับ 7 วัน "2026-11-17", "2026-11-19" -> "17-19 พ.ย. 2569" */
export function thaiDateRange(start: string, end: string): string {
  const [ys, ms, ds] = start.split("-").map(Number);
  const [ye, me, de] = end.split("-").map(Number);
  const tail = `${MONTHS_SHORT[me - 1]} ${ye + 543}`;
  if (start === end) return `${de} ${tail}`;
  if (ys === ye && ms === me) return `${ds}-${de} ${tail}`;
  return `${ds} ${MONTHS_SHORT[ms - 1]}${ys === ye ? "" : ` ${ys + 543}`} - ${de} ${tail}`;
}
