import { ViewTransition, type ReactNode } from "react";

// ทรานสิชันเปลี่ยนหน้า (React <ViewTransition> + View Transitions API ของเบราว์เซอร์, ดู node_modules/next/dist/docs/01-app/02-guides/view-transitions.md)
// ใส่ในแต่ละ page.tsx ไม่ใช่ layout เพราะ layout ไม่ถูกถอด enter/exit จึงไม่ทำงาน
// เนื้อหาเก่าจางออกเร็ว เนื้อหาใหม่จางเข้าพร้อมเลื่อนขึ้นเล็กน้อย (CSS ใน globals.css) · เบราว์เซอร์ที่ไม่รองรับเปลี่ยนหน้าปกติ
// default="none": เปลี่ยน query ในหน้าเดียวกัน (แท็บ/ภาค) ไม่เล่นทรานสิชันหน้า
export function PageTransition({ children }: { children: ReactNode }) {
  return (
    <ViewTransition enter="page-enter" exit="page-exit" default="none">
      {children}
    </ViewTransition>
  );
}
