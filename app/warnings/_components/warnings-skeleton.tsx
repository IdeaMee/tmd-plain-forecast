import { Skeleton } from "@/components/ui/skeleton";

// ระหว่างโหลดหน้าเตือนภัย: โครงเดียวกับของจริง (บรรทัดสถานะ ชิปฉบับ การ์ดประกาศ) ของจริงเข้าแทนที่ด้วยอนิเมชันเข้า
export function WarningsSkeleton() {
  return (
    <div className="space-y-6" role="status" aria-label="กำลังโหลดประกาศเตือนภัย">
      <Skeleton className="h-5 w-72" />
      <div className="flex gap-2 overflow-hidden">
        {Array.from({ length: 6 }, (_, i) => (
          <Skeleton key={i} className="h-10 w-24 shrink-0" />
        ))}
      </div>
      <Skeleton className="h-96 rounded-lg" />
    </div>
  );
}
