import { Skeleton } from "@/components/ui/skeleton";

// ระหว่างโหลดหน้าสรุปรายสัปดาห์: โครงเดียวกับของจริง (บรรทัดสถานะ ตัวเลือกสัปดาห์ ชิปภาค การ์ดภาพรวม การ์ดภาค)
export function SummariesSkeleton() {
  return (
    <div className="space-y-6" role="status" aria-label="กำลังโหลดสรุปรายสัปดาห์">
      <Skeleton className="h-5 w-72" />
      <Skeleton className="h-11 rounded-lg" />
      <div className="flex gap-2 overflow-hidden">
        {Array.from({ length: 6 }, (_, i) => (
          <Skeleton key={i} className="h-10 w-24 shrink-0" />
        ))}
      </div>
      <Skeleton className="h-40 rounded-lg" />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 3 }, (_, i) => (
          <Skeleton key={i} className="h-72 rounded-lg" />
        ))}
      </div>
    </div>
  );
}
