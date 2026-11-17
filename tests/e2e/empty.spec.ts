import { expect, test } from "@playwright/test";

test("ไม่มีข้อมูล: บอกสาเหตุ ไม่แสดงการ์ดว่าง", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("ยังไม่มีข้อมูลพยากรณ์รายวัน")).toBeVisible();
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(0);
  // ภาพหน้าจอให้คนดู (test-results/ ไม่ขึ้น repo)
  for (const width of [375, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    await page.screenshot({ path: `test-results/screens/empty-${width}.png`, fullPage: true });
  }
});

test("ไม่มีข้อมูลเดินเรือ (ไม่มีโฟลเดอร์ shipping): บอกว่ายังไม่มีข้อมูล ไม่ใช่หน้าข้อผิดพลาด", async ({ page }) => {
  await page.goto("/?type=shipping");
  await expect(page.getByText("ยังไม่มีข้อมูลพยากรณ์เดินเรือ")).toBeVisible();
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(0);
});

test("ไม่มีประกาศเตือนภัย (ไม่มีโฟลเดอร์ warning): บอกว่ายังไม่มี พร้อมลิงก์ไปเว็บกรม ไม่ใช่หน้าข้อผิดพลาด", async ({ page }) => {
  await page.goto("/warnings");
  await expect(page.getByRole("heading", { level: 1, name: "ประกาศเตือนภัย" })).toBeVisible();
  await expect(page.getByText("ยังไม่มีประกาศเตือนภัยในระบบ", { exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "ประกาศเตือนภัยที่กรมอุตุนิยมวิทยา" })).toHaveAttribute("href", /tmd\.go\.th/);
  await expect(page.getByRole("heading", { name: "ประกาศย้อนหลัง" })).toHaveCount(0);
  for (const width of [375, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    await page.screenshot({ path: `test-results/screens/warnings-empty-${width}.png`, fullPage: true });
  }
});

test("ไม่มีสรุปรายสัปดาห์ (ไม่มีโฟลเดอร์ weekly): บอกว่ายังไม่มี พร้อมลิงก์ไปเว็บกรม ไม่ใช่หน้าข้อผิดพลาด", async ({ page }) => {
  await page.goto("/summaries");
  await expect(page.getByRole("heading", { level: 1, name: "สรุปสภาพอากาศรายสัปดาห์" })).toBeVisible();
  await expect(page.getByText("ยังไม่มีสรุปรายสัปดาห์ในระบบ", { exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "สรุปสภาพอากาศรายสัปดาห์ที่กรมอุตุนิยมวิทยา" })).toHaveAttribute("href", /tmd\.go\.th/);
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(0);
});

