import { readFileSync } from "node:fs";
import path from "node:path";

import { describe, expect, it } from "vitest";

import { ERROR_MESSAGES_TH } from "@/lib/contract/summarize";
import {
  checkFile,
  formatSize,
  MAX_UPLOAD_BYTES,
  NETWORK_MESSAGE_TH,
  PENDING_KIND_MESSAGE_TH,
  readResponse,
  SUMMARIZE_URL,
} from "@/lib/upload";

const ROOT = path.resolve(import.meta.dirname, "..");
const sample = JSON.parse(readFileSync(path.join(ROOT, "tests/fixtures/contract/issue-daily-example.json"), "utf-8"));

describe("checkFile ตรวจก่อนส่ง", () => {
  it("เพดานเท่ากับ max_upload_bytes ของท่อประมวลผล", () => {
    const toml = readFileSync(path.join(ROOT, "src/tmd_plain/config.toml"), "utf-8");
    expect(toml).toContain(`max_upload_bytes = ${MAX_UPLOAD_BYTES}`);
  });

  it.each([
    [{ name: "a.pdf", size: 0, type: "application/pdf" }, "empty_file"],
    [{ name: "a.pdf", size: MAX_UPLOAD_BYTES + 1, type: "application/pdf" }, "too_large"],
    [{ name: "a.docx", size: 10, type: "application/msword" }, "unsupported_document"],
    [{ name: "a.pdf", size: MAX_UPLOAD_BYTES, type: "application/pdf" }, null],
    // บางเบราว์เซอร์/ระบบไม่บอกชนิดไฟล์ ดูจากนามสกุลแทน
    [{ name: "T_261116.PDF", size: 10, type: "" }, null],
  ])("%o -> %s", (file, expected) => {
    expect(checkFile(file)).toBe(expected);
  });
});

describe("readResponse แปลงคำตอบ", () => {
  it("สำเร็จได้ issue", () => {
    const out = readResponse({ ok: true, kind: "issue", document: sample, trace: null });
    expect(out.kind === "ok" && out.result.kind === "issue" && out.result.document.issue_id).toBe(sample.issue_id);
  });

  it("ขอภาพขั้นตอนทุกครั้ง", () => {
    expect(SUMMARIZE_URL).toBe("/api/summarize?trace=1");
  });

  it("ข้อผิดพลาดใช้ message_th จากฟังก์ชัน", () => {
    const out = readResponse({ ok: false, error: { code: "extract_failed", message_th: ERROR_MESSAGES_TH.extract_failed } });
    expect(out).toEqual({ kind: "error", code: "extract_failed", message: ERROR_MESSAGES_TH.extract_failed });
  });

  it("โหมดทั่วไปพร้อม trace แสดงผลได้", () => {
    const generic = JSON.parse(
      readFileSync(path.join(ROOT, "tests/fixtures/contract/summarize-v2-generic-example.json"), "utf-8"),
    );
    const out = readResponse(generic);
    expect(out.kind === "ok" && out.result.kind === "generic" && out.result.trace !== null).toBe(true);
  });

  it("ประกาศเตือนภัยแสดงผลได้ (11.4) ไม่ใช่คำแจ้งว่ายังไม่รองรับ", () => {
    const warning = JSON.parse(readFileSync(path.join(ROOT, "tests/fixtures/contract/warning-example.json"), "utf-8"));
    const out = readResponse({ ok: true, kind: "warning", document: warning, trace: null });
    expect(out.kind === "ok" && out.result.kind === "warning" && out.result.document.issue_id === warning.issue_id).toBe(true);
  });

  it("พยากรณ์เดินเรือแสดงผลได้ (11.6) ไม่ใช่คำแจ้งว่ายังไม่รองรับ", () => {
    const shipping = JSON.parse(
      readFileSync(path.join(ROOT, "tests/fixtures/contract/shipping-example.json"), "utf-8"),
    );
    const out = readResponse({ ok: true, kind: "shipping", document: shipping, trace: null });
    expect(out.kind === "ok" && out.result.kind === "shipping" && out.result.document.issue_id === shipping.issue_id).toBe(true);
  });

  it("ชนิดที่ยังไม่มีหน้าแสดงผล (สรุปรายสัปดาห์) = แจ้งว่าอ่านได้แต่ยังแสดงไม่ได้ (ไม่ใช่ข้อผิดพลาด)", () => {
    const weekly = JSON.parse(readFileSync(path.join(ROOT, "tests/fixtures/contract/weekly-example.json"), "utf-8"));
    expect(readResponse({ ok: true, kind: "weekly", document: weekly, trace: null })).toEqual({
      kind: "notice",
      message: PENDING_KIND_MESSAGE_TH,
    });
  });

  it.each([null, "<html>Request Entity Too Large</html>", { ok: true, issue: sample }, { ok: true, kind: "issue" }])(
    "คำตอบที่ไม่ผ่านสัญญา (%o) = ติดต่อระบบไม่สำเร็จ",
    (body) => {
      expect(readResponse(body)).toEqual({ kind: "network", message: NETWORK_MESSAGE_TH });
    },
  );
});

it("formatSize", () => {
  expect(formatSize(312 * 1024)).toBe("312 KB");
  expect(formatSize(100)).toBe("1 KB");
  expect(formatSize(4.2 * 1024 * 1024)).toBe("4.2 MB");
});
