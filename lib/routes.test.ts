import { describe, expect, it } from "vitest";

import { isRegionKey } from "@/lib/format/thai";
import { homeHref, parseHomeQuery } from "@/lib/routes";

describe("ลิงก์หน้าแรก", () => {
  it("ค่าเริ่มต้นไม่อยู่ใน URL", () => {
    expect(homeHref({ type: "daily", issue: null, month: null, region: null })).toBe("/");
    expect(homeHref({ type: "sevenday", issue: null, month: null, region: null })).toBe("/?type=sevenday");
    // เดินเรือไม่มีตัวเลือกภาค
    expect(homeHref({ type: "shipping", issue: "161120261300", month: null, region: "north" })).toBe(
      "/?type=shipping&issue=161120261300",
    );
    expect(homeHref({ type: "daily", issue: "151120261200", month: null, region: "north" })).toBe(
      "/?issue=151120261200&region=north",
    );
  });

  it("เดือนของตัวเลือกรอบ (11.6) อยู่ใน URL เมื่อระบุ และคงไว้กับฉบับและภาค", () => {
    expect(homeHref({ type: "daily", issue: null, month: "2026-10", region: null })).toBe("/?month=2026-10");
    expect(homeHref({ type: "sevenday", issue: "261101", month: "2026-10", region: "east" })).toBe(
      "/?type=sevenday&issue=261101&month=2026-10&region=east",
    );
  });

  it("ค่าที่ไม่รู้จักหรือรูปแบบผิดกลับเป็นค่าเริ่มต้น", () => {
    expect(parseHomeQuery({ type: "x", region: ["north"], issue: "abc", month: "2026-13" }, isRegionKey)).toEqual({
      type: "daily",
      issue: null,
      month: null,
      region: null,
    });
    // รหัส 6 หลักใช้กับ 7 วันเท่านั้น
    expect(parseHomeQuery({ issue: "261116" }, isRegionKey).issue).toBeNull();
    expect(parseHomeQuery({ type: "sevenday", issue: "261116", month: "2026-11", region: "east" }, isRegionKey)).toEqual({
      type: "sevenday",
      issue: "261116",
      month: "2026-11",
      region: "east",
    });
    expect(parseHomeQuery({ type: "shipping", issue: "161120261300", region: "east" }, isRegionKey)).toEqual({
      type: "shipping",
      issue: "161120261300",
      month: null,
      region: null,
    });
    expect(parseHomeQuery({ type: "shipping", issue: "261116" }, isRegionKey).issue).toBeNull();
    expect(parseHomeQuery({ month: ["2026-11"] }, isRegionKey).month).toBeNull();
  });
});
