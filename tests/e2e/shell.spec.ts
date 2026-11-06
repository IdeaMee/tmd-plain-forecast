// e2e โครงเว็บ (Phase 7.3): เมนูมือถือแผงเต็มกว้าง, เมนูเดสก์ท็อป 5 หมวด (เฉพาะหน้าที่มี), ทรานสิชันหน้า
import { expect, test, type Page } from "@playwright/test";

const menuButton = (page: Page) => page.getByRole("button", { name: /^(เมนู|ปิด)$/ });
const mobileNav = (page: Page) => page.getByRole("navigation", { name: "เมนูหลัก" });

test.describe("มือถือ 375", () => {
  test.use({ viewport: { width: 375, height: 812 }, hasTouch: true });

  test("เปิด/ปิดแผงเมนูด้วยปุ่ม แตะพื้นมืด และ Esc (โฟกัสกลับที่ปุ่ม) + ล็อกการเลื่อน", async ({ page }) => {
    await page.goto("/");
    const button = menuButton(page);
    await expect(button).toHaveAttribute("aria-expanded", "false");
    await expect(mobileNav(page)).toBeHidden();
    await button.click();
    await expect(button).toHaveAttribute("aria-expanded", "true");
    await expect(mobileNav(page)).toBeVisible();
    // แผงกว้างเต็มจอ (ไม่ใช่ลิ้นชักเล็ก)
    const box = await mobileNav(page).locator("..").boundingBox();
    expect(box?.width).toBe(375);
    expect(await page.evaluate(() => document.body.style.overflow)).toBe("hidden");
    await page.screenshot({ path: "test-results/screens/shell-menu-open-375.png", animations: "disabled" });

    await page.keyboard.press("Escape");
    await expect(button).toHaveAttribute("aria-expanded", "false");
    await expect(button).toBeFocused();
    expect(await page.evaluate(() => document.body.style.overflow)).toBe("");

    await button.click();
    // แตะพื้นมืดด้านล่างแผง: ปิดแล้วโฟกัสกลับที่ปุ่ม
    await page.mouse.click(187, 780);
    await expect(button).toHaveAttribute("aria-expanded", "false");
    await expect(button).toBeFocused();

    // เปิดค้างแล้วจอกว้างถึงเมนูเดสก์ท็อป: ปิดเองและปลดล็อกการเลื่อน
    await button.click();
    await page.setViewportSize({ width: 1280, height: 812 });
    await expect.poll(() => page.evaluate(() => document.body.style.overflow)).toBe("");
  });

  test("Tab วนอยู่ในแผงขณะเปิด และลิงก์ในแผงพาไปหน้าแล้วปิดแผง", async ({ page }) => {
    await page.goto("/");
    await menuButton(page).click();
    const links = mobileNav(page).getByRole("link");
    const count = await links.count();
    await expect(links.first()).toBeFocused();
    for (let i = 0; i < count; i++) await page.keyboard.press("Tab");
    await expect(links.first()).toBeFocused();
    await mobileNav(page).getByRole("link", { name: "ลองอัปโหลด PDF" }).click();
    await expect(page).toHaveURL(/\/demo$/);
    await expect(menuButton(page)).toHaveAttribute("aria-expanded", "false");
    await expect(mobileNav(page)).toBeHidden();
  });

  test("ลิงก์ในแผงสูงอย่างน้อย 48 px", async ({ page }) => {
    await page.goto("/");
    await menuButton(page).click();
    const heights = await mobileNav(page)
      .getByRole("link")
      .evaluateAll((els) => els.map((el) => el.getBoundingClientRect().height));
    expect(Math.min(...heights)).toBeGreaterThanOrEqual(48);
  });
});

test.describe("เดสก์ท็อป 1280", () => {
  test.use({ viewport: { width: 1280, height: 900 } });

  test("หมวดเปิดหมวดย่อยด้วยคลิกและคีย์บอร์ด ปิดด้วย Esc/คลิกนอกเมนู", async ({ page }) => {
    await page.goto("/");
    await expect(menuButton(page)).toBeHidden();
    const nav = page.getByRole("navigation", { name: "เมนูหลัก" });
    const group = nav.getByRole("button", { name: "พยากรณ์" });
    await group.click();
    await expect(group).toHaveAttribute("aria-expanded", "true");
    await page.screenshot({ path: "test-results/screens/shell-menu-open-1280.png", animations: "disabled" });
    await page.mouse.click(1200, 600);
    await expect(group).toHaveAttribute("aria-expanded", "false");

    await group.focus();
    await page.keyboard.press("Enter");
    await expect(nav.getByRole("link", { name: /7 วันข้างหน้า/ })).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(group).toHaveAttribute("aria-expanded", "false");
    await expect(group).toBeFocused();

    await group.click();
    await nav.getByRole("link", { name: /7 วันข้างหน้า/ }).click();
    await expect(page).toHaveURL(/type=sevenday/);
    await expect(group).toHaveAttribute("aria-expanded", "false");
  });

  test("เบราว์เซอร์ที่ไม่รองรับ View Transitions ยังเปลี่ยนหน้าได้ปกติ", async ({ page }) => {
    await page.addInitScript(() => {
      // จำลองเบราว์เซอร์รุ่นเก่า
      Object.defineProperty(Document.prototype, "startViewTransition", { value: undefined, configurable: true });
    });
    await page.goto("/");
    await page.getByRole("navigation", { name: "เมนูหลัก" }).getByRole("link", { name: "ลองอัปโหลด PDF" }).click();
    await expect(page.getByRole("heading", { level: 1, name: "ลองอัปโหลด PDF พยากรณ์" })).toBeVisible();
  });
});

test("ทุกลิงก์ในเมนูและท้ายหน้าตอบ 200", async ({ page, request }) => {
  await page.goto("/");
  const hrefs = await page
    .locator("header a[href], footer nav a[href]")
    .evaluateAll((els) => [...new Set(els.map((el) => el.getAttribute("href") ?? ""))]);
  expect(hrefs.length).toBeGreaterThanOrEqual(3);
  for (const href of hrefs) {
    expect((await request.get(href)).status(), href).toBe(200);
  }
});

for (const width of [320, 375, 768, 1280]) {
  test(`ไม่มี scroll แนวนอนที่ ${width}px (หน้าแรกและ /demo) + ภาพหน้าจอ`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    for (const url of ["/", "/demo"]) {
      await page.goto(url);
      const name = url === "/" ? "home" : "demo";
      await page.screenshot({ path: `test-results/screens/v2-${name}-${width}.png`, fullPage: true, animations: "disabled" });
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      expect(overflow, url).toBeLessThanOrEqual(0);
    }
    // ต่ำกว่า 1024 ใช้ปุ่มเมนู ตั้งแต่ 1024 ใช้เมนูแนวนอน (V10)
    await expect(menuButton(page)).toBeVisible({ visible: width < 1024 });
  });
}
