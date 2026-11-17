import { expect, test } from "@playwright/test";

import { chooseIssue, dayOf, expectCalendarDays, loadProcessed, monthOf, monthsOf } from "./data";

// ฉบับล่าสุดอ่านจากข้อมูลจริง (11.6: ขึ้นเว็บทุกฉบับที่เก็บ จึงไม่ตรึงวัน)
const DAILY = loadProcessed("daily");
const SEVENDAY = loadProcessed("sevenday");

const REGIONS = [
  "ภาคเหนือ",
  "ภาคตะวันออกเฉียงเหนือ",
  "ภาคกลาง",
  "ภาคตะวันออก",
  "ภาคใต้ฝั่งตะวันออก",
  "ภาคใต้ฝั่งตะวันตก",
  "กรุงเทพมหานครและปริมณฑล",
];

test("เห็นครบ 7 ภาคของฉบับรายวันล่าสุด พร้อมข้อความสงวนสิทธิ์", async ({ page }) => {
  await page.goto("/");
  for (const name of REGIONS) {
    await expect(page.getByRole("heading", { level: 3, name, exact: true })).toBeVisible();
  }
  await expect(page.getByText(DAILY[0].source_label)).toBeVisible();
  await expect(page.getByText("ตัวช่วยสรุป ไม่ใช่ประกาศทางการ").first()).toBeVisible();
  // ร้อยละพื้นที่ไม่ถูกเขียนเป็นโอกาส
  await expect(page.getByText(/โอกาส.*%/)).toHaveCount(0);
});

test("สลับเป็นพยากรณ์ 7 วัน แสดงตามช่วงวัน", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "พยากรณ์ 7 วัน" }).click();
  await expect(page).toHaveURL(/type=sevenday/);
  await expect(page.getByText(SEVENDAY[0].source_label)).toBeVisible();
  await expect(page.getByRole("heading", { level: 4, name: /พ\.ย\. 2569/ }).first()).toBeVisible();
});

test("เลือกรอบเก่าจากประวัติย้อนหลัง (เดือนเดียวกับฉบับล่าสุด)", async ({ page }) => {
  await page.goto("/");
  await page.getByText(/^เลือกรอบอื่น/).click();
  const old = DAILY.find((d) => d.issue_id === "161120261200")!;
  // ปฏิทิน: กดวันที่ก่อน แล้วเลือกเวลา (ปุ่มเวลาเป็นลิงก์ไปฉบับนั้น)
  await chooseIssue(page, DAILY, old);
  await expect(page).toHaveURL(new RegExp(`issue=${old.issue_id}`));
  await expect(page.getByText(`${old.source_label} (ฉบับย้อนหลัง)`)).toBeVisible();
  // เลือกแล้วลิ้นชักปิดเอง เห็นผลสรุปทันที
  await expect(page.locator("details[open]")).toHaveCount(0);
});

test("ปฏิทิน: วันที่ไม่มีฉบับกดไม่ได้ วันที่มีฉบับกดได้ และเห็นปุ่มเวลาของวันที่เลือก", async ({ page }) => {
  await page.goto("/");
  await page.getByText(/^เลือกรอบอื่น/).click();
  const month = monthOf(DAILY[0].issued_at);
  const monthDocs = DAILY.filter((d) => monthOf(d.issued_at) === month);
  await expectCalendarDays(page, monthDocs);
  // วันของฉบับล่าสุดเปิดปุ่มเวลาไว้ให้เลย และฉบับที่ดูอยู่ถูกทำเครื่องหมาย
  const times = page.getByRole("group", { name: /^เลือกเวลาของวันที่/ });
  await expect(times.getByRole("link")).toHaveCount(monthDocs.filter((d) => dayOf(d.source_label) === dayOf(DAILY[0].source_label)).length);
  await expect(times.locator('a[aria-current="page"]')).toHaveCount(1);
  // วันที่ไม่มีฉบับไม่ใช่ปุ่มหรือลิงก์ (เห็นจางลง ไม่อยู่ใน accessibility tree)
  const calendar = page.getByRole("group", { name: /^ปฏิทิน/ });
  const disabled = calendar.locator('span[aria-hidden="true"].cursor-not-allowed');
  expect(await disabled.count()).toBeGreaterThan(0);
});

// 11.6: ทุกหมวดดูย้อนหลังได้ทุกฉบับที่เก็บ ไม่ใช่แค่ 7 วัน
for (const [type, docs, query] of [
  ["รายวัน", DAILY, ""],
  ["7 วัน", SEVENDAY, "?type=sevenday"],
] as const) {
  test(`ตัวเลือกรอบรายเดือน (${type}): เปิดเดือนเก่าสุดแล้วเข้าฉบับนั้นได้ ไม่มี scroll แนวนอนที่ 320 px`, async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 800 });
    await page.goto(`/${query}`);
    await page.getByText(/^เลือก(รอบ|ฉบับ)อื่น/).click();
    const months = monthsOf(docs);
    await expect(page.getByText(/^เลือก(รอบ|ฉบับ)อื่น/)).toContainText(`ทั้งหมด ${docs.length} ฉบับ ใน ${months.length} เดือน`);
    const monthLinks = page.getByRole("list", { name: "ทุกเดือนที่มีข้อมูล" }).getByRole("link");
    await expect(monthLinks).toHaveCount(months.length);
    const oldest = months.at(-1)!;
    await monthLinks.last().click();
    await expect(page).toHaveURL(new RegExp(`month=${oldest}`));
    // เลือกเดือนแล้วกล่องยังเปิดอยู่ ปฏิทินของเดือนนั้นมีทุกวันที่มีฉบับ
    const inOldest = docs.filter((d) => monthOf(d.issued_at) === oldest);
    await expectCalendarDays(page, inOldest);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(0);
    const target = inOldest[0];
    await chooseIssue(page, docs, target);
    await expect(page).toHaveURL(new RegExp(`issue=${target.issue_id}`));
    await expect(page.getByText(`${target.source_label} (ฉบับย้อนหลัง)`)).toBeVisible();
  });
}

test("ฉบับที่ไม่มีในระบบ บอกว่าไม่พบและมีทางกลับฉบับล่าสุด", async ({ page }) => {
  await page.goto("/?issue=010120200000");
  await expect(page.getByText("ไม่พบพยากรณ์รายวันฉบับที่เลือก")).toBeVisible();
  await page.getByRole("link", { name: "ดูฉบับล่าสุด" }).click();
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(7);
});

test.describe("มือถือ", () => {
  test.use({ viewport: { width: 375, height: 812 }, hasTouch: true });

  test("ภาคเป็นลิ้นชัก: เปิดแล้วเลือกภาค เหลือการ์ดเดียว ลิ้นชักปิดเองและบอกภาคที่เลือก ไม่มี scroll แนวนอน", async ({ page }) => {
    await page.goto("/");
    // ปิดอยู่ตอนแรก เห็นแค่ภาคที่เลือกอยู่ ไม่ใช่ชิปยาวๆ
    const drawer = page.getByText(/^เลือกภาค/);
    await expect(drawer).toContainText("ทุกภาค");
    await expect(page.getByRole("link", { name: "ภาคกลาง", exact: true })).toBeHidden();
    await drawer.click();
    await page.getByRole("link", { name: "ภาคกลาง", exact: true }).click();
    await expect(page).toHaveURL(/region=central/);
    await expect(page.getByRole("heading", { level: 3 })).toHaveCount(1);
    await expect(page.getByText(/^เลือกภาค/)).toContainText("ภาคกลาง");
    await expect(page.locator("details[open]")).toHaveCount(0);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(0);
  });

  test("ตัวเลือกรอบ: ปฏิทินพอดีจอ ปุ่มวันและเวลาใหญ่พอแตะ และลิ้นชักไม่สูงเกินจอ", async ({ page }) => {
    await page.goto("/");
    await page.getByText(/^เลือกรอบอื่น/).click();
    const calendar = page.getByRole("group", { name: /^ปฏิทิน/ });
    await expect(calendar).toBeVisible();
    const box = await calendar.boundingBox();
    expect(box!.width).toBeLessThanOrEqual(375);
    for (const control of await calendar.locator("button, a").all()) {
      const b = await control.boundingBox();
      expect(b!.height).toBeGreaterThanOrEqual(43.5);
      expect(b!.width).toBeGreaterThanOrEqual(40);
    }
    for (const control of await page.getByRole("group", { name: /^เลือกเวลาของวันที่/ }).getByRole("link").all()) {
      expect((await control.boundingBox())!.height).toBeGreaterThanOrEqual(43.5);
    }
    const open = await page.locator("details[open]").boundingBox();
    expect(open!.height).toBeLessThan(900);
  });
});

test("ใช้คีย์บอร์ดเปลี่ยนชนิดพยากรณ์ได้", async ({ page }) => {
  await page.goto("/");
  const link = page.getByRole("link", { name: "พยากรณ์ 7 วัน" });
  await link.focus();
  await expect(link).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/type=sevenday/);
  await expect(page.getByRole("link", { name: "พยากรณ์ 7 วัน" })).toHaveAttribute("aria-current", "page");
});
