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

function Body({ step, steps }: StepVisualProps) {
  switch (step.id) {
    case "read_pdf":
      return (
        <Stats
          items={[
            ["จำนวนหน้า", num(step, "pages") ?? "-"],
            ["ตัวอักษรที่อ่านได้", num(step, "chars") ?? "-"],
          ]}
        />
      );
    case "clean": {
      const before = strings(step, "before");
      const after = strings(step, "after");
      return (
        <div className="space-y-4">
          <Stats
            items={[
              ["ก่อนทำความสะอาด", num(step, "chars_before") ?? "-"],
              ["หลังทำความสะอาด", num(step, "chars_after") ?? "-"],
              ["อักขระพิเศษที่แก้", num(step, "pua_fixed") ?? 0],
            ]}
          />
          {before.length > 0 ? (
            <ol className="space-y-3">
              {before.map((line, i) => (
                <li key={`${i}-${line}`} className="animate-enter-up space-y-1 stagger" style={order(i)}>
                  <p className="text-body-sm text-body">ก่อน</p>
                  <Sentence>{line}</Sentence>
                  <p className="text-body-sm text-body">หลัง</p>
                  <Sentence>{after[i] ?? ""}</Sentence>
                </li>
              ))}
            </ol>
          ) : null}
        </div>
      );
    }
    case "detect_type":
      return (
        <p className="flex flex-wrap items-center gap-2 text-body-md text-ink">
          <Badge className="animate-pop">{text(step, "kind") === "generic" ? "โหมดทั่วไป" : "สรุปเต็ม"}</Badge>
          {step.note_th}
        </p>
      );
    case "segment": {
      const regions = strings(step, "regions");
      const headings = strings(step, "headings");
      const title = text(step, "title");
      return (
        <div className="space-y-4">
          {title ? <Sentence>หัวเรื่อง: {title}</Sentence> : null}
          {regions.length > 0 ? <RegionCounts rows={record(step, "lines_by_region")} unit="บรรทัด" /> : null}
          {headings.length > 0 ? (
            <div className="space-y-2">
              <p className="text-body-sm text-body">หัวข้อที่พบ</p>
              <TextList items={headings} />
            </div>
          ) : null}
        </div>
      );
    }
    case "units":
      return <TextList items={strings(step, "units")} ordered />;
    case "tokenize":
      return (
        <div className="space-y-4">
          <Sentence>{text(step, "unit")}</Sentence>
          <Tokens step={step} steps={steps} />
        </div>
      );
    case "filter_tokens":
      return (
        <div className="space-y-4">
          <Tokens step={step} steps={steps} />
          <Legend />
          <p className="text-body-sm text-ink">
            เหลือ {strings(step, "kept").length} คำส่งให้ตัวจัดประเภท
            {num(step, "known_ratio") !== null ? ` · อยู่ในคลังคำ ${percent(num(step, "known_ratio") ?? 0)}` : ""}
          </p>
        </div>
      );
    case "classify": {
      const label = text(step, "label") ?? "";
      const scores = record(step, "scores").map(([k, v]) => [unitLabelTh(k), v] as [string, number]);
      const counts = record(step, "label_counts").map(([k, v]) => [unitLabelTh(k), v] as [string, number]);
      return (
        <div className="space-y-5">
          <Sentence>{text(step, "unit")}</Sentence>
          <div className="space-y-2">
            <p className="text-body-md text-ink">
              ป้ายที่ได้: <strong>{unitLabelTh(label)}</strong> (คะแนนรวมเป็น 1)
            </p>
            <Bars rows={scores} highlight={unitLabelTh(label)} format={percent} />
          </div>
          {strings(step, "top_words").length > 0 ? (
            <div className="space-y-2">
              <p className="text-body-sm text-body">คำที่ดันป้ายนี้มากที่สุด</p>
              <ul className="flex flex-wrap gap-2">
                {strings(step, "top_words").map((w, i) => (
                  <Chip key={w} index={i}>
                    {w}
                  </Chip>
                ))}
              </ul>
            </div>
          ) : null}
          {counts.length > 0 ? (
            <div className="space-y-2">
              <p className="text-body-sm text-body">จำนวนหน่วยต่อป้ายทั้งเอกสาร</p>
              <Bars rows={counts} highlight={unitLabelTh(label)} />
            </div>
          ) : null}
        </div>
      );
    }
    case "scope": {
      const byRegion = record(step, "advice_by_region");
      const units = record(step, "units_by_region");
      return (
        <div className="space-y-4">
          {byRegion.length > 0 ? (
            <>
              <p className="text-body-md text-ink">
                ข้อแนะนำทั่วไป {num(step, "general") ?? 0} ข้อ · คำแนะนำรายภาค {num(step, "regional") ?? 0} ข้อ
              </p>
              <RegionCounts rows={byRegion} unit="ข้อ" />
            </>
          ) : null}
          {units.length > 0 ? (
            <>
              <p className="text-body-md text-ink">หน่วยที่บอกที่ตั้ง {num(step, "units_with_region") ?? 0} หน่วย</p>
              <RegionCounts rows={units} unit="หน่วย" />
            </>
          ) : null}
          {strings(step, "advice").length > 0 ? <TextList items={strings(step, "advice")} /> : null}
        </div>
      );
    }
    case "extract": {
      const facts = record(step, "facts_by_region");
      const groups: [string, string[]][] = [
        ["ตัวเลข", strings(step, "numbers")],
        ["วันที่", strings(step, "dates")],
        ["จังหวัด", strings(step, "provinces")],
      ];
      return (
        <div className="space-y-4">
          {facts.length > 0 ? <RegionCounts rows={facts} unit="ค่า" /> : null}
          {strings(step, "sample").length > 0 ? (
            <ul className="space-y-2">
              {/* แสดงไม่กี่แถวแรก ขั้นนี้ไม่ยาวจนต้องเลื่อนไกลกว่าจะถึงปุ่มถัดไป */}
              {strings(step, "sample").slice(0, SAMPLE_ROWS).map((line, i) => {
                const [fact, source] = line.split(" ← ");
                return (
                  <li
                    key={`${i}-${line}`}
                    className="grid animate-enter-up gap-1 rounded-md border border-hairline-strong p-3 stagger sm:grid-cols-2"
                    style={order(i)}
                  >
                    <span className="font-semibold text-ink [overflow-wrap:anywhere]">{fact}</span>
                    <span className="text-body-sm text-body [overflow-wrap:anywhere]">จาก: {source}</span>
                  </li>
                );
              })}
            </ul>
          ) : null}
          {strings(step, "sample").length > SAMPLE_ROWS ? (
            <p className="text-body-sm text-body">
              และอีก {strings(step, "sample").length - SAMPLE_ROWS} ค่าของภาคนี้ (ทุกค่าตรวจแล้วในขั้นตรวจ)
            </p>
          ) : null}
          {groups.map(([label, items]) =>
            items.length > 0 ? (
              <div key={label} className="space-y-2">
                <p className="text-body-sm text-body">{label}</p>
                <ul className="flex flex-wrap gap-2">
                  {items.map((item, i) => (
                    <Chip key={`${i}-${item}`} index={i} className={label === "ตัวเลข" ? "bg-num-tint" : undefined}>
                      {item}
                    </Chip>
                  ))}
                </ul>
              </div>
            ) : null,
          )}
        </div>
      );
    }
    case "template":
      return (
        <div className="space-y-4">
          <RegionCounts rows={record(step, "lines_by_region")} unit="บรรทัด" />
          <TextList items={strings(step, "sample")} />
        </div>
      );
    case "verify":
      return (
        <ul className="space-y-2">
          {strings(step, "checks").map((check, i) => (
            <li key={check} className="flex animate-enter-up items-start gap-3 text-body-md text-ink stagger" style={order(i)}>
              <svg
                aria-hidden="true"
                viewBox="0 0 20 20"
                className="mt-1 size-5 shrink-0 animate-pop stagger"
                style={order(i)}
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <circle cx="10" cy="10" r="8.5" strokeWidth="1.5" />
                <path d="m6 10.5 2.5 2.5L14 7.5" />
              </svg>
              <span>
                <span className="sr-only">ผ่าน: </span>
                {check}
              </span>
            </li>
          ))}
        </ul>
      );
    case "result": {
      const items: [string, ReactNode][] = Object.entries(step.data)
        .filter(([, v]) => typeof v === "number")
        .map(([k, v]) => [RESULT_LABELS[k] ?? k, v as number]);
      return <Stats items={items} />;
    }
    default:
      return null;
  }
}

const RESULT_LABELS: Record<string, string> = {
  lines: "ประโยคสรุป",
  advice: "คำแนะนำ",
  sections: "ส่วน",
  units: "หน่วยประโยค",
};

/** ภาพของขั้นหนึ่ง: ขั้นที่ข้ามแสดงเหตุผล ขั้นที่ข้อมูลถูกตัดเพราะเกินเพดานแสดงแค่คำอธิบาย */
export function StepVisual({ step, steps }: StepVisualProps) {
  if (step.status !== "done" || Object.keys(step.data).length === 0) return null;
  return <Body step={step} steps={steps} />;
}
