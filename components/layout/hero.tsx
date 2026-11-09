import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import { Container } from "@/components/layout/container";

// hero-band แบบกระชับ (design-system ข้อ D7): พื้นไล่สีท้องฟ้าเฉพาะแถบนี้ ข้อความ ink เท่านั้น ไม่มี mockup
export function Hero() {
  return (
    <section className="bg-linear-to-b from-gradient-sky-light to-canvas">
      <Container className="py-12 lg:py-16">
        <h1 className="text-display-mega-mobile sm:text-display-xl">สรุปพยากรณ์อากาศแบบอ่านง่าย</h1>
        <p className="mt-3 max-w-prose text-body-md text-ink">
          พยากรณ์รายวันและ 7 วันของกรมอุตุนิยมวิทยา เขียนใหม่เป็นภาษาไทยง่ายๆ แยกตามภาค
        </p>
        <div className="mt-6">
          <Link href="/demo" className={buttonVariants({ variant: "primary" })}>
            ลองอัปโหลด PDF พยากรณ์
          </Link>
        </div>
      </Container>
    </section>
  );
}
