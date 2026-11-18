import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps } from "react";

import { cn } from "@/lib/cn";

// button-primary / button-secondary / button-tertiary-text ของ DESIGN-expo · สูง 40px บนเมาส์ 44px บนจอสัมผัส (D4)
// v2 (D13): เปลี่ยนสีพื้นนุ่มขึ้น และยุบเล็กน้อยตอนกด (เคลื่อนแค่ transform)
export const buttonVariants = cva(
  "inline-flex min-h-10 items-center justify-center gap-2 rounded-md text-button transition-[background-color,transform] duration-(--duration-base) ease-standard active:scale-[0.98] pointer-coarse:min-h-11",
  {
    variants: {
      variant: {
        primary: "bg-primary px-4.5 text-on-primary hover:bg-primary-active",
        secondary: "border border-hairline-strong bg-surface-card px-4 text-ink hover:bg-canvas-soft",
        text: "px-1 text-text-link underline-offset-4 hover:underline active:scale-100",
      },
    },
    defaultVariants: { variant: "primary" },
  },
);

type ButtonProps = ComponentProps<"button"> & VariantProps<typeof buttonVariants>;

export function Button({ className, variant, type = "button", ...props }: ButtonProps) {
  return <button type={type} className={cn(buttonVariants({ variant }), className)} {...props} />;
}
