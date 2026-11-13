import type { CSSProperties } from "react";

import { AdviceList } from "@/components/features/advice-list";
import { SummaryLines } from "@/components/features/forecast-card";
import { Card } from "@/components/ui/card";
import { SEA_AREA_KEYS, type SeaAreaKey, type ShippingIssue } from "@/lib/contract/documents";

type ShippingSummaryProps = { issue: ShippingIssue };

// การ์ดพื้นที่ทะเล: บรรทัดของทั้งพื้นที่ (ฝน) แล้วแยกตอนบน/ตอนล่างถ้าต้นฉบับแยก (อ่าวไทย)
function SeaAreaCard({ issue, areaKey, index }: { issue: ShippingIssue; areaKey: SeaAreaKey; index: number }) {
  const area = issue.areas[areaKey];
  return (
    <Card
      motion="lift"
      className="flex animate-enter-up flex-col gap-4 stagger"
      style={{ "--i": index } as CSSProperties}
    >
      <h3 className="text-title-md">{area.name_th}</h3>
      {area.lines.length > 0 ? <SummaryLines lines={area.lines} /> : null}
      {area.parts.map((part) => (
        <section key={part.name_th} className="space-y-2 border-t border-hairline pt-4">
          <h4 className="text-title-sm">{part.name_th}</h4>
          <SummaryLines lines={part.lines} />
        </section>
      ))}
    </Card>
  );
}

// พยากรณ์เดินเรือหนึ่งฉบับ: ภาพรวม + คำแนะนำชาวเรือ (คัดคำต่อคำ) + การ์ด 4 พื้นที่ทะเลตามลำดับของ TMD
export function ShippingSummary({ issue }: ShippingSummaryProps) {
  return (
    <>
      {issue.overview.length > 0 ? (
        <Card className="animate-enter-up space-y-3">
          <h2 className="text-title-md">ภาพรวมลมและคลื่น</h2>
          <ul className="space-y-2">
            {issue.overview.map((line, i) => (
              <li key={`${line.kind}-${i}`} className="text-body-md text-ink">
                {line.text}
              </li>
            ))}
          </ul>
        </Card>
      ) : null}

      {issue.advice.length > 0 ? (
        <Card className="animate-enter-up space-y-3">
          <h2 className="text-title-md">คำแนะนำสำหรับชาวเรือ</h2>
          <AdviceList items={issue.advice} />
        </Card>
      ) : null}

      <h2 className="sr-only">สรุปรายพื้นที่ทะเล</h2>
      <div className="grid gap-4 sm:grid-cols-2">
        {SEA_AREA_KEYS.map((key, i) => (
          <SeaAreaCard key={key} issue={issue} areaKey={key} index={i} />
        ))}
      </div>
    </>
  );
}
