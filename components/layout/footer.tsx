import Link from "next/link";

import { Container } from "@/components/layout/container";
import { Disclaimer } from "@/components/features/disclaimer";
import { NAV_CTA, NAV_GROUPS } from "@/lib/nav";

const footerLink =
  "inline-flex min-h-11 items-center text-body-sm text-ink underline underline-offset-4 hover:decoration-2";

// footer-light ของ DESIGN-expo (body-sm สี body) + ลิงก์เมนูชุดเดียวกับ Header (lib/nav.ts) · พื้นขาวเพื่อให้ลิงก์ที่มาสีฟ้าผ่านความต่างสี
export function Footer() {
  return (
    <footer className="mt-12 border-t border-hairline bg-canvas lg:mt-24">
      <Container className="grid gap-8 py-12 md:grid-cols-[2fr_1fr]">
        <div className="space-y-2">
          <Disclaimer />
          <p className="text-body-sm text-body">
            ข้อความสรุปเขียนจากประกาศของกรมอุตุนิยมวิทยาโดยอัตโนมัติ ตัวเลข ชื่อจังหวัด และคำแนะนำคัดจากต้นฉบับ
            ถ้าต้องตัดสินใจเรื่องความปลอดภัย โปรดดูประกาศฉบับเต็มของกรมอุตุนิยมวิทยา
          </p>
          <p className="text-body-sm text-body">โครงงานรายวิชา NLP และ Machine Learning</p>
        </div>
        <nav aria-label="เมนูท้ายหน้า" className="space-y-3">
          {NAV_GROUPS.map((group) => (
            <div key={group.id}>
              <p className="text-title-sm text-ink">{group.label}</p>
              <ul className="flex flex-wrap gap-x-4">
                {group.links.map((link) => (
                  <li key={link.href}>
                    <Link href={link.href} className={footerLink}>
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
          <Link href={NAV_CTA.href} className={footerLink}>
            {NAV_CTA.label}
          </Link>
        </nav>
      </Container>
    </footer>
  );
}
