import { describe, expect, it } from "vitest";

import { cn } from "@/lib/cn";
import { REGION_KEYS } from "@/lib/contract/issue";
import {
  bangkokMonthKey,
  isRegionKey,
  LINE_KIND_LABELS,
  REGION_LABELS,
  thaiDate,
  thaiDateRange,
  thaiDateTimeShort,
  thaiMonthOfKey,
} from "@/lib/format/thai";

describe("วันที่ไทย", () => {
  it("แสดงเป็น พ.ศ. ตามเวลาไทย", () => {
    expect(thaiDate("2026-11-16T18:00:00+07:00")).toBe("16 พฤศจิกายน 2569");
    // 23.30 UTC = 06.30 ของวันถัดไปในไทย
    expect(thaiDateTimeShort("2026-11-15T23:30:00Z")).toBe("16 พ.ย. 2569 06.30 น.");
  });

  it("ช่วงวันของฉบับ 7 วัน", () => {
    expect(thaiDateRange("2026-11-17", "2026-11-19")).toBe("17-19 พ.ย. 2569");
    expect(thaiDateRange("2026-11-18", "2026-11-18")).toBe("18 พ.ย. 2569");
    expect(thaiDateRange("2026-10-31", "2026-11-02")).toBe("31 ต.ค. - 2 พ.ย. 2569");
    expect(thaiDateRange("2026-12-30", "2027-01-02")).toBe("30 ธ.ค. 2569 - 2 ม.ค. 2570");
  });
});

describe("เดือนของตัวเลือกรอบ (11.6)", () => {
  it("คีย์เดือนตามเวลาไทย ไม่ใช่ UTC", () => {
    expect(bangkokMonthKey("2026-11-16T18:00:00+07:00")).toBe("2026-11");
    // 31 ต.ค. 17:00 UTC = 1 พ.ย. 00:00 เวลาไทย
    expect(bangkokMonthKey("2026-10-31T17:00:00.000Z")).toBe("2026-11");
    expect(bangkokMonthKey("2026-10-31T16:59:59.000Z")).toBe("2026-10");
    expect(bangkokMonthKey("2025-12-31T23:30:00+07:00")).toBe("2025-12");
  });

  it("ชื่อเดือน พ.ศ. จากคีย์ ถ้าคีย์ผิดรูปคืนตามเดิม", () => {
    expect(thaiMonthOfKey("2026-11")).toBe("พฤศจิกายน 2569");
    expect(thaiMonthOfKey("2025-01")).toBe("มกราคม 2568");
    expect(thaiMonthOfKey("2026-13")).toBe("2026-13");
    expect(thaiMonthOfKey("abc")).toBe("abc");
  });
});

describe("ชื่อภาคและชนิด", () => {
  it("ครบทุกภาคตามสัญญา", () => {
    expect(Object.keys(REGION_LABELS).sort()).toEqual([...REGION_KEYS].sort());
    expect(Object.keys(LINE_KIND_LABELS)).toHaveLength(6);
  });

  it("ตรวจคีย์ภาคจาก query string", () => {
    expect(isRegionKey("north")).toBe(true);
    expect(isRegionKey("mars")).toBe(false);
    expect(isRegionKey(undefined)).toBe(false);
  });
});

describe("cn", () => {
  it("ไม่ตัดขนาดตัวอักษรทิ้งเมื่อมีสีข้อความ", () => {
    expect(cn("text-body-md", "text-ink")).toBe("text-body-md text-ink");
    expect(cn("text-body-md", "text-title-md")).toBe("text-title-md");
    expect(cn("px-4", false && "px-2", "px-6")).toBe("px-6");
  });
});
