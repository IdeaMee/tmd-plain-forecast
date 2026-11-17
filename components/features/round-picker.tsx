import Link from "next/link";
import type { CSSProperties } from "react";

import { Disclosure } from "@/components/ui/disclosure";
import { cn } from "@/lib/cn";
import type { HistoryGroup } from "@/lib/history";
import type { HomeType } from "@/lib/routes";

type RoundPickerProps = {
  docType: HomeType;
  groups: HistoryGroup[];
  currentId: string;
  // ลิงก์ของแต่ละฉบับ (คงภาคที่เลือกไว้)
  hrefFor: (issueId: string) => string;
};

// เลือกรอบ (รายวัน/เดินเรือ) หรือฉบับ (7 วัน) ย้อนหลัง 1 สัปดาห์ ล่าสุดก่อน · <details> ใช้ได้โดยไม่ต้องมี JavaScript
export function RoundPicker({ docType, groups, currentId, hrefFor }: RoundPickerProps) {
  const title = docType === "sevenday" ? "เลือกฉบับอื่น (ย้อนหลัง 7 วัน)" : "เลือกรอบอื่น (ย้อนหลัง 7 วัน)";
  return (
    <Disclosure summary={title}>
      <div className="space-y-4">
        {groups.map((group, i) => (
          // แถววันไหลเข้าทีละแถวเมื่อเปิด (D13)
          <div key={group.day} className="animate-enter-up stagger" style={{ "--i": i } as CSSProperties}>
            <p className="text-body-sm font-semibold text-ink">{group.day}</p>
            <ul className="mt-2 flex flex-wrap gap-2">
              {group.entries.map((entry) => {
                const current = entry.issueId === currentId;
                return (
                  <li key={entry.issueId}>
                    <Link
                      href={hrefFor(entry.issueId)}
                      aria-current={current ? "page" : undefined}
                      className={cn(
                        "inline-flex min-h-10 items-center rounded-md px-4 text-button transition-colors duration-(--duration-base) pointer-coarse:min-h-11",
                        current
                          ? "bg-primary font-semibold text-on-primary"
                          : "border border-hairline-strong bg-surface-card text-ink hover:bg-canvas-soft",
                      )}
                    >
                      {entry.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
    </Disclosure>
  );
}
