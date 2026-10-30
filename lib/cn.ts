// รวมคลาส Tailwind (clsx + tailwind-merge) ให้รู้จักชื่อขนาดตัวอักษรของ DESIGN-expo
// ไม่งั้น text-body-md (ขนาด) กับ text-ink (สี) จะถูกมองว่าชนกันแล้วตัดทิ้ง
import { clsx, type ClassValue } from "clsx";
import { extendTailwindMerge } from "tailwind-merge";

const FONT_SIZES = [
  "display-mega",
  "display-mega-mobile",
  "display-xl",
  "display-lg",
  "display-md",
  "display-sm",
  "title-md",
  "title-sm",
  "body-md",
  "body-sm",
  "caption",
  "button",
  "nav-link",
];

const twMerge = extendTailwindMerge({
  extend: { classGroups: { "font-size": [{ text: FONT_SIZES }] } },
});

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
