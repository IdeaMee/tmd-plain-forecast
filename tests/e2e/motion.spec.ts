// e2e การเคลื่อนไหว (Phase 7.2, D13): มีอนิเมชันตามปกติ และปิดหมดเมื่อผู้ใช้ขอลดการเคลื่อนไหว
import { expect, test, type Page } from "@playwright/test";

const running = (page: Page) => page.evaluate(() => document.getAnimations().length);

async function openRoundPicker(page: Page) {
  await page.getByText(/เลือก(รอบ|ฉบับ)อื่น/).click();
  await expect(page.locator("details[open]")).toHaveCount(1);
}

test.describe("ลดการเคลื่อนไหว", () => {
  test.use({ reducedMotion: "reduce" });

  test("หน้าแรก: ไม่มีอนิเมชันทั้งตอนโหลดและหลังเปิดตัวเลือกรอบ", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 3 }).first()).toBeVisible();
    expect(await running(page)).toBe(0);
    await openRoundPicker(page);
    expect(await running(page)).toBe(0);
    // เปลี่ยนภาค (view transition ของการ์ด) และเปลี่ยนหน้า ต้องไม่มีอนิเมชันค้างทำงาน
    await page.getByRole("link", { name: "ภาคกลาง", exact: true }).click();
    await expect(page.getByRole("heading", { level: 3 })).toHaveCount(1);
    // ทรานสิชันที่ลดเวลาเป็น 0 อาจยังถูกนับอยู่หนึ่งเฟรม จึงรอสั้นๆ (ไม่ใช่รอให้อนิเมชันจริงเล่นจบ)
    await expect.poll(() => running(page), { timeout: 300 }).toBe(0);
    await page.getByRole("navigation", { name: "เมนูหลัก" }).getByRole("link", { name: "ลองอัปโหลด PDF" }).click();
    await expect(page.getByRole("heading", { level: 1, name: "ลองอัปโหลด PDF พยากรณ์" })).toBeVisible();
    await expect.poll(() => running(page), { timeout: 300 }).toBe(0);
  });
});

test.describe("การเคลื่อนไหวปกติ", () => {
  test.use({ reducedMotion: "no-preference" });

  test("การ์ด 7 ภาคเข้าแบบเหลื่อมเวลา และเปลี่ยนภาคใช้ View Transition (การ์ดเลื่อนเข้าที่)", async ({ page }) => {
    await page.addInitScript(() => {
      // นับครั้งที่ React เริ่ม view transition (การ์ดชื่อเดียวกัน morph ระหว่างก่อน/หลัง)
      const w = window as unknown as { __vt: number };
      w.__vt = 0;
      const original = Document.prototype.startViewTransition;
      if (original) {
        Document.prototype.startViewTransition = function (...args: Parameters<typeof original>) {
          w.__vt += 1;
          return original.apply(this, args);
        };
      }
    });
    await page.goto("/");
    const cards = page.locator("article").filter({ has: page.getByRole("heading", { level: 3 }) });
    await expect(cards).toHaveCount(7);
    const delays = await cards.evaluateAll((els) => els.map((el) => getComputedStyle(el).animationDelay));
    expect(new Set(delays).size).toBeGreaterThan(1);
    await page.getByRole("link", { name: "ภาคกลาง", exact: true }).click();
    await expect(page.getByRole("heading", { level: 3 })).toHaveCount(1);
    expect(await page.evaluate(() => (window as unknown as { __vt: number }).__vt)).toBeGreaterThan(0);
  });

  test("เปิดตัวเลือกรอบแล้วแถววันไหลเข้า (มีอนิเมชันทำงาน)", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 3 }).first()).toBeVisible();
    await openRoundPicker(page);
    expect(await running(page)).toBeGreaterThan(0);
    // ชิปภาคที่เลือกมีเครื่องหมายถูกแต่ชื่อที่อ่านออกเสียงเท่าเดิม
    await expect(page.getByRole("navigation", { name: "เลือกภาค" }).getByRole("link", { name: "ทุกภาค" })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });
});
