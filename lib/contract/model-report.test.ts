import { readFileSync } from "node:fs";
import path from "node:path";

import { describe, expect, it } from "vitest";

import { modelReportItemSchema, modelReportSchema } from "@/lib/contract/model-report";

const ROOT = path.resolve(import.meta.dirname, "../..");
const read = (name: string) => JSON.parse(readFileSync(path.join(ROOT, "lib/generated", name), "utf-8"));
const report = read("model-report.json");
const schema = read("model-report.schema.json");

describe("รายงานโมเดล", () => {
  it("ไฟล์จริงผ่าน Zod", () => {
    const parsed = modelReportSchema.parse(report);
    expect(parsed.models[0].facts.total_units).toBe(292);
    // 11.3: แท็บประกาศเตือนภัย 3 ป้าย ไม่มีค่าถ่วงน้ำหนัก
    const warning = parsed.models.find((m) => m.id === "warning-role");
    expect(warning?.labels).toEqual(["weather", "advice", "cause"]);
    expect(warning?.results.every((r) => r.test_all_weighted === null)).toBe(true);
  });

  it("ชื่อฟิลด์ตรงกับ JSON Schema ของ pydantic", () => {
    const pyFields = Object.keys(schema.$defs.SentenceRoleReport.properties).sort();
    expect(Object.keys(modelReportItemSchema.shape).sort()).toEqual(pyFields);
  });

  it("ฟิลด์ที่ไม่รู้จักถูกปฏิเสธ (strict)", () => {
    const bad = structuredClone(report);
    bad.models[0].extra = 1;
    expect(modelReportSchema.safeParse(bad).success).toBe(false);
  });
});
