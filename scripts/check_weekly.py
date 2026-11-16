"""Phase 11.5: ตรวจสรุปรายสัปดาห์ทุกฉบับที่เก็บ -> docs/results/weekly-check.md (ต้องพิมพ์ errors: 0).

รัน: .venv/Scripts/python.exe -X utf8 scripts/check_weekly.py
ข้อผิดพลาด (ทำให้ล้ม): แยกโครงไม่ได้, ไม่ผ่าน F (ข้อความ/ช่องคัดคำต่อคำและครบ, วันที่, จังหวัด, ไม่มีคำว่าโอกาส),
วัน เดือน ปีของรหัสรอบไม่ตรงบรรทัดออกประกาศ, ช่องตารางที่ดึงค่าไม่ได้
ข้อสังเกต (ไม่ล้ม): รหัสรอบที่ชั่วโมงต่างจากเวลาออกประกาศ · จำนวนช่องที่มีค่า
PDF ของหมวดนี้เป็นแผนที่คนละเลย์เอาต์: ต้องไม่ถูกตรวจเป็นชนิดอื่น (ไปโหมดทั่วไป) ไม่เช่นนั้นเป็นข้อผิดพลาด
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from tmd_plain.contract import REGION_KEYS, SummarizeError
from tmd_plain.doctypes.registry import spec_for
from tmd_plain.doctypes.weekly.build import assemble_weekly, check_weekly
from tmd_plain.doctypes.weekly.parse import WeeklyParseError, norm, parse_weekly
from tmd_plain.doctypes.weekly.runner import summarize_weekly
from tmd_plain.prep.extract import document_from_pdf
from tmd_plain.prep.pdf_text import PdfTextError
from tmd_plain.raw_io import load_weekly

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORT = ROOT / "docs" / "results" / "weekly-check.md"
CELLS = ("rain_max", "temp_max", "temp_min")


def main() -> int:
    raws = load_weekly(RAW)
    errors: list[str] = []
    notes: list[str] = []
    filled: Counter[str] = Counter()
    second: Counter[str] = Counter()
    two_paragraphs = 0
    echoed: list[str] = []
    for raw in raws:
        text = raw.txt.read_text(encoding="utf-8")
        where = f"weekly/{raw.issue_id}"
        try:
            parsed = parse_weekly(text)
        except WeeklyParseError as exc:
            errors.append(f"{where}: แยกโครงไม่ได้: {exc}")
            continue
        summary = assemble_weekly(parsed, raw.issue_id)
        errors += [f"{where}: {m}" for m in check_weekly(summary, parsed)]
        if isinstance(summarize_weekly(text, raw.issue_id), SummarizeError):
            errors.append(f"{where}: summarize_weekly ล้ม")
        if raw.issue_id[:8] != summary.issued_at.strftime("%d%m%Y"):
            errors.append(f"{where}: วันของรหัสรอบไม่ตรงบรรทัดออกประกาศ {parsed.issued_line}")
        elif raw.issue_id[8:10] != summary.issued_at.strftime("%H"):
            notes.append(f"{where}: ชั่วโมงของรหัสรอบต่างจาก {parsed.issued_line}")
        two_paragraphs += len(parsed.overview) > 1
        for key, region in parsed.regions.items():
            cell_norms = {norm(c) for c in region.cells if c}
            if any(norm(p) in cell_norms for p in region.paragraphs):
                echoed.append(f"{where}: ภาค {key} ไม่มีย่อหน้า ต้นฉบับใส่ข้อความช่องตารางแทน")
        for key in REGION_KEYS:
            region = summary.regions[key]
            for name in CELLS:
                cell = getattr(region, name)
                if cell is not None:
                    filled[name] += 1
                    second[name] += "second_value" in cell.facts
    pdfs = sorted((RAW / "weekly").glob("*.pdf"))
    wrong: list[str] = []
    unreadable = 0
    for pdf in pdfs:
        try:
            doc = document_from_pdf(pdf.read_bytes())
        except PdfTextError:
            unreadable += 1
            continue
        if spec_for(doc.text).key != "generic":
            wrong.append(pdf.name)
    errors += [f"PDF {name}: ถูกตรวจเป็นชนิดอื่นที่ไม่ใช่โหมดทั่วไป" for name in wrong]
    lines = [
        "# ตรวจสรุปรายสัปดาห์ (Phase 11.5)",
        "",
        "สร้างโดย `scripts/check_weekly.py` (อย่าแก้ด้วยมือ) · แหล่ง: ข้อความหน้าเว็บที่เก็บใน `data/raw/weekly/`",
        "",
        f"- ฉบับ: {len(raws)} · ข้อผิดพลาด: {len(errors)} · ภาพรวม 2 ย่อหน้า: {two_paragraphs} ฉบับ",
        f"- ช่องตารางที่มีค่า (จาก {len(raws) * len(REGION_KEYS)} ภาค×ฉบับ): "
        + ", ".join(f"{name} {filled[name]}" for name in CELLS)
        + " · ช่องที่มีค่าที่สองในวงเล็บ: "
        + ", ".join(f"{name} {second[name]}" for name in CELLS),
        f"- PDF {len(pdfs)} ไฟล์ (แผนที่คนละเลย์เอาต์): อ่านไม่ได้ {unreadable}, ไม่ถูกตรวจเป็นชนิดอื่น {len(pdfs) - unreadable - len(wrong)} (ไปโหมดทั่วไป)",
        f"- ข้อสังเกตรหัสรอบ: {len(notes)} · ภาคที่ต้นฉบับไม่มีย่อหน้า: {len(echoed)}",
        "",
        "## ข้อผิดพลาด",
        "",
        *([f"- {e}" for e in errors] or ["- ไม่มี"]),
        "",
        "## ข้อสังเกตรหัสรอบ (รหัสรอบของหน้าเว็บใช้เป็น issue_id เพราะเป็นรหัสที่ลิงก์ในหน้า TMD ใช้)",
        "",
        *([f"- {n}" for n in notes] or ["- ไม่มี"]),
        "",
        "## ภาคที่ต้นฉบับไม่มีย่อหน้า (ข้อบกพร่องของหน้าต้นทาง: ข้อความสถานีฝนอยู่ที่ย่อหน้าและซ้ำในตาราง คัดตามต้นฉบับ ไม่แก้)",
        "",
        *([f"- {n}" for n in echoed] or ["- ไม่มี"]),
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(
        f"issues {len(raws)} · pdf generic {len(pdfs) - unreadable - len(wrong)}/{len(pdfs)} · errors: {len(errors)}"
    )
    for e in errors[:20]:
        print(e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
