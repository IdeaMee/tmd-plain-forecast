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

export function KnnSection({ report }: R) {
  return (
    <Section
      n={6}
      title="k-NN ดูเพื่อนบ้านที่ใกล้ที่สุด"
      lead={
        <>
          k-NN เปลี่ยนแต่ละประโยคเป็นเวกเตอร์จำนวนคำ (ปรับความยาวเป็น 1) แล้วหาประโยคในชุดฝึกที่ระยะใกล้สุด
          ค่าที่เลือกคือ k = {report.tuning.best_k} (โหวตจากเพื่อนบ้าน {report.tuning.best_k} ตัว) ตารางแสดง {report.knn_examples[0]?.neighbors.length ?? 0} ตัวใกล้สุดให้เห็นภาพ
        </>
      }
    >
      <div className="grid gap-4 lg:grid-cols-2">
        {report.knn_examples.map((ex) => (
          <Card key={ex.unit_id} className="space-y-3">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant={ex.predicted === ex.true_label ? "default" : "sample"}>
                {ex.predicted === ex.true_label ? "ทายถูก" : "ทายผิด"}
              </Badge>
              <span className="text-body-sm text-ink">
                ป้ายจริง {th(report, ex.true_label)} · k-NN ทาย {th(report, ex.predicted)}
              </span>
            </div>
            <Quote>{ex.text}</Quote>
            <ol className="space-y-2">
              {ex.neighbors.map((n, i) => (
                <li key={n.unit_id} className="space-y-1 border-t border-hairline pt-2 first:border-t-0 first:pt-0">
                  <p className="flex flex-wrap items-center gap-2 text-body-sm text-ink">
                    <span className="font-semibold">ใกล้อันดับ {i + 1}</span>
                    <Badge variant="muted">{th(report, n.label)}</Badge>
                    <span className="tabular-nums">ระยะ {n.distance.toFixed(3)}</span>
                  </p>
                  <p className="text-body-sm text-body [overflow-wrap:anywhere]">{n.text}</p>
                </li>
              ))}
            </ol>
          </Card>
        ))}
      </div>
    </Section>
  );
}

export function EvaluationSection({ report }: R) {
  const labels = report.labels.map((l) => th(report, l));
  // ชุดของประกาศไม่ได้นับครั้งที่พบต่อฉบับ จึงไม่มีคอลัมน์ถ่วงน้ำหนัก
  const weighted = report.results.some((r) => r.test_all_weighted !== null);
  const nbAll = report.tuning.nb_m_factor.every((p) => p.dev_accuracy === report.tuning.nb_m_factor[0].dev_accuracy);
  return (
    <Section
      n={7}
      title="ปรับค่าบนชุด dev แล้ววัดผลบนชุดทดสอบ"
      lead={
        <>
          ลองค่า m ของ Naive Bayes และ k ของ k-NN บนชุด dev เท่านั้น (ไม่แตะชุดทดสอบ) แล้ววัดทั้งสองโมเดลเทียบกับกฎคำสำคัญ
          (keyword) ที่เขียนก่อนมีป้าย · ตัวที่ใช้ในเว็บ: <strong>{report.chosen}</strong> (เลือกจากชุด dev)
        </>
      }
    >
      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="space-y-2 p-4">
          <h3 className="text-title-sm">Naive Bayes: ค่า m (× ขนาดคลังคำ {report.tuning.vocab_train} คำ)</h3>
          <BarTable
            caption="ความแม่นบนชุด dev ต่อค่า m"
            columns={["ค่า m", "ความแม่นบน dev"]}
            max={1}
            rows={report.tuning.nb_m_factor.map((p) => ({
              label: `m = ${p.value}`,
              value: p.dev_accuracy,
              display: pct(p.dev_accuracy),
              strong: p.value === report.tuning.best_m_factor,
            }))}
          />
          {nbAll ? (
            <p className="text-body-sm text-body">ทุกค่าได้เท่ากัน (dev มีน้อย) จึงเลือกค่าแรกในรายการ</p>
          ) : null}
        </Card>
        <Card className="space-y-2 p-4">
          <h3 className="text-title-sm">k-NN: จำนวนเพื่อนบ้าน k</h3>
          <BarTable
            caption="ความแม่นบนชุด dev ต่อค่า k"
            columns={["ค่า k", "ความแม่นบน dev"]}
            max={1}
            rows={report.tuning.knn_k.map((p) => ({
              label: `k = ${p.value}`,
              value: p.dev_accuracy,
              display: pct(p.dev_accuracy),
              strong: p.value === report.tuning.best_k,
            }))}
          />
        </Card>
      </div>
      <Card className="space-y-2">
        <h3 className="text-title-sm">ความแม่นบนชุดทดสอบ (ถ้อยคำที่ไม่เคยเห็นตอนฝึก)</h3>
        <BarTable
          caption="ความแม่น (accuracy) บนหน่วยถ้อยคำใหม่ในชุดทดสอบ"
          columns={["วิธี", "ความแม่น"]}
          max={1}
          rows={report.results.map((r) => ({
            label: r.name,
            value: r.test_new,
            display: pct(r.test_new),
            strong: r.name === report.chosen,
          }))}
        />
        <details className="text-body-sm text-ink">
          <summary className="min-h-11 cursor-pointer py-2 text-button">ดูทุกชุดวัด</summary>
          <div className="overflow-x-auto">
            <table className="w-full text-left tabular-nums">
              <thead>
                <tr className="text-body">
                  <th scope="col" className="py-1 pr-4 font-normal">วิธี</th>
                  <th scope="col" className="py-1 pr-4 font-normal">dev</th>
                  <th scope="col" className="py-1 pr-4 font-normal">ทดสอบ ทุกหน่วย</th>
                  {weighted ? <th scope="col" className="py-1 pr-4 font-normal">ทดสอบ ถ่วงตามครั้งที่พบ</th> : null}
                  <th scope="col" className="py-1 font-normal">ทดสอบ ถ้อยคำใหม่</th>
                </tr>
              </thead>
              <tbody>
                {report.results.map((r) => (
                  <tr key={r.name}>
                    <th scope="row" className="py-1 pr-4 font-normal">{r.name}</th>
                    <td className="py-1 pr-4">{pct(r.dev)}</td>
                    <td className="py-1 pr-4">{pct(r.test_all)}</td>
                    {weighted ? (
                      <td className="py-1 pr-4">{r.test_all_weighted === null ? "-" : pct(r.test_all_weighted)}</td>
                    ) : null}
                    <td className="py-1">{pct(r.test_new)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      </Card>
      <div className="grid gap-4 lg:grid-cols-3">
        {report.confusion.map((c) => (
          <Card key={c.name} className="p-4">
            <ConfusionMatrix caption={`ตารางสับสน: ${c.name}`} labels={labels} matrix={c.matrix} />
          </Card>
        ))}
      </div>
      <p className="text-body-sm text-body">ช่องทแยงพื้นฟ้า = ทายถูก · ช่องอื่นที่มีตัวเลข (ตัวหนา พื้นส้มอ่อน) = ทายผิด</p>
    </Section>
  );
}

export function LearningCurveSection({ report }: R) {
  const curve = report.learning_curve;
  const fractions = curve.map((p) => pct(p.fraction, 0)).join(", ");
  const dev = report.splits.find((s) => s.split === "dev")?.total ?? 0;
  return (
    <Section
      n={8}
      title="ข้อมูลมากขึ้น ช่วยแค่ไหน"
      lead={`ฝึกด้วย${report.group_th}แรกๆ ของชุดฝึก ${fractions} ของจำนวน${report.group_th} แล้ววัดบนชุด dev เดิม (dev มีแค่ ${dev} หน่วย เส้นจึงแกว่งได้ ดูแนวโน้มมากกว่าตัวเลขเป๊ะ)`}
    >
      <Card>
        <LineChart
          title="ความแม่นบนชุด dev ตามจำนวนหน่วยที่ใช้ฝึก"
          xLabel="จำนวนหน่วยที่ใช้ฝึก"
          yLabel="ความแม่นบน dev"
          xTicks={curve.map((p) => p.train_units)}
          yTicks={[0.7, 0.8, 0.9, 1]}
          yMin={0.7}
          yMax={1}
          formatY={(y) => pct(y, 0)}
          series={[
            { name: "Naive Bayes", points: curve.map((p) => ({ x: p.train_units, y: p.nb_dev_accuracy })) },
            {
              name: "k-NN",
              dashed: true,
              square: true,
              points: curve.map((p) => ({ x: p.train_units, y: p.knn_dev_accuracy })),
            },
          ]}
        />
        <details className="mt-3 text-body-sm text-ink">
          <summary className="min-h-11 cursor-pointer py-2 text-button">ดูเป็นตาราง</summary>
          <div className="overflow-x-auto">
            <table className="w-full text-left tabular-nums">
              <thead>
                <tr className="text-body">
                  <th scope="col" className="py-1 pr-4 font-normal">ส่วนของชุดฝึก</th>
                  <th scope="col" className="py-1 pr-4 font-normal">{report.group_th} / หน่วย</th>
                  <th scope="col" className="py-1 pr-4 font-normal">NB ความแม่น / macro-F1</th>
                  <th scope="col" className="py-1 font-normal">k-NN ความแม่น / macro-F1</th>
                </tr>
              </thead>
              <tbody>
                {curve.map((p) => (
                  <tr key={p.fraction}>
                    <th scope="row" className="py-1 pr-4 font-normal">{pct(p.fraction, 0)}</th>
                    <td className="py-1 pr-4">
                      {p.train_groups} / {p.train_units}
                    </td>
                    <td className="py-1 pr-4">
                      {pct(p.nb_dev_accuracy)} / {pct(p.nb_dev_macro_f1)}
                    </td>
                    <td className="py-1">
                      {pct(p.knn_dev_accuracy)} / {pct(p.knn_dev_macro_f1)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      </Card>
    </Section>
  );
}

export function LimitsSection({ report }: R) {
  const keyword = report.results.find((r) => r.name.startsWith("กฎ"));
  const chosen = report.results.find((r) => r.name === report.chosen);
  return (
    <Section
      n={9}
      title="จุดที่ทายผิดและข้อจำกัด"
      lead={`${report.chosen} ทายผิด ${report.mistakes.length} หน่วยในชุดทดสอบ (ถ้อยคำใหม่) ด้านล่างคือทุกหน่วยที่ผิด พร้อมความมั่นใจของโมเดลและเหตุผลที่คาด`}
    >
      <div className="space-y-3">
        {report.mistakes.map((m) => (
          <Card key={m.unit_id} className="space-y-2 p-4">
            <p className="flex flex-wrap items-center gap-2 text-body-sm text-ink">
              <Badge variant="sample">ทายผิด</Badge>
              ป้ายจริง {th(report, m.true_label)} · ทาย {th(report, m.predicted)} · มั่นใจ {pct(m.confidence)}
            </p>
            <Quote>{m.text}</Quote>
            {m.note_th ? <p className="text-body-sm text-body">เหตุผลที่คาด: {m.note_th}</p> : null}
          </Card>
        ))}
      </div>
      <Card className="space-y-2">
        <h3 className="text-title-sm">ข้อจำกัดที่ต้องรู้</h3>
        <ul className="list-disc space-y-2 pl-5 text-body-md text-ink">
          <li>{report.label_source_th}</li>
          {keyword && chosen && keyword.test_new > chosen.test_new ? (
            <li>
              กฎคำสำคัญได้ {pct(keyword.test_new)} สูงกว่า {report.chosen} ({pct(chosen.test_new)}) ส่วนหนึ่งเพราะป้ายตรงกับกฎ{" "}
              {report.facts.keyword_agrees_with_labels}/{report.facts.total_units} หน่วยตั้งแต่ก่อนวัด และกรมใช้ถ้อยคำเป็นแบบแผน
              จึงไม่ได้แปลว่ากฎจะดีกว่ากับถ้อยคำแบบอื่น
            </li>
          ) : null}
          <li>
            ข้อมูลน้อย: ชุดฝึก {report.splits.find((s) => s.split === "train")?.total ?? 0} หน่วย dev{" "}
            {report.splits.find((s) => s.split === "dev")?.total ?? 0} หน่วย ตัวเลขแกว่งได้มากถ้าเปลี่ยน{report.group_th}ที่ใช้แบ่งชุด
          </li>
          {report.labels.includes("other") ? (
            <li>
              ป้าย &quot;{th(report, "other")}&quot; มี {report.facts.other_units} หน่วยในข้อมูลทั้งหมด โมเดลจึงแทบทายป้ายนี้ไม่ได้
            </li>
          ) : null}
          <li>bag of words ไม่รู้ลำดับคำ ประโยคที่ใช้คำเดียวกันแต่คนละความหมายจึงสับสนได้</li>
        </ul>
      </Card>
    </Section>
  );
}
