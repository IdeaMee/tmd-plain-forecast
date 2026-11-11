"use client";

import { useState, type CSSProperties } from "react";

import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { GenericDocument } from "@/lib/contract/documents";
import { REGION_KEYS, type RegionKey } from "@/lib/contract/issue";
import { cn } from "@/lib/cn";
import { REGION_LABELS } from "@/lib/format/thai";
import { highlight, percent, unitLabelTh, type HighlightKind } from "@/lib/trace-view";

type Unit = GenericDocument["sections"][number]["units"][number];

const MARK_STYLE: Record<HighlightKind, string> = {
  number: "rounded-xs bg-num-tint px-0.5 text-ink",
  date: "underline decoration-2 underline-offset-4",
  province: "font-semibold",
};

function UnitText({ unit }: { unit: Unit }) {
  const parts = highlight(unit.text, [
    ...unit.numbers.map((text) => ({ text, kind: "number" as const })),
    ...unit.dates.map((text) => ({ text, kind: "date" as const })),
    ...unit.provinces.map((text) => ({ text, kind: "province" as const })),
  ]);
  return (
    <p className="text-body-md text-ink [overflow-wrap:anywhere]">
      {parts.map((p, i) =>
        p.kind ? (
          <mark key={i} className={cn("bg-transparent text-ink", MARK_STYLE[p.kind])}>
            {p.text}
          </mark>
        ) : (
          <span key={i}>{p.text}</span>
        ),
      )}
    </p>
  );
}

function UnitRow({ unit, index }: { unit: Unit; index: number }) {
  return (
    <li
      className="animate-enter-up space-y-2 border-t border-hairline pt-3 stagger first:border-t-0 first:pt-0"
      style={{ "--i": Math.min(index, 12) } as CSSProperties}
    >
      <div className="flex flex-wrap items-center gap-2">
        <Badge>{unitLabelTh(unit.label)}</Badge>
        <span className="text-body-sm text-body">มั่นใจ {percent(unit.confidence)}</span>
        {unit.uncertain ? <Badge variant="sample">ไม่แน่ใจ</Badge> : null}
      </div>
      <UnitText unit={unit} />
    </li>
  );
}

type GenericResultProps = { document: GenericDocument };

// ผลโหมดทั่วไป: ข้อความต้นฉบับแบ่งส่วน + ป้ายจากโมเดล (ไม่มีข้อความที่เขียนใหม่) · มีหัวข้อภาค = กรองตามภาคได้
export function GenericResult({ document: doc }: GenericResultProps) {
  const [region, setRegion] = useState<RegionKey | null>(null);
  const units = doc.sections.flatMap((s) => s.units);
  const regions = REGION_KEYS.filter((k) => units.some((u) => u.regions.includes(k)));
  const visible = (u: Unit) => region === null || u.regions.includes(region);
  // กรองตามภาคเดียวกับส่วนด้านล่าง ไม่ให้คำแนะนำของภาคอื่นดูเหมือนใช้กับภาคที่เลือก
  const advice = units.filter((u) => u.label === "advice" && visible(u));
  const sections = doc.sections
    .map((s) => ({ ...s, units: s.units.filter(visible) }))
    .filter((s) => s.units.length > 0);

  return (
    <div className="space-y-6">
      {!doc.tmd_like ? (
        <Alert tone="warning">
          <p className="font-semibold">ไฟล์นี้ดูไม่เหมือนเอกสารของกรมอุตุนิยมวิทยา</p>
          <p className="mt-1">ผลด้านล่างแสดงตามข้อความในไฟล์เท่านั้น ป้ายประเภทประโยคอาจไม่มีความหมายกับเอกสารชนิดนี้</p>
        </Alert>
      ) : null}

      <Card className="space-y-2">
        <p className="text-body-md text-ink">
          ไฟล์นี้ไม่ใช่พยากรณ์รายวันหรือ 7 วัน จึงแสดงแบบโหมดทั่วไป: ข้อความต้นฉบับแบ่งเป็นส่วน
          พร้อมป้ายประเภทประโยคจากโมเดลที่ฝึกจากพยากรณ์รายวัน/7 วัน ไม่ได้เขียนข้อความใหม่
        </p>
        <p className="text-body-sm text-body">
          {doc.page_count} หน้า · {units.length} หน่วยประโยค · ไม่แน่ใจ {units.filter((u) => u.uncertain).length} หน่วย
        </p>
        <ul className="flex flex-wrap gap-x-6 gap-y-1 text-body-sm text-ink">
          <li>
            <mark className={cn("bg-transparent", MARK_STYLE.number)}>พื้นฟ้า</mark> = ตัวเลข
          </li>
          <li>
            <mark className={cn("bg-transparent text-ink", MARK_STYLE.date)}>ขีดเส้นใต้</mark> = วันที่
          </li>
          <li>
            <mark className={cn("bg-transparent text-ink", MARK_STYLE.province)}>ตัวหนา</mark> = จังหวัด
          </li>
        </ul>
        {doc.truncated ? (
          <p className="text-body-sm text-ink">เอกสารยาว แสดงเฉพาะส่วนต้นของไฟล์</p>
        ) : null}
      </Card>

      {advice.length > 0 ? (
        <Card className="space-y-3">
          {/* เป็นผลของโมเดล ไม่ใช่การยืนยันว่าเป็นคำแนะนำจริง จึงบอกที่มาในหัวข้อ */}
          <h3 className="text-title-md">ประโยคที่โมเดลจัดเป็นคำแนะนำ (คัดจากต้นฉบับ)</h3>
          <ul className="list-disc space-y-2 pl-5 text-body-md text-ink">
            {advice.map((u) => (
              <li key={u.unit_id} className="[overflow-wrap:anywhere]">
                {u.text}
                {u.uncertain ? <span className="text-body-sm text-body"> (ไม่แน่ใจว่าเป็นคำแนะนำ)</span> : null}
              </li>
            ))}
          </ul>
        </Card>
      ) : null}

      {doc.has_region_headings && regions.length > 1 ? (
        <div role="group" aria-label="กรองตามภาค" className="-mx-4 overflow-x-auto px-4 py-1 sm:mx-0 sm:px-0">
          <ul className="flex w-max gap-2 sm:w-auto sm:flex-wrap">
            {[null, ...regions].map((key) => {
              const on = region === key;
              return (
                <li key={key ?? "all"} className="shrink-0">
                  <button
                    type="button"
                    aria-pressed={on}
                    onClick={() => setRegion(key)}
                    className={cn(
                      "inline-flex min-h-10 items-center rounded-md border px-4 text-button whitespace-nowrap transition-colors duration-(--duration-base) pointer-coarse:min-h-11",
                      on
                        ? "animate-pop border-primary bg-primary text-on-primary"
                        : "border-hairline-strong bg-surface-card text-ink hover:bg-canvas-soft",
                    )}
                  >
                    {key ? REGION_LABELS[key] : "ทุกส่วน"}
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      ) : null}

      <div className="space-y-4">
        {sections.map((section, i) => (
          <Card key={`${i}-${section.heading ?? ""}`} className="space-y-3">
            {section.heading ? <h3 className="text-title-md">{section.heading}</h3> : null}
            <ol className="space-y-3">
              {section.units.map((u, j) => (
                <UnitRow key={u.unit_id} unit={u} index={j} />
              ))}
            </ol>
          </Card>
        ))}
      </div>

      {doc.glossary.length > 0 ? (
        <Card className="space-y-3">
          <h3 className="text-title-md">คำอธิบายศัพท์ (จากหมายเหตุของกรมอุตุนิยมวิทยา)</h3>
          <dl className="space-y-2 text-body-md text-ink">
            {doc.glossary.map((g) => (
              <div key={g.term}>
                <dt className="font-semibold">{g.term}</dt>
                <dd>{g.explanation}</dd>
              </div>
            ))}
          </dl>
        </Card>
      ) : null}
    </div>
  );
}
