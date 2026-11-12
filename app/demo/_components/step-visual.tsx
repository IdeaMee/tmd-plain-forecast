// ภาพของแต่ละขั้นในตัวเดินขั้นตอน /demo: อ่านจาก data ของขั้นนั้นเท่านั้น (ไม่ hard-code ค่า)
// อนิเมชันเคลื่อนแค่ transform/opacity ตัวเลขแสดงค่าสุดท้ายทันที (D13) ลดการเคลื่อนไหวแล้วปิดทั้งหมดจาก globals.css
import type { CSSProperties, ReactNode } from "react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/cn";
import {
  num,
  percent,
  record,
  regionName,
  strings,
  text,
  tokenDisplay,
  tokenStates,
  unitLabelTh,
  type TraceStep,
} from "@/lib/trace-view";

type StepVisualProps = {
  step: TraceStep;
  // ขั้นอื่นในชุดเดียวกัน (ขั้นคัดคำต้องใช้โทเคนจากขั้นตัดคำ)
  steps: TraceStep[];
};

// เหลื่อมเวลาสูงสุด 16 ชิ้น รายการยาว (เช่น 50 โทเคน) จึงเข้าครบในไม่ถึง 1 วินาที
const STAGGER_CAP = 16;
// แถวตัวอย่างค่าที่ดึงได้ (ขั้นดึงข้อเท็จจริง) ที่แสดงในขั้น
const SAMPLE_ROWS = 6;
const order = (i: number) => ({ "--i": Math.min(i, STAGGER_CAP) }) as CSSProperties;

function Stat({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-md border border-hairline-strong bg-surface-card px-4 py-3">
      <dt className="text-body-sm text-body">{label}</dt>
      <dd className="text-title-md text-ink">{value}</dd>
    </div>
  );
}

function Stats({ items }: { items: [string, ReactNode][] }) {
  return (
    <dl className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      {items.map(([label, value]) => (
        <Stat key={label} label={label} value={value} />
      ))}
    </dl>
  );
}

function Sentence({ children }: { children: ReactNode }) {
  return (
    <p className="rounded-md border border-hairline bg-canvas-soft p-4 text-body-md text-ink [overflow-wrap:anywhere]">
      {children}
    </p>
  );
}

function Chip({ children, className, index = 0 }: { children: ReactNode; className?: string; index?: number }) {
  return (
    <li
      className={cn(
        "inline-flex min-h-9 animate-enter-up items-center rounded-md border border-ink bg-surface-card px-3 text-body-md text-ink stagger",
        className,
      )}
      style={order(index)}
    >
      {children}
    </li>
  );
}

// แท่งคะแนน: ความยาวตามค่า ยืดเข้าจากซ้าย ตัวเลขร้อยละอยู่ข้างแท่งตั้งแต่แรก
function Bars({
  rows,
  highlight,
  format = String,
}: {
  rows: [string, number][];
  highlight?: string;
  format?: (value: number) => string;
}) {
  const max = Math.max(...rows.map(([, v]) => v), 0) || 1;
  return (
    <ul className="space-y-2">
      {rows.map(([label, value], i) => (
        <li key={label} className="grid grid-cols-[7rem_1fr_3.5rem] items-center gap-3 text-body-sm text-ink">
          <span className={cn(label === highlight && "font-semibold")}>{label}</span>
          <span className="h-3 rounded-pill bg-surface-strong" aria-hidden="true">
            <span
              className={cn(
                "block h-full origin-left animate-grow-x rounded-pill stagger",
                label === highlight ? "bg-primary" : "bg-body",
              )}
              style={{ ...order(i), width: `${Math.max((value / max) * 100, value > 0 ? 2 : 0)}%` }}
            />
          </span>
          <span className="text-right tabular-nums">{format(value)}</span>
        </li>
      ))}
    </ul>
  );
}

function TextList({ items, ordered = false }: { items: string[]; ordered?: boolean }) {
  const Tag = ordered ? "ol" : "ul";
  return (
    <Tag className={cn("space-y-2 pl-5 text-body-md text-ink", ordered ? "list-decimal" : "list-disc")}>
      {items.map((item, i) => (
        <li key={`${i}-${item}`} className="animate-enter-up stagger [overflow-wrap:anywhere]" style={order(i)}>
          {item}
        </li>
      ))}
    </Tag>
  );
}

function RegionCounts({ rows, unit }: { rows: [string, number][]; unit: string }) {
  return (
    <ul className="flex flex-wrap gap-2">
      {rows.map(([key, n], i) => (
        <Chip key={key} index={i} className={cn(n === 0 && "border-hairline-strong text-body")}>
          {regionName(key)}: {n} {unit}
        </Chip>
      ))}
    </ul>
  );
}

const STATE_STYLE = {
  kept: "border-ink",
  dropped: "border-dashed border-body bg-surface-strong text-body",
  number: "bg-num-tint",
  unknown: "border-dashed border-ink",
};
const STATE_NOTE = {
  kept: "",
  dropped: "ทิ้ง",
  number: "→ <num>",
  unknown: "นอกคลังคำ",
};

function Tokens({ step, steps }: StepVisualProps) {
  const tokens = strings(steps.find((s) => s.id === "tokenize"), "tokens");
  const filter = step.id === "filter_tokens" ? step : undefined;
  const items = filter ? tokenStates(tokens, filter) : tokens.map((token) => ({ token, state: "kept" as const }));
  return (
    <ul className="flex flex-wrap gap-2" aria-label={filter ? "ผลการคัดคำ" : "คำที่ตัดได้"}>
      {items.map(({ token, state }, i) => (
        <li
          key={`${i}-${token}`}
          className={cn(
            "inline-flex min-h-9 animate-enter-up flex-col items-center justify-center rounded-md border bg-surface-card px-3 py-1 text-ink stagger",
            STATE_STYLE[state],
          )}
          style={order(i)}
        >
          <span className={cn("text-body-md", state === "dropped" && "line-through")}>{tokenDisplay(token)}</span>
          {STATE_NOTE[state] ? <span className="text-caption text-body">{STATE_NOTE[state]}</span> : null}
        </li>
      ))}
    </ul>
  );
}

function Legend() {
  return (
    <ul className="flex flex-wrap gap-x-6 gap-y-2 text-body-sm text-ink">
      <li>เส้นประ + ขีดฆ่า = ทิ้ง (เครื่องหมาย/ช่องว่าง)</li>
      <li>พื้นฟ้า = ตัวเลขเปลี่ยนเป็น &lt;num&gt;</li>
      <li>เส้นประ = ไม่อยู่ในคลังคำของโมเดล (ข้ามตอนคำนวณ)</li>
    </ul>
  );
}
