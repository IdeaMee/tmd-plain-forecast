"""สร้าง/อัปเดต golden file ของผลสรุปทั้งฉบับ (Phase 3.3) จากฉบับจริง 3 ฉบับ (รายวัน 2, 7 วัน 1).

รัน: .venv/Scripts/python.exe -X utf8 scripts/make_golden_issues.py
อัปเดตเมื่อจงใจเปลี่ยนแม่แบบ/การเลือกคำแนะนำเท่านั้น และต้องอ่าน diff ก่อนเก็บ
"""

from __future__ import annotations

import json
from pathlib import Path

from tmd_plain.classify.model_io import load_labeler
from tmd_plain.contract import Issue
from tmd_plain.generate.assemble import (
    IssueMeta,
    assemble_issue,
    default_source_label,
    issued_at_from_id,
)
from tmd_plain.prep.extract import document_from_pdf, document_from_txt
from tmd_plain.prep.regions import ParsedIssue, parse_issue
from tmd_plain.raw_io import load_manifest

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "tests" / "golden" / "issues"
# (ชนิด, รหัสฉบับ, แหล่งข้อความ)
CASES = {
    "daily_161120261800_txt": ("daily", "161120261800", "txt"),
    "daily_131120261200_pdf": ("daily", "131120261200", "pdf"),
    "sevenday_261116_txt": ("sevenday", "261116", "txt"),
}


def source_path(name: str) -> Path:
    doc_type, issue_id, kind = CASES[name]
    return RAW / doc_type / f"{doc_type}_{issue_id}.{kind}"


def build(name: str) -> tuple[Issue, ParsedIssue]:
    doc_type, issue_id, kind = CASES[name]
    path = source_path(name)
    doc = (
        document_from_txt(path.read_text(encoding="utf-8"))
        if kind == "txt"
        else document_from_pdf(path.read_bytes())
    )
    parsed = parse_issue(doc)
    labels = {(i.doc_type, i.issue_id): i.label for i in load_manifest(RAW)}
    meta = IssueMeta(
        issue_id=issue_id,
        issued_at=issued_at_from_id(doc_type, issue_id),  # type: ignore[arg-type]
        source_label=labels.get((doc_type, issue_id)) or default_source_label(doc_type, issue_id),  # type: ignore[arg-type]
    )
    return assemble_issue(parsed, meta, load_labeler(ROOT / "models")), parsed


def render(issue: Issue) -> str:
    data = issue.model_dump(mode="json")
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in CASES:
        issue, _ = build(name)
        (OUT / f"{name}.json").write_text(render(issue), encoding="utf-8", newline="\n")
        print(f"wrote tests/golden/issues/{name}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
