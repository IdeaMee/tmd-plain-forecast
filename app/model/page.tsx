import type { Metadata } from "next";

import {
  DataSection,
  EvaluationSection,
  KnnSection,
  LearningCurveSection,
  LimitsSection,
  NaiveBayesSection,
  PipelineSection,
  TokensSection,
  TopWordsSection,
} from "@/app/model/_components/sections";
import { Disclaimer } from "@/components/features/disclaimer";
import { Container } from "@/components/layout/container";
import { PageTransition } from "@/components/layout/page-transition";
import { pct } from "@/app/model/_components/charts";
import { getSentenceRoleReport } from "@/lib/data/model-report";

export const metadata: Metadata = {
  title: "โมเดลทำงานอย่างไร | สรุปพยากรณ์อากาศแบบอ่านง่าย",
  description:
    "ภาพผลการฝึกตัวจัดประเภทประโยค (Naive Bayes และ k-NN ที่เขียนเอง) ของเว็บสรุปพยากรณ์อากาศ: ข้อมูล วิธีตัดสิน ผลวัด และจุดที่พลาด",
};

// หน้า /model (Phase 8.2): อธิบายส่วน ML ด้วยวิธีพื้นฐานของรายวิชา ตัวเลขทั้งหมดจาก lib/generated/model-report.json
export default function ModelPage() {
  const report = getSentenceRoleReport();
  const chosen = report.results.find((r) => r.name === report.chosen);
  return (
    <PageTransition>
      <main>
        <Container className="space-y-12 py-8 lg:py-12">
          <div className="max-w-prose animate-enter-up space-y-3">
            <h1 className="text-display-md sm:text-display-lg">โมเดลทำงานอย่างไร</h1>
            <p className="text-body-md text-ink">
              เว็บนี้ใช้การเรียนรู้ของเครื่องในขั้นเดียว: จัดประเภทหน่วยประโยคในประกาศว่าเป็น สภาพอากาศ สาเหตุ คำแนะนำ หรืออื่นๆ
              เพื่อหยิบคำแนะนำไปไว้ในการ์ดของแต่ละภาค ใช้ {report.chosen} ที่เขียนเอง
              {chosen ? ` ได้ความแม่น ${pct(chosen.test_new)} บนถ้อยคำใหม่ในชุดทดสอบ` : ""}
            </p>
            <Disclaimer />
          </div>
          <PipelineSection report={report} />
          <DataSection report={report} />
          <TokensSection report={report} />
          <TopWordsSection report={report} />
          <NaiveBayesSection report={report} />
          <KnnSection report={report} />
          <EvaluationSection report={report} />
          <LearningCurveSection report={report} />
          <LimitsSection report={report} />
        </Container>
      </main>
    </PageTransition>
  );
}
