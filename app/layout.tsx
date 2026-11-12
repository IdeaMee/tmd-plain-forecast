import type { Metadata } from "next";
import { Anuphan } from "next/font/google";
import { Footer } from "@/components/layout/footer";
import { Header } from "@/components/layout/header";

import "./globals.css";

// ฟอนต์เดียวทั้งแอป (แทน Inter ของ DESIGN-expo.md ตาม docs/spec/design-system.md ข้อ D1); ไม่ระบุ weight = ฟอนต์ตัวแปร
const anuphan = Anuphan({
  subsets: ["thai", "latin"],
  variable: "--font-anuphan",
  display: "swap",
});

export const metadata: Metadata = {
  title: "สรุปพยากรณ์อากาศแบบอ่านง่าย",
  description:
    "สรุปพยากรณ์อากาศรายวันและ 7 วันของกรมอุตุนิยมวิทยาเป็นภาษาไทยง่ายๆ แยกตามภาค (ตัวช่วยสรุป ไม่ใช่ประกาศทางการ)",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="th" className={anuphan.variable}>
      <body>
        {/* ส่วนหัว/ส่วนท้ายอยู่ที่ layout เพื่อให้หน้าผิดพลาด (error.tsx) ยังมีเมนูและข้อความสงวนสิทธิ์ */}
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  );
}
