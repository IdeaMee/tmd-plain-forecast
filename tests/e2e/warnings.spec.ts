// หน้า /warnings (11.4) อ่าน data/processed/warning (155 ฉบับ 13 เหตุการณ์ ฉบับล่าสุด 2569_315 ฉบับที่ 7 ของเหตุการณ์ 2569_309)
import { readFileSync } from "node:fs";
import path from "node:path";

import { expect, test } from "@playwright/test";

const read = (id: string) => JSON.parse(readFileSync(path.resolve(`data/processed/warning/${id}.json`), "utf-8"));
const LATEST = read("2569_315");
const FINAL = read("2569_234");

test("ฉบับล่าสุด: หัวเรื่องของ TMD, ช่วงที่มีผล, ภาค, สถานการณ์ และข้อควรระวังคัดคำต่อคำ", async ({ page }) => {
  const res = await page.goto("/warnings");
  expect(res?.status()).toBe(200);
  await expect(page.getByRole("heading", { level: 1, name: "ประกาศเตือนภัย" })).toBeVisible();
  await expect(page.getByText("ประกาศล่าสุดในระบบ")).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: LATEST.title })).toBeVisible();
  await expect(page.getByText(`ประกาศเลขที่ ${LATEST.notice_no}`)).toBeVisible();
  await expect(page.getByText(LATEST.effect.text, { exact: true })).toBeVisible();
  await expect(page.getByRole("list", { name: "ภาคที่กล่าวถึง" }).getByRole("listitem")).toHaveCount(LATEST.regions.length);
  for (const p of LATEST.precautions) await expect(page.getByText(p.text, { exact: true })).toBeVisible();
  for (const l of LATEST.lines) await expect(page.getByText(l.text, { exact: true })).toBeVisible();
  // ร้อยละพื้นที่ไม่ถูกเขียนเป็นโอกาส และมีข้อความสงวนสิทธิ์ + เครดิต
  await expect(page.getByText(/โอกาส.*%/)).toHaveCount(0);
  await expect(page.getByText("ตัวช่วยสรุป ไม่ใช่ประกาศทางการ").first()).toBeVisible();
});

test("ฉบับต่อเนื่อง: ชิปฉบับของเหตุการณ์เดียวกัน เลือกแล้ว URL และการ์ดเปลี่ยนตาม", async ({ page }) => {
  await page.goto("/warnings");
  const picker = page.getByRole("navigation", { name: "เลือกฉบับของเหตุการณ์นี้" });
  await expect(picker.getByRole("link")).toHaveCount(7);
  await expect(picker.getByRole("link", { name: "ฉบับที่ 7" })).toHaveAttribute("aria-current", "page");
  await picker.getByRole("link", { name: "ฉบับที่ 3" }).click();
  await expect(page).toHaveURL(/\/warnings\?issue=2569_\d+$/);
  await expect(page.getByText("ประกาศย้อนหลัง ·")).toBeVisible();
  await expect(page.getByRole("link", { name: "ดูฉบับล่าสุด" })).toBeVisible();
  await expect(picker.getByRole("link", { name: "ฉบับที่ 3" })).toHaveAttribute("aria-current", "page");
});

test("ฉบับสุดท้ายของเหตุการณ์ปิดแล้ว: ป้ายฉบับสุดท้าย และไม่มีป้ายฉบับต่อไป", async ({ page }) => {
  await page.goto(`/warnings?issue=${FINAL.issue_id}`);
  await expect(page.getByRole("heading", { level: 2, name: FINAL.title })).toBeVisible();
  await expect(page.getByText("ฉบับสุดท้ายของเหตุการณ์นี้", { exact: true })).toBeVisible();
  await expect(page.getByText(/^ฉบับต่อไป /)).toHaveCount(0);
  await expect(page.getByText("เหตุการณ์นี้ประกาศต่อเนื่อง 18 ฉบับ")).toBeVisible();
});

test("ย้อนหลังจัดกลุ่มตามเดือน: 13 เหตุการณ์ เลือกแล้วไปฉบับล่าสุดของเหตุการณ์นั้น", async ({ page }) => {
  await page.goto("/warnings");
  const history = page.getByRole("region", { name: "ประกาศย้อนหลัง" });
  for (const month of ["พฤศจิกายน 2569", "ตุลาคม 2569", "กันยายน 2569", "สิงหาคม 2569"]) {
    await expect(history.getByRole("heading", { level: 3, name: month })).toBeVisible();
  }
  await expect(history.getByRole("link")).toHaveCount(13);
  await history.getByRole("link", { name: /ฉบับที่ 1-18/ }).click();
  await expect(page).toHaveURL(/\/warnings\?issue=2569_234$/);
  await expect(page.getByRole("heading", { level: 2, name: FINAL.title })).toBeVisible();
});

test("รหัสผิดรูปใช้ฉบับล่าสุด ส่วนรหัสที่ไม่มีในระบบบอกว่าไม่พบ พร้อมทางกลับ", async ({ page }) => {
  await page.goto("/warnings?issue=abc");
  await expect(page.getByText("ประกาศล่าสุดในระบบ")).toBeVisible();
  await page.goto("/warnings?issue=2569_9999");
  await expect(page.getByText("ไม่พบประกาศฉบับที่เลือก")).toBeVisible();
  await page.getByRole("link", { name: "ดูฉบับล่าสุด" }).click();
  await expect(page).toHaveURL(/\/warnings$/);
  await expect(page.getByText("ประกาศล่าสุดในระบบ")).toBeVisible();
});

test("เข้าจากเมนู เตือนภัย → ประกาศเตือนภัย", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "เมนูหลัก" });
  await nav.getByRole("button", { name: "เตือนภัย" }).click();
  await nav.getByRole("link", { name: /ประกาศเตือนภัย/ }).click();
  await expect(page).toHaveURL(/\/warnings$/);
});

for (const width of [320, 375, 768, 1280]) {
  test(`ไม่มี scroll แนวนอนที่ ${width}px + ภาพหน้าจอ`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    for (const [url, title] of [
      ["/warnings", LATEST.title],
      [`/warnings?issue=${FINAL.issue_id}`, FINAL.title],
    ]) {
      await page.goto(url);
      await expect(page.getByRole("heading", { level: 2, name: title })).toBeVisible();
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      expect(overflow, `${url} @${width}`).toBeLessThanOrEqual(0);
    }
    await page.goto("/warnings");
    // รอเนื้อหาที่สตรีมมา (ไม่งั้นได้ภาพโครงตอนโหลด) ทั้งการ์ดและรายการย้อนหลัง
    await expect(page.getByRole("heading", { level: 2, name: LATEST.title })).toBeVisible();
    await expect(page.getByRole("heading", { level: 2, name: "ประกาศย้อนหลัง" })).toBeVisible();
    await page.screenshot({ path: `test-results/screens/warnings-${width}.png`, fullPage: true, animations: "disabled" });
  });
}
