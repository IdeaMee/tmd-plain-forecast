import { readFileSync } from "node:fs";
import path from "node:path";

import { describe, expect, it } from "vitest";

import { parseIssuePayload, toListItem } from "@/lib/forecast-rows";

const ROOT = path.resolve(import.meta.dirname, "..");
const payload = readFileSync(path.join(ROOT, "tests/fixtures/contract/issue-daily-example.json"), "utf-8");

describe("แถวจาก forecast_issue", () => {
  it("payload เป็นออบเจกต์หรือข้อความ JSON ก็อ่านได้", () => {
    expect(parseIssuePayload(JSON.parse(payload)).doc_type).toBe("daily");
    expect(parseIssuePayload(payload).doc_type).toBe("daily");
  });

  it("payload ที่ไม่ผ่านสัญญาโยนข้อผิดพลาด (ไม่แสดงข้อมูลเสีย)", () => {
    expect(() => parseIssuePayload({ issue_id: "x" })).toThrow();
  });

  it("แปลงแถวรายการเป็น DTO เล็ก", () => {
    const item = toListItem({
      issue_id: "161120261800",
      doc_type: "daily",
      issued_at: new Date("2026-11-16T11:00:00Z"),
      source_label: "ประจำวันที่ 16 พฤศจิกายน 2569 17.00 น.",
    });
    expect(item).toEqual({
      issueId: "161120261800",
      docType: "daily",
      issuedAt: "2026-11-16T11:00:00.000Z",
      sourceLabel: "ประจำวันที่ 16 พฤศจิกายน 2569 17.00 น.",
    });
  });
});
