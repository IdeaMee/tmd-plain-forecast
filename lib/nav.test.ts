import { existsSync } from "node:fs";
import path from "node:path";

import { describe, expect, it } from "vitest";

import { isGroupCurrent, NAV_CTA, NAV_GROUPS, navPaths } from "@/lib/nav";

const ROOT = path.resolve(import.meta.dirname, "..");

describe("เมนู", () => {
  it("ทุกลิงก์ในเมนูมีหน้าจริง (ไม่มีลิงก์ 404)", () => {
    for (const p of navPaths()) {
      const page = path.join(ROOT, "app", ...p.split("/").filter(Boolean), "page.tsx");
      expect(existsSync(page), p).toBe(true);
    }
  });

  it("ไม่มีหมวดว่าง และชื่อลิงก์ไม่ซ้ำกันในหมวด", () => {
    for (const g of NAV_GROUPS) {
      expect(g.links.length).toBeGreaterThan(0);
      expect(new Set(g.links.map((l) => l.label)).size).toBe(g.links.length);
    }
    expect(NAV_CTA.href).toBe("/demo");
  });

  it("หมวดปัจจุบันดูจาก path อย่างเดียว", () => {
    const forecast = NAV_GROUPS[0];
    expect(isGroupCurrent(forecast, "/")).toBe(true);
    expect(isGroupCurrent(forecast, "/demo")).toBe(false);
    // หน้าย่อยนับเป็นหมวดเดียวกัน แต่ "/" ไม่กินทุกหน้า
    const knowledge = NAV_GROUPS.find((g) => g.id === "knowledge")!;
    expect(isGroupCurrent(knowledge, "/model/warning")).toBe(true);
    expect(isGroupCurrent(forecast, "/model/warning")).toBe(false);
  });
});
