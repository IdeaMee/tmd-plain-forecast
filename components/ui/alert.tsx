import type { ComponentProps, ReactNode } from "react";

import { cn } from "@/lib/cn";

type AlertProps = ComponentProps<"div"> & {
  icon?: ReactNode;
  tone?: "info" | "warning";
};

// มาตรฐานไม่มี Alert: สร้างจากโทเคนเดิม ข้อความเป็น ink เสมอ สีใช้แค่แถบ/ไอคอน (D6, D10)
export function Alert({ className, icon, tone = "info", children, ...props }: AlertProps) {
  return (
    <div
      className={cn(
        "flex gap-3 rounded-md border border-hairline-strong bg-canvas-soft p-4 text-body-md text-ink",
        tone === "warning" && "border-l-4 border-l-accent-warning bg-canvas",
        className,
      )}
      {...props}
    >
      {icon ? <span className="mt-0.5 shrink-0" aria-hidden="true">{icon}</span> : null}
      <div className="min-w-0">{children}</div>
    </div>
  );
}
