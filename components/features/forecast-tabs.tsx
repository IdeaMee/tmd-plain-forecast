import { TabLinks } from "@/components/ui/tab-links";
import { REGION_KEYS } from "@/lib/contract/issue";
import { REGION_LABELS } from "@/lib/format/thai";
import { homeHref, type HomeQuery } from "@/lib/routes";

type ForecastTabsProps = { query: HomeQuery };

// แท็บชนิดพยากรณ์ (DocTypeTabs)
export function DocTypeTabs({ query }: ForecastTabsProps) {
  return (
    <TabLinks
      label="ชนิดพยากรณ์"
      variant="segmented"
      items={[
        { href: homeHref({ type: "daily", issue: null, region: query.region }), label: "พยากรณ์รายวัน", shortLabel: "รายวัน", current: query.type === "daily" },
        {
          href: homeHref({ type: "sevenday", issue: null, region: query.region }),
          label: "พยากรณ์ 7 วัน",
          shortLabel: "7 วัน",
          current: query.type === "sevenday",
        },
        {
          href: homeHref({ type: "shipping", issue: null, region: null }),
          label: "พยากรณ์เดินเรือ",
          shortLabel: "เดินเรือ",
          current: query.type === "shipping",
        },
      ]}
    />
  );
}

// แท็บภาค (RegionTabs): ชิปเลื่อนแนวนอนบนมือถือ "ทุกภาค" = แสดง 7 การ์ด
export function RegionTabs({ query }: ForecastTabsProps) {
  return (
    <TabLinks
      label="เลือกภาค"
      items={[
        { href: homeHref({ ...query, region: null }), label: "ทุกภาค", current: query.region === null },
        ...REGION_KEYS.map((key) => ({
          href: homeHref({ ...query, region: key }),
          label: REGION_LABELS[key],
          current: query.region === key,
        })),
      ]}
    />
  );
}
