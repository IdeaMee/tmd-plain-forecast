import type { ComponentProps } from "react";

import { cn } from "@/lib/cn";

// กรอบเนื้อหากว้างสุด 1200px ขอบข้าง 16px มือถือ / 24px ตั้งแต่ 640px
export function Container({ className, ...props }: ComponentProps<"div">) {
  return <div className={cn("mx-auto w-full max-w-content px-4 sm:px-6", className)} {...props} />;
}
