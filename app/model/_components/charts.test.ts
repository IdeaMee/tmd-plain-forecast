// ฟังก์ชันล้วนของกราฟหน้า /model
import { describe, expect, it } from "vitest";

import { pct, spreadLabels } from "@/app/model/_components/charts";

describe("spreadLabels", () => {
  it("ไม่ขยับป้ายที่ห่างกันพออยู่แล้ว", () => {
    expect(spreadLabels([10, 50], 14)).toEqual([10, 50]);
  });
  it("ดันป้ายล่างลงให้ห่างอย่างน้อย gap และคงลำดับเดิมของ input", () => {
    expect(spreadLabels([40, 35], 14)).toEqual([49, 35]);
    expect(spreadLabels([20, 20, 20], 10)).toEqual([20, 30, 40]);
  });
});

describe("pct", () => {
  it("แสดงร้อยละทศนิยมตามที่ขอ", () => {
    expect(pct(0.9667)).toBe("96.7%");
    expect(pct(0.9, 0)).toBe("90%");
  });
});
