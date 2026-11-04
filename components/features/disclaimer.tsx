import { cn } from "@/lib/cn";

type DisclaimerProps = { className?: string };

// ต้องแสดงทุกหน้าที่มีสรุป (สเปกหัวข้อ 4 ข้อ 6)
export function Disclaimer({ className }: DisclaimerProps) {
  return (
    <p className={cn("text-body-sm text-ink", className)}>
      ตัวช่วยสรุป ไม่ใช่ประกาศทางการ · ที่มา:{" "}
      <a href="https://www.tmd.go.th" className="text-text-link underline underline-offset-4" rel="noreferrer">
        กรมอุตุนิยมวิทยา
      </a>
    </p>
  );
}
