// ตัวช่วยของภาพขั้นตอนใน /demo (ฟังก์ชันบริสุทธิ์ ทดสอบได้): อ่านค่าของแต่ละขั้นอย่างปลอดภัย ป้ายภาษาไทย ไฮไลต์ข้อความ
import type { z } from "zod";

import type { traceStepSchema } from "@/lib/contract/documents";
import { isRegionKey, REGION_LABELS } from "@/lib/format/thai";

export type TraceStep = z.infer<typeof traceStepSchema>;

// ป้ายของตัวจัดประเภท (UnitLabel) เป็นภาษาไทย
export const UNIT_LABEL_TH: Record<string, string> = {
  weather: "สภาพอากาศ",
  cause: "สาเหตุ",
  advice: "คำแนะนำ",
  other: "อื่นๆ",
};

export const unitLabelTh = (label: string): string => UNIT_LABEL_TH[label] ?? label;

/** ข้อมูลในขั้นเป็น JSON ทั่วไป อ่านเฉพาะชนิดที่คาด ผิดชนิด/ไม่มี = ค่าว่าง (ไม่ throw) */
export function strings(step: TraceStep | undefined, key: string): string[] {
  const v = step?.data[key];
  return Array.isArray(v) ? v.filter((x): x is string => typeof x === "string") : [];
}

export function text(step: TraceStep | undefined, key: string): string | null {
  const v = step?.data[key];
  return typeof v === "string" ? v : null;
}

export function num(step: TraceStep | undefined, key: string): number | null {
  const v = step?.data[key];
  return typeof v === "number" ? v : null;
}

export function flag(step: TraceStep | undefined, key: string): boolean | null {
  const v = step?.data[key];
  return typeof v === "boolean" ? v : null;
}

export function record(step: TraceStep | undefined, key: string): [string, number][] {
  const v = step?.data[key];
  if (!v || typeof v !== "object" || Array.isArray(v)) return [];
  return Object.entries(v).filter((e): e is [string, number] => typeof e[1] === "number");
}

/** ชื่อภาคจากคีย์ (รายวัน) ถ้าเป็นชื่อไทยอยู่แล้ว (โหมดทั่วไป) ใช้ตามเดิม */
export const regionName = (key: string): string => (isRegionKey(key) ? REGION_LABELS[key] : key);

/** ร้อยละสำหรับแสดง (ปัดเป็นจำนวนเต็ม) เช่น 0.9599 -> "96%" */
export const percent = (score: number): string => `${Math.round(score * 100)}%`;

export type TokenState = "kept" | "dropped" | "number" | "unknown";

/** สถานะของโทเคนแต่ละตัวตามขั้นคัดคำ: ถูกทิ้ง (เครื่องหมาย/ช่องว่าง), ตัวเลข -> <num>, นอกคลังคำ, เก็บไว้ */
export function tokenStates(tokens: string[], filter: TraceStep | undefined): { token: string; state: TokenState }[] {
  const dropped = new Set(strings(filter, "dropped"));
  const numbers = new Set(strings(filter, "numbers"));
  const unknown = new Set(strings(filter, "unknown"));
  return tokens.map((token) => {
    if (dropped.has(token)) return { token, state: "dropped" };
    if (numbers.has(token)) return { token, state: "number" };
    if (unknown.has(token.trim().toLowerCase()) || unknown.has(token)) return { token, state: "unknown" };
    return { token, state: "kept" };
  });
}

/** ป้ายสั้นของโทเคนที่ไม่ใช่ตัวอักษร (ช่องว่างมองไม่เห็นจึงต้องมีชื่อ) */
export function tokenDisplay(token: string): string {
  if (token.trim() === "") return "ช่องว่าง";
  return token;
}

export type HighlightKind = "number" | "date" | "province";
export type Segment = { text: string; kind: HighlightKind | null };

/**
 * แบ่งข้อความเป็นช่วงปกติ/ช่วงที่ไฮไลต์ (ตัวเลข วันที่ จังหวัด ที่หลังบ้านคืนมาแบบคำต่อคำ)
 * ยาวก่อน ไม่ทับกัน ทุกครั้งที่พบในข้อความ · ต่อกันกลับได้ข้อความเดิมทุกตัวอักษร
 */
export function highlight(source: string, spans: { text: string; kind: HighlightKind }[]): Segment[] {
  const marks: { start: number; end: number; kind: HighlightKind }[] = [];
  const ordered = [...spans].filter((s) => s.text).sort((a, b) => b.text.length - a.text.length);
  for (const span of ordered) {
    let from = 0;
    for (;;) {
      const at = source.indexOf(span.text, from);
      if (at < 0) break;
      const end = at + span.text.length;
      if (!marks.some((m) => at < m.end && m.start < end)) marks.push({ start: at, end, kind: span.kind });
      from = end;
    }
  }
  marks.sort((a, b) => a.start - b.start);
  const out: Segment[] = [];
  let pos = 0;
  for (const m of marks) {
    if (m.start > pos) out.push({ text: source.slice(pos, m.start), kind: null });
    out.push({ text: source.slice(m.start, m.end), kind: m.kind });
    pos = m.end;
  }
  if (pos < source.length) out.push({ text: source.slice(pos), kind: null });
  return out;
}
