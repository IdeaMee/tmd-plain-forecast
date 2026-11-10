import Link from "next/link";

import { DocTypeTabs, RegionTabs } from "@/components/features/forecast-tabs";
import { IssueSummary } from "@/components/features/issue-summary";
import { RoundPicker } from "@/components/features/round-picker";
import { Alert } from "@/components/ui/alert";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/cn";
import { getIssue, getLatestIssue, listRecentIssues } from "@/lib/data/forecasts";
import { isRegionKey } from "@/lib/format/thai";
import { groupByDay } from "@/lib/history";
import { homeHref, parseHomeQuery } from "@/lib/routes";

type ForecastViewProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

const INFO_ICON = (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <circle cx="10" cy="10" r="8.5" stroke="currentColor" strokeWidth="1.5" />
    <path d="M10 9v5M10 6v.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
);

// มุมมองหลักของหน้า / : ฉบับที่เลือก (ค่าเริ่มต้นล่าสุด) 7 ภาค หรือภาคเดียว + ตัวเลือกรอบย้อนหลัง
export async function ForecastView({ searchParams }: ForecastViewProps) {
  const query = parseHomeQuery(await searchParams, isRegionKey);
  const [history, issue] = await Promise.all([
    listRecentIssues(query.type),
    query.issue ? getIssue(query.type, query.issue) : getLatestIssue(query.type),
  ]);
  const typeName = query.type === "daily" ? "พยากรณ์รายวัน" : "พยากรณ์ 7 วัน";

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <DocTypeTabs query={query} />
        <RegionTabs query={query} />
      </div>

      {!issue ? (
        // ว่าง: ไม่มีข้อมูลเลย หรือฉบับที่ขอไม่มีในระบบ (บอกสาเหตุและทางไปต่อ)
        <Alert icon={INFO_ICON} role="status">
          {query.issue ? (
            <>
              <p className="font-semibold">ไม่พบ{typeName}ฉบับที่เลือก</p>
              <p className="mt-1">ฉบับนี้อาจเก่ากว่า 7 วันหรือยังไม่ได้โหลดเข้าระบบ</p>
              <Link href={homeHref({ ...query, issue: null })} className={cn(buttonVariants({ variant: "secondary" }), "mt-3")}>
                ดูฉบับล่าสุด
              </Link>
            </>
          ) : (
            <>
              <p className="font-semibold">ยังไม่มีข้อมูล{typeName}</p>
              <p className="mt-1">
                ระบบนี้นำประกาศของกรมอุตุนิยมวิทยาเข้ามาเป็นรอบ ยังไม่มีฉบับของชนิดนี้ในระบบ
                ระหว่างนี้ดูประกาศฉบับเต็มได้ที่เว็บไซต์กรมอุตุนิยมวิทยา
              </p>
            </>
          )}
        </Alert>
      ) : (
        <>
          <p className="text-body-sm text-body">
            {typeName} {issue.source_label}
            {history[0] && issue.issue_id !== history[0].issueId ? " (ฉบับย้อนหลัง)" : ""}
          </p>

          {history.length > 1 ? (
            <RoundPicker
              docType={query.type}
              groups={groupByDay(history)}
              currentId={issue.issue_id}
              hrefFor={(issueId) => homeHref({ ...query, issue: issueId })}
            />
          ) : null}

          <IssueSummary issue={issue} region={query.region} />
        </>
      )}
    </div>
  );
}
