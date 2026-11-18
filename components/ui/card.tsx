import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps } from "react";

import { cn } from "@/lib/cn";

// feature-card ของ DESIGN-expo: รัศมี lg 12px, padding 24px, เส้นขอบ hairline-strong, เงาเฉพาะตอนโฮเวอร์
// lift (v2 แนวทาง A, D13): โฮเวอร์แล้วยกขึ้น 2px เงาจางเข้า เงาอยู่ใน ::after จึงเปลี่ยนแค่ opacity
export const cardVariants = cva("rounded-lg border border-hairline-strong bg-surface-card p-6", {
  variants: {
    motion: {
      none: "",
      lift: "relative transition-transform duration-(--duration-base) ease-standard after:pointer-events-none after:absolute after:-inset-px after:rounded-[inherit] after:opacity-0 after:shadow-card-hover after:transition-opacity after:duration-(--duration-base) hover:-translate-y-0.5 hover:after:opacity-100",
    },
  },
  defaultVariants: { motion: "none" },
});

type CardProps = ComponentProps<"article"> & VariantProps<typeof cardVariants>;

export function Card({ className, motion, ...props }: CardProps) {
  return <article className={cn(cardVariants({ motion }), className)} {...props} />;
}
