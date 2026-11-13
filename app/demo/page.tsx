import type { Metadata } from "next";

import { UploadForm } from "@/app/demo/_components/upload-form";
import { Container } from "@/components/layout/container";
import { PageTransition } from "@/components/layout/page-transition";
import { Disclaimer } from "@/components/features/disclaimer";

export const metadata: Metadata = {
  title: "ลองอัปโหลด PDF พยากรณ์ | สรุปพยากรณ์อากาศแบบอ่านง่าย",
  description: "อัปโหลด PDF พยากรณ์รายวันหรือ 7 วันของกรมอุตุนิยมวิทยา แล้วดูสรุปภาษาง่ายแยก 7 ภาค (ไม่เก็บไฟล์)",
};

// หน้า /demo: เปลือกหน้าเป็น Server Component มีแค่ฟอร์มอัปโหลดที่เป็น Client Component
export default function DemoPage() {
  return (
    <PageTransition>
      <main>
        <Container className="space-y-6 py-8 lg:py-12">
          <div className="space-y-3">
            <h1 className="text-display-md sm:text-display-lg">ลองอัปโหลด PDF พยากรณ์</h1>
            <p className="max-w-prose text-body-md text-ink">
              เลือกไฟล์ PDF พยากรณ์อากาศรายวันหรือพยากรณ์ 7 วันที่ดาวน์โหลดจากเว็บไซต์กรมอุตุนิยมวิทยา
              ระบบจะสรุปเป็นภาษาไทยง่ายๆ แยก 7 ภาคด้วยวิธีเดียวกับหน้าหลัก และแสดงทีละขั้นว่าระบบทำอะไรกับไฟล์
              เอกสารชนิดอื่นของกรมจะแสดงแบบโหมดทั่วไป (ข้อความต้นฉบับพร้อมป้ายประเภทประโยค ไม่เขียนใหม่)
            </p>
            <Disclaimer />
            <ul className="max-w-prose list-disc space-y-1 pl-5 text-body-md text-ink">
              <li>ไม่เก็บไฟล์ที่อัปโหลดและไม่เก็บผลสรุป</li>
              <li>รับเฉพาะไฟล์ PDF ไม่เกิน 4 MB</li>
              <li>ผลจาก PDF อาจแม่นน้อยกว่าผลบนหน้าหลัก เพราะข้อความใน PDF อาจเพี้ยน</li>
            </ul>
          </div>
          <UploadForm />
        </Container>
      </main>
    </PageTransition>
  );
}
