import { readFileSync } from "node:fs";
import path from "node:path";

import { describe, expect, it } from "vitest";

import { traceSchema } from "@/lib/contract/documents";
import {
  flag,
  highlight,
  num,
  percent,
  record,
  regionName,
  strings,
  text,
  tokenDisplay,
  tokenStates,
  unitLabelTh,
} from "@/lib/trace-view";

const ROOT = path.resolve(import.meta.dirname, "..");
const trace = (name: string) =>
  traceSchema.parse(JSON.parse(readFileSync(path.join(ROOT, "tests/golden", name), "utf-8")));
const daily = trace("trace/daily_161120261800_pdf.json");
const generic = trace("generic/generic_enso_2569_09.trace.json");
const step = (t: typeof daily, id: string) => t.steps.find((s) => s.id === id);

describe("อ่านค่าของขั้นอย่างปลอดภัย", () => {
  it("ชนิดถูกได้ค่า ผิดชนิดหรือไม่มีได้ค่าว่าง", () => {
    const read = step(daily, "read_pdf");
    expect(num(read, "pages")).toBe(1);
    expect(num(read, "missing")).toBeNull();
    expect(text(step(daily, "detect_type"), "doc_type")).toBe("daily");
    expect(strings(read, "pages")).toEqual([]);
    expect(record(step(daily, "segment"), "lines_by_region").length).toBe(7);
    expect(flag(step(generic, "segment"), "has_region_headings")).toBe(false);
    expect(strings(undefined, "x")).toEqual([]);
  });

  it("ชื่อภาค ป้าย และร้อยละ", () => {
    expect(regionName("north")).toBe("ภาคเหนือ");
    expect(regionName("ภาคใต้")).toBe("ภาคใต้");
    expect(unitLabelTh("advice")).toBe("คำแนะนำ");
    expect(percent(0.9599)).toBe("96%");
  });
});

describe("tokenStates", () => {
  it("แยกโทเคนตามขั้นคัดคำ", () => {
    const filter = {
      id: "filter_tokens" as const,
      title_th: "คัดคำ",
      status: "done" as const,
      note_th: "",
      data: { dropped: [" ", "."], numbers: ["30"], unknown: ["เอนโซ"], kept: [] },
    };
    expect(tokenStates(["ฝน", " ", "30", "เอนโซ", "."], filter).map((t) => t.state)).toEqual([
      "kept",
      "dropped",
      "number",
      "unknown",
      "dropped",
    ]);
    expect(tokenDisplay(" ")).toBe("ช่องว่าง");
  });

  it("ขั้นตัดคำของ golden ทุกโทเคนมีสถานะ", () => {
    const tokens = strings(step(daily, "tokenize"), "tokens");
    expect(tokenStates(tokens, step(daily, "filter_tokens"))).toHaveLength(tokens.length);
  });
});

describe("highlight", () => {
  it("ต่อกลับได้ข้อความเดิม ไฮไลต์ยาวก่อนไม่ทับกัน", () => {
    const source = "คลื่นสูง 2 - 4 เมตร ที่จังหวัดชุมพร วันที่ 11 พ.ย. คลื่นสูง 2 - 4 เมตร";
    const parts = highlight(source, [
      { text: "2 - 4 เมตร", kind: "number" },
      { text: "4", kind: "number" },
      { text: "11 พ.ย.", kind: "date" },
      { text: "ชุมพร", kind: "province" },
    ]);
    expect(parts.map((p) => p.text).join("")).toBe(source);
    expect(parts.filter((p) => p.kind === "number").map((p) => p.text)).toEqual(["2 - 4 เมตร", "2 - 4 เมตร"]);
    expect(parts.filter((p) => p.kind).map((p) => p.kind)).toEqual(["number", "province", "date", "number"]);
  });

  it("ไม่มีช่วงไฮไลต์ = ช่วงเดียว", () => {
    expect(highlight("ข้อความ", [])).toEqual([{ text: "ข้อความ", kind: null }]);
    expect(highlight("ข้อความ", [{ text: "", kind: "date" }])).toEqual([{ text: "ข้อความ", kind: null }]);
  });
});
