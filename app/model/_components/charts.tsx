// กราฟของหน้า /model เขียนด้วย HTML/SVG ล้วน (ไม่เพิ่ม dependency) · ทุกกราฟเป็นตารางที่อ่านออกเสียงได้หรือมีตารางคู่
// สีจากโทเคนเท่านั้น: ชุดข้อมูลหลัก ink ชุดเทียบ body (ระบบดีไซน์ห้ามเพิ่มสีอิ่มตัว D10) แยกด้วยเส้นประ รูปจุด และป้ายตรง
// ค่าแสดงเป็นตัวเลขสุดท้ายเสมอ ไม่มีอนิเมชันกับค่า (D13)
import type { ReactNode } from "react";

import { cn } from "@/lib/cn";

export const pct = (x: number, digits = 1) => `${(x * 100).toFixed(digits)}%`;

type BarRow = { label: ReactNode; value: number; display: string; strong?: boolean };

type BarTableProps = {
  caption: string;
  columns: [string, string];
  rows: BarRow[];
  // ค่าที่เท่ากับแท่งเต็ม (ไม่ระบุ = ค่ามากสุดในตาราง)
  max?: number;
};

/** ตารางแท่งแนวนอน: ชื่อ | แท่ง + ค่า (แท่งเป็นของตกแต่ง ค่าอยู่ในตัวเลข) */
export function BarTable({ caption, columns, rows, max }: BarTableProps) {
  const top = max ?? Math.max(...rows.map((r) => r.value), 0);
  return (
    <table className="w-full border-collapse text-body-sm text-ink">
      <caption className="mb-2 text-left text-body-sm text-body">{caption}</caption>
      <thead className="sr-only">
        <tr>
          <th scope="col">{columns[0]}</th>
          <th scope="col">{columns[1]}</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i} className="align-middle">
            <th scope="row" className={cn("w-32 py-1.5 pr-3 text-left font-normal sm:w-40", row.strong && "font-semibold")}>
              {row.label}
            </th>
            <td className="py-1.5">
              <div className="flex items-center gap-3">
                <span className="h-2.5 flex-1 rounded-pill bg-surface-strong" aria-hidden="true">
                  <span
                    className={cn("block h-full rounded-pill", row.strong ? "bg-primary" : "bg-body")}
                    style={{ width: `${top > 0 ? Math.max((row.value / top) * 100, row.value > 0 ? 1.5 : 0) : 0}%` }}
                  />
                </span>
                <span className={cn("w-16 text-right tabular-nums", row.strong && "font-semibold")}>{row.display}</span>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

type MatrixProps = {
  caption: string;
  labels: string[];
  matrix: number[][];
};

/** ตารางสับสน: แถว = ป้ายจริง คอลัมน์ = ที่ทาย · ช่องทแยง (ทายถูก) พื้นฟ้า ช่องผิดที่ไม่เป็นศูนย์ตัวหนาบนพื้นส้มอ่อน */
export function ConfusionMatrix({ caption, labels, matrix }: MatrixProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border-collapse text-center text-body-sm text-ink">
        <caption className="mb-2 text-left text-body-sm text-body">{caption}</caption>
        <thead>
          <tr>
            <th scope="col" className="p-2 text-left font-normal text-body">
              จริง \ ทาย
            </th>
            {labels.map((l) => (
              <th key={l} scope="col" className="p-2 font-semibold">
                {l}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, i) => (
            <tr key={labels[i]}>
              <th scope="row" className="p-2 text-left font-semibold">
                {labels[i]}
              </th>
              {row.map((n, j) => (
                <td
                  key={labels[j]}
                  className={cn(
                    "min-w-11 border border-hairline p-2 tabular-nums",
                    i === j && n > 0 && "bg-num-tint font-semibold",
                    i !== j && n > 0 && "bg-warning-tint font-semibold",
                  )}
                >
                  {n}
                  {i !== j && n > 0 ? <span className="sr-only"> (ทายผิด)</span> : null}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

type Point = { x: number; y: number };
type Series = { name: string; points: Point[]; dashed?: boolean; square?: boolean };

type LineChartProps = {
  title: string;
  xLabel: string;
  yLabel: string;
  series: Series[];
  yMin: number;
  yMax: number;
  xTicks: number[];
  yTicks: number[];
  formatY: (y: number) => string;
};

// ระยะห่างต่ำสุดของป้ายตรงสองป้าย (ร้อยละของความสูงกราฟ) กันป้ายทับกัน
const LABEL_GAP = 14;

/** เลื่อนป้ายตรงลงให้ห่างกันอย่างน้อย LABEL_GAP โดยคงลำดับบนลงล่าง */
export function spreadLabels(tops: number[], gap = LABEL_GAP): number[] {
  const order = tops.map((t, i) => ({ t, i })).sort((a, b) => a.t - b.t);
  const out = [...tops];
  let prev = -Infinity;
  for (const { t, i } of order) {
    out[i] = Math.max(t, prev + gap);
    prev = out[i];
  }
  return out;
}

/**
 * กราฟเส้นแกนเดียว · เส้นวาดด้วย SVG ที่ยืดตามกล่อง (เส้นหนาคงที่ด้วย non-scaling-stroke)
 * ส่วนตัวอักษรและจุดเป็น HTML วางตามร้อยละ จึงอ่านได้ขนาดจริงทั้งมือถือและจอใหญ่
 */
export function LineChart({ title, xLabel, yLabel, series, yMin, yMax, xTicks, yTicks, formatY }: LineChartProps) {
  const xs = series.flatMap((s) => s.points.map((p) => p.x));
  const xMin = Math.min(...xs, ...xTicks);
  const xMax = Math.max(...xs, ...xTicks);
  const px = (x: number) => ((x - xMin) / (xMax - xMin || 1)) * 100;
  const py = (y: number) => (1 - (y - yMin) / (yMax - yMin || 1)) * 100;
  const lasts = series.map((s) => s.points[s.points.length - 1]);
  const labelTops = spreadLabels(lasts.map((p) => py(p.y)));
  return (
    <figure className="space-y-3">
      <figcaption className="text-body-sm text-body">{title}</figcaption>
      <ul className="flex flex-wrap gap-x-6 gap-y-1 text-body-sm text-ink" aria-label="คำอธิบายเส้น">
        {series.map((s) => (
          <li key={s.name} className="inline-flex items-center gap-2">
            <svg width="28" height="10" aria-hidden="true">
              <line
                x1="0"
                y1="5"
                x2="28"
                y2="5"
                className={s.dashed ? "stroke-body" : "stroke-ink"}
                strokeWidth="2"
                strokeDasharray={s.dashed ? "6 4" : undefined}
              />
            </svg>
            {s.name}
          </li>
        ))}
      </ul>
      <div role="img" aria-label={`${title} (ค่าอยู่ในตารางใต้กราฟ)`} className="max-w-3xl pt-2">
        <p className="text-caption text-body" aria-hidden="true">
          แกนตั้ง: {yLabel}
        </p>
        <div aria-hidden="true" className="mt-3 ml-11 mr-24 sm:mr-32">
          <div className="relative h-48 sm:h-64">
            <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 size-full overflow-visible">
              {yTicks.map((t) => (
                <line
                  key={t}
                  x1="0"
                  x2="100"
                  y1={py(t)}
                  y2={py(t)}
                  className="stroke-hairline-strong"
                  strokeWidth="1"
                  vectorEffect="non-scaling-stroke"
                />
              ))}
              {series.map((s) => (
                <polyline
                  key={s.name}
                  points={s.points.map((p) => `${px(p.x)},${py(p.y)}`).join(" ")}
                  fill="none"
                  className={s.dashed ? "stroke-body" : "stroke-ink"}
                  strokeWidth="2"
                  strokeDasharray={s.dashed ? "6 4" : undefined}
                  strokeLinejoin="round"
                  vectorEffect="non-scaling-stroke"
                />
              ))}
            </svg>
            {yTicks.map((t) => (
              <span
                key={t}
                className="absolute right-full mr-2 -translate-y-1/2 text-caption text-body"
                style={{ top: `${py(t)}%` }}
              >
                {formatY(t)}
              </span>
            ))}
            {series.map((s) =>
              s.points.map((p) => (
                <span
                  key={`${s.name}-${p.x}`}
                  title={`${s.name}: ${xLabel} ${p.x} → ${formatY(p.y)}`}
                  className={cn(
                    "absolute size-2.5 -translate-x-1/2 -translate-y-1/2 ring-2 ring-canvas",
                    s.square ? "bg-body" : "rounded-full bg-ink",
                  )}
                  style={{ left: `${px(p.x)}%`, top: `${py(p.y)}%` }}
                />
              )),
            )}
            {series.map((s, i) => (
              <span
                key={s.name}
                className="absolute left-full ml-3 w-20 -translate-y-1/2 text-caption font-semibold text-ink sm:w-28"
                style={{ top: `${labelTops[i]}%` }}
              >
                {s.name} {formatY(lasts[i].y)}
              </span>
            ))}
          </div>
          <div className="relative mt-2 h-6">
            {xTicks.map((t) => (
              <span
                key={t}
                className="absolute -translate-x-1/2 text-caption text-body"
                style={{ left: `${px(t)}%` }}
              >
                {t}
              </span>
            ))}
          </div>
          <p className="text-center text-caption text-ink">{xLabel}</p>
        </div>
      </div>
    </figure>
  );
}
