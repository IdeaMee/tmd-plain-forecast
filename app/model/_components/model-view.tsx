// เนื้อหาของหน้า /model ใช้ร่วมกันสองแท็บ (ประโยคของรายวัน/7 วัน และท่อนของประกาศเตือนภัย, 11.3)
// ทุกตัวเลขมาจาก lib/generated/model-report.json ผ่าน lib/data/model-report.ts
import type { ReactNode } from "react";

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
import { TabLinks } from "@/components/ui/tab-links";
import type { ModelReportId, SentenceRoleReport } from "@/lib/contract/model-report";

const TABS: { id: ModelReportId; href: string; label: string; shortLabel: string }[] = [
  { id: "sentence-role", href: "/model", label: "พยากรณ์รายวัน/7 วัน", shortLabel: "พยากรณ์" },
  { id: "warning-role", href: "/model/warning", label: "ประกาศเตือนภัย", shortLabel: "เตือนภัย" },
];

type ModelViewProps = {
  report: SentenceRoleReport;
  // ย่อหน้าแนะนำของแท็บนั้น (หน้าที่ของโมเดลต่างกัน)
  intro: ReactNode;
};

export function ModelView({ report, intro }: ModelViewProps) {
  return (
    <PageTransition>
      <main>
        <Container className="space-y-12 py-8 lg:py-12">
          <div className="max-w-prose animate-enter-up space-y-4">
            <h1 className="text-display-md sm:text-display-lg">โมเดลทำงานอย่างไร</h1>
            <TabLinks
              label="เลือกโมเดล"
              variant="segmented"
              items={TABS.map((t) => ({
                href: t.href,
                label: t.label,
                shortLabel: t.shortLabel,
                current: t.id === report.id,
              }))}
            />
            <h2 className="text-title-md">{report.title_th}</h2>
            <p className="text-body-md text-ink">{intro}</p>
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
