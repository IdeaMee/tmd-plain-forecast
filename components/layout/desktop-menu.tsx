"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState, type FocusEvent } from "react";

import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/cn";
import { isGroupCurrent, NAV_CTA, NAV_GROUPS } from "@/lib/nav";

// เมนูเดสก์ท็อป (ตั้งแต่ 1024 px, V10): หมวดเปิดหมวดย่อยด้วยคลิกหรือคีย์บอร์ด (Enter/Space ที่ปุ่ม, Esc ปิด)
// ปิดเมื่อคลิกนอกเมนู โฟกัสออกจากหมวด หรือเปลี่ยนหน้า · แผงหมวดย่อยจางเข้าและเลื่อนลงเล็กน้อย
export function DesktopMenu() {
  const pathname = usePathname();
  const [openId, setOpenId] = useState<string | null>(null);
  const [lastPath, setLastPath] = useState(pathname);
  const navRef = useRef<HTMLElement>(null);

  if (pathname !== lastPath) {
    setLastPath(pathname);
    setOpenId(null);
  }

  useEffect(() => {
    if (!openId) return;
    function onPointer(event: PointerEvent) {
      if (!navRef.current?.contains(event.target as Node)) setOpenId(null);
    }
    function onKey(event: KeyboardEvent) {
      if (event.key !== "Escape") return;
      setOpenId(null);
      navRef.current?.querySelector<HTMLElement>(`[data-group="${openId}"]`)?.focus();
    }
    document.addEventListener("pointerdown", onPointer);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointer);
      document.removeEventListener("keydown", onKey);
    };
  }, [openId]);

  function onBlur(event: FocusEvent<HTMLLIElement>) {
    // โฟกัสออกนอกหมวดนี้ (เช่น Tab ต่อไปหมวดอื่น) = ปิด
    if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setOpenId(null);
  }

  return (
    <nav ref={navRef} aria-label="เมนูหลัก" className="flex items-center gap-2">
      <ul className="flex items-center gap-1">
        {NAV_GROUPS.map((group) => {
          const open = openId === group.id;
          const panelId = `menu-${group.id}`;
          const current = isGroupCurrent(group, pathname);
          return (
            <li key={group.id} className="relative" onBlur={onBlur}>
              <button
                type="button"
                data-group={group.id}
                aria-expanded={open}
                aria-controls={panelId}
                onClick={() => setOpenId(open ? null : group.id)}
                className={cn(
                  "inline-flex min-h-10 items-center gap-1 rounded-md px-3 text-nav-link text-ink transition-colors duration-(--duration-base) hover:bg-canvas-soft pointer-coarse:min-h-11",
                  current && "font-semibold underline decoration-2 underline-offset-8",
                )}
              >
                {group.label}
                <svg
                  aria-hidden="true"
                  viewBox="0 0 16 16"
                  className={cn("size-4 transition-transform duration-(--duration-base) ease-standard", open && "rotate-180")}
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="m4 6 4 4 4-4" />
                </svg>
              </button>
              {/* อยู่ใน DOM เสมอให้ aria-controls ชี้ถึง ซ่อนด้วย hidden ตอนปิด (เปิดแล้วอนิเมชันเล่นใหม่) */}
                <div
                  id={panelId}
                  hidden={!open}
                  className="absolute left-0 top-full z-40 mt-2 w-72 animate-drop-in rounded-lg border border-hairline-strong bg-canvas p-2 shadow-panel"
                >
                  <ul className="space-y-1">
                    {group.links.map((link) => (
                      <li key={link.href}>
                        <Link
                          href={link.href}
                          onClick={() => setOpenId(null)}
                          className="flex min-h-11 flex-col justify-center rounded-md px-3 py-2 text-ink transition-colors duration-(--duration-base) hover:bg-canvas-soft"
                        >
                          <span className="text-body-md font-semibold">{link.label}</span>
                          <span className="text-body-sm text-body">{link.description}</span>
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
            </li>
          );
        })}
      </ul>
      <Link
        href={NAV_CTA.href}
        aria-current={pathname === NAV_CTA.href ? "page" : undefined}
        className={buttonVariants({ variant: "primary" })}
      >
        {NAV_CTA.label}
      </Link>
    </nav>
  );
}
