import { describe, expect, it } from "vitest";

import { groupByDay, splitLabel } from "@/lib/history";

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
