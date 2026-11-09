import { Skeleton } from "@/components/ui/skeleton";

// ระหว่างโหลดมุมมองพยากรณ์: โครงเดียวกับของจริง (แท็บชนิด, ชิปภาค, การ์ด) การ์ดจริงเข้าแบบเหลื่อมเวลาแทนที่ (D13)
export function ForecastViewSkeleton() {
  return (
    <div className="space-y-6" role="status" aria-label="กำลังโหลดพยากรณ์">
      <div className="space-y-3">
        <Skeleton className="h-12 w-full max-w-100 rounded-lg" />
        <div className="flex gap-2 overflow-hidden">
          {Array.from({ length: 5 }, (_, i) => (
            <Skeleton key={i} className="h-10 w-24 shrink-0" />
          ))}
        </div>
      </div>
      <Skeleton className="h-5 w-72" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }, (_, i) => (
          <Skeleton key={i} className="h-64 rounded-lg" />
        ))}
      </div>
    </div>
  );
}
