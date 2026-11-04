import { AdviceList } from "@/components/features/advice-list";
import { Card } from "@/components/ui/card";
import type { RegionSummary, SummaryLine } from "@/lib/contract/issue";
import { cn } from "@/lib/cn";
import { LINE_KIND_LABELS, thaiDateRange } from "@/lib/format/thai";

type ForecastCardProps = {
  title: string;
  summary: RegionSummary;
  className?: string;
  // โหมดโฟกัสภาคเดียว: หัวข้อใหญ่ขึ้น
  focused?: boolean;
};

function Lines({ lines }: { lines: SummaryLine[] }) {
  return (
    <dl className="space-y-3">
      {lines.map((line, i) => (
        <div key={`${line.kind}-${i}`}>
          <dt className="text-caption font-semibold text-body">{LINE_KIND_LABELS[line.kind]}</dt>
          <dd className="text-body-md text-ink">{line.text}</dd>
        </div>
      ))}
    </dl>
  );
}

// การ์ดภาค: สรุปสภาพอากาศ (รายวัน = lines, 7 วัน = แยกตามช่วงวัน) + คำแนะนำของภาคนั้น
export function ForecastCard({ title, summary, className, focused = false }: ForecastCardProps) {
  return (
    <Card className={cn("flex flex-col gap-4", className)}>
      <h3 className={focused ? "text-display-sm" : "text-title-md"}>{title}</h3>
      {summary.lines.length > 0 ? <Lines lines={summary.lines} /> : null}
      {summary.periods.map((period) => (
        <section key={`${period.start}-${period.end}`} className="space-y-2">
          <h4 className="text-title-sm">{thaiDateRange(period.start, period.end)}</h4>
          <Lines lines={period.lines} />
        </section>
      ))}
      {summary.advice.length > 0 ? (
        <section className="space-y-2 border-t border-hairline pt-4">
          <h4 className="text-title-sm">คำแนะนำสำหรับภาคนี้</h4>
          <AdviceList items={summary.advice} />
        </section>
      ) : null}
    </Card>
  );
}
