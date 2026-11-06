import { readFileSync } from "node:fs";
import path from "node:path";

import { describe, expect, it } from "vitest";

import { LOADED_DOC_TYPES } from "../lib/contract/stored.ts";

import { checkFile, mergeEnv, missingKeys, parseEnv, readProcessed, UPSERT } from "./load-to-neon.mts";

const ROOT = path.resolve(import.meta.dirname, "..");
const REAL = path.join(ROOT, "data", "processed", "daily", "161120261800.json");

describe("parseEnv / mergeEnv / missingKeys", () => {
  it("อ่าน KEY=VALUE ข้ามคอมเมนต์ ตัดเครื่องหมายคำพูด และเก็บ = ในค่า", () => {
    const env = parseEnv('# c\n\nA=1\nB="two"\nC=x=y&z\n  D = \' sp \' \nnoequals\n');
    expect(env).toEqual({ A: "1", B: "two", C: "x=y&z", D: " sp " });
  });

  it("ค่าใน env ของเครื่องชนะไฟล์ เฉพาะคีย์ที่สคริปต์ใช้", () => {
    const merged = mergeEnv({ SITE_URL: "a", OTHER: "1" }, { SITE_URL: "b", PATH: "x" });
    expect(merged).toEqual({ SITE_URL: "b", OTHER: "1" });
  });

  it("บอกคีย์ที่ขาด", () => {
    expect(missingKeys({ SITE_URL: "a", REVALIDATE_SECRET: "" })).toEqual(["DATABASE_URL_DIRECT", "REVALIDATE_SECRET"]);
  });
});

describe("checkFile ตรวจด้วย Zod ชุดเดียวกับเว็บ", () => {
  const text = readFileSync(REAL, "utf-8");

  it("ไฟล์จริงผ่าน", () => {
    const res = checkFile(REAL, text);
    expect(res.ok && res.value.issue.issue_id).toBe("161120261800");
  });

  it.each([
    ["ไม่ใช่ JSON", REAL, "{oops", "ไม่ใช่ JSON"],
    ["ไม่ผ่านสัญญา", REAL, JSON.stringify({ issue_id: "x" }), "ไม่ผ่านสัญญา"],
    ["ชื่อไฟล์ไม่ตรง", path.join(path.dirname(REAL), "010120260000.json"), text, "ชื่อไฟล์ไม่ตรง"],
    ["โฟลเดอร์ไม่ตรงชนิด", path.join(ROOT, "x", "sevenday", "161120261800.json"), text, "ชื่อไฟล์ไม่ตรง"],
  ])("%s", (_name, file, body, message) => {
    const res = checkFile(file, body);
    expect(res.ok).toBe(false);
    expect(!res.ok && res.error).toContain(message);
  });
});

it("ไฟล์ทั้งหมดใน data/processed ผ่านสัญญา และมีครบทุกชนิดอย่างน้อยเท่าชุดเดิม", () => {
  const checks = readProcessed(path.join(ROOT, "data", "processed"));
  expect(checks.filter((c) => !c.ok)).toEqual([]);
  const count = (t: string) => checks.filter((c) => c.ok && c.value.issue.doc_type === t).length;
  // 11.6: รายวัน/7 วันขึ้นเว็บทุกฉบับที่เก็บ (จำนวนโตตามข้อมูล) จึงตรวจขั้นต่ำของชุดเดิม · ชนิดอื่นตรงจำนวนที่เก็บ
  expect(count("daily")).toBeGreaterThanOrEqual(28);
  expect(count("sevenday")).toBeGreaterThanOrEqual(7);
  expect([count("shipping"), count("warning"), count("weekly")]).toEqual([100, 155, 100]);
});

it("ชนิดที่ตารางยอมรับ (schema.sql) ครอบทุกชนิดที่ตัวโหลดส่ง", () => {
  const schema = readFileSync(path.join(ROOT, "db", "schema.sql"), "utf-8");
  for (const t of LOADED_DOC_TYPES) expect(schema).toContain(`'${t}'`);
});

it("upsert ใส่ครบทุกคอลัมน์ที่ตารางบังคับ และอัปเดตเมื่อชนกุญแจหลัก", () => {
  const schema = readFileSync(path.join(ROOT, "db", "schema.sql"), "utf-8");
  for (const col of ["issue_id", "doc_type", "issued_at", "source_label", "payload"]) {
    expect(schema).toMatch(new RegExp(`${col}\\s+\\w+\\s+not null`));
    expect(UPSERT).toContain(col);
  }
  expect(UPSERT).toContain("on conflict (doc_type, issue_id) do update");
});
