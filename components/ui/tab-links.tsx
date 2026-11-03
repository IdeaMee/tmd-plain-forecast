import Link from "next/link";

import { cn } from "@/lib/cn";

export type TabLink = { href: string; label: string; current: boolean };

type TabLinksProps = {
  label: string;
  items: TabLink[];
  // chips = แถบเลื่อนแนวนอนบนมือถือ (ชิปภาค)
  scroll?: boolean;
  className?: string;
};

// แท็บแบบลิงก์ (ไม่ต้องใช้ JavaScript ฝั่งเบราว์เซอร์) ตัวที่เลือกใช้พื้นดำ ไม่พึ่งแค่เส้นขอบ (design-system หัวข้อ 6)
export function TabLinks({ label, items, scroll = false, className }: TabLinksProps) {
  return (
    <nav aria-label={label} className={cn(scroll && "-mx-4 overflow-x-auto px-4 sm:mx-0 sm:px-0", className)}>
      <ul className={cn("flex gap-2", scroll ? "w-max sm:w-auto sm:flex-wrap" : "flex-wrap")}>
        {items.map((item) => (
          <li key={item.href} className="shrink-0">
            <Link
              href={item.href}
              aria-current={item.current ? "page" : undefined}
              className={cn(
                "inline-flex min-h-10 items-center rounded-md px-4 text-button whitespace-nowrap pointer-coarse:min-h-11",
                item.current
                  ? "bg-primary text-on-primary"
                  : "border border-hairline-strong bg-surface-card text-ink hover:bg-canvas-soft",
              )}
            >
              {item.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
