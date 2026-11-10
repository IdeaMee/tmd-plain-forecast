"use client";

import { useId, useRef, useState, type DragEvent, type FormEvent } from "react";

import { GenericResult } from "@/app/demo/_components/generic-result";
import { TraceStepper } from "@/app/demo/_components/trace-stepper";
import { IssueSummary } from "@/components/features/issue-summary";
import { Alert } from "@/components/ui/alert";
import { Button, buttonVariants } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/cn";
import {
  checkFile,
  errorOutcome,
  formatSize,
  NETWORK_MESSAGE_TH,
  readResponse,
  SUMMARIZE_URL,
  type UploadOutcome,
} from "@/lib/upload";

type Status = { kind: "idle" } | { kind: "busy" } | UploadOutcome;

const WARNING_ICON = (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <path d="M10 2.5 18 17H2L10 2.5Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    <path d="M10 8v4M10 14.5v.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
);

// ฟอร์มอัปโหลด PDF ของหน้า /demo: เลือกหรือลากไฟล์ -> ตรวจในเบราว์เซอร์ -> POST PDF ดิบ -> แสดงการ์ดชุดเดียวกับหน้าหลัก
export function UploadForm() {
  const inputId = useId();
  const hintId = useId();
  const resultId = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<Status>({ kind: "idle" });
  const [dragging, setDragging] = useState(false);
  const busy = status.kind === "busy";

  function choose(next: File | null) {
    setFile(next);
    setStatus({ kind: "idle" });
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragging(false);
    if (busy) return;
    const dropped = event.dataTransfer.files;
    if (dropped.length === 0) return;
    // ให้ช่องเลือกไฟล์แสดงไฟล์เดียวกับที่ลากมาวาง
    if (inputRef.current) inputRef.current.files = dropped;
    choose(dropped[0]);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file || busy) return;
    const invalid = checkFile(file);
    if (invalid) {
      setStatus(errorOutcome(invalid));
      return;
    }
    setStatus({ kind: "busy" });
    try {
      const res = await fetch(SUMMARIZE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/pdf" },
        body: file,
      });
      setStatus(readResponse(await res.json().catch(() => null)));
    } catch {
      setStatus({ kind: "network", message: NETWORK_MESSAGE_TH });
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={onSubmit} className="max-w-2xl space-y-4" aria-busy={busy}>
        <div
          onDragOver={(e) => {
            e.preventDefault();
            // ระหว่างประมวลผลไม่รับไฟล์ จึงไม่แสดงว่าวางได้
            if (!busy) setDragging(true);
          }}
          onDragLeave={(e) => {
            // ออกจากกรอบจริงเท่านั้น (เลื่อนผ่านป้าย/ปุ่มข้างในก็ทำให้เกิด dragleave)
            if (!e.currentTarget.contains(e.relatedTarget as Node | null)) setDragging(false);
          }}
          onDrop={onDrop}
          data-testid="dropzone"
          className={cn(
            "space-y-3 rounded-lg border-2 border-dashed border-hairline-strong bg-canvas-soft p-6",
            dragging && "border-ink bg-surface-strong",
          )}
        >
          <label htmlFor={inputId} className="block text-title-sm text-ink">
            เลือกไฟล์ PDF พยากรณ์ของกรมอุตุนิยมวิทยา
          </label>
          <p id={hintId} className="text-body-sm text-body">
            ลากไฟล์มาวางในกรอบนี้ หรือกดปุ่มเลือกไฟล์ (ไม่เกิน 4 MB · พยากรณ์รายวัน/7 วันได้สรุปเต็ม
            เอกสารอื่นของกรมแสดงแบบโหมดทั่วไป)
          </p>
          {/* ช่องเลือกไฟล์จริง (โฟกัสด้วยคีย์บอร์ดได้) ซ่อนด้วยสายตาเพราะปุ่มของเบราว์เซอร์เป็นภาษาอังกฤษ ("Choose File") */}
          <div className="flex flex-wrap items-center gap-3">
            <input
              ref={inputRef}
              id={inputId}
              type="file"
              accept="application/pdf,.pdf"
              aria-describedby={hintId}
              disabled={busy}
              onChange={(e) => choose(e.target.files?.[0] ?? null)}
              className="peer sr-only"
            />
            <label
              htmlFor={inputId}
              className={cn(
                buttonVariants({ variant: "secondary" }),
                "cursor-pointer peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-ink peer-disabled:cursor-not-allowed peer-disabled:opacity-60",
              )}
            >
              {file ? "เปลี่ยนไฟล์" : "เลือกไฟล์ PDF"}
            </label>
            <p className="min-w-0 text-body-sm text-ink">
              {file ? (
                <>
                  ไฟล์ที่เลือก: <span className="font-semibold [overflow-wrap:anywhere]">{file.name}</span> (
                  {formatSize(file.size)})
                </>
              ) : (
                "ยังไม่ได้เลือกไฟล์"
              )}
            </p>
          </div>
        </div>
        <Button type="submit" variant="primary" disabled={!file || busy} className="w-full disabled:opacity-60 sm:w-auto">
          {busy ? "กำลังสรุป…" : "สรุปพยากรณ์จากไฟล์นี้"}
        </Button>
      </form>

      {/* อ่านออกเสียงเฉพาะข้อความสถานะสั้นๆ ไม่ใช่การ์ดผลลัพธ์ทั้งหมด */}
      <div aria-live="polite" role="status" className="space-y-4">
        {status.kind === "busy" ? (
          <p className="text-body-md text-ink">กำลังอ่านและสรุปไฟล์ อาจใช้เวลาสักครู่</p>
        ) : null}
        {status.kind === "error" || status.kind === "network" ? (
          <Alert tone="warning" icon={WARNING_ICON}>
            <p className="font-semibold">สรุปไฟล์นี้ไม่ได้</p>
            <p className="mt-1">{status.message}</p>
          </Alert>
        ) : null}
        {status.kind === "notice" ? (
          // ไม่ใช่ข้อผิดพลาด จึงไม่ใช้ไอคอนเตือน
          <Alert>
            <p className="font-semibold">อ่านไฟล์นี้ได้แล้ว</p>
            <p className="mt-1">{status.message}</p>
          </Alert>
        ) : null}
        {status.kind === "ok" ? <p className="sr-only">สรุปเสร็จแล้ว ผลอยู่ด้านล่าง</p> : null}
      </div>

      {status.kind === "busy" ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }, (_, i) => (
            <Skeleton key={i} className="h-48 rounded-lg" />
          ))}
        </div>
      ) : null}

      <div>
        {status.kind === "ok" ? (
          <div className="space-y-8">
            {status.result.trace ? <TraceStepper trace={status.result.trace} resultId={resultId} /> : null}
            <section className="space-y-6" aria-labelledby={resultId}>
              {status.result.kind === "issue" ? (
                <>
                  <div className="space-y-1">
                    <h2 id={resultId} tabIndex={-1} className="text-display-sm">
                      ผลสรุป{status.result.document.doc_type === "daily" ? "พยากรณ์รายวัน" : "พยากรณ์ 7 วัน"}
                    </h2>
                    <p className="text-body-md text-ink">{status.result.document.source_label}</p>
                    <p className="text-body-sm text-body">
                      คำนวณจากไฟล์ที่อัปโหลด ผลจาก PDF อาจแม่นน้อยกว่าผลบนหน้าหลัก ตรวจกับประกาศฉบับเต็มก่อนใช้ตัดสินใจ
                    </p>
                  </div>
                  <IssueSummary issue={status.result.document} />
                </>
              ) : (
                <>
                  <div className="space-y-1">
                    <h2 id={resultId} tabIndex={-1} className="text-display-sm">
                      ผลอ่านเอกสาร (โหมดทั่วไป)
                    </h2>
                    {status.result.document.title ? (
                      <p className="text-body-md text-ink">{status.result.document.title}</p>
                    ) : null}
                  </div>
                  <GenericResult document={status.result.document} />
                </>
              )}
            </section>
          </div>
        ) : null}
      </div>
    </div>
  );
}
