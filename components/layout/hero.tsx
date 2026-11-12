import Link from "next/link";
import type { CSSProperties } from "react";

import { buttonVariants } from "@/components/ui/button";
import { Container } from "@/components/layout/container";

// hero-band แบบกระชับ (design-system ข้อ D7): พื้นไล่สีท้องฟ้าเฉพาะแถบนี้ ข้อความ ink เท่านั้น ไม่มี mockup
export function Hero() {
  return (
    <section className="bg-linear-to-b from-gradient-sky-light to-canvas">
      {/* ข้อความเข้าทีละบรรทัด (เหลื่อมเวลา D13) */}
      <Container className="py-12 lg:py-16">
        <h1 className="animate-enter-up text-display-mega-mobile sm:text-display-xl">สรุปพยากรณ์อากาศแบบอ่านง่าย</h1>
        <p className="mt-3 max-w-prose animate-enter-up text-body-md text-ink stagger" style={{ "--i": 1 } as CSSProperties}>
          พยากรณ์รายวันและ 7 วันของกรมอุตุนิยมวิทยา เขียนใหม่เป็นภาษาไทยง่ายๆ แยกตามภาค
        </p>
        <div className="mt-6 animate-enter-up stagger" style={{ "--i": 2 } as CSSProperties}>
          <Link href="/demo" className={buttonVariants({ variant: "primary" })}>
            ลองอัปโหลด PDF พยากรณ์
          </Link>
        </div>
      </Container>
    </section>
  );
}
