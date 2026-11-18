import Link from "next/link";

import { cn } from "@/lib/cn";

// shortLabel: ป้ายสั้นที่เห็นบนจอแคบ (segmented) ชื่อเต็มยังอยู่สำหรับโปรแกรมอ่านจอ
export type TabLink = { href: string; label: string; current: boolean; shortLabel?: string };

type TabLinksProps = {
  label: string;
  items: TabLink[];
  // segmented = ตัวเลือกชนิด (พื้นเทา ก้อนดำที่ตัวเลือก) · chips = ชิปภาค (เลื่อนแนวนอนบนมือถือ)
  variant?: "segmented" | "chips";
  className?: string;
};

function CheckIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 16 16"
      className="size-4 shrink-0 animate-fade-in"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3.5 8.5 6.5 11.5 12.5 4.5" />
    </svg>
  );
}

// แท็บแบบลิงก์ (ไม่ต้องใช้ JavaScript ฝั่งเบราว์เซอร์) ตัวที่เลือก = พื้นดำ + ตัวหนา/เครื่องหมายถูก + aria-current
// ไม่พึ่งสีอย่างเดียว (design-system หัวข้อ 6) · อนิเมชัน pop/fade ตอนถูกเลือก (D13)
export function TabLinks({ label, items, variant = "chips", className }: TabLinksProps) {
  if (variant === "segmented") {
    return (
      <nav aria-label={label} className={className}>
        <ul className="grid w-full max-w-100 auto-cols-fr grid-flow-col gap-1 rounded-lg bg-surface-strong p-1">
          {items.map((item) => (
            <li key={item.href} className="min-w-0">
              <Link
                href={item.href}
                aria-current={item.current ? "page" : undefined}
                className={cn(
                  "flex min-h-10 items-center justify-center rounded-md px-3 text-center text-button whitespace-nowrap transition-colors duration-(--duration-base) ease-standard pointer-coarse:min-h-11",
                  item.current
                    ? "animate-pop bg-primary font-semibold text-on-primary"
                    : "text-ink hover:bg-canvas",
                )}
              >
                {item.shortLabel ? (
                  // จอแคบกว่า sm: เห็นป้ายสั้น ไม่ตัดคำกลางบรรทัด ชื่อเต็มเป็น sr-only
                  <>
                    <span aria-hidden="true" className="sm:hidden">
                      {item.shortLabel}
                    </span>
                    <span className="max-sm:sr-only">{item.label}</span>
                  </>
                ) : (
                  item.label
                )}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    );
  }
  return (
    <nav aria-label={label} className={cn("-mx-4 overflow-x-auto px-4 py-1 sm:mx-0 sm:px-0", className)}>
      <ul className="flex w-max gap-2 sm:w-auto sm:flex-wrap">
        {items.map((item) => (
          <li key={item.href} className="shrink-0">
            <Link
              href={item.href}
              aria-current={item.current ? "page" : undefined}
              className={cn(
                "inline-flex min-h-10 items-center gap-1.5 rounded-md border px-4 text-button whitespace-nowrap transition-colors duration-(--duration-base) ease-standard pointer-coarse:min-h-11",
                item.current
                  ? "animate-pop border-primary bg-primary text-on-primary"
                  : "border-hairline-strong bg-surface-card text-ink hover:bg-canvas-soft",
              )}
            >
              {item.current ? <CheckIcon /> : null}
              {item.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
