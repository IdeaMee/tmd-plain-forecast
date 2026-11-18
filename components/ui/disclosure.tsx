import type { ReactNode } from "react";

import { cn } from "@/lib/cn";

type DisclosureProps = {
  summary: ReactNode;
  children: ReactNode;
  className?: string;
  // เปิดไว้ตั้งแต่แรก (เช่น ผู้ใช้เลือกเดือนย้อนหลังแล้วหน้าโหลดใหม่ ต้องเห็นรายการที่เลือกต่อ)
  defaultOpen?: boolean;
};

// กล่องเปิด-ปิดด้วย <details> (ใช้ได้โดยไม่มี JavaScript) · v2 แนวทาง A: ลูกศรหมุน เนื้อหาเลื่อนลงจางเข้า (D13)
export function Disclosure({ summary, children, className, defaultOpen = false }: DisclosureProps) {
  return (
    <details open={defaultOpen} className={cn("group rounded-lg border border-hairline-strong bg-surface-card", className)}>
      <summary className="flex min-h-11 cursor-pointer list-none items-center gap-3 rounded-lg px-4 py-2 text-button text-ink transition-colors duration-(--duration-base) hover:bg-canvas-soft [&::-webkit-details-marker]:hidden">
        <span className="min-w-0 flex-1">{summary}</span>
        <svg
          aria-hidden="true"
          viewBox="0 0 16 16"
          className="size-4 shrink-0 transition-transform duration-(--duration-base) ease-standard group-open:rotate-180"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="m4 6 4 4 4-4" />
        </svg>
      </summary>
      <div className="animate-drop-in border-t border-hairline px-4 py-4">{children}</div>
    </details>
  );
}
