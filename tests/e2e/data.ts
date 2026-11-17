// ตัวช่วยอ่านข้อมูลจริงใน data/processed ให้เทสต์ e2e ไม่ตรึงว่า "ฉบับล่าสุด" คือวันไหน (ข้อมูลโตตามที่เก็บ)
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";

import { expect, type Page } from "@playwright/test";

export type Processed = { issue_id: string; doc_type: string; issued_at: string; source_label: string };

export function loadProcessed(docType: string): Processed[] {
  const dir = path.resolve("data/processed", docType);
  return readdirSync(dir)
    .filter((f) => f.endsWith(".json"))
    .map((f) => JSON.parse(readFileSync(path.join(dir, f), "utf-8")) as Processed)
    .sort((a, b) => Date.parse(b.issued_at) - Date.parse(a.issued_at) || (a.issue_id < b.issue_id ? 1 : -1));
}

/** เดือนตามเวลาไทยของเวลาออกฉบับ (เหมือน bangkokMonthKey ในเว็บ) */
export const monthOf = (iso: string) => new Date(Date.parse(iso) + 7 * 3600_000).toISOString().slice(0, 7);

/** วันที่ในป้ายของ TMD เช่น "16 พฤศจิกายน 2569" (ตัวเลือกรอบแบบปฏิทินใช้ป้ายนี้เรียกวัน) */
export const dayOf = (label: string) => /(\d{1,2}\s+\S+\s+\d{4})/.exec(label)![1];

/**
 * เลือกฉบับในตัวเลือกรอบแบบปฏิทิน (ต้องเปิดลิ้นชักและอยู่เดือนของฉบับนั้นแล้ว)
 * วันที่มีหลายรอบ: กดวันก่อนจึงเห็นปุ่มเวลา · วันที่มีรอบเดียว: ช่องวันเป็นลิงก์ตรง
 */
export async function chooseIssue(page: Page, docs: Processed[], doc: Processed) {
  const day = dayOf(doc.source_label);
  const month = monthOf(doc.issued_at);
  // นับรอบเฉพาะของเดือนที่แสดง (ฉบับ 23.00 น. ของวันสิ้นเดือนที่ออกหลังเที่ยงคืนถูกนับเป็นเดือนถัดไป และอยู่นอกช่องวัน)
  const rounds = docs.filter((d) => dayOf(d.source_label) === day && monthOf(d.issued_at) === month && inCalendar(d)).length;
  if (rounds > 1) await page.getByRole("button", { name: `${day} มี ${rounds} รอบ`, exact: true }).click();
  await page.locator(`a[href*="issue=${doc.issue_id}"]`).click();
}

const THAI_MONTHS = [
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

/** เดือน "YYYY-MM" (ค.ศ.) ที่ป้ายวันของ TMD บอก (ต่างจากเดือนของเวลาออกฉบับได้ เมื่อออกหลังเที่ยงคืน) */
const labelMonthOf = (label: string) => {
  const m = /(\d{1,2})\s+(\S+)\s+(\d{4})/.exec(label)!;
  return `${Number(m[3]) - 543}-${String(THAI_MONTHS.indexOf(m[2]) + 1).padStart(2, "0")}`;
};

/** ฉบับที่อยู่ในช่องวันของปฏิทิน = ป้ายวันตรงกับเดือนของเวลาออกฉบับ */
const inCalendar = (d: Processed) => labelMonthOf(d.source_label) === monthOf(d.issued_at);

/** จำนวนวันที่กดได้ในปฏิทินของเดือนที่เปิดอยู่ (ปุ่มวันหลายรอบ + ลิงก์วันรอบเดียว) ต้องเท่ากับจำนวนวันที่มีฉบับ */
export async function expectCalendarDays(page: Page, monthDocs: Processed[]) {
  const calendar = page.getByRole("region", { name: /^ฉบับของ/ }).getByRole("group", { name: /^ปฏิทิน/ });
  const days = new Set(monthDocs.filter(inCalendar).map((d) => dayOf(d.source_label))).size;
  await expect(calendar.locator("button, a")).toHaveCount(days);
}

/** เดือนที่มีฉบับ ใหม่สุดก่อน */
export function monthsOf(docs: Processed[]): string[] {
  return [...new Set(docs.map((d) => monthOf(d.issued_at)))].sort().reverse();
}
