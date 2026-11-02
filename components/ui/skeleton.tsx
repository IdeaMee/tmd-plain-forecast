import type { ComponentProps } from "react";

import { cn } from "@/lib/cn";

// ตัวแทนตอนโหลด (มาตรฐานไม่มี) พื้น surface-strong ไม่มีข้อความให้อ่าน
export function Skeleton({ className, ...props }: ComponentProps<"div">) {
  return <div aria-hidden="true" className={cn("animate-pulse rounded-md bg-surface-strong", className)} {...props} />;
}
