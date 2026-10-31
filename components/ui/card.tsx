import type { ComponentProps } from "react";

import { cn } from "@/lib/cn";

// feature-card ของ DESIGN-expo: รัศมี lg 12px, padding 24px, เส้นขอบ hairline-strong, เงาเฉพาะตอนโฮเวอร์
export function Card({ className, ...props }: ComponentProps<"article">) {
  return (
    <article
      className={cn("rounded-lg border border-hairline-strong bg-surface-card p-6", className)}
      {...props}
    />
  );
}
