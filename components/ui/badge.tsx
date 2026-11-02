import type { ComponentProps } from "react";

import { cn } from "@/lib/cn";

// badge-pill ของ DESIGN-expo (ป้ายสถานะเท่านั้น ไม่ใช่ปุ่ม) · caption 13px น้ำหนัก 600 ไม่ตัวพิมพ์ใหญ่ (D2)
export function Badge({ className, ...props }: ComponentProps<"span">) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-pill bg-surface-strong px-2.5 py-1 text-caption font-semibold text-ink",
        className,
      )}
      {...props}
    />
  );
}
