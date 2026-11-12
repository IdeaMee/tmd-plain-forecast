"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useId, useRef, useState, type KeyboardEvent } from "react";

import { cn } from "@/lib/cn";
import { isGroupCurrent, NAV_CTA, NAV_GROUPS } from "@/lib/nav";

const FOCUSABLE = "a[href], button:not([disabled])";
// ตรงกับ lg ของ Tailwind (V10: เมนูเดสก์ท็อปตั้งแต่ 1024 px)
const DESKTOP_QUERY = "(min-width: 1024px)";

// เมนูมือถือ (ต่ำกว่า 1024 px, V10): แผงกว้างเต็มจอใต้ Header เลื่อนลงตอนเปิด เลื่อนขึ้นตอนปิด (ดีไซน์ A)
// ปิดด้วยปุ่มเดิม แตะพื้นมืด Esc หรือเปลี่ยนหน้า · ล็อกการเลื่อนพื้นหลัง · โฟกัสวนในแผงขณะเปิด
export function MobileMenu() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const [lastPath, setLastPath] = useState(pathname);
  const panelId = useId();
  const buttonRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  // เปลี่ยนหน้าแล้วปิด (ปรับ state ระหว่าง render ตามแนวทางของ React แทน effect)
  if (pathname !== lastPath) {
    setLastPath(pathname);
    setOpen(false);
  }

  useEffect(() => {
    if (!open) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    panelRef.current?.querySelector<HTMLElement>(FOCUSABLE)?.focus();
    function onKey(event: globalThis.KeyboardEvent) {
      if (event.key !== "Escape") return;
      setOpen(false);
      buttonRef.current?.focus();
    }
    document.addEventListener("keydown", onKey);
    // จอกว้างขึ้นถึงเมนูเดสก์ท็อป (หมุนแท็บเล็ต) = ปิด ไม่ให้การล็อกการเลื่อนค้าง
    const desktop = window.matchMedia(DESKTOP_QUERY);
    const onWide = () => desktop.matches && setOpen(false);
    desktop.addEventListener("change", onWide);
    return () => {
      document.body.style.overflow = previous;
      document.removeEventListener("keydown", onKey);
      desktop.removeEventListener("change", onWide);
    };
  }, [open]);

  // Tab วนในแผง (ไม่หลุดไปเนื้อหาด้านหลังที่ถูกบัง)
  function trapFocus(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key !== "Tab" || !panelRef.current) return;
    const items = [...panelRef.current.querySelectorAll<HTMLElement>(FOCUSABLE)];
    if (items.length === 0) return;
    const first = items[0];
    const last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  const close = () => setOpen(false);
  // ปิดโดยไม่เปลี่ยนหน้า (แตะพื้นมืด) คืนโฟกัสให้ปุ่ม ไม่ให้ค้างอยู่ในแผงที่ถูกซ่อน
  const dismiss = () => {
    setOpen(false);
    buttonRef.current?.focus();
  };

  return (
    <>
      <button
        ref={buttonRef}
        type="button"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((v) => !v)}
        className="inline-flex min-h-11 items-center gap-2 rounded-md border border-hairline-strong px-3 text-button text-ink transition-colors duration-(--duration-base) hover:bg-canvas-soft"
      >
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
          {/* สามขีดหมุนเป็นกากบาท (เคลื่อนแค่ transform) */}
          <path
            d="M3 5h14"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            className={cn(
              "origin-center transition-transform duration-(--duration-base) ease-standard [transform-box:fill-box]",
              open && "translate-y-[5px] rotate-45",
            )}
          />
          <path
            d="M3 10h14"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            className={cn("transition-opacity duration-(--duration-fast)", open && "opacity-0")}
          />
          <path
            d="M3 15h14"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            className={cn(
              "origin-center transition-transform duration-(--duration-base) ease-standard [transform-box:fill-box]",
              open && "-translate-y-[5px] -rotate-45",
            )}
          />
        </svg>
        {open ? "ปิด" : "เมนู"}
      </button>

      {/* ชั้นใต้ Header: ปิดอยู่ = inert (กดไม่ได้ โปรแกรมอ่านจอข้าม) และซ่อน (visibility) หลังแผงเลื่อนขึ้นเสร็จ */}
      <div
        className={cn(
          "fixed inset-x-0 top-16 bottom-0 z-20 overflow-hidden",
          // เปิด = มองเห็นทันที (โฟกัสลิงก์แรกได้) ปิด = ซ่อนหลังแผงเลื่อนขึ้นเสร็จ
          open
            ? "visible"
            : "pointer-events-none invisible transition-[visibility] delay-(--duration-base)",
        )}
        inert={!open}
      >
        <div
          aria-hidden="true"
          onClick={dismiss}
          className={cn(
            "absolute inset-0 bg-ink/40 transition-opacity duration-(--duration-slow) ease-standard",
            open ? "opacity-100" : "opacity-0",
          )}
        />
        <div
          ref={panelRef}
          id={panelId}
          onKeyDown={trapFocus}
          className={cn(
            "relative max-h-full overflow-y-auto border-b border-hairline-strong bg-canvas shadow-panel transition-transform ease-standard",
            open ? "translate-y-0 duration-(--duration-slow)" : "-translate-y-full duration-(--duration-base)",
          )}
        >
          <nav aria-label="เมนูหลัก" className="mx-auto max-w-content px-4 py-4 sm:px-6">
            <ul className="divide-y divide-hairline">
              {NAV_GROUPS.map((group) => (
                <li key={group.id} className="py-3">
                  {/* บอกหมวดของหน้าปัจจุบันที่หัวหมวด (ลิงก์ย่อยของหน้าแรกต่างกันแค่ query จึงไม่ระบุลิงก์) */}
                  <p className="text-title-sm text-ink">
                    {group.label}
                    {isGroupCurrent(group, pathname) ? <span className="text-body-sm text-body"> · หน้านี้</span> : null}
                  </p>
                  <p className="text-body-sm text-body">{group.description}</p>
                  <ul className="mt-2 space-y-1">
                    {group.links.map((link) => (
                      <li key={link.href}>
                        <Link
                          href={link.href}
                          onClick={close}
                          className="flex min-h-12 items-center justify-between gap-3 rounded-md px-3 text-body-md text-ink transition-colors duration-(--duration-base) hover:bg-canvas-soft"
                        >
                          <span>{link.label}</span>
                          <span className="text-body-sm text-body">{link.description}</span>
                        </Link>
                      </li>
                    ))}
                  </ul>
                </li>
              ))}
            </ul>
            <Link
              href={NAV_CTA.href}
              onClick={close}
              className="mt-4 flex min-h-12 items-center justify-center rounded-md bg-primary px-4 text-button text-on-primary transition-colors duration-(--duration-base) hover:bg-primary-active"
            >
              {NAV_CTA.label}
            </Link>
          </nav>
        </div>
      </div>
    </>
  );
}
