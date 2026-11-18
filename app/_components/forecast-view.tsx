import Link from "next/link";

import { DocTypeTabs, RegionTabs } from "@/components/features/forecast-tabs";
import { IssueSummary } from "@/components/features/issue-summary";
import { MonthPicker } from "@/components/features/month-picker";
import { ShippingSummary } from "@/components/features/shipping-summary";
import { Alert } from "@/components/ui/alert";
import { buttonVariants } from "@/components/ui/button";
import type { ShippingIssue } from "@/lib/contract/documents";
import type { Issue } from "@/lib/contract/issue";
import { cn } from "@/lib/cn";
import {
  getIssue,
  getLatestIssue,
  getLatestShippingIssue,
  getShippingIssue,
  listIssueMonths,
  listIssuesInMonth,
} from "@/lib/data/forecasts";
import { isRegionKey } from "@/lib/format/thai";
import { groupByDay, resolveMonth } from "@/lib/history";
import { hasRegions, homeHref, parseHomeQuery, type HomeQuery, type HomeType } from "@/lib/routes";

type ForecastViewProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

const TYPE_NAMES: Record<HomeType, string> = {
  daily: "พยากรณ์รายวัน",
  sevenday: "พยากรณ์ 7 วัน",
  shipping: "พยากรณ์เดินเรือ",
};

// หัวกล่องตัวเลือกรอบ: 7 วันเป็นฉบับ ที่เหลือเป็นรอบ
const PICKER_TITLES: Record<HomeType, string> = {
  daily: "เลือกรอบอื่น",
  sevenday: "เลือกฉบับอื่น",
  shipping: "เลือกรอบอื่น",
};

const INFO_ICON = (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <circle cx="10" cy="10" r="8.5" stroke="currentColor" strokeWidth="1.5" />
    <path d="M10 9v5M10 6v.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
);

type Selected = { kind: "issue"; doc: Issue } | { kind: "shipping"; doc: ShippingIssue } | null;

async function loadSelected(query: HomeQuery): Promise<Selected> {
  if (query.type === "shipping") {
    const doc = query.issue ? await getShippingIssue(query.issue) : await getLatestShippingIssue();
    return doc ? { kind: "shipping", doc } : null;
  }
  const doc = query.issue ? await getIssue(query.type, query.issue) : await getLatestIssue(query.type);
  return doc ? { kind: "issue", doc } : null;
}

// มุมมองหลักของหน้า / : ฉบับที่เลือก (ค่าเริ่มต้นล่าสุด) 7 ภาค หรือภาคเดียว หรือ 4 พื้นที่ทะเล + ตัวเลือกรอบย้อนหลัง
export async function ForecastView({ searchParams }: ForecastViewProps) {
  const query = parseHomeQuery(await searchParams, isRegionKey);
  const [months, selected] = await Promise.all([listIssueMonths(query.type), loadSelected(query)]);
  const typeName = TYPE_NAMES[query.type];
  // เดือนของตัวเลือกรอบ: เดือนที่ขอ > เดือนของฉบับที่เลือก > เดือนล่าสุด
  const month = resolveMonth(months, query.month, selected?.doc.issued_at ?? null);
  const [items, latest] = await Promise.all([
    selected && month ? listIssuesInMonth(query.type, month) : Promise.resolve([]),
    selected && query.issue ? loadSelected({ ...query, issue: null }) : Promise.resolve(selected),
  ]);
  const total = months.reduce((sum, m) => sum + m.count, 0);

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <DocTypeTabs query={query} />
        {hasRegions(query.type) ? <RegionTabs query={query} /> : null}
      </div>

      {!selected ? (
        // ว่าง: ไม่มีข้อมูลเลย หรือฉบับที่ขอไม่มีในระบบ (บอกสาเหตุและทางไปต่อ)
        <Alert icon={INFO_ICON} role="status" className="animate-fade-in">
          {query.issue ? (
            <>
              <p className="font-semibold">ไม่พบ{typeName}ฉบับที่เลือก</p>
              <p className="mt-1">ฉบับนี้อาจยังไม่ได้โหลดเข้าระบบ</p>
              <Link href={homeHref({ ...query, issue: null, month: null })} className={cn(buttonVariants({ variant: "secondary" }), "mt-3")}>
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
            {typeName} {selected.doc.source_label}
            {latest && selected.doc.issue_id !== latest.doc.issue_id ? " (ฉบับย้อนหลัง)" : ""}
          </p>

          {total > 1 && month ? (
            <MonthPicker
              title={PICKER_TITLES[query.type]}
              months={months}
              month={month}
              groups={groupByDay(items)}
              currentId={selected.doc.issue_id}
              hrefForMonth={(m) => homeHref({ ...query, month: m })}
              // เลือกฉบับแล้วไม่ต้องคงเดือนใน URL: หน้าใหม่ปิดกล่อง (เห็นผลสรุปทันที) และใช้เดือนของฉบับนั้นเอง
              hrefForIssue={(issueId) => homeHref({ ...query, issue: issueId, month: null })}
              defaultOpen={query.month !== null}
            />
          ) : null}

          {selected.kind === "shipping" ? (
            <ShippingSummary issue={selected.doc} />
          ) : (
            <IssueSummary issue={selected.doc} region={query.region} />
          )}
        </>
      )}
    </div>
  );
}
