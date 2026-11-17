"use client";

import Link from "next/link";
import { useState } from "react";

import { cn } from "@/lib/cn";

// ฉบับในช่องของวัน พร้อมลิงก์ (คำนวณฝั่งเซิร์ฟเวอร์ เพราะฟังก์ชันส่งเข้าคอมโพเนนต์ฝั่งเบราว์เซอร์ไม่ได้)
export type CalendarEntryLink = { issueId: string; label: string; href: string };
export type CalendarDayCell = { day: number; label: string; entries: CalendarEntryLink[] } | null;

type DayCalendarProps = {
  // ชื่อเดือนสำหรับโปรแกรมอ่านจอ เช่น "พฤศจิกายน 2569"
  monthName: string;
  cells: CalendarDayCell[];
  // ฉบับของเดือนนี้ที่ป้ายวันเป็นเดือนอื่น (ออกหลังเที่ยงคืน) ใส่ในช่องวันไม่ได้ จึงแสดงเป็นปุ่มต่างหากใต้ปฏิทิน
  extras: { day: string; entries: CalendarEntryLink[] }[];
  currentId: string;
};

const WEEKDAYS = ["อา", "จ", "อ", "พ", "พฤ", "ศ", "ส"];

const cellBase =
  "flex min-h-11 items-center justify-center rounded-md text-button transition-colors duration-(--duration-base) ease-standard";
const idle = "border border-hairline-strong bg-surface-card text-ink hover:bg-canvas-soft";
const chosen = "bg-primary font-semibold text-on-primary";

function initialDay(cells: CalendarDayCell[], currentId: string): number | null {
  const days = cells.filter((c): c is NonNullable<CalendarDayCell> => c !== null && c.entries.length > 1);
  const own = days.find((c) => c.entries.some((e) => e.issueId === currentId));
  // ไม่ได้ดูฉบับของเดือนนี้ = เปิดวันที่ใหม่สุดที่มีหลายรอบไว้ให้เห็นปุ่มเวลาเลย
  return (own ?? days.at(-1))?.day ?? null;
}

// ปฏิทินเลือกวัน (7 ช่อง/แถว): วันที่ไม่มีฉบับกดไม่ได้ · วันที่มีรอบเดียวเป็นลิงก์ตรงไปฉบับนั้น
// · วันที่มีหลายรอบกดแล้วมีปุ่มเลือกเวลาด้านล่าง (ลิงก์ไปฉบับ)
export function DayCalendar({ monthName, cells, extras, currentId }: DayCalendarProps) {
  const [selected, setSelected] = useState<number | null>(() => initialDay(cells, currentId));
  const picked = cells.find((c) => c !== null && c.day === selected) ?? null;
  const times = picked && picked.entries.length > 1 ? picked : null;

  return (
    // จอกว้าง (md ขึ้นไป): ปฏิทินซ้าย กล่องเวลาขวา ไม่ปล่อยพื้นที่ว่างข้างปฏิทิน · มือถือเรียงลงตามเดิม
    <div className="space-y-4 md:grid md:grid-cols-[22rem_minmax(0,1fr)] md:items-start md:gap-6 md:space-y-0">
      <div role="group" aria-label={`ปฏิทิน${monthName}`} className="max-w-sm space-y-1">
        <div aria-hidden="true" className="grid grid-cols-7 gap-1 text-center text-body-sm font-semibold text-body">
          {WEEKDAYS.map((d) => (
            <span key={d}>{d}</span>
          ))}
        </div>
        <div className="grid grid-cols-7 gap-1">
          {cells.map((cell, i) => {
            if (cell === null) return <span key={`blank-${i}`} aria-hidden="true" />;
            const { day, label, entries } = cell;
            if (entries.length === 0) {
              return (
                // วันไม่มีฉบับ: ไม่ใช่ตัวควบคุม จึงซ่อนจากโปรแกรมอ่านจอ (ผู้ใช้เห็นจางลง)
                <span key={day} aria-hidden="true" className={cn(cellBase, "cursor-not-allowed opacity-35")}>
                  {day}
                </span>
              );
            }
            if (entries.length === 1) {
              const only = entries[0];
              const isCurrent = only.issueId === currentId;
              return (
                <Link
                  key={day}
                  href={only.href}
                  aria-label={label}
                  aria-current={isCurrent ? "page" : undefined}
                  className={cn(cellBase, isCurrent ? chosen : idle)}
                >
                  {day}
                </Link>
              );
            }
            const isSelected = selected === day;
            const hasCurrent = entries.some((e) => e.issueId === currentId);
            return (
              <button
                key={day}
                type="button"
                aria-pressed={isSelected}
                aria-label={`${label} มี ${entries.length} รอบ`}
                onClick={() => setSelected(day)}
                className={cn(cellBase, "cursor-pointer", isSelected ? chosen : idle, hasCurrent && !isSelected && "border-ink")}
              >
                {day}
              </button>
            );
          })}
        </div>
        <p className="pt-1 text-body-sm text-body">กดวันที่เพื่อเลือก · วันที่จางไม่มีประกาศ</p>
      </div>

      <div className="space-y-4 md:min-h-40 md:rounded-lg md:border md:border-hairline md:bg-canvas-soft md:p-5">
      {!times && extras.length === 0 ? (
        <p className="hidden text-body-sm text-body md:block">กดวันที่ทางซ้ายเพื่อดูเวลาของวันนั้น</p>
      ) : null}
      {times ? (
        <div role="group" aria-label={`เลือกเวลาของวันที่ ${times.label}`} className="animate-fade-in space-y-2" key={times.day}>
          <p className="text-body-sm font-semibold text-ink">{times.label} · เลือกเวลา</p>
          <ul className="flex flex-wrap gap-2">
            {times.entries.map((entry) => {
              const isCurrent = entry.issueId === currentId;
              return (
                <li key={entry.issueId}>
                  <Link
                    href={entry.href}
                    aria-current={isCurrent ? "page" : undefined}
                    className={cn(
                      "inline-flex min-h-11 min-w-24 items-center justify-center rounded-md px-4 text-button transition-colors duration-(--duration-base) ease-standard",
                      isCurrent ? chosen : idle,
                    )}
                  >
                    {entry.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ) : null}

      {extras.length > 0 ? (
        <div role="group" aria-label="ฉบับที่ออกหลังเที่ยงคืน" className="space-y-2">
          <p className="text-body-sm font-semibold text-ink">ออกหลังเที่ยงคืน (ป้ายวันเป็นเดือนก่อน)</p>
          <ul className="flex flex-wrap gap-2">
            {extras.flatMap((group) =>
              group.entries.map((entry) => {
                const isCurrent = entry.issueId === currentId;
                return (
                  <li key={entry.issueId}>
                    <Link
                      href={entry.href}
                      aria-current={isCurrent ? "page" : undefined}
                      className={cn(
                        "inline-flex min-h-11 items-center justify-center rounded-md px-4 text-button transition-colors duration-(--duration-base) ease-standard",
                        isCurrent ? chosen : idle,
                      )}
                    >
                      {group.day} {entry.label}
                    </Link>
                  </li>
                );
              }),
            )}
          </ul>
        </div>
      ) : null}
      </div>
    </div>
  );
}
