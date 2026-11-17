import { expect, test } from "@playwright/test";

test("ข้อมูลเสีย: แสดงข้อผิดพลาดพร้อมปุ่มลองใหม่ และยังมีเมนูกับข้อความสงวนสิทธิ์", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "โหลดข้อมูลพยากรณ์ไม่สำเร็จ" })).toBeVisible();
  await expect(page.getByRole("button", { name: "ลองใหม่" })).toBeVisible();
  await expect(page.getByText("ตัวช่วยสรุป ไม่ใช่ประกาศทางการ").first()).toBeVisible();
  // ภาพหน้าจอให้คนดู (test-results/ ไม่ขึ้น repo)
  for (const width of [375, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    await page.screenshot({ path: `test-results/screens/error-${width}.png`, fullPage: true });
  }
});

test("ประกาศเตือนภัยเสีย: แสดงข้อผิดพลาดพร้อมปุ่มลองใหม่ ไม่แสดงข้อมูลที่ไม่ผ่านสัญญา", async ({ page }) => {
  await page.goto("/warnings");
  await expect(page.getByRole("heading", { name: "โหลดข้อมูลพยากรณ์ไม่สำเร็จ" })).toBeVisible();
  await expect(page.getByRole("button", { name: "ลองใหม่" })).toBeVisible();
});

test("สรุปรายสัปดาห์เสีย: แสดงข้อผิดพลาดพร้อมปุ่มลองใหม่ ไม่แสดงข้อมูลที่ไม่ผ่านสัญญา", async ({ page }) => {
  await page.goto("/summaries");
  await expect(page.getByRole("heading", { name: "โหลดข้อมูลพยากรณ์ไม่สำเร็จ" })).toBeVisible();
  await expect(page.getByRole("button", { name: "ลองใหม่" })).toBeVisible();
});

