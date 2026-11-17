import type { Metadata } from "next";

import { pct } from "@/app/model/_components/charts";
import { ModelView } from "@/app/model/_components/model-view";
import { getModelReport } from "@/lib/data/model-report";

export const metadata: Metadata = {
  title: "โมเดลของประกาศเตือนภัย | สรุปพยากรณ์อากาศแบบอ่านง่าย",
  description:
    "ผลการฝึกตัวจัดประเภทท่อนของประกาศเตือนภัย (Naive Bayes และ k-NN ที่เขียนเอง) เทียบกฎคำสำคัญและตัวของพยากรณ์รายวัน",
};

// แท็บที่สองของ /model (Phase 11.3): ตัวจัดประเภทที่ฝึกจากประกาศเตือนภัย ตัวเลขทั้งหมดจาก lib/generated/model-report.json
export default function WarningModelPage() {
  const report = getModelReport("warning-role");
  const chosen = report.results.find((r) => r.name === report.chosen);
  // ตัวของรายวันเป็นวิธีเทียบเพิ่ม: มีในตารางผลวัดแต่ไม่มีตารางสับสน (model_report.build_report)
  const daily = report.results.find((r) => !report.confusion.some((c) => c.name === r.name));
  return (
    <ModelView
      report={report}
      intro={
        <>
          ประกาศเตือนภัยใช้ตัวจัดประเภทของตัวเอง: จัดแต่ละท่อนของเนื้อหาว่าเป็น สภาพอากาศ สาเหตุ หรือคำแนะนำ
          ท่อนที่เป็นคำแนะนำไปเป็นข้อควรระวังของประกาศ (คัดคำต่อคำ) ใช้ {report.chosen} ที่เขียนเอง
          {chosen ? ` ได้ความแม่น ${pct(chosen.test_new)} บนถ้อยคำใหม่ในชุดทดสอบ` : ""}
          {daily ? ` (ตัวของพยากรณ์รายวันที่ไม่ได้ฝึกใหม่ได้ ${pct(daily.test_new)})` : ""}
        </>
      }
    />
  );
}
