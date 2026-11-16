// /summaries (11.5): อ่าน query แบบไม่เชื่อค่า + ลิงก์ที่คงตัวเลือกไว้
import { describe, expect, it } from "vitest";

import { isRegionKey } from "@/lib/format/thai";
import { parseSummariesQuery, splitCellLead, summariesHref } from "@/lib/summaries";

describe("ลิงก์ /summaries", () => {
  it("ค่าเริ่มต้นไม่ใส่ใน URL และคงตัวเลือกที่ระบุ", () => {
    expect(summariesHref({ issue: null, month: null, region: null })).toBe("/summaries");
    expect(summariesHref({ issue: "310820261200", month: "2026-08", region: "north" })).toBe(
      "/summaries?issue=310820261200&month=2026-08&region=north",
    );
    expect(summariesHref({ issue: null, month: "2026-08", region: null })).toBe("/summaries?month=2026-08");
  });

  it("อ่าน query: ค่าผิดรูปใช้ค่าเริ่มต้น (รหัสต้อง 12 หลัก เดือนต้อง YYYY-MM ภาคต้องรู้จัก)", () => {
    expect(parseSummariesQuery({ issue: "310820261200", month: "2026-08", region: "central" }, isRegionKey)).toEqual({
      issue: "310820261200",
      month: "2026-08",
      region: "central",
    });
    for (const raw of [
      { issue: "abc", month: "2026-13", region: "mars" },
      { issue: ["310820261200"], month: ["2026-08"] },
      { issue: "31082026120", month: "2026-8" },
      {},
    ]) {
      expect(parseSummariesQuery(raw, isRegionKey)).toEqual({ issue: null, month: null, region: null });
    }
  });
});

describe("ช่องตารางของสัปดาห์", () => {
  it("แยกค่านำออกจากข้อความโดยต่อกันได้ข้อความเดิม (ฝน อุณหภูมิ ทั้งสองสัญลักษณ์องศา)", () => {
    for (const text of [
      "61.5 มม. ที่ อ.แม่สอด จ.ตาก เมื่อวันที่ 26 ส.ค.",
      "38.5 º ซ. ที่ อ.ชัยบาดาล จ.ลพบุรี เมื่อวันที่ 12 เม.ย. (40.0 ° ซ. ที่ อ.ลับแล เมื่อวันที่ 11 เม.ย.)",
    ]) {
      const split = splitCellLead(text);
      expect(split).not.toBeNull();
      expect(`${split!.lead} ${split!.rest}`).toBe(text);
    }
    expect(splitCellLead("61.5 มม. ที่ อ.แม่สอด")?.lead).toBe("61.5 มม.");
    expect(splitCellLead("ภาคกลาง 37.9 º ซ. ที่ อ.ก")).toBeNull();
  });
});

