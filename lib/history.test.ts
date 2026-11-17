import { describe, expect, it } from "vitest";

import {
  countByMonth,
  groupByDay,
  groupWeeks,
  neighborMonths,
  parseMonthParam,
  resolveMonth,
  splitLabel,
  weekShortLabel,
} from "@/lib/history";

const item = (issueId: string, sourceLabel: string) => ({
  issueId,
  docType: "daily" as const,
  issuedAt: "2026-11-16T11:00:00.000Z",
  sourceLabel,
});

describe("ประวัติย้อนหลัง", () => {
  it("แยกวันและรอบจากป้ายของ TMD", () => {
    expect(splitLabel("ประจำวันที่ 16 พฤศจิกายน 2569 17.00 น.")).toEqual({
      day: "16 พฤศจิกายน 2569",
      time: "17.00 น.",
    });
    expect(splitLabel("ประจำวันที่ 1 พฤศจิกายน 2569 รอบ 18.00 น.").time).toBe("18.00 น.");
    expect(splitLabel("ฉบับวันที่ 16 พฤศจิกายน 2569")).toEqual({ day: "16 พฤศจิกายน 2569", time: null });
    // พยากรณ์เดินเรือ (11.1) ใช้ป้ายเวลาออกประกาศ คงเครื่องหมาย : ของต้นฉบับ
    expect(splitLabel("ออกประกาศ 16 พฤศจิกายน 2569 13:00 น.")).toEqual({
      day: "16 พฤศจิกายน 2569",
      time: "13:00 น.",
    });
  });

  it("รวมรอบของวันเดียวกัน ใหม่สุดก่อน", () => {
    const groups = groupByDay([
      item("161120261800", "ประจำวันที่ 16 พฤศจิกายน 2569 17.00 น."),
      item("161120261200", "ประจำวันที่ 16 พฤศจิกายน 2569 11.00 น."),
      item("161120260000", "ประจำวันที่ 15 พฤศจิกายน 2569 23.00 น."),
    ]);
    expect(groups.map((g) => [g.day, g.entries.map((e) => e.label)])).toEqual([
      ["16 พฤศจิกายน 2569", ["17.00 น.", "11.00 น."]],
      ["15 พฤศจิกายน 2569", ["23.00 น."]],
    ]);
  });
});

describe("ตัวเลือกรอบรายเดือน (11.6)", () => {
  const at = (issuedAt: string) => ({ issuedAt });

  it("นับต่อเดือนตามเวลาไทย ใหม่สุดก่อน (ขอบเดือน 31 ต.ค. 17:00 UTC = 1 พ.ย. เวลาไทย)", () => {
    const months = countByMonth([
      at("2026-11-16T18:00:00+07:00"),
      at("2026-10-31T17:00:00.000Z"),
      at("2026-10-31T16:59:00.000Z"),
      at("2026-10-01T00:00:00+07:00"),
      at("2025-12-30T10:00:00+07:00"),
    ]);
    expect(months).toEqual([
      { month: "2026-11", count: 2 },
      { month: "2026-10", count: 2 },
      { month: "2025-12", count: 1 },
    ]);
  });

  it("เลือกเดือนที่แสดง: เดือนที่ขอ > เดือนของฉบับที่เลือก > เดือนล่าสุด > ไม่มีข้อมูล", () => {
    const months = [
      { month: "2026-11", count: 5 },
      { month: "2026-10", count: 3 },
    ];
    expect(resolveMonth(months, "2026-10", "2026-11-16T18:00:00+07:00")).toBe("2026-10");
    // เดือนที่ขอไม่มีข้อมูล = ถอยไปเดือนของฉบับที่เลือก
    expect(resolveMonth(months, "2024-01", "2026-10-05T10:00:00+07:00")).toBe("2026-10");
    expect(resolveMonth(months, null, null)).toBe("2026-11");
    expect(resolveMonth([], "2026-10", null)).toBeNull();
  });

  it("เดือนก่อน/ถัดไปที่มีข้อมูล", () => {
    const months = [{ month: "2026-11", count: 1 }, { month: "2026-09", count: 1 }, { month: "2025-12", count: 1 }];
    expect(neighborMonths(months, "2026-09")).toEqual({ older: "2025-12", newer: "2026-11" });
    expect(neighborMonths(months, "2026-11")).toEqual({ older: "2026-09", newer: null });
    expect(neighborMonths(months, "2025-12").older).toBeNull();
    expect(neighborMonths(months, "1999-01")).toEqual({ older: null, newer: null });
  });

  it("อ่าน ?month= แบบไม่เชื่อค่า", () => {
    expect(parseMonthParam("2026-11")).toBe("2026-11");
    for (const bad of ["2026-13", "2026-00", "26-11", "2026-1", "<script>", "", undefined, ["2026-11"]]) {
      expect(parseMonthParam(bad as string)).toBeNull();
    }
  });

  it("ป้ายสัปดาห์สั้นและกลุ่มสัปดาห์ของเดือน", () => {
    expect(weekShortLabel("24 สิงหาคม 2569 - 30 สิงหาคม 2569")).toBe("24-30 ส.ค. 2569");
    expect(weekShortLabel("28 กันยายน 2569 - 4 ตุลาคม 2569")).toBe("28 ก.ย. - 4 ต.ค. 2569");
    expect(weekShortLabel("29 ธันวาคม 2568 - 4 มกราคม 2569")).toBe("29 ธ.ค. 2568 - 4 ม.ค. 2569");
    expect(weekShortLabel("ไม่ใช่ช่วงสัปดาห์")).toBe("ไม่ใช่ช่วงสัปดาห์");
    const items = [
      { issueId: "a", docType: "weekly" as const, issuedAt: "2026-08-31T12:00:00+07:00", sourceLabel: "24 สิงหาคม 2569 - 30 สิงหาคม 2569" },
    ];
    expect(groupWeeks(items, "หัว")).toEqual([{ day: "หัว", entries: [{ issueId: "a", label: "24-30 ส.ค. 2569" }] }]);
    expect(groupWeeks([], "หัว")).toEqual([]);
  });
});
