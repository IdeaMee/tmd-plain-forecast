// e2e หน้า /model (Phase 8.2): ครบทุกส่วน ตัวเลขตรงกับ model-report.json ไม่มี scroll แนวนอน
import { readFileSync } from "node:fs";
import path from "node:path";

import { expect, test } from "@playwright/test";

const MODELS = JSON.parse(readFileSync(path.resolve("lib/generated/model-report.json"), "utf-8")).models;
const REPORT = MODELS[0];
const WARNING = MODELS.find((m: { id: string }) => m.id === "warning-role");
const pct = (x: number) => `${(x * 100).toFixed(1)}%`;

test("ครบ 9 ส่วน และความแม่นบนหน้าตรงกับไฟล์รายงาน", async ({ page }) => {
  const res = await page.goto("/model");
  expect(res?.status()).toBe(200);
  await expect(page.getByRole("heading", { level: 1, name: "โมเดลทำงานอย่างไร" })).toBeVisible();
  for (let n = 1; n <= 9; n++) await expect(page.getByText(`ส่วนที่ ${n}`, { exact: true })).toBeVisible();
  const chosen = REPORT.results.find((r: { name: string }) => r.name === REPORT.chosen);
  await expect(page.getByText(pct(chosen.test_new)).first()).toBeVisible();
  // ทุกหน่วยที่ทายผิดอยู่ในส่วนที่ 9 (ประโยคเดียวกันอาจอยู่ในตัวอย่างของส่วน 5-6 ด้วย)
  const limits = page.getByRole("region", { name: "จุดที่ทายผิดและข้อจำกัด" });
  for (const m of REPORT.mistakes) await expect(limits.getByText(m.text, { exact: true })).toBeVisible();
  // ข้อจำกัดเรื่องกฎ keyword ต้องขึ้น (หาแถวกฎจากชื่อขึ้นต้น "กฎ" ถ้าเปลี่ยนชื่อในรายงาน ข้อนี้จะเตือน)
  await expect(limits.getByText(/^กฎคำสำคัญได้/)).toBeVisible();
  // ตารางสับสนครบทุกวิธี
  for (const c of REPORT.confusion) await expect(page.getByText(`ตารางสับสน: ${c.name}`)).toBeVisible();
  // กราฟเส้นมีตารางคู่
  await page.getByText("ดูเป็นตาราง").click();
  await expect(page.getByRole("columnheader", { name: "ส่วนของชุดฝึก" })).toBeVisible();
});

test("แท็บประกาศเตือนภัย (11.3): ครบ 9 ส่วน ตัวเลขตรงกับรายงาน สลับแท็บได้", async ({ page }) => {
  await page.goto("/model");
  const tabs = page.getByRole("navigation", { name: "เลือกโมเดล" });
  await expect(tabs.getByRole("link", { name: "พยากรณ์รายวัน/7 วัน" })).toHaveAttribute("aria-current", "page");
  await tabs.getByRole("link", { name: "ประกาศเตือนภัย" }).click();
  await expect(page).toHaveURL(/\/model\/warning$/);
  // ระหว่างเปลี่ยนหน้า (view transition) หน้าเก่ายังอยู่ชั่วครู่: ดูเฉพาะ main ของหน้าใหม่
  const main = page.getByRole("main");
  await expect(main.getByRole("heading", { level: 2, name: WARNING.title_th })).toBeVisible();
  for (let n = 1; n <= 9; n++) await expect(main.getByText(`ส่วนที่ ${n}`, { exact: true })).toBeVisible();
  for (const r of WARNING.results) await expect(main.getByText(pct(r.test_new)).first()).toBeVisible();
  for (const c of WARNING.confusion) await expect(main.getByText(`ตารางสับสน: ${c.name}`)).toBeVisible();
  const limits = main.getByRole("region", { name: "จุดที่ทายผิดและข้อจำกัด" });
  for (const m of WARNING.mistakes) await expect(limits.getByText(m.text, { exact: true })).toBeVisible();
  // ไม่มีป้าย "อื่นๆ" ในชุดนี้ จึงไม่มีข้อจำกัดเรื่องป้ายนั้น
  await expect(limits.getByText(/อื่นๆ/)).toHaveCount(0);
  for (const width of [320, 375, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow, `width ${width}`).toBeLessThanOrEqual(0);
    await page.screenshot({ path: `test-results/screens/model-warning-${width}.png`, fullPage: true, animations: "disabled" });
  }
});

test("เข้าจากเมนู ความรู้ → โมเดลทำงานอย่างไร", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "เมนูหลัก" });
  await nav.getByRole("button", { name: "ความรู้" }).click();
  await nav.getByRole("link", { name: /โมเดลทำงานอย่างไร/ }).click();
  await expect(page).toHaveURL(/\/model$/);
});

for (const width of [320, 375, 768, 1280]) {
  test(`ไม่มี scroll แนวนอนที่ ${width}px + ภาพหน้าจอ`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/model");
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(0);
    await page.screenshot({ path: `test-results/screens/model-${width}.png`, fullPage: true, animations: "disabled" });
  });
}
