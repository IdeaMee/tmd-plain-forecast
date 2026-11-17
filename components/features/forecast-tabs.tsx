import Link from "next/link";

import { Disclosure } from "@/components/ui/disclosure";
import { TabLinks } from "@/components/ui/tab-links";
import { cn } from "@/lib/cn";
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
        { href: homeHref({ type: "daily", issue: null, month: null, region: query.region }), label: "พยากรณ์รายวัน", shortLabel: "รายวัน", current: query.type === "daily" },
        {
          href: homeHref({ type: "sevenday", issue: null, month: null, region: query.region }),
          label: "พยากรณ์ 7 วัน",
          shortLabel: "7 วัน",
          current: query.type === "sevenday",
        },
        {
          href: homeHref({ type: "shipping", issue: null, month: null, region: null }),
          label: "พยากรณ์เดินเรือ",
          shortLabel: "เดินเรือ",
          current: query.type === "shipping",
        },
      ]}
    />
  );
}

// แท็บภาค (RegionTabs) "ทุกภาค" = แสดง 7 การ์ด
// จอตั้งแต่ sm ขึ้นไป: ชิปแถวเดียวเหมือนเดิม · จอแคบ: ลิ้นชักพับ เห็นภาคที่เลือกอยู่ กดแล้วเลือกจากตาราง 2 คอลัมน์ (ไม่ดันเนื้อหาลงไปไกล)
// สองชุดมีลิงก์ชุดเดียวกัน แต่ชุดที่ไม่ตรงขนาดจอถูกซ่อน (display: none) จึงไม่ซ้ำสำหรับผู้ใช้และโปรแกรมอ่านจอ
export function RegionTabs({ query }: ForecastTabsProps) {
  const items = [
    { href: homeHref({ ...query, region: null }), label: "ทุกภาค", current: query.region === null },
    ...REGION_KEYS.map((key) => ({
      href: homeHref({ ...query, region: key }),
      label: REGION_LABELS[key],
      current: query.region === key,
    })),
  ];
  const selected = items.find((item) => item.current)?.label ?? "ทุกภาค";
  return (
    <>
      <div className="sm:hidden">
        {/* key = ภาคที่เลือก: เลือกแล้วลิ้นชักปิดเอง */}
        <Disclosure key={selected} summary={`เลือกภาค · ${selected}`}>
          <nav aria-label="เลือกภาค">
            <ul className="grid grid-cols-2 gap-2">
              {items.map((item) => (
                <li key={item.href} className="min-w-0">
                  <Link
                    href={item.href}
                    aria-current={item.current ? "page" : undefined}
                    className={cn(
                      "flex min-h-11 items-center justify-center rounded-md border px-3 py-2 text-center text-button transition-colors duration-(--duration-base) ease-standard",
                      item.current ? "border-primary bg-primary font-semibold text-on-primary" : "border-hairline-strong bg-surface-card text-ink hover:bg-canvas-soft",
                    )}
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </Disclosure>
      </div>
      <div className="max-sm:hidden">
        <TabLinks label="เลือกภาค" items={items} />
      </div>
    </>
  );
}
