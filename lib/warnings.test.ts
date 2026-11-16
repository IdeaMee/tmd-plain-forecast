import { existsSync, readdirSync, readFileSync } from "node:fs";
import path from "node:path";

import { describe, expect, it } from "vitest";

import { warningNoticeSchema } from "@/lib/contract/documents";
import {
  groupSeriesByMonth,
  linkSeries,
  seriesOf,
  toWarningListItem,
  toWarningListItemFromRow,
  type WarningListItem,
} from "@/lib/warnings";

const DIR = path.resolve(import.meta.dirname, "../data/processed/warning");

function item(id: string, no: number, at: string, next: string | null = null, title = "ฝนตกหนัก"): WarningListItem {
  return { issueId: id, title, seriesNo: no, noticeNo: `${id.split("_")[1]}/2569`, issuedAt: at, effectText: null, nextIssueAt: next };
}

describe("linkSeries", () => {
  it("ฉบับที่ 1 เริ่มชุดใหม่ ฉบับที่ n ต่อจาก n-1 และฉบับสุดท้ายปิดชุด", () => {
    const series = linkSeries([
      item("2569_2", 2, "2026-11-02T10:00:00+07:00", null),
      item("2569_1", 1, "2026-11-01T17:00:00+07:00", "2026-11-02T10:00:00+07:00"),
      item("2569_9", 1, "2026-11-10T17:00:00+07:00", "2026-11-11T05:00:00+07:00"),
    ]);
    expect(series.map((s) => [s.id, s.notices.map((n) => n.seriesNo), s.closed, s.completeStart])).toEqual([
      ["2569_1", [1, 2], true, true],
      ["2569_9", [1], false, true],
    ]);
  });

  it("ห่างเกิน 48 ชั่วโมงไม่ต่อชุด ชุดที่ฉบับแรกไม่ใช่ที่ 1 ถูกทำเครื่องหมายว่าเริ่มไม่ครบ", () => {
    const series = linkSeries([
      item("2569_1", 1, "2026-11-01T17:00:00+07:00", "2026-11-02T10:00:00+07:00"),
      item("2569_2", 2, "2026-11-05T10:00:00+07:00", null),
    ]);
    expect(series).toHaveLength(2);
    expect(series[1].completeStart).toBe(false);
  });

  it("สองเหตุการณ์ซ้อนกัน เลือกชุดที่บอกเวลาฉบับต่อไปตรงกับเวลาฉบับนี้ก่อน แล้วหัวเรื่องเหมือนกัน", () => {
    const series = linkSeries([
      item("2569_1", 1, "2026-11-01T05:00:00+07:00", "2026-11-01T17:00:00+07:00", "เรื่องเอ"),
      item("2569_2", 1, "2026-11-01T06:00:00+07:00", "2026-11-01T18:00:00+07:00", "เรื่องบี"),
      item("2569_3", 2, "2026-11-01T17:00:00+07:00", null, "เรื่องเอ"),
      item("2569_4", 2, "2026-11-01T18:00:00+07:00", null, "เรื่องบี"),
    ]);
    expect(series.map((s) => s.notices.map((n) => n.issueId))).toEqual([
      ["2569_1", "2569_3"],
      ["2569_2", "2569_4"],
    ]);
  });
});

describe("groupSeriesByMonth", () => {
  it("เรียงใหม่สุดก่อน จัดกลุ่มตามเดือน พ.ศ. ของฉบับล่าสุดของชุด", () => {
    const series = linkSeries([
      item("2569_1", 1, "2026-10-30T10:00:00+07:00", null),
      item("2569_2", 1, "2026-11-03T10:00:00+07:00", null),
      item("2569_3", 1, "2026-11-10T10:00:00+07:00", null),
    ]);
    const groups = groupSeriesByMonth(series);
    expect(groups.map((g) => [g.month, g.series.map((s) => s.id)])).toEqual([
      ["พฤศจิกายน 2569", ["2569_3", "2569_2"]],
      ["ตุลาคม 2569", ["2569_1"]],
    ]);
  });
});

describe("toWarningListItemFromRow", () => {
  it("แปลงแถวจากฐานข้อมูล (วันที่เป็น Date ได้) และปฏิเสธแถวผิดรูป", () => {
    const row = {
      issue_id: "2569_315",
      issued_at: new Date("2026-11-17T22:00:00Z"),
      title: "ฝนตกหนัก",
      series_no: 7,
      notice_no: "315/2569",
      effect_text: null,
      next_issue_at: "2026-11-18T17:00:00+07:00",
    };
    expect(toWarningListItemFromRow(row)).toMatchObject({ issueId: "2569_315", seriesNo: 7, issuedAt: "2026-11-17T22:00:00.000Z" });
    expect(() => toWarningListItemFromRow({ ...row, issue_id: "315" })).toThrow();
  });
});

// ข้อมูลจริงใน data/processed/warning (ผลของ scripts/run_pipeline.py) ต้องได้ชุดเดียวกับ series.py
describe.skipIf(!existsSync(DIR))("ข้อมูลจริง", () => {
  const items = readdirSync(DIR)
    .filter((f) => f.endsWith(".json"))
    .map((f) => toWarningListItem(warningNoticeSchema.parse(JSON.parse(readFileSync(path.join(DIR, f), "utf-8")))));
  const series = linkSeries(items);

  it("155 ฉบับ -> 13 ชุด ปิด 12 ชุด ความยาวตรง docs/results/warning-check.md", () => {
    expect(items).toHaveLength(155);
    expect(series).toHaveLength(13);
    expect(series.filter((s) => s.closed)).toHaveLength(12);
    expect(series.map((s) => s.notices.length)).toEqual([7, 13, 10, 14, 12, 18, 12, 13, 13, 11, 15, 10, 7]);
    expect(series.filter((s) => !s.completeStart).map((s) => s.id)).toEqual(["2569_161"]);
    expect(series.map((s) => s.id)).toEqual([
      "2569_161", "2569_168", "2569_181", "2569_191", "2569_205", "2569_217", "2569_235",
      "2569_247", "2569_260", "2569_273", "2569_284", "2569_299", "2569_309",
    ]);
  });

  it("ทุกฉบับอยู่ในชุดเดียว และฉบับล่าสุดของข้อมูลอยู่ชุดสุดท้ายที่ยังเปิด", () => {
    expect(series.flatMap((s) => s.notices)).toHaveLength(155);
    const latest = series.at(-1)!;
    expect(latest.closed).toBe(false);
    expect(seriesOf(series, "2569_315")).toBe(latest);
    expect(seriesOf(series, "nope")).toBeUndefined();
  });
});
