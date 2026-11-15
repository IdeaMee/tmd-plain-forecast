"""Phase 11.2: ตรวจประกาศเตือนภัยทุกฉบับที่เก็บ -> docs/results/warning-check.md (ต้องพิมพ์ errors: 0).

รัน: .venv/Scripts/python.exe -X utf8 scripts/check_warnings.py
ข้อผิดพลาด (ทำให้ล้ม): ตรวจชนิดไม่ได้, แยกโครง/ประกอบผล/ตัวตรวจไม่ผ่าน, รหัสจากเลขประกาศไม่ตรงชื่อไฟล์,
PDF กับหน้าเว็บของฉบับเดียวกันให้หัวเรื่อง เลขประกาศ ช่วงที่มีผล หรือวันเวลาประกาศไม่ตรงกัน
ข้อสังเกต (ไม่ล้ม): ท่อนที่มีคำแนะนำ (ควร/ขอให้) แต่ตัวจัดประเภทไม่ได้ให้ป้าย advice (ตัวจัดประเภทฝึกจากรายวัน/7 วัน
ตัวเฉพาะของประกาศมาในแผน 11.3) · ชุดที่ฉบับแรกไม่อยู่ในข้อมูล
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

from tmd_plain.classify.model_io import load_classifier
from tmd_plain.contract import SummarizeError, WarningNotice
from tmd_plain.doctypes.warning.runner import WarningDetails, summarize_warning
from tmd_plain.doctypes.warning.series import NoticeKey, link_series
from tmd_plain.prep.doctype import detect_doc_type
from tmd_plain.prep.extract import document_from_pdf, document_from_txt

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "warning"
REPORT = ROOT / "docs" / "results" / "warning-check.md"
_ADVICE_WORDS = re.compile(r"ควร|ขอให้|หลีกเลี่ยง|งดออกจากฝั่ง")


def _header(n: WarningNotice) -> tuple[object, ...]:
    effect = n.effect.model_dump(mode="json") if n.effect else None
    return (n.title, n.series_no, n.notice_no, effect, n.issued_at, n.next_issue_at)


def main() -> int:
    # ตัวเดียวกับที่ /demo ใช้กับประกาศ (ตัวเฉพาะของประกาศถ้ามี)
    label_of = load_classifier(ROOT / "models").for_doc("warning").label
    errors: list[str] = []
    notes: list[str] = []
    keys: list[NoticeKey] = []
    roles: Counter[str] = Counter()
    kinds: Counter[str] = Counter()
    effects: Counter[str] = Counter()
    txts = sorted(RAW.glob("warning_*.txt"))
    pdfs = {p.stem: p for p in RAW.glob("warning_*.pdf")}
    pdf_ok = 0
    for path in txts:
        stem = path.stem
        issue_id = stem.removeprefix("warning_")
        text = document_from_txt(path.read_text(encoding="utf-8")).text
        if detect_doc_type(text) != "warning":
            errors.append(f"{issue_id}: ตรวจชนิดไม่ได้ ({detect_doc_type(text)})")
            continue
        run = summarize_warning(text, label_of)
        if isinstance(run, SummarizeError):
            errors.append(f"{issue_id}: {run.error.code}")
            continue
        notice: WarningNotice = run.document  # type: ignore[assignment]
        details: WarningDetails = run.details
        if notice.issue_id != issue_id:
            errors.append(f"{issue_id}: รหัสจากเลขประกาศ {notice.issue_id} ไม่ตรงชื่อไฟล์")
        roles.update(u.label for u in details.units)
        kinds.update(ln.kind for ln in notice.lines)
        e = notice.effect
        effects[
            "ไม่มี"
            if e is None
            else f"เริ่ม {'มี' if e.start else 'ไม่มี'} / สิ้นสุด {'มี' if e.end else 'ไม่มี'}"
        ] += 1
        for line in notice.lines:
            if _ADVICE_WORDS.search(line.text):
                notes.append(
                    f"{issue_id}: ป้าย {line.facts.get('unit_role')} แต่มีคำแนะนำ: {line.text[:80]}"
                )
        keys.append(
            NoticeKey(
                issue_id=notice.issue_id,
                series_no=notice.series_no,
                title=notice.title,
                issued_at=notice.issued_at,
                next_issue_at=notice.next_issue_at,
                final=details.parsed.final,
            )
        )
        pdf = pdfs.get(stem)
        if pdf is None:
            continue
        pdf_run = summarize_warning(document_from_pdf(pdf.read_bytes()).text, label_of)
        if isinstance(pdf_run, SummarizeError):
            errors.append(f"{issue_id}: PDF {pdf_run.error.code}")
            continue
        if _header(pdf_run.document) != _header(notice):  # type: ignore[arg-type]
            errors.append(f"{issue_id}: หัวประกาศจาก PDF ไม่ตรงกับหน้าเว็บ")
            continue
        pdf_ok += 1

    series = link_series(keys)
    partial = [s for s in series if not s.complete_start]
    lengths = Counter(len(s.notices) for s in series)
    lines = [
        "# ตรวจประกาศเตือนภัย (Phase 11.2)",
        "",
        "สร้างโดย `scripts/check_warnings.py` (อย่าแก้ด้วยมือ) · แหล่ง: ข้อความหน้าเว็บใน `data/raw/warning/` "
        "และ PDF ของฉบับเดียวกัน (หน้าที่มีประกาศ)",
        "",
        f"- ฉบับ (หน้าเว็บ): {len(txts)} · ผ่าน: {len(keys)} · PDF ที่หัวประกาศตรงกับหน้าเว็บ: {pdf_ok}/{len(pdfs)} · ข้อผิดพลาด: {len(errors)}",
        f"- ป้ายของท่อน (ตัวจัดประเภทที่ใช้ในเว็บ): {', '.join(f'{k} {v}' for k, v in sorted(roles.items()))}",
        f"- ชนิดของท่อนที่ไม่ใช่คำแนะนำ: {', '.join(f'{k} {v}' for k, v in sorted(kinds.items()))}",
        f"- ช่วงที่มีผล: {', '.join(f'{k} {v}' for k, v in sorted(effects.items()))}",
        f"- ชุดประกาศ (เหตุการณ์): {len(series)} ชุด · ความยาว (ฉบับ: จำนวนชุด) "
        f"{', '.join(f'{k}: {v}' for k, v in sorted(lengths.items()))} · ชุดที่ฉบับแรกไม่อยู่ในข้อมูล {len(partial)}",
        f"- ข้อสังเกตป้าย (มีคำแนะนำแต่ไม่ได้ป้าย advice): {len(notes)}",
        "",
        "## ข้อผิดพลาด",
        "",
        *([f"- {e}" for e in errors] or ["- ไม่มี"]),
        "",
        "## ชุดประกาศ",
        "",
        "| ชุด (ฉบับแรกที่มี) | ฉบับ | หัวเรื่องฉบับแรก | ฉบับสุดท้ายในข้อมูล |",
        "|---|---|---|---|",
        *[
            f"| {s.series_id} | {s.notices[0].series_no}-{s.last.series_no} ({len(s.notices)}) | {s.notices[0].title} | "
            f"{s.last.issue_id}{' (ฉบับสุดท้าย)' if s.closed else ''} |"
            for s in series
        ],
        "",
        "## ข้อสังเกตป้าย",
        "",
        *([f"- {n}" for n in notes] or ["- ไม่มี"]),
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(
        f"issues {len(txts)} · ok {len(keys)} · pdf match {pdf_ok}/{len(pdfs)} · series {len(series)} "
        f"· label notes {len(notes)} · errors: {len(errors)}"
    )
    for e in errors[:10]:
        print(f"  {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
