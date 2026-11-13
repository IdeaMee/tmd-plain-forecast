// smoke test 15 ข้อบนเว็บจริง (vercel-deploy-checklist ส่วนที่ 4) · ไม่แก้ข้อมูลใน DB
// ไฟล์ PDF จริงอ่านจาก data/raw (ไม่ขึ้น repo) ถ้าไม่มีข้อนั้นถูกข้าม · ภาพหน้าจออยู่ test-results/screens/smoke-*.png
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

import { expect, test, type Page } from "@playwright/test";

const RAW = path.resolve("data/raw");
const DAILY_PDF = path.join(RAW, "daily", "daily_161120261800.pdf");
const SEVENDAY_PDF = path.join(RAW, "sevenday", "sevenday_261116.pdf");
const NON_TMD_PDF = path.resolve("course/slides/0_MiniProject.pdf");
const LATEST_DAILY = "ประจำวันที่ 16 พฤศจิกายน 2569 17.00 น.";
const FILE_LABEL = "เลือกไฟล์ PDF พยากรณ์ของกรมอุตุนิยมวิทยา";
const SUBMIT = "สรุปพยากรณ์จากไฟล์นี้";
const PDF_BYTES = { name: "x.pdf", mimeType: "application/pdf" };

async function noHorizontalScroll(page: Page) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow).toBeLessThanOrEqual(0);
}

async function upload(page: Page, file: string | { name: string; mimeType: string; buffer: Buffer }) {
  await page.getByLabel(FILE_LABEL).setInputFiles(file);
  await page.getByRole("button", { name: SUBMIT }).click();
}

test("01 หน้าแรก: รายวันฉบับล่าสุด 7 ภาค ไม่มีคำว่าโอกาส…%", async ({ page }) => {
  const res = await page.goto("/");
  expect(res?.status()).toBe(200);
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(7);
  await expect(page.getByText(LATEST_DAILY)).toBeVisible();
  await expect(page.getByText(/โอกาส.*%/)).toHaveCount(0);
});

test("02 หน้าแรก: พยากรณ์ 7 วัน 7 ภาค แยกช่วงวัน", async ({ page }) => {
  await page.goto("/?type=sevenday");
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(7);
  await expect(page.getByText("ฉบับวันที่ 16 พฤศจิกายน 2569")).toBeVisible();
  await expect(page.getByRole("heading", { level: 4, name: /พ\.ย\. 2569/ }).first()).toBeVisible();
});

test("03 ตัวเลือกรอบย้อนหลัง", async ({ page }) => {
  await page.goto("/");
  await page.getByText("เลือกรอบอื่น (ย้อนหลัง 7 วัน)").click();
  await page.getByRole("link", { name: "11.00 น." }).first().click();
  await expect(page).toHaveURL(/issue=161120261200/);
  await expect(page.getByText("ประจำวันที่ 16 พฤศจิกายน 2569 11.00 น. (ฉบับย้อนหลัง)")).toBeVisible();
});

test.describe("มือถือ", () => {
  test.use({ viewport: { width: 375, height: 812 }, hasTouch: true });

  test("04 แท็บภาคบนมือถือ: เหลือการ์ดเดียว ไม่มี scroll แนวนอน", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "ภาคกลาง", exact: true }).click();
    await expect(page).toHaveURL(/region=central/);
    await expect(page.getByRole("heading", { level: 3 })).toHaveCount(1);
    await noHorizontalScroll(page);
  });
});

test("05 /demo: PDF รายวันจริง ได้ 7 ภาค", async ({ page }) => {
  test.skip(!existsSync(DAILY_PDF), "ไม่มีข้อมูลดิบ");
  await page.goto("/demo");
  await upload(page, DAILY_PDF);
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(7, { timeout: 60_000 });
  await expect(page.getByText(LATEST_DAILY)).toBeVisible();
});

test("06 /demo: PDF 7 วันจริง ได้ 7 ภาค", async ({ page }) => {
  test.skip(!existsSync(SEVENDAY_PDF), "ไม่มีข้อมูลดิบ");
  await page.goto("/demo");
  await upload(page, SEVENDAY_PDF);
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(7, { timeout: 60_000 });
  await expect(page.getByRole("heading", { level: 2, name: "ผลสรุปพยากรณ์ 7 วัน" })).toBeVisible();
});

test("07 /demo: PDF ที่ไม่ใช่พยากรณ์ของ TMD ถูกปฏิเสธ", async ({ page }) => {
  test.skip(!existsSync(NON_TMD_PDF), "ไม่มีสไลด์วิชา");
  await page.goto("/demo");
  await upload(page, NON_TMD_PDF);
  await expect(page.getByRole("status").getByText("ไม่ใช่พยากรณ์อากาศรายวันหรือพยากรณ์ 7 วัน")).toBeVisible({
    timeout: 60_000,
  });
});

test("08 /demo: ไฟล์ที่ไม่ใช่ PDF ถูกปฏิเสธก่อนส่ง", async ({ page }) => {
  await page.goto("/demo");
  await upload(page, { name: "notes.txt", mimeType: "text/plain", buffer: Buffer.from("hello") });
  await expect(page.getByRole("status").getByText("ไม่ใช่พยากรณ์อากาศรายวันหรือพยากรณ์ 7 วัน")).toBeVisible();
});

test("09 /demo: ไฟล์เกิน 4 MB ถูกปฏิเสธก่อนส่ง", async ({ page }) => {
  await page.goto("/demo");
  await upload(page, { ...PDF_BYTES, buffer: Buffer.alloc(4 * 1024 * 1024 + 1, 0x20) });
  await expect(page.getByRole("status").getByText("ไฟล์ใหญ่เกิน 4 MB")).toBeVisible();
});

test("10 /demo: ไฟล์ว่างถูกปฏิเสธ", async ({ page }) => {
  await page.goto("/demo");
  await upload(page, { ...PDF_BYTES, buffer: Buffer.alloc(0) });
  await expect(page.getByRole("status").getByText("ไฟล์ว่างเปล่า")).toBeVisible();
});

test("11 ข้อความสงวนสิทธิ์และเครดิต TMD บนทุกหน้าที่มีสรุป", async ({ page }) => {
  for (const url of ["/", "/demo"]) {
    await page.goto(url);
    await expect(page.getByText("ตัวช่วยสรุป ไม่ใช่ประกาศทางการ").first()).toBeVisible();
    await expect(page.getByRole("link", { name: "กรมอุตุนิยมวิทยา" }).first()).toHaveAttribute("href", /tmd\.go\.th/);
  }
});

test("12 ฟังก์ชัน /api/summarize ตอบตามสัญญา (ว่าง/ไม่ใช่ PDF/ใหญ่เกิน/GET)", async ({ request }) => {
  const post = (data: Buffer) =>
    request.post("/api/summarize", { data, headers: { "Content-Type": "application/pdf" } });
  const cases: [Buffer, number, string][] = [
    [Buffer.alloc(0), 422, "empty_file"],
    [Buffer.from("not a pdf"), 422, "unsupported_document"],
    [Buffer.concat([Buffer.from("%PDF-1.4"), Buffer.alloc(4_300_000)]), 413, "too_large"],
  ];
  for (const [data, status, code] of cases) {
    const res = await post(data);
    expect(res.status(), code).toBe(status);
    expect((await res.json()).error.code).toBe(code);
  }
  expect((await request.get("/api/summarize")).status()).toBe(405);
});

test("13 route ล้างแคชปฏิเสธเมื่อไม่มี/ผิด secret และหน้าชั่วคราวถูกลบแล้ว", async ({ request }) => {
  expect((await request.post("/internal/revalidate")).status()).toBe(401);
  const wrong = await request.post("/internal/revalidate", { headers: { "x-revalidate-secret": "wrong" } });
  expect(wrong.status()).toBe(401);
  expect((await request.get("/styleguide")).status()).toBe(404);
});

test("14 เวลาตอบสนอง: หน้าแรกและฟังก์ชัน ครั้งแรก/ครั้งที่สอง", async ({ request }) => {
  test.skip(!existsSync(DAILY_PDF), "ไม่มีข้อมูลดิบ");
  const pdf = readFileSync(DAILY_PDF);
  const time = async (fn: () => Promise<{ status(): number }>) => {
    const t0 = Date.now();
    const res = await fn();
    expect(res.status()).toBe(200);
    return Date.now() - t0;
  };
  const home = [await time(() => request.get("/")), await time(() => request.get("/"))];
  const api = [];
  for (let i = 0; i < 2; i++) {
    api.push(
      await time(() =>
        request.post("/api/summarize", { data: pdf, headers: { "Content-Type": "application/pdf" } }),
      ),
    );
  }
  console.log(`TIMING home_ms=${home.join("/")} summarize_ms=${api.join("/")}`);
  // เกณฑ์หลวมไว้จับกรณีพังชัดๆ ไม่ใช่วัดประสิทธิภาพ
  expect(Math.max(...home, ...api)).toBeLessThan(15_000);
});

test.describe("15 ภาพหน้าจอ 320 และ 375 px ไม่มี scroll แนวนอน", () => {
  for (const width of [320, 375]) {
    test(`กว้าง ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 800 });
      for (const [name, url] of [
        ["home", "/"],
        ["demo", "/demo"],
      ]) {
        await page.goto(url);
        await page.waitForLoadState("networkidle");
        await noHorizontalScroll(page);
        await page.screenshot({ path: `test-results/screens/smoke-${name}-${width}.png`, fullPage: true });
      }
    });
  }
});
