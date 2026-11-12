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
