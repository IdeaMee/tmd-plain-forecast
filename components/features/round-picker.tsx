import Link from "next/link";

import type { DocType } from "@/lib/contract/issue";
import { cn } from "@/lib/cn";
import type { HistoryGroup } from "@/lib/history";

type RoundPickerProps = {
  docType: DocType;
  groups: HistoryGroup[];
  currentId: string;
  // ลิงก์ของแต่ละฉบับ (คงภาคที่เลือกไว้)
  hrefFor: (issueId: string) => string;
};

// เลือกรอบ (รายวัน) หรือฉบับ (7 วัน) ย้อนหลัง 1 สัปดาห์ ล่าสุดก่อน · <details> ใช้ได้โดยไม่ต้องมี JavaScript
export function RoundPicker({ docType, groups, currentId, hrefFor }: RoundPickerProps) {
  const title = docType === "daily" ? "เลือกรอบอื่น (ย้อนหลัง 7 วัน)" : "เลือกฉบับอื่น (ย้อนหลัง 7 วัน)";
  return (
    <details className="rounded-lg border border-hairline-strong bg-surface-card">
      <summary className="flex min-h-11 cursor-pointer items-center rounded-lg px-4 text-button text-ink hover:bg-canvas-soft">
        {title}
      </summary>
      <div className="space-y-4 border-t border-hairline px-4 py-4">
        {groups.map((group) => (
          <div key={group.day}>
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
                        "inline-flex min-h-10 items-center rounded-md px-4 text-button pointer-coarse:min-h-11",
                        current
                          ? "bg-primary text-on-primary"
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
    </details>
  );
}
