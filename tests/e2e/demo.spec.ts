// e2e หน้า /demo บนเครื่อง: ฟังก์ชัน Python ไม่มีใน next start จึงจำลองคำตอบของ /api/summarize ในเบราว์เซอร์
// (ไฟล์จริงทดสอบบน preview URL ของ Vercel หลัง push)
import { readFileSync } from "node:fs";
import path from "node:path";

import { expect, test, type Page, type Route } from "@playwright/test";

const ISSUE = JSON.parse(readFileSync(path.resolve("data/processed/daily/161120261800.json"), "utf-8"));
const PDF = { name: "daily.pdf", mimeType: "application/pdf", buffer: Buffer.from("%PDF-1.4 ทดสอบ") };
const MESSAGES: Record<string, string> = {
  unsupported_document: "ไฟล์นี้ไม่ใช่ PDF",
  too_large: "ไฟล์ใหญ่เกิน 4 MB กรุณาเลือกไฟล์พยากรณ์ฉบับเดียว",
  extract_failed: "อ่านหรือสรุปข้อความในไฟล์ไม่สำเร็จ ไฟล์อาจเป็นภาพสแกนที่ไม่มีข้อความหรือไฟล์เสีย กรุณาลองไฟล์อื่น",
  empty_file: "ไฟล์ว่างเปล่า กรุณาเลือกไฟล์ใหม่",
};

function json(route: Route, status: number, body: unknown) {
  return route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

async function upload(page: Page, file = PDF) {
  await page.getByLabel("เลือกไฟล์ PDF พยากรณ์ของกรมอุตุนิยมวิทยา").setInputFiles(file);
  await page.getByRole("button", { name: "สรุปพยากรณ์จากไฟล์นี้" }).click();
}

const submit = (page: Page) => page.getByRole("button", { name: /สรุปพยากรณ์จากไฟล์นี้|กำลังสรุป/ });

test("ก่อนเลือกไฟล์: มีช่องเลือกไฟล์จริงพร้อมป้าย ข้อความสงวนสิทธิ์ และปุ่มยังกดไม่ได้", async ({ page }) => {
  await page.goto("/demo");
  await expect(page.getByRole("heading", { level: 1, name: "ลองอัปโหลด PDF พยากรณ์" })).toBeVisible();
  const input = page.getByLabel("เลือกไฟล์ PDF พยากรณ์ของกรมอุตุนิยมวิทยา");
  await expect(input).toHaveAttribute("type", "file");
  await expect(input).toHaveAttribute("accept", /application\/pdf/);
  await expect(page.getByText("ไม่เก็บไฟล์ที่อัปโหลด")).toBeVisible();
  await expect(page.getByText("ตัวช่วยสรุป ไม่ใช่ประกาศทางการ").first()).toBeVisible();
  await expect(submit(page)).toBeDisabled();
});

test("ส่ง PDF ดิบแล้วเห็นการ์ด 7 ภาคชุดเดียวกับหน้าหลัก", async ({ page }) => {
  let contentType = "";
  let bodyStart = "";
  await page.route("**/api/summarize**", (route) => {
    contentType = route.request().headers()["content-type"] ?? "";
    bodyStart = (route.request().postDataBuffer() ?? Buffer.alloc(0)).subarray(0, 5).toString();
    return json(route, 200, { ok: true, kind: "issue", document: ISSUE, trace: null });
  });
  await page.goto("/demo");
  await upload(page);
  await expect(page.getByRole("heading", { level: 2, name: "ผลสรุปพยากรณ์รายวัน" })).toBeVisible();
  await expect(page.getByText(ISSUE.source_label)).toBeVisible();
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(7);
  await expect(page.getByText(/โอกาส.*%/)).toHaveCount(0);
  expect(contentType).toBe("application/pdf");
  expect(bodyStart).toBe("%PDF-");
});

// ---- 10.4: ตัวเดินขั้นตอน + 3 ระดับ (ข้อมูลจาก golden ของหลังบ้านจริง) ----
const golden = (name: string) => JSON.parse(readFileSync(path.resolve("tests/golden", name), "utf-8"));
const DAILY_TRACE = golden("trace/daily_161120261800_pdf.json");
const GENERIC_DOC = golden("generic/generic_enso_2569_09.json");
const GENERIC_TRACE = golden("generic/generic_enso_2569_09.trace.json");
const stepper = (page: Page) => page.getByRole("region", { name: "ระบบทำอะไรกับไฟล์นี้ทีละขั้น" });
const stepTitle = (page: Page) => page.getByTestId("step-title");

test("ขอภาพขั้นตอนทุกครั้ง และเดินครบทุกขั้นด้วยปุ่ม (ภาพหน้าจอทุกขั้น 375/1280)", async ({ page }) => {
  let url = "";
  await page.route("**/api/summarize**", (route) => {
    url = route.request().url();
    return json(route, 200, { ok: true, kind: "issue", document: ISSUE, trace: DAILY_TRACE });
  });
  await page.goto("/demo");
  await upload(page);
  expect(url).toContain("trace=1");
  const box = stepper(page);
  await expect(box).toBeVisible();
  const steps = DAILY_TRACE.steps as { id: string; title_th: string }[];
  for (const [i, step] of steps.entries()) {
    await expect(box.getByText(`ขั้นที่ ${i + 1} จาก ${steps.length}`)).toBeVisible();
    await expect(stepTitle(page)).toHaveText(step.title_th);
    for (const width of [375, 1280]) {
      await page.setViewportSize({ width, height: 900 });
      await box.screenshot({
        path: `test-results/screens/demo-trace-${String(i + 1).padStart(2, "0")}-${step.id}-${width}.png`,
        animations: "disabled",
      });
    }
    if (i < steps.length - 1) await box.getByRole("button", { name: "ถัดไป" }).click();
  }
  await expect(box.getByRole("button", { name: "ถัดไป" })).toBeDisabled();
  // ผลสรุปยังเป็นการ์ด 7 ภาคชุดเดิม
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(7);
});

test("ตัวเดินขั้นตอน: คีย์บอร์ด ลูกศรซ้าย/ขวา และปุ่มข้ามไปผลลัพธ์", async ({ page }) => {
  await page.route("**/api/summarize**", (route) =>
    json(route, 200, { ok: true, kind: "issue", document: ISSUE, trace: DAILY_TRACE }),
  );
  await page.goto("/demo");
  await upload(page);
  const box = stepper(page);
  await expect(box.getByRole("button", { name: "ย้อนกลับ" })).toBeDisabled();
  await box.getByRole("button", { name: "ถัดไป" }).focus();
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("ArrowRight");
  await expect(box.getByText("ขั้นที่ 3 จาก")).toBeVisible();
  await page.keyboard.press("ArrowLeft");
  await expect(stepTitle(page)).toHaveText(DAILY_TRACE.steps[1].title_th);
  await box.getByRole("button", { name: "ข้ามไปผลลัพธ์" }).click();
  await expect(page.getByRole("heading", { level: 2, name: "ผลสรุปพยากรณ์รายวัน" })).toBeFocused();
});

test("ขั้นคัดคำ: เห็นคำที่ถูกทิ้ง/ตัวเลขเป็น <num> พร้อมคำอธิบาย ขั้นจัดประเภทเห็นคะแนนเป็นร้อยละ", async ({ page }) => {
  const trace = structuredClone(DAILY_TRACE);
  const tokenize = trace.steps.find((s: { id: string }) => s.id === "tokenize");
  const filter = trace.steps.find((s: { id: string }) => s.id === "filter_tokens");
  tokenize.data.tokens = ["ฝน", " ", "30", "."];
  filter.data = { kept: ["ฝน", "<num>"], dropped: [" ", "."], numbers: ["30"], unknown: [] };
  await page.route("**/api/summarize**", (route) => json(route, 200, { ok: true, kind: "issue", document: ISSUE, trace }));
  await page.goto("/demo");
  await upload(page);
  const box = stepper(page);
  const ids = trace.steps.map((s: { id: string }) => s.id);
  for (let i = 0; i < ids.indexOf("filter_tokens"); i++) await box.getByRole("button", { name: "ถัดไป" }).click();
  const tokens = box.getByRole("list", { name: "ผลการคัดคำ" });
  await expect(tokens.getByText("ช่องว่าง")).toBeVisible();
  await expect(tokens.getByText("→ <num>")).toBeVisible();
  await expect(tokens.getByText("ทิ้ง")).toHaveCount(2);
  await box.getByRole("button", { name: "ถัดไป" }).click();
  await expect(box.getByText("100%")).toBeVisible();
});

test("โหมดทั่วไป: ข้อความต้นฉบับพร้อมป้าย ความมั่นใจ และ ไม่แน่ใจ ภาพขั้นตอนไม่มีขั้นแม่แบบ", async ({ page }) => {
  await page.route("**/api/summarize**", (route) =>
    json(route, 200, { ok: true, kind: "generic", document: GENERIC_DOC, trace: GENERIC_TRACE }),
  );
  await page.goto("/demo");
  await upload(page);
  await expect(page.getByRole("heading", { level: 2, name: "ผลอ่านเอกสาร (โหมดทั่วไป)" })).toBeVisible();
  await expect(page.getByText(GENERIC_DOC.title).first()).toBeVisible();
  await expect(page.getByText("ไม่แน่ใจ", { exact: true }).first()).toBeVisible();
  await expect(page.getByText(/^มั่นใจ \d+%$/).first()).toBeVisible();
  await expect(page.getByText("ไฟล์นี้ดูไม่เหมือนเอกสารของกรมอุตุนิยมวิทยา")).toHaveCount(0);
  const box = stepper(page);
  const steps = GENERIC_TRACE.steps as { id: string }[];
  expect(steps.map((s) => s.id)).not.toContain("template");
  await expect(box.getByText(`ขั้นที่ 1 จาก ${steps.length}`)).toBeVisible();
  for (const width of [375, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    await page.screenshot({ path: `test-results/screens/demo-generic-${width}.png`, fullPage: true, animations: "disabled" });
    expect(await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)).toBeLessThanOrEqual(0);
  }
});

test("โหมดทั่วไปที่มีหัวข้อภาค: กรองตามภาคได้ และคำแนะนำ/ส่วนเปลี่ยนตามภาคที่เลือก", async ({ page }) => {
  const weekly = golden("generic/weekly_161120261100.json");
  await page.route("**/api/summarize**", (route) => json(route, 200, { ok: true, kind: "generic", document: weekly, trace: null }));
  await page.goto("/demo");
  await upload(page);
  const filter = page.getByRole("group", { name: "กรองตามภาค" });
  await expect(filter.getByRole("button", { name: "ทุกส่วน" })).toHaveAttribute("aria-pressed", "true");
  const units = page.locator("main ol > li");
  const all = await units.count();
  await filter.getByRole("button", { name: "ภาคเหนือ" }).click();
  await expect(filter.getByRole("button", { name: "ภาคเหนือ" })).toHaveAttribute("aria-pressed", "true");
  await expect.poll(() => units.count()).toBeLessThan(all);
  // หน่วยที่เหลือทุกหน่วยพูดถึงภาคเหนือ (ตามคำบอกที่ตั้ง)
  const north = weekly.sections
    .flatMap((s: { units: { text: string; regions: string[] }[] }) => s.units)
    .filter((u: { regions: string[] }) => u.regions.includes("north"));
  await expect(units).toHaveCount(north.length);
  await filter.getByRole("button", { name: "ทุกส่วน" }).click();
  await expect(units).toHaveCount(all);
});

test("โหมดทั่วไปที่ไม่ใช่เอกสาร TMD: แสดงพร้อมคำเตือน", async ({ page }) => {
  const doc = { ...GENERIC_DOC, tmd_like: false, warnings: ["not_tmd_like"] };
  await page.route("**/api/summarize**", (route) => json(route, 200, { ok: true, kind: "generic", document: doc, trace: null }));
  await page.goto("/demo");
  await upload(page);
  await expect(page.getByText("ไฟล์นี้ดูไม่เหมือนเอกสารของกรมอุตุนิยมวิทยา")).toBeVisible();
  await expect(stepper(page)).toHaveCount(0);
});

test("ประกาศเตือนภัย (11.4): แสดงการ์ดประกาศพร้อมตัวเดินขั้นตอน ไม่ใช่โหมดทั่วไป", async ({ page }) => {
  const warning = JSON.parse(readFileSync(path.resolve("tests/golden/warning/2569_315.json"), "utf-8"));
  const trace = JSON.parse(readFileSync(path.resolve("tests/golden/warning/2569_315.trace.json"), "utf-8"));
  await page.route("**/api/summarize**", (route) => json(route, 200, { ok: true, kind: "warning", document: warning, trace }));
  await page.goto("/demo");
  await upload(page);
  await expect(page.getByRole("heading", { level: 2, name: "ผลสรุปประกาศเตือนภัย" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 3, name: warning.title })).toBeVisible();
  await expect(page.getByText(`ประกาศเลขที่ ${warning.notice_no}`)).toBeVisible();
  for (const p of warning.precautions) await expect(page.getByText(p.text, { exact: true })).toBeVisible();
  await expect(page.getByText("ผลอ่านเอกสาร (โหมดทั่วไป)")).toHaveCount(0);
  await expect(stepper(page)).toBeVisible();
});

test("พยากรณ์เดินเรือ (11.6): แสดงการ์ด 4 พื้นที่ทะเลพร้อมตัวเดินขั้นตอน ไม่ใช่คำแจ้ง", async ({ page }) => {
  const shipping = JSON.parse(readFileSync(path.resolve("tests/golden/shipping/101120261900.json"), "utf-8"));
  const trace = JSON.parse(readFileSync(path.resolve("tests/golden/shipping/101120261900.trace.json"), "utf-8"));
  await page.route("**/api/summarize**", (route) => json(route, 200, { ok: true, kind: "shipping", document: shipping, trace }));
  await page.goto("/demo");
  await upload(page);
  await expect(page.getByRole("heading", { level: 2, name: "ผลสรุปพยากรณ์เดินเรือ" })).toBeVisible();
  await expect(page.getByText(shipping.source_label)).toBeVisible();
  for (const name of ["อ่าวไทยทั้งสองฝั่ง", "ทะเลอันดามันและช่องแคบมะละกา", "เส้นทางเดินเรือโกตาบารูถึงสิงคโปร์", "ปลายแหลมญวน"]) {
    await expect(page.getByRole("heading", { level: 3, name, exact: true })).toBeVisible();
  }
  await expect(page.getByText("ระบบอ่านเอกสารนี้ได้แล้ว")).toHaveCount(0);
  await expect(stepper(page)).toBeVisible();
  // เดินครบทุกขั้นด้วยปุ่มถัดไปได้ (ข้อมูลของขั้นเดินเรือต่างจากรายวัน ภาพต้องไม่พัง)
  const next = stepper(page).getByRole("button", { name: "ถัดไป" });
  for (let i = 0; i < trace.steps.length - 1; i++) await next.click();
  await expect(next).toBeDisabled();
});

test("ชนิดที่ยังไม่มีหน้าแสดงผล (สรุปรายสัปดาห์): แจ้งว่าอ่านได้แล้วแต่ยังแสดงไม่ได้", async ({ page }) => {
  const weekly = JSON.parse(readFileSync(path.resolve("tests/fixtures/contract/weekly-example.json"), "utf-8"));
  await page.route("**/api/summarize**", (route) =>
    json(route, 200, { ok: true, kind: "weekly", document: weekly, trace: null }),
  );
  await page.goto("/demo");
  await upload(page);
  await expect(page.getByRole("status").getByText("ระบบอ่านเอกสารนี้ได้แล้ว")).toBeVisible();
  await expect(page.getByText("สรุปไฟล์นี้ไม่ได้")).toHaveCount(0);
});

test.describe("ลดการเคลื่อนไหว", () => {
  test.use({ reducedMotion: "reduce" });
  test("เปลี่ยนขั้นแล้วไม่มีอนิเมชันทำงาน", async ({ page }) => {
    await page.route("**/api/summarize**", (route) =>
      json(route, 200, { ok: true, kind: "issue", document: ISSUE, trace: DAILY_TRACE }),
    );
    await page.goto("/demo");
    await upload(page);
    const box = stepper(page);
    for (let i = 0; i < 7; i++) await box.getByRole("button", { name: "ถัดไป" }).click();
    expect(await page.evaluate(() => document.getAnimations().length)).toBe(0);
  });
});

test("ระหว่างประมวลผล: ปุ่มกดไม่ได้ บอกสถานะ และส่งครั้งเดียว", async ({ page }) => {
  let calls = 0;
  let release: () => void = () => {};
  const held = new Promise<void>((resolve) => (release = resolve));
  await page.route("**/api/summarize**", async (route) => {
    calls += 1;
    await held;
    await json(route, 200, { ok: true, kind: "issue", document: ISSUE, trace: null });
  });
  await page.goto("/demo");
  await upload(page);
  await expect(submit(page)).toBeDisabled();
  await expect(page.getByText("กำลังอ่านและสรุปไฟล์")).toBeVisible();
  await submit(page).click({ force: true });
  release();
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(7);
  expect(calls).toBe(1);
});

for (const code of Object.keys(MESSAGES)) {
  test(`ฟังก์ชันตอบ ${code}: แสดงข้อความของรหัสนั้น`, async ({ page }) => {
    const fullMessage = {
      unsupported_document: "ไฟล์นี้ไม่ใช่ PDF กรุณาเลือกไฟล์ PDF จากเว็บไซต์กรมอุตุนิยมวิทยา",
    }[code] ?? MESSAGES[code];
    await page.route("**/api/summarize**", (route) =>
      json(route, code === "too_large" ? 413 : 422, { ok: false, error: { code, message_th: fullMessage } }),
    );
    await page.goto("/demo");
    await upload(page);
    await expect(page.getByRole("status").getByText(MESSAGES[code])).toBeVisible();
    await expect(page.getByRole("heading", { level: 3 })).toHaveCount(0);
    // เลือกไฟล์ใหม่แล้วข้อความเดิมต้องหาย
    await page.getByLabel("เลือกไฟล์ PDF พยากรณ์ของกรมอุตุนิยมวิทยา").setInputFiles({ ...PDF, name: "other.pdf" });
    await expect(page.getByText(MESSAGES[code])).toHaveCount(0);
  });
}

test("ลากผ่านป้ายข้างในกรอบ ไฟยังติด / ระหว่างประมวลผลไม่แสดงว่าวางได้", async ({ page }) => {
  let release: () => void = () => {};
  const held = new Promise<void>((resolve) => (release = resolve));
  await page.route("**/api/summarize**", async (route) => {
    await held;
    await json(route, 200, { ok: true, kind: "issue", document: ISSUE, trace: null });
  });
  await page.goto("/demo");
  const zone = page.getByTestId("dropzone");
  const label = zone.locator("label").first();
  const isActive = () => zone.evaluate((el) => el.classList.contains("border-ink"));
  const transfer = await page.evaluateHandle(() => new DataTransfer());
  // เหตุการณ์แรกหลังโหลดหน้าอาจมาก่อน React ผูกตัวจัดการ (hydration ช้าตอนเครื่องหนัก) จึงส่งซ้ำจนไฟติด
  await expect
    .poll(async () => {
      await zone.dispatchEvent("dragover", { dataTransfer: transfer });
      return isActive();
    })
    .toBe(true);
  // dragleave ที่ relatedTarget ยังอยู่ในกรอบ (เลื่อนไปบนป้าย) ต้องไม่ดับไฟ
  await zone.evaluate((el, target) => {
    el.dispatchEvent(new DragEvent("dragleave", { bubbles: true, relatedTarget: target }));
  }, await label.elementHandle());
  expect(await isActive()).toBe(true);
  await zone.dispatchEvent("dragleave", { dataTransfer: transfer });
  await expect.poll(isActive).toBe(false);
  await upload(page);
  await zone.dispatchEvent("dragover", { dataTransfer: transfer });
  expect(await isActive()).toBe(false);
  release();
});

test.describe("ตรวจในเบราว์เซอร์ก่อนส่ง (ไม่เรียกฟังก์ชัน)", () => {
  const cases = [
    { name: "ใหญ่เกิน 4 MB", file: { ...PDF, buffer: Buffer.alloc(4 * 1024 * 1024 + 1, 0x20) }, code: "too_large" },
    { name: "ไม่ใช่ PDF", file: { name: "notes.txt", mimeType: "text/plain", buffer: Buffer.from("hello") }, code: "unsupported_document" },
    { name: "ไฟล์ว่าง", file: { ...PDF, buffer: Buffer.alloc(0) }, code: "empty_file" },
  ];
  for (const c of cases) {
    test(c.name, async ({ page }) => {
      let calls = 0;
      await page.route("**/api/summarize**", (route) => {
        calls += 1;
        return json(route, 500, {});
      });
      await page.goto("/demo");
      await upload(page, c.file);
      await expect(page.getByRole("status").getByText(MESSAGES[c.code])).toBeVisible();
      expect(calls).toBe(0);
    });
  }
});

test("ติดต่อระบบไม่ได้ หรือได้คำตอบที่ไม่ใช่ JSON ของเรา", async ({ page }) => {
  await page.route("**/api/summarize**", (route) => route.abort());
  await page.goto("/demo");
  await upload(page);
  await expect(page.getByRole("status").getByText("ติดต่อระบบสรุปไม่สำเร็จ")).toBeVisible();
  await page.unroute("**/api/summarize**");
  await page.route("**/api/summarize**", (route) =>
    route.fulfill({ status: 413, contentType: "text/html", body: "<html>Request Entity Too Large</html>" }),
  );
  await submit(page).click();
  await expect(page.getByRole("status").getByText("ติดต่อระบบสรุปไม่สำเร็จ")).toBeVisible();
});

test("ลากไฟล์มาวางในกรอบได้", async ({ page }) => {
  await page.route("**/api/summarize**", (route) => json(route, 200, { ok: true, kind: "issue", document: ISSUE, trace: null }));
  await page.goto("/demo");
  const transfer = await page.evaluateHandle(() => {
    const dt = new DataTransfer();
    dt.items.add(new File(["%PDF-1.4 drop"], "dropped.pdf", { type: "application/pdf" }));
    return dt;
  });
  await page.getByTestId("dropzone").dispatchEvent("drop", { dataTransfer: transfer });
  await expect(page.getByText("dropped.pdf")).toBeVisible();
  await submit(page).click();
  await expect(page.getByRole("heading", { level: 3 })).toHaveCount(7);
});

test("ใช้คีย์บอร์ดอย่างเดียวได้: Tab ถึงช่องเลือกไฟล์และปุ่ม", async ({ page }) => {
  await page.goto("/demo");
  const input = page.getByLabel("เลือกไฟล์ PDF พยากรณ์ของกรมอุตุนิยมวิทยา");
  await input.focus();
  await expect(input).toBeFocused();
  await input.setInputFiles(PDF);
  await page.keyboard.press("Tab");
  await expect(submit(page)).toBeFocused();
});

test.describe("ภาพหน้าจอทุกสถานะ", () => {
  for (const width of [375, 1280]) {
    test(`กว้าง ${width}px ไม่มี scroll แนวนอน`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      let mode: "hold" | "ok" | "error" = "hold";
      let release: () => void = () => {};
      const held = new Promise<void>((resolve) => (release = resolve));
      await page.route("**/api/summarize**", async (route) => {
        if (mode === "hold") await held;
        if (mode === "error") {
          return json(route, 422, { ok: false, error: { code: "extract_failed", message_th: MESSAGES.extract_failed } });
        }
        return json(route, 200, { ok: true, kind: "issue", document: ISSUE, trace: null });
      });
      const shot = async (state: string) => {
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
        expect(overflow, state).toBeLessThanOrEqual(0);
        await page.screenshot({ path: `test-results/screens/demo-${state}-${width}.png`, fullPage: true });
      };
      await page.goto("/demo");
      await shot("idle");
      await upload(page);
      await expect(page.getByText("กำลังอ่านและสรุปไฟล์")).toBeVisible();
      await shot("busy");
      mode = "ok";
      release();
      await expect(page.getByRole("heading", { level: 3 })).toHaveCount(7);
      await shot("result");
      mode = "error";
      await submit(page).click();
      await expect(page.getByRole("status").getByText(MESSAGES.extract_failed)).toBeVisible();
      await shot("error");
    });
  }
});
