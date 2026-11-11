import { readFileSync } from "node:fs";
import path from "node:path";

import { describe, expect, it } from "vitest";

import { ERROR_CODES, ERROR_MESSAGES_TH, summarizeResponseSchema } from "@/lib/contract/summarize";

const ROOT = path.resolve(import.meta.dirname, "../..");
const jsonSchema = JSON.parse(readFileSync(path.join(ROOT, "lib/contract/summarize-response.schema.json"), "utf-8"));
const contractPy = readFileSync(path.join(ROOT, "src/tmd_plain/contract.py"), "utf-8");
const sample = JSON.parse(readFileSync(path.join(ROOT, "tests/fixtures/contract/issue-daily-example.json"), "utf-8"));

describe("คำตอบ /api/summarize ตรงกับสัญญาฝั่ง Python", () => {
  it("รหัสข้อผิดพลาดตรงกับ JSON Schema", () => {
    expect([...ERROR_CODES].sort()).toEqual([...jsonSchema.$defs.ErrorDetail.properties.code.enum].sort());
  });

  it.each(ERROR_CODES)("ข้อความภาษาไทยของ %s เหมือน ERROR_MESSAGES_TH ใน contract.py", (code) => {
    expect(contractPy).toContain(`"${code}": "${ERROR_MESSAGES_TH[code]}"`);
  });

  it("รับคำตอบสำเร็จและข้อผิดพลาด ปฏิเสธรูปอื่น", () => {
    expect(summarizeResponseSchema.safeParse({ ok: true, kind: "issue", document: sample, trace: null }).success).toBe(
      true,
    );
    // รูป v1 ใช้ไม่ได้แล้ว (ADR 0017)
    expect(summarizeResponseSchema.safeParse({ ok: true, issue: sample }).success).toBe(false);
    const err = { ok: false, error: { code: "too_large", message_th: ERROR_MESSAGES_TH.too_large } };
    expect(summarizeResponseSchema.safeParse(err).success).toBe(true);
    expect(summarizeResponseSchema.safeParse({ ok: false }).success).toBe(false);
    expect(summarizeResponseSchema.safeParse({ ok: false, error: { code: "boom", message_th: "x" } }).success).toBe(false);
    expect(summarizeResponseSchema.safeParse("<html>413</html>").success).toBe(false);
  });
});
