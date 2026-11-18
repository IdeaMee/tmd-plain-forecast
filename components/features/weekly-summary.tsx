import type { CSSProperties } from "react";

import { SummaryLines } from "@/components/features/forecast-card";
import { Card } from "@/components/ui/card";
import type { TableCell, WeeklyRegion, WeeklySummary } from "@/lib/contract/documents";
import { REGION_KEYS, type RegionKey } from "@/lib/contract/issue";
import { REGION_LABELS } from "@/lib/format/thai";
import { splitCellLead } from "@/lib/summaries";

// ชื่อแถวตามหัวตารางของ TMD ("ปริมาณฝนสูงสุด" "อุณหภูมิสูงสุด" "อุณหภูมิต่ำสุด")
const CELLS: { key: "rain_max" | "temp_max" | "temp_min"; label: string }[] = [
  { key: "rain_max", label: "ปริมาณฝนสูงสุด" },
  { key: "temp_max", label: "อุณหภูมิสูงสุด" },
  { key: "temp_min", label: "อุณหภูมิต่ำสุด" },
];

function CellValue({ cell }: { cell: TableCell | null }) {
  // ช่องว่างในต้นฉบับ: บอกตรงๆ ว่าไม่มีค่าในฉบับนี้ (ไม่ใช่ 0 และไม่เดาสาเหตุ)
  if (!cell) return <span className="text-body">ไม่มีข้อมูลในฉบับนี้</span>;
  // ข้อความช่องคำต่อคำ (สถานี วันที่ และค่าที่สองในวงเล็บถ้ามี) เน้นเฉพาะค่านำ ไม่แสดงค่าซ้ำ
  const split = splitCellLead(cell.text);
  return (
    <span className="text-body-md [overflow-wrap:anywhere]">
      {split ? (
        <>
          <strong className="text-title-md font-semibold tabular-nums">{split.lead}</strong> {split.rest}
        </>
      ) : (
        cell.text
      )}
      {/* ต้นฉบับบางช่องใส่ค่าผิดคอลัมน์ (เช่น อุณหภูมิในช่องฝน) คัดตามเดิมแต่บอกผู้อ่าน ไม่เดาว่าตั้งใจหรือพิมพ์ผิด */}
      {cell.facts.column_unit_mismatch === true ? (
        <span className="mt-1 block text-body-sm text-ink">หน่วยของค่านี้ไม่ตรงกับหัวแถวตามต้นฉบับของกรม ดูฉบับเต็มก่อนใช้</span>
      ) : null}
    </span>
  );
}

// ค่าสูงสุด/ต่ำสุดของสัปดาห์ตามตารางต้นฉบับ: แถวละค่า หัวแถวเป็นคำของ TMD
function MaxTable({ region, name }: { region: WeeklyRegion; name: string }) {
  return (
    <table className="w-full text-left">
      <caption className="sr-only">ค่าสูงสุดและต่ำสุดของสัปดาห์ {name}</caption>
      <tbody className="divide-y divide-hairline">
        {CELLS.map(({ key, label }) => (
          <tr key={key} className="block py-2.5 sm:table-row">
            <th scope="row" className="block pr-4 text-body-sm font-semibold text-body sm:table-cell sm:w-40 sm:py-2.5 sm:align-top">
              {label}
            </th>
            <td className="block text-ink sm:table-cell sm:py-2.5">
              <CellValue cell={region[key]} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function RegionCard({ summary, regionKey, index, focused }: { summary: WeeklySummary; regionKey: RegionKey; index: number; focused: boolean }) {
  const region = summary.regions[regionKey];
  return (
    <Card
      motion="lift"
      className="flex animate-enter-up flex-col gap-4 stagger"
      style={{ "--i": Math.min(index, 4) } as CSSProperties}
    >
      <h3 className={focused ? "text-display-sm" : "text-title-md"}>{REGION_LABELS[regionKey]}</h3>
      <SummaryLines lines={region.lines} />
      <section className="mt-auto space-y-1 border-t border-hairline pt-4">
        <h4 className="text-title-sm">ค่าสูงสุดและต่ำสุดของสัปดาห์</h4>
        <MaxTable region={region} name={REGION_LABELS[regionKey]} />
      </section>
    </Card>
  );
}

type WeeklySummaryProps = { summary: WeeklySummary; region: RegionKey | null };

// สรุปรายสัปดาห์หนึ่งฉบับ: ภาพรวมทั้งประเทศ + การ์ดภาค (7 ภาค หรือภาคที่เลือก) ข้อความและตารางคัดจากต้นฉบับคำต่อคำ
export function WeeklySummaryView({ summary, region }: WeeklySummaryProps) {
  const keys = region ? [region] : REGION_KEYS;
  return (
    <>
      {summary.overview.length > 0 ? (
        <Card className="animate-enter-up space-y-3">
          <h2 className="text-title-md">ภาพรวมทั้งประเทศ</h2>
          <ul className="space-y-2">
            {summary.overview.map((line, i) => (
              <li key={i} className="text-body-md text-ink">
                {line.text}
              </li>
            ))}
          </ul>
        </Card>
      ) : null}
      <h2 className="sr-only">สรุปรายภาค</h2>
      <div className={region ? "grid gap-4" : "grid gap-4 md:grid-cols-2 xl:grid-cols-3"}>
        {keys.map((key, i) => (
          <RegionCard key={key} summary={summary} regionKey={key} index={i} focused={region !== null} />
        ))}
      </div>
    </>
  );
}
