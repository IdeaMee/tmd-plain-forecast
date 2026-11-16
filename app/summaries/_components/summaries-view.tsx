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
