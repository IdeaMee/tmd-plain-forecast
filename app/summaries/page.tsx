import type { Metadata } from "next";
import { Suspense } from "react";

import { SummariesSkeleton } from "@/app/summaries/_components/summaries-skeleton";
import { SummariesView } from "@/app/summaries/_components/summaries-view";
import { Disclaimer } from "@/components/features/disclaimer";
import { Container } from "@/components/layout/container";
import { PageTransition } from "@/components/layout/page-transition";

export const metadata: Metadata = {
  title: "สรุปสภาพอากาศรายสัปดาห์ | สรุปพยากรณ์อากาศแบบอ่านง่าย",
  description:
    "สรุปสภาพอากาศรายสัปดาห์ของกรมอุตุนิยมวิทยา แยกตามภาค พร้อมค่าฝนสูงสุด อุณหภูมิสูงสุดและต่ำสุดตามตารางต้นฉบับ ข้อความคัดคำต่อคำ ดูย้อนหลังได้ทุกสัปดาห์ที่เก็บไว้",
};

// หน้า /summaries (Phase 11.5): อ่าน query string จึงอยู่ใน Suspense ตาม Cache Components (แบบเดียวกับหน้า / และ /warnings)
export default function SummariesPage({ searchParams }: PageProps<"/summaries">) {
  return (
    <PageTransition>
      <main>
        <Container className="space-y-6 py-8 lg:py-12">
          <div className="max-w-prose animate-enter-up space-y-3">
            <h1 className="text-display-md sm:text-display-lg">สรุปสภาพอากาศรายสัปดาห์</h1>
            <p className="text-body-md text-ink">
              สรุปสิ่งที่เกิดขึ้นจริงในแต่ละสัปดาห์ แยกตามภาค พร้อมค่าฝนสูงสุด อุณหภูมิสูงสุดและต่ำสุดตามตารางของกรมอุตุนิยมวิทยา
              ข้อความและตัวเลขคัดจากต้นฉบับคำต่อคำ
            </p>
            <Disclaimer />
          </div>
          <Suspense fallback={<SummariesSkeleton />}>
            <SummariesView searchParams={searchParams} />
          </Suspense>
        </Container>
      </main>
    </PageTransition>
  );
}
