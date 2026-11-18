import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps } from "react";

import { cn } from "@/lib/cn";

// badge-pill ของ DESIGN-expo (ป้ายสถานะเท่านั้น ไม่ใช่ปุ่ม) · caption 13px น้ำหนัก 600 ไม่ตัวพิมพ์ใหญ่ (D2)
// v2 แนวทาง A: พื้นขาวเส้นขอบ hairline-strong · sample = เส้นประ ใช้กับข้อมูลตัวอย่าง/สมมติ
export const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-pill px-2.5 py-0.5 text-caption font-semibold whitespace-nowrap text-ink",
  {
    variants: {
      variant: {
        default: "border border-hairline-strong bg-canvas",
        muted: "bg-surface-strong",
        sample: "border border-dashed border-ink bg-canvas",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

type BadgeProps = ComponentProps<"span"> & VariantProps<typeof badgeVariants>;

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
