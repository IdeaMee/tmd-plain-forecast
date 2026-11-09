import Link from "next/link";

import { Container } from "@/components/layout/container";

const NAV = [
  { href: "/", label: "หน้าหลัก" },
  { href: "/demo", label: "ลองอัปโหลด PDF" },
];

const linkClass =
  "inline-flex min-h-10 items-center rounded-md px-3 text-nav-link text-ink hover:bg-surface-strong pointer-coarse:min-h-11";

// top-nav ของ DESIGN-expo สูง 64px · ต่ำกว่า 768px เป็นเมนูพับ (<details> ไม่ต้องใช้ JavaScript)
export function Header() {
  return (
    <header className="border-b border-hairline bg-canvas">
      <Container className="flex min-h-16 items-center justify-between gap-4">
        <Link href="/" className="inline-flex min-h-11 items-center rounded-md text-title-sm text-ink">
          สรุปพยากรณ์อ่านง่าย
        </Link>
        <nav aria-label="เมนูหลัก" className="hidden md:block">
          <ul className="flex gap-1">
            {NAV.map((item) => (
              <li key={item.href}>
                <Link href={item.href} className={linkClass}>
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <details className="group relative md:hidden">
          <summary
            className="flex min-h-11 min-w-11 cursor-pointer list-none items-center justify-center rounded-md text-ink hover:bg-surface-strong [&::-webkit-details-marker]:hidden"
            aria-label="เปิดเมนู"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </summary>
          <nav
            aria-label="เมนูหลัก"
            className="absolute right-0 z-10 mt-2 w-56 rounded-lg border border-hairline-strong bg-canvas p-2 shadow-card-hover"
          >
            <ul className="flex flex-col gap-1">
              {NAV.map((item) => (
                <li key={item.href}>
                  <Link href={item.href} className={`${linkClass} w-full`}>
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </details>
      </Container>
    </header>
  );
}
