import { expect, test } from "@playwright/test";

import { chooseIssue, expectCalendarDays, loadProcessed, monthOf, monthsOf } from "./data";

const SHIPPING = loadProcessed("shipping");

// แท็บพยากรณ์เดินเรือบนหน้า / (11.1) อ่าน data/processed/shipping (ฉบับล่าสุด 18 พ.ย. 2569 13:00 น.)
const AREAS = [
  "อ่าวไทยทั้งสองฝั่ง",
  "ทะเลอันดามันและช่องแคบมะละกา",
  "เส้นทางเดินเรือโกตาบารูถึงสิงคโปร์",
  "ปลายแหลมญวน",
];

test("แท็บพยากรณ์เดินเรือ: 4 พื้นที่ทะเล ตอนบน/ตอนล่างของอ่าวไทย และคำแนะนำชาวเรือ", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "พยากรณ์เดินเรือ" }).click();
  await expect(page).toHaveURL(/type=shipping/);
  await expect(page.getByText("พยากรณ์เดินเรือ ออกประกาศ 18 พฤศจิกายน 2569 13:00 น.")).toBeVisible();
  for (const name of AREAS) {
    await expect(page.getByRole("heading", { level: 3, name, exact: true })).toBeVisible();
  }
  await expect(page.getByRole("heading", { level: 4, name: "ตอนบน" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 4, name: "ตอนล่าง" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "คำแนะนำสำหรับชาวเรือ" })).toBeVisible();
  // ไม่มีตัวเลือกภาค (เดินเรือแบ่งตามพื้นที่ทะเล) และร้อยละพื้นที่ไม่ถูกเขียนเป็นโอกาส
  await expect(page.getByRole("navigation", { name: "เลือกภาค" })).toHaveCount(0);
  await expect(page.getByText(/โอกาส.*%/)).toHaveCount(0);
  await expect(page.getByText("ตัวช่วยสรุป ไม่ใช่ประกาศทางการ").first()).toBeVisible();
});

test("เดินเรือ: เลือกรอบย้อนหลังแล้ว URL และป้ายเปลี่ยนตาม", async ({ page }) => {
  await page.goto("/?type=shipping");
  await page.getByText(/^เลือกรอบอื่น/).click();
  await chooseIssue(page, SHIPPING, SHIPPING.find((d) => d.issue_id === "171120261300")!);
  await expect(page).toHaveURL(/type=shipping&issue=171120261300/);
  await expect(page.getByText("ออกประกาศ 17 พฤศจิกายน 2569 13:00 น. (ฉบับย้อนหลัง)")).toBeVisible();
});

test("เดินเรือ: ตัวเลือกรอบรายเดือนเปิดเดือนเก่าสุดได้ทุกรอบที่เก็บ", async ({ page }) => {
  await page.goto("/?type=shipping");
  await page.getByText(/^เลือกรอบอื่น/).click();
  const months = monthsOf(SHIPPING);
  await expect(page.getByText(/^เลือกรอบอื่น/)).toContainText(`ทั้งหมด ${SHIPPING.length} ฉบับ ใน ${months.length} เดือน`);
  await page.getByRole("list", { name: "ทุกเดือนที่มีข้อมูล" }).getByRole("link").last().click();
  const oldest = months.at(-1)!;
  const inOldest = SHIPPING.filter((d) => monthOf(d.issued_at) === oldest);
  await expectCalendarDays(page, inOldest);
  await chooseIssue(page, SHIPPING, inOldest[0]);
  await expect(page.getByText(`${inOldest[0].source_label} (ฉบับย้อนหลัง)`)).toBeVisible();
});

test("เดินเรือ: ภาคใน URL ถูกละ และรหัสฉบับผิดรูปใช้ฉบับล่าสุด", async ({ page }) => {
  await page.goto("/?type=shipping&region=north&issue=261116");
  await expect(page.getByText("ออกประกาศ 18 พฤศจิกายน 2569 13:00 น.")).toBeVisible();
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(4);
});

test("เดินเรือ: เข้าจากเมนูได้ ไม่มี scroll แนวนอน (ภาพหน้าจอ 320/375/768/1280)", async ({ page }) => {
  for (const width of [320, 375, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/?type=shipping");
    await expect(page.getByRole("heading", { level: 3, name: AREAS[0] })).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow, `width ${width}`).toBeLessThanOrEqual(0);
    await page.screenshot({ path: `test-results/screens/shipping-${width}.png`, fullPage: true, animations: "disabled" });
  }
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto("/model");
  const nav = page.getByRole("navigation", { name: "เมนูหลัก" });
  await nav.getByRole("button", { name: "พยากรณ์" }).click();
  await nav.getByRole("link", { name: /เดินเรือ/ }).click();
  await expect(page).toHaveURL(/\/\?type=shipping$/);
});
