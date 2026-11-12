import Link from "next/link";

import { Container } from "@/components/layout/container";
import { DesktopMenu } from "@/components/layout/desktop-menu";
import { MobileMenu } from "@/components/layout/mobile-menu";

// top-nav ของ DESIGN-expo สูง 64px · ต่ำกว่า 1024 px เป็นเมนูแผงเต็มกว้าง (V10: 7 รายการไม่พอที่ 768)
// ชื่อ view transition "site-header" ให้ Header อยู่นิ่งตอนเปลี่ยนหน้า (globals.css)
export function Header() {
  return (
    <header className="relative z-30 border-b border-hairline bg-canvas [view-transition-name:site-header]">
      <Container className="flex min-h-16 items-center justify-between gap-4">
        <Link href="/" className="inline-flex min-h-11 items-center rounded-md text-title-sm text-ink">
          สรุปพยากรณ์อ่านง่าย
        </Link>
        <div className="hidden lg:block">
          <DesktopMenu />
        </div>
        <div className="lg:hidden">
          <MobileMenu />
        </div>
      </Container>
    </header>
  );
}
