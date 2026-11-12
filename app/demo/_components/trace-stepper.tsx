"use client";

import { useId, useState, type KeyboardEvent } from "react";

import { StepVisual } from "@/app/demo/_components/step-visual";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Trace } from "@/lib/contract/documents";
import { cn } from "@/lib/cn";

type TraceStepperProps = {
  trace: Trace;
  // id ของหัวข้อผลลัพธ์ ใช้กับปุ่ม "ข้ามไปผลลัพธ์"
  resultId: string;
};

// ตัวเดินขั้นตอน: เรียงตาม trace.steps ที่หลังบ้านส่งมา (มีเฉพาะขั้นที่ทำจริงของชนิดนั้น ไม่ hard-code ลำดับ)
// ปุ่มถัดไป/ย้อนกลับ + ลูกศรซ้าย/ขวาเมื่อโฟกัสอยู่ในส่วนนี้ · บอกขั้นปัจจุบันผ่าน aria-live
export function TraceStepper({ trace, resultId }: TraceStepperProps) {
  const headingId = useId();
  const [index, setIndex] = useState(0);
  const steps = trace.steps;
  if (steps.length === 0) return null;
  const step = steps[index];
  const last = steps.length - 1;
  const go = (next: number) => setIndex(Math.min(Math.max(next, 0), last));

  function onKeyDown(event: KeyboardEvent<HTMLElement>) {
    if (event.key === "ArrowRight") go(index + 1);
    else if (event.key === "ArrowLeft") go(index - 1);
    else return;
    event.preventDefault();
  }

  function skipToResult() {
    const target = document.getElementById(resultId);
    target?.scrollIntoView({ block: "start" });
    target?.focus();
  }

  return (
    <section
      aria-labelledby={headingId}
      onKeyDown={onKeyDown}
      className="space-y-5 rounded-lg border border-hairline-strong bg-surface-card p-4 sm:p-6"
    >
      <div className="space-y-1">
        <h2 id={headingId} className="text-title-md">
          ระบบทำอะไรกับไฟล์นี้ทีละขั้น
        </h2>
        <p className="text-body-sm text-body">
          กดถัดไป/ย้อนกลับ หรือใช้ลูกศรซ้าย-ขวา ตัวอย่างในขั้นตัดคำถึงจัดประเภทใช้หน่วยประโยคเดียวจากไฟล์
        </p>
      </div>

      {/* แถบความคืบหน้าเป็นของตกแต่ง ความหมายอยู่ในข้อความ "ขั้นที่ x จาก n" */}
      <ol aria-hidden="true" className="flex gap-1">
        {steps.map((s, i) => (
          <li
            key={s.id}
            className={cn(
              "h-1.5 flex-1 rounded-pill transition-colors duration-(--duration-base)",
              i <= index ? "bg-primary" : "bg-hairline-strong",
            )}
          />
        ))}
      </ol>

      <div aria-live="polite" className="space-y-1">
        <p className="text-body-sm text-body">
          ขั้นที่ {index + 1} จาก {steps.length}
        </p>
        <p className="flex flex-wrap items-center gap-2 text-display-sm text-ink" data-testid="step-title">
          {step.title_th}
          {step.status === "skipped" ? <Badge variant="muted">ข้าม</Badge> : null}
          {step.status === "failed" ? <Badge variant="sample">ไม่ผ่าน</Badge> : null}
        </p>
        {step.note_th ? <p className="text-body-md text-ink">{step.note_th}</p> : null}
      </div>

      {/* key ตามขั้น: เปลี่ยนขั้นแล้วอนิเมชันของขั้นใหม่เล่นใหม่ */}
      <div key={step.id} className="animate-fade-in">
        <StepVisual step={step} steps={steps} />
      </div>

      {trace.truncated ? (
        <p className="text-body-sm text-body">บางขั้นแสดงข้อมูลไม่ครบ เพราะภาพขั้นตอนของไฟล์นี้ยาวเกินเพดาน</p>
      ) : null}

      <div className="flex flex-wrap gap-2">
        <Button variant="secondary" onClick={() => go(index - 1)} disabled={index === 0} className="disabled:opacity-60">
          ย้อนกลับ
        </Button>
        <Button onClick={() => go(index + 1)} disabled={index === last} className="disabled:opacity-60">
          ถัดไป
        </Button>
        <Button variant="text" onClick={skipToResult} className="min-h-10 pointer-coarse:min-h-11">
          ข้ามไปผลลัพธ์
        </Button>
      </div>
    </section>
  );
}
