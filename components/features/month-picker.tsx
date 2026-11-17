import Link from "next/link";
import type { CSSProperties } from "react";

import { DayCalendar } from "@/components/features/day-calendar";
import { Disclosure } from "@/components/ui/disclosure";
import { cn } from "@/lib/cn";
import { thaiMonthOfKey } from "@/lib/format/thai";
import { buildCalendar, neighborMonths, type HistoryGroup, type MonthCount } from "@/lib/history";

type MonthPickerProps = {
  // หัวกล่อง เช่น "เลือกรอบอื่น" (ต่อท้ายด้วยจำนวนฉบับทั้งหมดและจำนวนเดือน)
  title: string;
  // เดือนที่มีฉบับ ใหม่สุดก่อน
  months: MonthCount[];
  // เดือนที่กำลังแสดงรายการ
  month: string;
  // ฉบับของเดือนนั้น (จัดกลุ่มแล้ว)
  groups: HistoryGroup[];
  currentId: string;
  hrefForMonth: (month: string) => string;
  hrefForIssue: (issueId: string) => string;
  // เปิดกล่องไว้ตั้งแต่แรก (เมื่อผู้ใช้เลือกเดือนที่ไม่ใช่เดือนของฉบับที่ดูอยู่)
  defaultOpen?: boolean;
};

const chip =
  "inline-flex min-h-10 shrink-0 items-center rounded-md px-4 text-button transition-colors duration-(--duration-base) pointer-coarse:min-h-11";
const idleChip = "border border-hairline-strong bg-surface-card text-ink hover:bg-canvas-soft";
const arrow =
  "inline-flex size-11 shrink-0 items-center justify-center rounded-md border border-hairline-strong bg-surface-card text-ink transition-colors duration-(--duration-base)";

function Chevron({ dir }: { dir: "left" | "right" }) {
  return (
    <svg aria-hidden="true" viewBox="0 0 16 16" className="size-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d={dir === "left" ? "m10 3-5 5 5 5" : "m6 3 5 5-5 5"} />
    </svg>
  );
}

// เลือกรอบ/ฉบับย้อนหลังทุกเดือนที่มีข้อมูล: ลูกศรเดือนก่อน/ถัดไป + ชิปทุกเดือน + ปฏิทินเลือกวัน แล้วเลือกเวลา
// เดือนเปลี่ยนด้วยลิงก์ (?month=) ลิงก์ตรงไปรอบได้ (?issue=) · ป้ายที่ไม่ใช่รายวัน (เช่นสัปดาห์) ใช้รายการชิปแทนปฏิทิน
export function MonthPicker({ title, months, month, groups, currentId, hrefForMonth, hrefForIssue, defaultOpen }: MonthPickerProps) {
  const total = months.reduce((sum, m) => sum + m.count, 0);
  const { older, newer } = neighborMonths(months, month);
  const current = months.find((m) => m.month === month);
  const monthName = thaiMonthOfKey(month);
  const withHref = (entries: { issueId: string; label: string }[]) => entries.map((e) => ({ ...e, href: hrefForIssue(e.issueId) }));
  const calendar = buildCalendar(month, groups);
  const cells = calendar?.cells.map((cell) => (cell === null ? null : { ...cell, entries: withHref(cell.entries) }));
  const extras = calendar?.extras.map((group) => ({ day: group.day, entries: withHref(group.entries) })) ?? [];
  return (
    // key: เลือกฉบับใหม่แล้วกล่องปิดเอง (React ไม่แตะแอตทริบิวต์ open ที่ผู้ใช้เปิดไว้ถ้าไม่สร้างใหม่) · เปลี่ยนเดือนแล้วเปิดค้างไว้
    <Disclosure
      key={`${currentId}|${defaultOpen ? "open" : "closed"}`}
      defaultOpen={defaultOpen}
      summary={`${title} · ทั้งหมด ${total} ฉบับ ใน ${months.length} เดือน`}
    >
      <div className="space-y-5">
        {/* จอกว้าง: ลูกศร+ชื่อเดือนซ้าย ชิปทุกเดือนขวา อยู่แถวเดียวกัน · มือถือเรียงลง */}
        <nav aria-label="เลือกเดือน" className="space-y-3 md:flex md:items-center md:justify-between md:gap-6 md:space-y-0">
          <div className="flex items-center justify-between gap-3 md:justify-start">
            {older ? (
              <Link href={hrefForMonth(older)} aria-label={`เดือนก่อน (${thaiMonthOfKey(older)})`} className={cn(arrow, "hover:bg-canvas-soft")}>
                <Chevron dir="left" />
              </Link>
            ) : (
              <span aria-hidden="true" className={cn(arrow, "cursor-not-allowed opacity-35")}>
                <Chevron dir="left" />
              </span>
            )}
            {/* ไม่ใช้หัวข้อ (h3) เพราะกล่องนี้อยู่ในหน้าที่การ์ดภาคเป็น h3 ลำดับหัวข้อของหน้าต้องไม่เพี้ยนตอนเปิดกล่อง */}
            <p className="min-w-0 flex-1 text-center text-title-sm font-semibold md:min-w-56 md:flex-none">
              {monthName}
              {current ? ` · ${current.count} ฉบับ` : ""}
            </p>
            {newer ? (
              <Link href={hrefForMonth(newer)} aria-label={`เดือนถัดไป (${thaiMonthOfKey(newer)})`} className={cn(arrow, "hover:bg-canvas-soft")}>
                <Chevron dir="right" />
              </Link>
            ) : (
              <span aria-hidden="true" className={cn(arrow, "cursor-not-allowed opacity-35")}>
                <Chevron dir="right" />
              </span>
            )}
          </div>
          {/* ชิปทุกเดือน: แถวเดียวเลื่อนแนวนอน ไม่ดันหน้าให้ยาว */}
          <ul
            className="-mx-4 flex gap-2 overflow-x-auto px-4 py-1 [scrollbar-width:none] sm:mx-0 sm:px-0 md:justify-end [&::-webkit-scrollbar]:hidden"
            aria-label="ทุกเดือนที่มีข้อมูล"
          >
            {months.map((m) => (
              <li key={m.month} className="shrink-0">
                <Link
                  href={hrefForMonth(m.month)}
                  aria-current={m.month === month ? "true" : undefined}
                  className={cn(chip, m.month === month ? "bg-primary font-semibold text-on-primary" : idleChip)}
                >
                  {thaiMonthOfKey(m.month)} ({m.count})
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <section aria-label={`ฉบับของ${monthName}`}>
          {cells ? (
            // key = เดือน: เปลี่ยนเดือนแล้วเริ่มเลือกวันใหม่ ไม่ค้างวันของเดือนก่อน
            <DayCalendar key={month} monthName={monthName} cells={cells} extras={extras} currentId={currentId} />
          ) : (
            <div className="space-y-4">
              {groups.map((group, i) => (
                // แถววันไหลเข้าทีละแถวเมื่อเปิด (D13)
                <div key={group.day} className="animate-enter-up stagger" style={{ "--i": Math.min(i, 8) } as CSSProperties}>
                  <p className="text-body-sm font-semibold text-ink">{group.day}</p>
                  <ul className="mt-2 flex flex-wrap gap-2">
                    {group.entries.map((entry) => {
                      const isCurrent = entry.issueId === currentId;
                      return (
                        <li key={entry.issueId}>
                          <Link
                            href={hrefForIssue(entry.issueId)}
                            aria-current={isCurrent ? "page" : undefined}
                            className={cn(chip, isCurrent ? "bg-primary font-semibold text-on-primary" : idleChip)}
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
          )}
        </section>
      </div>
    </Disclosure>
  );
}
