import Link from "next/link";

import { WarningNoticeCard } from "@/components/features/warning-notice";
import { Alert } from "@/components/ui/alert";
import { buttonVariants } from "@/components/ui/button";
import { TabLinks } from "@/components/ui/tab-links";
import { cn } from "@/lib/cn";
import { getLatestWarning, getWarning, listWarnings } from "@/lib/data/forecasts";
import { thaiDate, thaiDateTimeShort } from "@/lib/format/thai";
import {
  groupSeriesByMonth,
  linkSeries,
  parseWarningQuery,
  seriesOf,
  seriesRangeLabel,
  warningsHref,
  type WarningSeries,
} from "@/lib/warnings";

const TMD_WARNING_LIST = "https://www.tmd.go.th/warning-and-events/warning-storm";

const INFO_ICON = (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <circle cx="10" cy="10" r="8.5" stroke="currentColor" strokeWidth="1.5" />
    <path d="M10 9v5M10 6v.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
);

type WarningsViewProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

// ประกาศเรื่องเดียวกันหลายฉบับ: ชิปเลือกฉบับของเหตุการณ์ที่กำลังดู (ฉบับใหม่สุดก่อน)
function SeriesPicker({ series, currentId }: { series: WarningSeries; currentId: string }) {
  return (
    <div className="space-y-2">
      <p className="text-body-sm text-ink">
        เหตุการณ์นี้ประกาศต่อเนื่อง {series.notices.length} ฉบับ ({seriesRangeLabel(series)})
        {series.completeStart ? "" : " ฉบับก่อนหน้าไม่อยู่ในระบบ"}
        {series.closed ? " ฉบับสุดท้ายออกแล้ว" : " ยังไม่มีฉบับสุดท้ายในระบบ"}
      </p>
      <TabLinks
        label="เลือกฉบับของเหตุการณ์นี้"
        items={[...series.notices].reverse().map((n) => ({
          href: warningsHref(n.issueId),
          label: `ฉบับที่ ${n.seriesNo}`,
          current: n.issueId === currentId,
        }))}
      />
    </div>
  );
}

function History({ series, currentId, latestId }: { series: WarningSeries[]; currentId: string; latestId: string }) {
  return (
    <section aria-labelledby="warning-history" className="space-y-4">
      <div className="space-y-1">
        <h2 id="warning-history" className="text-display-sm">
          ประกาศย้อนหลัง
        </h2>
        <p className="max-w-prose text-body-md text-ink">
          แต่ละรายการคือเหตุการณ์หนึ่ง (ประกาศหลายฉบับของเรื่องเดียวกัน) เลือกเพื่อดูฉบับล่าสุดของเหตุการณ์นั้นในระบบ
        </p>
      </div>
      {groupSeriesByMonth(series).map((group) => (
        <div key={group.month} className="space-y-2">
          <h3 className="text-title-md">{group.month}</h3>
          <ul className="grid gap-2 md:grid-cols-2">
            {group.series.map((s) => {
              const last = s.notices.at(-1)!;
              const first = s.notices[0];
              const current = s.notices.some((n) => n.issueId === currentId);
              return (
                <li key={s.id}>
                  <Link
                    href={warningsHref(last.issueId === latestId ? null : last.issueId)}
                    aria-current={current ? "page" : undefined}
                    className={cn(
                      "block min-h-11 rounded-md border p-4 transition-colors duration-(--duration-base) hover:bg-canvas-soft",
                      current ? "border-ink bg-canvas-soft" : "border-hairline-strong bg-surface-card",
                    )}
                  >
                    <span className="block text-body-md font-semibold text-ink [overflow-wrap:anywhere]">{last.title}</span>
                    <span className="mt-1 block text-body-sm text-body">
                      {seriesRangeLabel(s)} · {s.notices.length} ฉบับ · {thaiDate(first.issuedAt)}
                      {thaiDate(first.issuedAt) === thaiDate(last.issuedAt) ? "" : ` ถึง ${thaiDate(last.issuedAt)}`}
                      {s.closed ? "" : " · ยังไม่มีฉบับสุดท้าย"}
                    </span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </section>
  );
}

// มุมมองหลักของหน้า /warnings: ประกาศที่เลือก (ค่าเริ่มต้นล่าสุด) + ชิปฉบับของเหตุการณ์ + ย้อนหลังจัดกลุ่มตามเดือน
export async function WarningsView({ searchParams }: WarningsViewProps) {
  const { issue } = parseWarningQuery(await searchParams);
  const [list, selected] = await Promise.all([listWarnings(), issue ? getWarning(issue) : getLatestWarning()]);

  if (!selected) {
    return (
      <Alert icon={INFO_ICON} role="status" className="animate-fade-in">
        {issue ? (
          <>
            <p className="font-semibold">ไม่พบประกาศฉบับที่เลือก</p>
            <p className="mt-1">ฉบับนี้อาจยังไม่ได้โหลดเข้าระบบ</p>
            <Link href={warningsHref(null)} className={cn(buttonVariants({ variant: "secondary" }), "mt-3")}>
              ดูฉบับล่าสุด
            </Link>
          </>
        ) : (
          <>
            <p className="font-semibold">ยังไม่มีประกาศเตือนภัยในระบบ</p>
            <p className="mt-1">
              ระบบนี้นำประกาศของกรมอุตุนิยมวิทยาเข้ามาเป็นชุด ชุดที่มีประกาศเตือนภัยยังไม่ได้โหลดเข้าระบบ
              ระหว่างนี้ดูประกาศฉบับเต็มได้ที่เว็บไซต์กรมอุตุนิยมวิทยา
            </p>
            <a href={TMD_WARNING_LIST} rel="noreferrer" className="mt-2 inline-block text-text-link underline underline-offset-4">
              ประกาศเตือนภัยที่กรมอุตุนิยมวิทยา
            </a>
          </>
        )}
      </Alert>
    );
  }

  const series = linkSeries(list);
  const current = seriesOf(series, selected.issue_id);
  const latestId = list[0]?.issueId ?? selected.issue_id;
  const isLatest = selected.issue_id === latestId;

  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <p className="text-body-sm text-body">
          {isLatest ? "ประกาศล่าสุดในระบบ" : "ประกาศย้อนหลัง"} · ประกาศ ณ {thaiDateTimeShort(selected.issued_at)}
          {isLatest ? null : (
            <>
              {" "}
              <Link href={warningsHref(null)} className="text-text-link underline underline-offset-4">
                ดูฉบับล่าสุด
              </Link>
            </>
          )}
        </p>
        {current && current.notices.length > 1 ? <SeriesPicker series={current} currentId={selected.issue_id} /> : null}
      </div>

      <WarningNoticeCard notice={selected} />

      <p className="text-body-sm text-ink">
        ข้อความในการ์ดคัดจากประกาศของกรมอุตุนิยมวิทยาคำต่อคำ ถ้าต้องตัดสินใจเรื่องความปลอดภัย โปรดดูประกาศฉบับเต็มที่{" "}
        <a href={TMD_WARNING_LIST} rel="noreferrer" className="text-text-link underline underline-offset-4">
          เว็บไซต์กรมอุตุนิยมวิทยา
        </a>
      </p>

      <History series={series} currentId={selected.issue_id} latestId={latestId} />
    </div>
  );
}
