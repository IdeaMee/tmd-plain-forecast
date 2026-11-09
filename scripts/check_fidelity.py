"""Phase 3.4: ตรวจ F1-F7 ของทุกฉบับที่แสดงบนเว็บ -> docs/results/fidelity-report.md.

ตั้งแต่ 11.6 F1-F6 ตรวจทุกฉบับรายวัน/7 วันที่ run_pipeline เขียนไว้ใน data/processed (ไม่ใช่แค่ 35 ฉบับเดิม);
ฉบับที่ไม่ผ่านท่อประมวลผลไม่มีไฟล์และข้ามที่นี่ (บันทึกใน docs/results/pipeline-run.md) · F7 ใช้ชุดเดิม

รัน (หลัง scripts/run_pipeline.py): .venv/Scripts/python.exe -X utf8 scripts/check_fidelity.py (ต้องพิมพ์ errors: 0)
F1-F5: generate/fidelity.py เทียบกับต้นฉบับของภาค · F6: รันซ้ำสองรอบในกระบวนการเดียว + เทียบไบต์กับไฟล์ใน data/processed
F7: ป้อนไฟล์ว่าง ไฟล์มั่ว ข้อความมั่ว และเอกสารที่ไม่ใช่พยากรณ์ ต้องได้ข้อผิดพลาดตามรหัส ไม่ crash
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from run_pipeline import display_issues, meta_for, out_path, render, run_one, web_issues

from tmd_plain.classify.model_io import load_labeler
from tmd_plain.contract import REGION_KEYS, Issue, SummarizeError
from tmd_plain.generate.fidelity import check_issue, cross_region_numbers
from tmd_plain.pipeline import document_from_bytes, parse_or_error, summarize
from tmd_plain.prep.extract import SourceDocument, document_from_txt

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "results" / "fidelity-report.md"
CHECKS = ("F1", "F2", "F3", "F4", "F5")


def f7_cases() -> list[tuple[str, object, str]]:
    """(ชื่อกรณี, ผลที่ได้, รหัสที่คาด) · ห่อทุกกรณีกันการ crash."""
    daily_txt = next(i for i in display_issues() if i.doc_type == "daily" and i.txt).txt
    real = daily_txt.read_text(encoding="utf-8")  # type: ignore[union-attr]
    # ฉบับจริงที่ตัดส่วนบล็อกภาคทิ้ง = เอกสารไม่ครบ
    cut = real.split("พยากรณ์อากาศสำหรับประเทศไทย")[0] + "พยากรณ์อากาศสำหรับประเทศไทย\n"
    marine = "พยากรณ์อากาศสำหรับการเดินเรือ\n" + real
    cases: list[tuple[str, bytes | SourceDocument, str]] = [
        ("ไฟล์ว่าง (0 ไบต์)", b"", "empty_file"),
        ("ไฟล์มั่ว (ไบต์สุ่ม ไม่ใช่ PDF)", bytes(range(256)) * 8, "extract_failed"),
        ("ข้อความว่าง", document_from_txt("   \n"), "empty_file"),
        ("ข้อความมั่ว", document_from_txt("กขค 123 abc ฟหกด\n" * 20), "unsupported_document"),
        ("ประกาศพยากรณ์การเดินเรือ", document_from_txt(marine), "unsupported_document"),
        # เป็นเอกสาร TMD แต่หาบล็อกภาคไม่ได้ = อ่านไม่สำเร็จ (กติกาของ prep/regions.py ตั้งแต่ 1.3)
        ("พยากรณ์รายวันที่ไม่มีบล็อกภาค", document_from_txt(cut), "extract_failed"),
    ]
    slide = ROOT / "course" / "slides" / "0_MiniProject.pdf"
    if slide.exists():
        cases.append(("PDF ที่ไม่ใช่ของ TMD (สไลด์รายวิชา)", slide.read_bytes(), "unsupported_document"))
    label_of = load_labeler(ROOT / "models")
    meta = meta_for(next(iter(display_issues())))
    out: list[tuple[str, object, str]] = []
    for name, payload, expected in cases:
        try:
            doc = document_from_bytes(payload) if isinstance(payload, bytes) else payload
            result = doc if isinstance(doc, SummarizeError) else summarize(doc, meta, label_of)
        except Exception as exc:  # noqa: BLE001 (F7: บันทึกว่า crash แทนที่จะหยุดทั้งรายงาน)
            result = f"crash: {type(exc).__name__}"
        out.append((name, result, expected))
    return out


def main() -> int:
    label_of = load_labeler(ROOT / "models")
    errors: list[str] = []
    rows: list[str] = []
    totals: Counter[str] = Counter()
    skipped = 0
    for raw in web_issues():
        tag = f"{raw.doc_type}/{raw.issue_id}"
        first = run_one(raw, label_of)
        second = run_one(raw, label_of)
        if isinstance(first, SummarizeError) or isinstance(second, SummarizeError):
            # ฉบับที่ไม่ผ่านท่อประมวลผลไม่มีไฟล์ใน data/processed (ไม่ขึ้นเว็บ) ผิดปกติเฉพาะเมื่อไฟล์ยังอยู่
            if out_path(raw).exists():
                errors.append(f"{tag}: ท่อประมวลผลคืนข้อผิดพลาดแต่ยังมีไฟล์ใน data/processed")
            skipped += 1
            continue
        path = out_path(raw)
        on_disk = path.read_text(encoding="utf-8") if path.exists() else ""
        f6 = render(first) == render(second) == on_disk
        Issue.model_validate_json(on_disk or "{}") if on_disk else None
        parsed = parse_or_error(raw.preferred())
        assert not isinstance(parsed, SummarizeError)
        found = check_issue(first, parsed) + cross_region_numbers(first, parsed)
        per = Counter(e[:2] for e in found)
        totals["issues"] += 1
        totals["regions"] += len(REGION_KEYS)
        lines = sum(
            len(r.lines) + sum(len(p.lines) for p in r.periods) for r in first.regions.values()
        )
        advice = sum(len(r.advice) for r in first.regions.values()) + len(first.general_advice)
        totals["lines"] += lines
        totals["advice"] += advice
        if not f6:
            errors.append(
                f"F6 {tag}: ผลสองรอบหรือไฟล์ใน data/processed ไม่ตรงกัน (รัน run_pipeline.py ใหม่)"
            )
        errors += [f"{tag} {e}" for e in found]
        cells = " | ".join("ผ่าน" if not per[c] else f"ไม่ผ่าน {per[c]}" for c in CHECKS)
        rows.append(f"| {tag} | {lines} | {advice} | {cells} | {'ผ่าน' if f6 else 'ไม่ผ่าน'} |")

    f7_rows: list[str] = []
    for name, result, expected in f7_cases():
        got = result.error.code if isinstance(result, SummarizeError) else str(result)[:40]
        ok = got == expected
        if not ok:
            errors.append(f"F7 {name}: ได้ {got} คาด {expected}")
        f7_rows.append(f"| {name} | `{expected}` | `{got}` | {'ผ่าน' if ok else 'ไม่ผ่าน'} |")

    report = [
        "# รายงานความถูกต้องของผลสรุป F1-F7 (Phase 3.4)",
        "",
        "คำสั่ง: `.venv/Scripts/python.exe -X utf8 scripts/run_pipeline.py` แล้ว `scripts/check_fidelity.py` · ไฟล์นี้สร้างโดยสคริปต์",
        "",
        f"ขอบเขต: ฉบับรายวัน/7 วันที่แสดงบนเว็บ {totals['issues']} ฉบับ (ข้ามฉบับที่ไม่ผ่านท่อประมวลผลและไม่ขึ้นเว็บ {skipped} ฉบับ) × 7 ภาค = {totals['regions']} ภาค · ประโยคสรุป {totals['lines']} · คำแนะนำ {totals['advice']} รายการ",
        "",
        "| เกณฑ์ | ความหมาย |",
        "|---|---|",
        "| F1 | ตัวเลขทุกตัวในสรุปของภาคอยู่ในบล็อกต้นฉบับของภาคนั้น (ยกเว้นค่าคำนวณตามสูตรและเกณฑ์ TMD ตาม ADR 0013) |",
        "| F2 | ชื่อจังหวัดในสรุปอยู่ในต้นฉบับ |",
        "| F3 | คำแนะนำทุกรายการเป็นสตริงย่อยของต้นฉบับ (หลังปรับช่องว่าง) |",
        '| F4 | ไม่มีคำว่า "โอกาส … %" หรือ "ความน่าจะเป็น" |',
        "| F5 | ไม่มีตัวเลขที่พบเฉพาะในบล็อกของภาคอื่น |",
        "| F6 | รันสองรอบได้ผลเท่ากันทุกไบต์ และตรงกับไฟล์ใน `data/processed/` |",
        "| F7 | ข้อมูลเข้าที่ผิดได้ข้อผิดพลาดตามรหัสในสัญญา ไม่ crash ไม่เดา |",
        "",
        f"**ผลรวม: ข้อผิดพลาด {len(errors)}**",
        "",
        "## F1-F6 รายฉบับ",
        "| ฉบับ | ประโยค | คำแนะนำ | F1 | F2 | F3 | F4 | F5 | F6 |",
        "|---|---|---|---|---|---|---|---|---|",
        *rows,
        "",
        "## F7 ข้อมูลเข้าที่ผิด",
        "| กรณี | รหัสที่คาด | ที่ได้ | ผล |",
        "|---|---|---|---|",
        *f7_rows,
        "",
        f"## ข้อผิดพลาด ({len(errors)})",
        *([f"- {e}" for e in errors] or ["ไม่มี"]),
        "",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8", newline="\n")
    print(f"issues {totals['issues']} lines {totals['lines']} advice {totals['advice']}")
    for e in errors[:20]:
        print(e)
    print(f"errors: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
