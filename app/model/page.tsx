import type { Metadata } from "next";

import { pct } from "@/app/model/_components/charts";
import { ModelView } from "@/app/model/_components/model-view";
import { getModelReport } from "@/lib/data/model-report";

export const metadata: Metadata = {
  title: "โมเดลทำงานอย่างไร | สรุปพยากรณ์อากาศแบบอ่านง่าย",
  description:
    "ภาพผลการฝึกตัวจัดประเภทประโยค (Naive Bayes และ k-NN ที่เขียนเอง) ของเว็บสรุปพยากรณ์อากาศ: ข้อมูล วิธีตัดสิน ผลวัด และจุดที่พลาด",
};

// หน้า /model (Phase 8.2): อธิบายส่วน ML ด้วยวิธีพื้นฐานของรายวิชา ตัวเลขทั้งหมดจาก lib/generated/model-report.json
// แท็บประกาศเตือนภัยอยู่ที่ /model/warning (11.3)
export default function ModelPage() {
  const report = getModelReport("sentence-role");
  const chosen = report.results.find((r) => r.name === report.chosen);
  return (
    <ModelView
      report={report}
      intro={
        <>
          เว็บนี้ใช้การเรียนรู้ของเครื่องในขั้นเดียว: จัดประเภทหน่วยประโยคในประกาศว่าเป็น สภาพอากาศ สาเหตุ คำแนะนำ หรืออื่นๆ
          เพื่อหยิบคำแนะนำไปไว้ในการ์ดของแต่ละภาค ใช้ {report.chosen} ที่เขียนเอง
          {chosen ? ` ได้ความแม่น ${pct(chosen.test_new)} บนถ้อยคำใหม่ในชุดทดสอบ` : ""}
        </>
      }
    />
  );
}
