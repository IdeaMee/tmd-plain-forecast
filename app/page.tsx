import { Suspense } from "react";

import { ForecastView } from "@/app/_components/forecast-view";
import { ForecastViewSkeleton } from "@/app/_components/forecast-view-skeleton";
import { Container } from "@/components/layout/container";
import { Hero } from "@/components/layout/hero";
import { PageTransition } from "@/components/layout/page-transition";
import { Disclaimer } from "@/components/features/disclaimer";

// หน้า / : แถบ hero และมุมมองพยากรณ์ (อ่าน query string จึงอยู่ใน Suspense ตาม Cache Components)
// สถานะกำลังโหลด = fallback ของ Suspense (เปลือกหน้าแสดงทันที) แทน loading.tsx ที่จะแทนทั้งหน้า
export default function Home({ searchParams }: PageProps<"/">) {
  return (
    <PageTransition>
      <main>
        <Hero />
        <Container className="space-y-6 pt-8">
          <Disclaimer />
          <Suspense fallback={<ForecastViewSkeleton />}>
            <ForecastView searchParams={searchParams} />
          </Suspense>
        </Container>
      </main>
    </PageTransition>
  );
}
