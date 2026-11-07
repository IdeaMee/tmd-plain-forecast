"""Phase 3.1: ความครอบคลุมของการดึงค่าบนฉบับที่แสดงบนเว็บ -> docs/results/facts-coverage.md.

รัน: .venv/Scripts/python.exe -X utf8 scripts/check_facts.py
ตรวจทุกบรรทัดในบล็อกภาคของฉบับ display_test (ทั้งหน้าเว็บและ PDF): มีค่าอย่างน้อยหนึ่งค่า, source ของทุกค่าอยู่ในบรรทัด,
ตัวเลขทุกตัวในบรรทัดถูกดึง, จังหวัดที่พบในบล็อกอยู่ในภาคนั้นจริง (ตามตารางจังหวัด) · พิมพ์ errors: N (ต้องเป็น 0)
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

from tmd_plain.extract.facts import extract_line
from tmd_plain.extract.provinces import province_region
from tmd_plain.prep.extract import document_from_pdf, document_from_txt
from tmd_plain.prep.regions import parse_issue
from tmd_plain.raw_io import load_manifest

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORT = ROOT / "docs" / "results" / "facts-coverage.md"
NUM = re.compile(r"\d+(?:\.\d+)?")


def main() -> int:
    stats: Counter[str] = Counter()
    names: Counter[str] = Counter()
    errors: list[str] = []
    no_fact: list[str] = []
    for issue in load_manifest(RAW):
        if issue.role != "display_test":
            continue
        docs = []
        if issue.txt:
            docs.append(document_from_txt(issue.txt.read_text(encoding="utf-8")))
        if issue.pdf:
            docs.append(document_from_pdf(issue.pdf.read_bytes()))
        for doc in docs:
            stats[f"files {issue.doc_type}/{doc.kind}"] += 1
            for key, block in parse_issue(doc).regions.items():
                for text in block.lines:
                    facts = extract_line(text)
                    stats["lines"] += 1
                    stats["lines with facts"] += bool(facts)
                    if not facts:
                        no_fact.append(f"{issue.issue_id} {doc.kind} {key}: {text}")
                    covered = " ".join(f.source for f in facts)
                    missing = [n for n in NUM.findall(text) if n not in covered]
                    if missing:
                        errors.append(
                            f"ตัวเลขไม่ถูกดึง {missing}: {issue.issue_id} {doc.kind} {key}: {text}"
                        )
                    for f in facts:
                        names[f.name] += 1
                        if f.source not in text:
                            errors.append(f"source ไม่อยู่ในบรรทัด: {issue.issue_id} {f}")
                        if f.name == "province" and province_region(str(f.value)) != key:
                            errors.append(
                                f"จังหวัดผิดภาค {f.value} ใน {key}: {issue.issue_id} {doc.kind}"
                            )
    pct = stats["lines with facts"] / stats["lines"] if stats["lines"] else 0.0
    lines = [
        "# ความครอบคลุมของการดึงค่า (Phase 3.1)",
        "",
        "คำสั่ง: `.venv/Scripts/python.exe -X utf8 scripts/check_facts.py` · ไฟล์นี้สร้างโดยสคริปต์",
        "",
        "ขอบเขต: บล็อกภาคของฉบับที่แสดงบนเว็บ (`display_test` ใน MANIFEST) ทั้งข้อความหน้าเว็บและ PDF · "
        + ", ".join(
            f"{k.removeprefix('files ')} {v} ไฟล์"
            for k, v in sorted(stats.items())
            if k.startswith("files")
        ),
        "",
        "| ตรวจ | ผล |",
        "|---|---|",
        f"| บรรทัดในบล็อกภาค | {stats['lines']} |",
        f"| บรรทัดที่ได้ค่าอย่างน้อยหนึ่งค่า | {stats['lines with facts']} ({pct:.1%}) |",
        f"| ข้อผิดพลาด (ตัวเลขไม่ถูกดึง, source ไม่อยู่ในบรรทัด, จังหวัดผิดภาค) | {len(errors)} |",
        "",
        "## จำนวนค่าที่ดึงได้ แยกตามชื่อ",
        "| ชื่อ | จำนวน |",
        "|---|---|",
        *[f"| `{n}` | {c} |" for n, c in sorted(names.items())],
        "",
        f"## บรรทัดที่ไม่ได้ค่า ({len(no_fact)})",
        *([f"- {x}" for x in no_fact] or ["ไม่มี"]),
        "",
        f"## ข้อผิดพลาด ({len(errors)})",
        *([f"- {x}" for x in errors] or ["ไม่มี"]),
        "",
        "## ข้อสังเกต",
        '- วลีช่วงวันที่ไม่ต่อเนื่อง ("16 และ 18 - 19 พ.ย.") เก็บเป็นวันแรกถึงวันสุดท้าย และเก็บวลีเต็มไว้ใน `period_text`',
        '- วลีช่วงวันกลางบรรทัด ("ฝนตกหนักมากในช่วงวันที่ 20 - 22 พ.ย.") หมายถึงเฉพาะส่วนนั้น ไม่ใช่ทั้งบรรทัด ขั้นแม่แบบ (3.3) ต้องดู `period_text` คู่กับตำแหน่ง',
        "- รายชื่อจังหวัดบางบรรทัดต่อจากบรรทัดก่อน (บรรทัดที่มีแต่จังหวัด) ขั้นแม่แบบต้องรวมกับบรรทัดก่อนหน้า",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"lines: {stats['lines']} with facts: {stats['lines with facts']} ({pct:.1%})")
    for e in errors[:20]:
        print(e)
    print(f"errors: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
