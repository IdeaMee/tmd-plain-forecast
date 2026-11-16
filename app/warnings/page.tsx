import type { Metadata } from "next";
import { Suspense } from "react";

import { WarningsSkeleton } from "@/app/warnings/_components/warnings-skeleton";
import { WarningsView } from "@/app/warnings/_components/warnings-view";
import { Disclaimer } from "@/components/features/disclaimer";
import { Container } from "@/components/layout/container";
import { PageTransition } from "@/components/layout/page-transition";

export const metadata: Metadata = {
  title: "ประกาศเตือนภัย | สรุปพยากรณ์อากาศแบบอ่านง่าย",
  description:
    "ประกาศเตือนภัยลักษณะอากาศของกรมอุตุนิยมวิทยา แสดงฉบับล่าสุด ฉบับต่อเนื่องของเหตุการณ์เดียวกัน และประกาศย้อนหลัง ข้อความคัดจากต้นฉบับคำต่อคำ",
};

// หน้า /warnings (Phase 11.4): อ่าน query string จึงอยู่ใน Suspense ตาม Cache Components (แบบเดียวกับหน้า /)
export default function WarningsPage({ searchParams }: PageProps<"/warnings">) {
  return (
    <PageTransition>
      <main>
        <Container className="space-y-6 py-8 lg:py-12">
          <div className="max-w-prose animate-enter-up space-y-3">
            <h1 className="text-display-md sm:text-display-lg">ประกาศเตือนภัย</h1>
            <p className="text-body-md text-ink">
              ประกาศเตือนภัยลักษณะอากาศของกรมอุตุนิยมวิทยา ประกาศหนึ่งเรื่องออกได้หลายฉบับ ระบบจัดฉบับของเรื่องเดียวกันไว้ด้วยกัน
            </p>
            <Disclaimer />
          </div>
          <Suspense fallback={<WarningsSkeleton />}>
            <WarningsView searchParams={searchParams} />
          </Suspense>
        </Container>
      </main>
    </PageTransition>
  );
}
