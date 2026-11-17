// หน้า /summaries (11.5) อ่าน data/processed/weekly (100 ฉบับ ฉบับล่าสุด 161120261100 สัปดาห์ 9-15 พ.ย. 2569)
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";

import { expect, test } from "@playwright/test";

const DIR = path.resolve("data/processed/weekly");
const read = (id: string) => JSON.parse(readFileSync(path.join(DIR, `${id}.json`), "utf-8"));
const ALL = readdirSync(DIR)
  .filter((f) => f.endsWith(".json"))
  .map((f) => JSON.parse(readFileSync(path.join(DIR, f), "utf-8")));
const LATEST = read("161120261100");
// ภาคเหนือฉบับนี้ไม่มีช่องอุณหภูมิสูงสุด/ต่ำสุด (ช่องว่างในต้นฉบับ)
const SAMPLE = read("040920261100");
const CELL_KEYS = ["rain_max", "temp_max", "temp_min"] as const;

// เดือนตามเวลาไทยของเวลาออกฉบับ (เหมือน bangkokMonthKey ในเว็บ)
const monthOf = (iso: string) => new Date(Date.parse(iso) + 7 * 3600_000).toISOString().slice(0, 7);
const MONTHS = [...new Set(ALL.map((d) => monthOf(d.issued_at)))].sort().reverse();

test("ฉบับล่าสุด: ภาพรวม 7 ภาค ข้อความและค่าตารางคัดคำต่อคำ", async ({ page }) => {
  const res = await page.goto("/summaries");
  expect(res?.status()).toBe(200);
  await expect(page.getByRole("heading", { level: 1, name: "สรุปสภาพอากาศรายสัปดาห์" })).toBeVisible();
  await expect(page.getByText(`สัปดาห์ ${LATEST.source_label}`)).toBeVisible();
  await expect(page.getByText("สรุปล่าสุดในระบบ")).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "ภาพรวมทั้งประเทศ" })).toBeVisible();
  for (const line of LATEST.overview) await expect(page.getByText(line.text, { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(7);
  for (const region of Object.values(LATEST.regions) as { lines: { text: string }[]; rain_max: { text: string } | null }[]) {
    // .first(): ฉบับนี้ภาคกลางไม่มีย่อหน้า ต้นฉบับใส่ข้อความสถานีฝนแทน จึงซ้ำกับช่องตาราง (ดู docs/results/weekly-check.md)
    for (const line of region.lines) await expect(page.getByText(line.text, { exact: true }).first()).toBeVisible();
    if (region.rain_max) await expect(page.getByText(region.rain_max.text, { exact: true }).first()).toBeVisible();
  }
  await expect(page.getByText(/โอกาส.*%/)).toHaveCount(0);
  await expect(page.getByText("ตัวช่วยสรุป ไม่ใช่ประกาศทางการ").first()).toBeVisible();
});

test("เลือกภาค: เหลือการ์ดเดียว และ URL เปลี่ยน", async ({ page }) => {
  await page.goto("/summaries");
  await page.getByRole("navigation", { name: "เลือกภาค" }).getByRole("link", { name: "ภาคกลาง" }).click();
  await expect(page).toHaveURL(/\/summaries\?region=central$/);
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(1);
  await expect(page.getByRole("heading", { level: 3, name: "ภาคกลาง" })).toBeVisible();
  await page.getByRole("navigation", { name: "เลือกภาค" }).getByRole("link", { name: "ทุกภาค" }).click();
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(7);
});

test("ช่องตารางที่ต้นฉบับเว้นว่าง: บอกว่าไม่มีข้อมูลในฉบับนี้ ไม่แสดงเป็น 0", async ({ page }) => {
  await page.goto(`/summaries?issue=${SAMPLE.issue_id}`);
  await expect(page.getByText("สรุปย้อนหลัง")).toBeVisible();
  const blanks = (Object.values(SAMPLE.regions) as Record<string, unknown>[]).flatMap((r) => CELL_KEYS.filter((k) => r[k] === null));
  expect(blanks.length).toBeGreaterThan(0);
  await expect(page.getByText("ไม่มีข้อมูลในฉบับนี้", { exact: true })).toHaveCount(blanks.length);
  // หัวแถวของ TMD ครบทุกการ์ด
  await expect(page.getByRole("rowheader", { name: "ปริมาณฝนสูงสุด" })).toHaveCount(7);
});

test("ตัวเลือกสัปดาห์รายเดือน: เปิดเดือนเก่าสุด เลือกสัปดาห์แล้วได้ฉบับนั้น", async ({ page }) => {
  expect(MONTHS.length).toBeGreaterThan(6);
  await page.goto("/summaries");
  const picker = page.getByText(/^เลือกสัปดาห์อื่น/);
  await expect(picker).toContainText(`ทั้งหมด ${ALL.length} ฉบับ ใน ${MONTHS.length} เดือน`);
  await picker.click();
  const months = page.getByRole("list", { name: "ทุกเดือนที่มีข้อมูล" });
  await expect(months.getByRole("link")).toHaveCount(MONTHS.length);
  const oldest = MONTHS.at(-1)!;
  // ตัวเลือกเรียงใหม่สุดก่อน
  const inOldest = ALL.filter((d) => monthOf(d.issued_at) === oldest).sort((a, b) => Date.parse(b.issued_at) - Date.parse(a.issued_at));
  await months.getByRole("link").last().click();
  await expect(page).toHaveURL(new RegExp(`month=${oldest}`));
  // เลือกเดือนแล้วกล่องยังเปิดอยู่ และมีสัปดาห์ของเดือนนั้นครบ
  const weeks = page.getByRole("region", { name: /^ฉบับของ/ });
  await expect(weeks.getByRole("link")).toHaveCount(inOldest.length);
  // ไม่มีเดือนเก่ากว่า: ไม่มีลิงก์ "เดือนก่อน"
  await expect(page.getByRole("link", { name: /เดือนก่อน/ })).toHaveCount(0);
  await expect(page.getByRole("link", { name: /เดือนถัดไป/ })).toHaveCount(1);
  const first = inOldest[0];
  await weeks.getByRole("link").first().click();
  await expect(page).toHaveURL(new RegExp(`issue=${first.issue_id}`));
  await expect(page.getByText(`สัปดาห์ ${first.source_label}`)).toBeVisible();
  await expect(page.getByText("สรุปย้อนหลัง")).toBeVisible();
});

test("รหัสผิดรูปใช้ฉบับล่าสุด ส่วนรหัสที่ไม่มีในระบบบอกว่าไม่พบ พร้อมทางกลับ", async ({ page }) => {
  await page.goto("/summaries?issue=abc&month=2026-13");
  await expect(page.getByText("สรุปล่าสุดในระบบ")).toBeVisible();
  await page.goto("/summaries?issue=999999999999");
  await expect(page.getByText("ไม่พบสรุปรายสัปดาห์ฉบับที่เลือก")).toBeVisible();
  await page.getByRole("link", { name: "ดูฉบับล่าสุด" }).click();
  await expect(page).toHaveURL(/\/summaries$/);
  await expect(page.getByText("สรุปล่าสุดในระบบ")).toBeVisible();
});

test("เข้าจากเมนู สรุปสภาพอากาศ → สรุปรายสัปดาห์", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "เมนูหลัก" });
  await nav.getByRole("button", { name: "สรุปสภาพอากาศ" }).click();
  await nav.getByRole("link", { name: /สรุปรายสัปดาห์/ }).click();
  await expect(page).toHaveURL(/\/summaries$/);
});

for (const width of [320, 375, 768, 1280]) {
  test(`ไม่มี scroll แนวนอนที่ ${width}px + ภาพหน้าจอ`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    for (const url of ["/summaries", `/summaries?issue=${SAMPLE.issue_id}`, "/summaries?region=south_east_coast"]) {
      await page.goto(url);
      await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
      await expect(page.getByRole("heading", { level: 2, name: "ภาพรวมทั้งประเทศ" })).toBeVisible();
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      expect(overflow, `${url} @${width}`).toBeLessThanOrEqual(0);
    }
    await page.goto("/summaries");
    await page.getByText(/^เลือกสัปดาห์อื่น/).click();
    await expect(page.getByRole("list", { name: "ทุกเดือนที่มีข้อมูล" })).toBeVisible();
    await page.screenshot({ path: `test-results/screens/summaries-${width}.png`, fullPage: true, animations: "disabled" });
  });
}
