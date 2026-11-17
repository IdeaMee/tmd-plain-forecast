import Link from "next/link";

import { MonthPicker } from "@/components/features/month-picker";
import { WeeklySummaryView } from "@/components/features/weekly-summary";
import { Alert } from "@/components/ui/alert";
import { buttonVariants } from "@/components/ui/button";
import { TabLinks } from "@/components/ui/tab-links";
import { REGION_KEYS } from "@/lib/contract/issue";
import { cn } from "@/lib/cn";
import { getLatestWeekly, getWeekly, listIssueMonths, listIssuesInMonth } from "@/lib/data/forecasts";
import { isRegionKey, REGION_LABELS, thaiDateTimeShort, thaiMonthOfKey } from "@/lib/format/thai";
import { groupWeeks, resolveMonth } from "@/lib/history";
import { parseSummariesQuery, summariesHref, type SummariesQuery } from "@/lib/summaries";

const TMD_WEEKLY_LIST = "https://www.tmd.go.th/climate/summaryweekly";

const INFO_ICON = (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <circle cx="10" cy="10" r="8.5" stroke="currentColor" strokeWidth="1.5" />
    <path d="M10 9v5M10 6v.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
);

type SummariesViewProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

function RegionTabs({ query }: { query: SummariesQuery }) {
  return (
    <TabLinks
      label="เลือกภาค"
      items={[
        { href: summariesHref({ ...query, region: null }), label: "ทุกภาค", current: query.region === null },
        ...REGION_KEYS.map((key) => ({
          href: summariesHref({ ...query, region: key }),
          label: REGION_LABELS[key],
          current: query.region === key,
        })),
      ]}
    />
  );
}

// มุมมองหลักของหน้า /summaries: ฉบับที่เลือก (ค่าเริ่มต้นล่าสุด) + ตัวเลือกสัปดาห์รายเดือน + ชิปภาค + ภาพรวม/การ์ดภาค
export async function SummariesView({ searchParams }: SummariesViewProps) {
  const query = parseSummariesQuery(await searchParams, isRegionKey);
  const [months, selected] = await Promise.all([
    listIssueMonths("weekly"),
    query.issue ? getWeekly(query.issue) : getLatestWeekly(),
  ]);

  if (!selected) {
    return (
      <Alert icon={INFO_ICON} role="status" className="animate-fade-in">
        {query.issue ? (
          <>
            <p className="font-semibold">ไม่พบสรุปรายสัปดาห์ฉบับที่เลือก</p>
            <p className="mt-1">ฉบับนี้อาจยังไม่ได้โหลดเข้าระบบ</p>
            <Link
              href={summariesHref({ issue: null, month: null, region: query.region })}
              className={cn(buttonVariants({ variant: "secondary" }), "mt-3")}
            >
              ดูฉบับล่าสุด
            </Link>
          </>
        ) : (
          <>
            <p className="font-semibold">ยังไม่มีสรุปรายสัปดาห์ในระบบ</p>
            <p className="mt-1">
              ระบบนี้นำประกาศของกรมอุตุนิยมวิทยาเข้ามาเป็นชุด ชุดที่มีสรุปรายสัปดาห์ยังไม่ได้โหลดเข้าระบบ
              ระหว่างนี้ดูสรุปฉบับเต็มได้ที่เว็บไซต์กรมอุตุนิยมวิทยา
            </p>
            <a href={TMD_WEEKLY_LIST} rel="noreferrer" className="mt-2 inline-block text-text-link underline underline-offset-4">
              สรุปสภาพอากาศรายสัปดาห์ที่กรมอุตุนิยมวิทยา
            </a>
          </>
        )}
      </Alert>
    );
  }

  const month = resolveMonth(months, query.month, selected.issued_at);
  const [items, latest] = await Promise.all([
    month ? listIssuesInMonth("weekly", month) : Promise.resolve([]),
    query.issue ? getLatestWeekly() : Promise.resolve(selected),
  ]);
  const isLatest = !latest || selected.issue_id === latest.issue_id;

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <p className="text-body-sm text-body">
          {isLatest ? "สรุปล่าสุดในระบบ" : "สรุปย้อนหลัง"} · สัปดาห์ {selected.source_label} · ออกประกาศ{" "}
          {thaiDateTimeShort(selected.issued_at)}
          {isLatest ? null : (
            <>
              {" "}
              <Link
                href={summariesHref({ issue: null, month: null, region: query.region })}
                className="text-text-link underline underline-offset-4"
              >
                ดูฉบับล่าสุด
              </Link>
            </>
          )}
        </p>
        {month && months.length > 0 ? (
          <MonthPicker
            title="เลือกสัปดาห์อื่น"
            months={months}
            month={month}
            groups={groupWeeks(items, `สัปดาห์ที่ออกประกาศใน${thaiMonthOfKey(month)}`)}
            currentId={selected.issue_id}
            hrefForMonth={(m) => summariesHref({ ...query, month: m })}
            // เลือกสัปดาห์แล้วไม่ต้องคงเดือนใน URL: หน้าใหม่ปิดกล่อง (เห็นผลสรุปทันที) และใช้เดือนของฉบับนั้นเอง
            hrefForIssue={(id) => summariesHref({ ...query, issue: id, month: null })}
            defaultOpen={query.month !== null}
          />
        ) : null}
        <RegionTabs query={query} />
      </div>

      <WeeklySummaryView summary={selected} region={query.region} />

      <p className="text-body-sm text-ink">
        ข้อความและตัวเลขในหน้านี้คัดจากสรุปของกรมอุตุนิยมวิทยาคำต่อคำ ช่องที่ต้นฉบับเว้นว่างแสดงว่า &quot;ไม่มีข้อมูลในฉบับนี้&quot;
        ดูฉบับเต็มได้ที่{" "}
        <a href={TMD_WEEKLY_LIST} rel="noreferrer" className="text-text-link underline underline-offset-4">
          เว็บไซต์กรมอุตุนิยมวิทยา
        </a>
      </p>
    </div>
  );
}
