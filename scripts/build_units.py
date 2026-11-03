"""Phase 1.4: สร้างตารางหน่วยไม่ซ้ำจากย่อหน้าภาพรวมและข้อควรระวังของทุกฉบับ -> data/labeled/units.csv.

รัน: .venv/Scripts/python.exe -X utf8 scripts/build_units.py
- ใช้ข้อความหน้าเว็บก่อน ถ้าไม่มีใช้ PDF (ฉบับ 7 วันย้อนหลังมีแต่ PDF)
- หน่วยถ้อยคำเดียวกัน (ไม่นับช่องว่าง) ในชนิดเอกสารเดียวกันรวมเป็นแถวเดียว เก็บรายการฉบับที่พบ
- บรรทัดในบล็อกภาคไม่อยู่ในตาราง (เป็น weather ตามตำแหน่ง) แต่นับจำนวนไว้
- ไฟล์เป็น UTF-8 มี BOM เพื่อให้เปิดใน Excel/Google Sheets แล้วภาษาไทยไม่เพี้ยน รันซ้ำได้ไฟล์เดิมทุกไบต์
"""

from __future__ import annotations

import csv
import io
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from tmd_plain.prep.regions import parse_issue
from tmd_plain.prep.units import split_section, unit_id
from tmd_plain.raw_io import RawIssue, issue_sort_key, load_manifest

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "labeled" / "units.csv"
COLUMNS = [
    "unit_id",
    "doc_type",
    "section",
    "first_seen",
    "n_issues",
    "appears_in",
    "text",
    "context_prev",
    "context_next",
    "suggested_label",
    "final_label",
    "scope",
    "reviewer",
    "note",
]
ADVICE_WORDS = ("ขอให้", "ควร", "ระวัง", "หลีกเลี่ยง", "งดออกจากฝั่ง", "ติดตาม")


@dataclass
class UnitRow:
    unit_id: str
    doc_type: str
    section: str
    first_seen: str
    text: str
    context_prev: str
    context_next: str
    appears_in: list[str] = field(default_factory=list)


def issue_date(issue: RawIssue) -> str:
    key = issue_sort_key(issue)  # YYYYMMDD...
    return f"{key[0:4]}-{key[4:6]}-{key[6:8]}"


def norm_key(text: str) -> str:
    return re.sub(r"\s+", "", text)


def build(issues: list[RawIssue]) -> tuple[list[UnitRow], dict[str, int]]:
    rows: dict[tuple[str, str], UnitRow] = {}
    stats: dict[str, int] = {}
    for issue in sorted(issues, key=lambda i: (issue_sort_key(i), i.doc_type)):
        parsed = parse_issue(issue.preferred())
        stats[f"region lines {issue.doc_type}"] = stats.get(
            f"region lines {issue.doc_type}", 0
        ) + sum(len(b.lines) for b in parsed.regions.values())
        for section, paragraphs in (("overview", parsed.overview), ("caution", parsed.caution)):
            units = split_section(paragraphs)
            stats[f"unit occurrences {issue.doc_type}"] = stats.get(
                f"unit occurrences {issue.doc_type}", 0
            ) + len(units)
            for n, text in enumerate(units):
                key = (issue.doc_type, norm_key(text))
                if key not in rows:
                    rows[key] = UnitRow(
                        unit_id=unit_id(issue.doc_type, text),
                        doc_type=issue.doc_type,
                        section=section,
                        first_seen=issue_date(issue),
                        text=text,
                        context_prev=units[n - 1] if n > 0 else "",
                        context_next=units[n + 1] if n + 1 < len(units) else "",
                    )
                if issue.issue_id not in rows[key].appears_in:
                    rows[key].appears_in.append(issue.issue_id)
    return list(rows.values()), stats


def render(rows: list[UnitRow]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(COLUMNS)
    for r in rows:
        writer.writerow(
            [
                r.unit_id,
                r.doc_type,
                r.section,
                r.first_seen,
                len(r.appears_in),
                ";".join(r.appears_in),
                r.text,
                r.context_prev,
                r.context_next,
                "",
                "",
                "",
                "",
                "",
            ]
        )
    return "\ufeff" + buf.getvalue()


def main() -> int:
    rows, stats = build(load_manifest(RAW))
    ids = [r.unit_id for r in rows]
    if len(ids) != len(set(ids)):
        print("unit_id ชนกัน", file=sys.stderr)
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(rows), encoding="utf-8", newline="")
    for doc_type in ("daily", "sevenday"):
        sub = [r for r in rows if r.doc_type == doc_type]
        lengths = [len(r.text) for r in sub]
        advice = sum(any(w in r.text for w in ADVICE_WORDS) for r in sub)
        print(
            f"{doc_type}: occurrences={stats.get(f'unit occurrences {doc_type}', 0)} "
            f"unique={len(sub)} advice-like={advice} mean_len={sum(lengths) / len(lengths):.0f} "
            f"short(<25)={sum(n < 25 for n in lengths)} region_lines={stats.get(f'region lines {doc_type}', 0)}"
        )
    print(f"total unique units: {len(rows)} -> {OUT.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
