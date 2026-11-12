// ส่วนต่างๆ ของหน้า /model (Server Components) ทุกตัวเลขมาจาก lib/generated/model-report.json เท่านั้น
import type { CSSProperties, ReactNode } from "react";

import { BarTable, ConfusionMatrix, LineChart, pct } from "@/app/model/_components/charts";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { SentenceRoleReport } from "@/lib/contract/model-report";
import { cn } from "@/lib/cn";

type R = { report: SentenceRoleReport };

const SPLIT_TH: Record<string, string> = { train: "ชุดฝึก", dev: "ชุดปรับค่า (dev)", test: "ชุดทดสอบ", gap: "ช่วงเว้น (ไม่ใช้)" };
const DOC_TH: Record<string, string> = { daily: "พยากรณ์รายวัน", sevenday: "พยากรณ์ 7 วัน", warning: "ประกาศเตือนภัย" };

const th = (report: SentenceRoleReport, label: string) => report.labels_th[label] ?? label;

export function Section({ n, title, lead, children }: { n: number; title: string; lead: ReactNode; children: ReactNode }) {
  return (
    <section
      aria-labelledby={`s${n}`}
      className="animate-enter-up space-y-4 stagger"
      style={{ "--i": Math.min(n, 4) } as CSSProperties}
    >
      <div className="space-y-1">
        <p className="text-body-sm text-body">ส่วนที่ {n}</p>
        <h2 id={`s${n}`} className="text-display-sm">
          {title}
        </h2>
        <div className="max-w-prose text-body-md text-ink">{lead}</div>
      </div>
      {children}
    </section>
  );
}

function Quote({ children }: { children: ReactNode }) {
  return (
    <p className="rounded-md border border-hairline bg-canvas-soft p-4 text-body-md text-ink [overflow-wrap:anywhere]">
      {children}
    </p>
  );
}

function Chips({ items, label, dropped = [] }: { items: string[]; label: string; dropped?: string[] }) {
  const drop = new Set(dropped);
  return (
    <ul className="flex flex-wrap gap-2" aria-label={label}>
      {items.map((t, i) => (
        <li
          key={`${i}-${t}`}
          className={cn(
            "inline-flex min-h-9 items-center rounded-md border px-3 text-body-md text-ink",
            drop.has(t) ? "border-dashed border-body bg-surface-strong text-body" : "border-ink bg-surface-card",
            t === "<num>" && "bg-num-tint",
          )}
        >
          <span className={cn(drop.has(t) && "line-through")}>{t.trim() === "" ? "ช่องว่าง" : t}</span>
          {drop.has(t) ? <span className="sr-only"> (ถูกทิ้ง)</span> : null}
        </li>
      ))}
    </ul>
  );
}

export function PipelineSection({ report }: R) {
  const ml = report.pipeline.filter((s) => s.kind === "ml");
  return (
    <Section
      n={1}
      title="ระบบทำงานกี่ขั้น และขั้นไหนเป็น ML"
      lead={`จากประกาศของกรมอุตุนิยมวิทยาจนเป็นสรุปภาษาง่าย มี ${report.pipeline.length} ขั้น ขั้นที่ใช้การเรียนรู้ของเครื่อง (ML) มี ${ml.length} ขั้น คือ${ml.map((s) => s.title_th).join(" และ ")} ที่เหลือเป็นกฎที่เขียนเอง`}
    >
      <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {report.pipeline.map((step, i) => (
          <li key={step.id}>
            <Card className={cn("h-full space-y-2 p-4", step.kind === "ml" && "border-ink")}>
              <div className="flex items-center gap-2">
                <span className="text-body-sm text-body">{i + 1}</span>
                <Badge variant={step.kind === "ml" ? "default" : "muted"}>{step.kind === "ml" ? "ML" : "กฎ"}</Badge>
              </div>
              <h3 className="text-title-sm">{step.title_th}</h3>
              <p className="text-body-sm text-body">{step.detail_th}</p>
            </Card>
          </li>
        ))}
      </ol>
    </Section>
  );
}

export function DataSection({ report }: R) {
  const total = report.facts.total_units;
  // ทุกชุดใช้สเกลเดียวกัน เทียบขนาดข้ามการ์ดได้
  const max = Math.max(...report.splits.flatMap((s) => Object.values(s.by_label)));
  return (
    <Section
      n={2}
      title="ข้อมูลที่ใช้ฝึกและวัดผล"
      lead={
        <>
          ตัดประกาศเป็นหน่วยประโยคได้ {total} หน่วย แต่ละหน่วยมีป้าย 1 ใน {report.labels.length} แบบ {report.split_note_th}{" "}
          {report.label_source_th}
        </>
      }
    >
      <div className="grid gap-6 lg:grid-cols-2">
        {report.splits.map((split) => (
          <Card key={split.split} className="space-y-2 p-4">
            <h3 className="text-title-sm">
              {SPLIT_TH[split.split] ?? split.split} · {split.total} หน่วย
            </h3>
            <BarTable
              caption={`จำนวนหน่วยต่อป้ายใน${SPLIT_TH[split.split] ?? split.split}`}
              columns={["ป้าย", "จำนวนหน่วย"]}
              max={max}
              rows={report.labels.map((l) => ({
                label: th(report, l),
                value: split.by_label[l] ?? 0,
                display: String(split.by_label[l] ?? 0),
              }))}
            />
          </Card>
        ))}
      </div>
      <p className="text-body-sm text-body">
        แยกตามชนิดเอกสาร:{" "}
        {Object.entries(report.by_doc_type)
          .map(([k, v]) => `${DOC_TH[k] ?? k} ${Object.values(v).reduce((a, b) => a + b, 0)} หน่วย`)
          .join(" · ")}
      </p>
    </Section>
  );
}

export function TokensSection({ report }: R) {
  return (
    <Section
      n={3}
      title="จากประโยคเป็นตัวเลขที่โมเดลอ่านได้"
      lead={
        <>
          ตัดคำด้วย newmm ทิ้งเครื่องหมายและช่องว่าง เปลี่ยนตัวเลขทุกตัวเป็น {report.facts.num_token}{" "}
          แล้วนับว่าคำไหนมากี่ครั้ง (bag of words) ไม่มีการตัดคำที่พบบ่อย (stop word) คลังคำทั้งหมด {report.facts.vocab_all} คำ
        </>
      }
    >
      <div className="space-y-4">
        {report.token_examples.map((ex) => (
          <Card key={ex.unit_id} className="space-y-3">
            <div className="flex flex-wrap items-center gap-2">
              <Badge>{th(report, ex.label)}</Badge>
              <span className="text-body-sm text-body">ตัวอย่างจากชุดฝึก</span>
            </div>
            <Quote>{ex.text}</Quote>
            <p className="text-body-sm text-body">1. ตัดคำ ({ex.tokens.length} ชิ้น) · เส้นประขีดฆ่า = ถูกทิ้ง</p>
            <Chips items={ex.tokens} label="ผลตัดคำ" dropped={ex.dropped} />
            <p className="text-body-sm text-body">2. นับคำที่เหลือ ({ex.kept.length} คำ)</p>
            <ul className="flex flex-wrap gap-2" aria-label="จำนวนครั้งของแต่ละคำ">
              {Object.entries(ex.counts).map(([w, n]) => (
                <li
                  key={w}
                  className={cn(
                    "inline-flex min-h-9 items-center gap-2 rounded-md border border-hairline-strong px-3 text-body-md text-ink",
                    w === report.facts.num_token && "bg-num-tint",
                  )}
                >
                  {w}
                  <span className="font-semibold tabular-nums">×{n}</span>
                </li>
              ))}
            </ul>
          </Card>
        ))}
      </div>
    </Section>
  );
}

export function TopWordsSection({ report }: R) {
  return (
    <Section
      n={4}
      title="คำไหนบอกป้ายไหน"
      lead="Naive Bayes จำว่าแต่ละคำพบบ่อยแค่ไหนในแต่ละป้าย ตารางนี้คือคำที่บอกป้ายนั้นได้ชัดที่สุด (โอกาสพบในป้ายนี้เทียบกับป้ายอื่น คะแนนเป็น log ยิ่งมากยิ่งชัด)"
    >
      <div className="grid gap-4 md:grid-cols-2">
        {report.labels
          .filter((l) => report.top_words[l]?.length)
          .map((l) => {
            const words = report.top_words[l].slice(0, 10);
            return (
              <Card key={l} className="space-y-2 p-4">
                <h3 className="text-title-sm">{th(report, l)}</h3>
                <BarTable
                  caption={`${words.length} คำเด่นของป้าย ${th(report, l)}`}
                  columns={["คำ", "คะแนน"]}
                  rows={words.map((w) => ({
                    label: w.word,
                    value: w.score,
                    display: w.score.toFixed(2),
                  }))}
                />
              </Card>
            );
          })}
      </div>
      {report.labels.includes("other") && report.facts.other_units <= 1 ? (
        <p className="text-body-sm text-body">
          ป้าย &quot;{th(report, "other")}&quot; มีแค่ {report.facts.other_units} หน่วยในข้อมูลทั้งหมด คำเด่นของป้ายนี้จึงแทบไม่มีความหมาย
        </p>
      ) : null}
    </Section>
  );
}

export function NaiveBayesSection({ report }: R) {
  return (
    <Section
      n={5}
      title="Naive Bayes ตัดสินอย่างไร"
      lead="คะแนนของแต่ละป้าย = log ของสัดส่วนป้ายในชุดฝึก + ผลรวม log ความน่าจะเป็นของแต่ละคำในป้ายนั้น ป้ายที่คะแนนสูงสุดชนะ แปลงคะแนนเป็นความน่าจะเป็นรวมเป็น 100% เพื่ออ่านง่าย ตัวอย่างจากชุดทดสอบ (โมเดลไม่เคยเห็น)"
    >
      <div className="grid gap-4 lg:grid-cols-2">
        {report.nb_examples.map((ex) => (
          <Card key={ex.unit_id} className="space-y-3">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant={ex.correct ? "default" : "sample"}>{ex.correct ? "ทายถูก" : "ทายผิด"}</Badge>
              <span className="text-body-sm text-ink">
                ป้ายจริง {th(report, ex.true_label)} · ทาย {th(report, ex.predicted)}
              </span>
            </div>
            <Quote>{ex.text}</Quote>
            <BarTable
              caption="ความน่าจะเป็นของแต่ละป้าย"
              columns={["ป้าย", "ความน่าจะเป็น"]}
              max={1}
              rows={report.labels.map((l) => ({
                label: th(report, l),
                value: ex.posterior[l] ?? 0,
                display: pct(ex.posterior[l] ?? 0),
                strong: l === ex.predicted,
              }))}
            />
            {ex.push_words.length > 0 ? (
              <div className="space-y-2">
                <p className="text-body-sm text-body">คำที่ดันไปทาง &quot;{th(report, ex.predicted)}&quot; มากที่สุด</p>
                <ul className="flex flex-wrap gap-2">
                  {ex.push_words.map((w) => (
                    <li key={w.word} className="inline-flex min-h-9 items-center rounded-md border border-ink px-3 text-body-md text-ink">
                      {w.word}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
            <details className="text-body-sm text-ink">
              <summary className="min-h-11 cursor-pointer py-2 text-button">ดูคะแนน log ทุกป้าย</summary>
              <table className="w-full text-left tabular-nums">
                <thead>
                  <tr className="text-body">
                    <th scope="col" className="py-1 font-normal">ป้าย</th>
                    <th scope="col" className="py-1 font-normal">log สัดส่วนในชุดฝึก</th>
                    <th scope="col" className="py-1 font-normal">คะแนนรวม</th>
                  </tr>
                </thead>
                <tbody>
                  {report.labels.map((l) => (
                    <tr key={l} className={cn(l === ex.predicted && "font-semibold")}>
                      <th scope="row" className="py-1 font-normal">{th(report, l)}</th>
                      <td className="py-1">{(ex.log_prior[l] ?? 0).toFixed(2)}</td>
                      <td className="py-1">{(ex.log_score[l] ?? 0).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </details>
          </Card>
        ))}
      </div>
    </Section>
  );
}
