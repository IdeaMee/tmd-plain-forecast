"""Phase 3.4: เอกสารให้ผู้ใช้อ่านสรุปเทียบต้นฉบับ 3 ฉบับ -> docs/results/review-sheet.md.

รัน (หลัง scripts/run_pipeline.py): .venv/Scripts/python.exe -X utf8 scripts/make_review_sheet.py
"""

from __future__ import annotations

from pathlib import Path

from run_pipeline import display_issues, out_path

from tmd_plain.contract import REGION_KEYS, REGION_LABELS_TH, Issue
from tmd_plain.prep.regions import parse_issue

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "results" / "review-sheet.md"
PICK = (("daily", "161120261800"), ("daily", "131120261200"), ("sevenday", "261116"))


def main() -> int:
    raws = {(i.doc_type, i.issue_id): i for i in display_issues()}
    out = [
        "# อ่านสรุปเทียบต้นฉบับ (Phase 3.4 ส่วนของผู้ใช้)",
        "",
        "ฉบับละ 7 ภาค: **ต้นฉบับ** = บล็อกภาคของ TMD, **สรุป** = ภาษาง่ายที่ระบบเขียน · คำแนะนำคัดจากต้นฉบับตรงๆ",
        "สิ่งที่ขอให้ดู: ตัวเลข/จังหวัดตรงต้นฉบับไหม, ถ้อยคำเข้าใจง่ายไหม, คำแนะนำไปอยู่ภาคที่ถูกไหม, มีอะไรตกหล่นไหม",
        "จดรายการแก้ไว้ใต้แต่ละภาค หรือบอกผู้ช่วยในแชตได้เลย · ไฟล์นี้สร้างโดย `scripts/make_review_sheet.py`",
        "",
    ]
    for doc_type, issue_id in PICK:
        raw = raws[(doc_type, issue_id)]
        issue = Issue.model_validate_json(out_path(raw).read_text(encoding="utf-8"))
        parsed = parse_issue(raw.preferred())
        out += [
            f"## {'พยากรณ์รายวัน' if doc_type == 'daily' else 'พยากรณ์ 7 วัน'} {issue.source_label}",
            "",
        ]
        out += ["<details><summary>ย่อหน้าภาพรวมต้นฉบับ</summary>", ""]
        out += [f"> {p}" for p in (*parsed.overview, *parsed.caution)] + ["", "</details>", ""]
        for key in REGION_KEYS:
            region = issue.regions[key]
            out += [f"### {REGION_LABELS_TH[key]}", "", "**ต้นฉบับ**", ""]
            out += [f"> {ln}  " for ln in parsed.regions[key].lines] + ["", "**สรุป**", ""]
            if region.lines:
                out += [f"- {ln.text}" for ln in region.lines]
            for p in region.periods:
                out.append(f"- **{p.start.isoformat()} ถึง {p.end.isoformat()}**")
                out += [f"  - {ln.text}" for ln in p.lines]
            if region.advice:
                out += ["", "**คำแนะนำของภาคนี้**", ""] + [f"- {a.text}" for a in region.advice]
            out += ["", "รายการแก้: ", ""]
        if issue.general_advice:
            out += (
                ["### ข้อแนะนำทั่วไป (ทุกภาค)", ""]
                + [f"- {a.text}" for a in issue.general_advice]
                + [""]
            )
    REPORT.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
