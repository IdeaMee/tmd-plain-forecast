"""Phase 3.4: รันท่อประมวลผลกับทุกฉบับที่แสดงบนเว็บ -> data/processed/<doc_type>/<issue_id>.json.

รัน: .venv/Scripts/python.exe -X utf8 scripts/run_pipeline.py
แหล่งข้อความ: หน้าเว็บ (.txt) ก่อน ถ้าไม่มีใช้ PDF (RawIssue.preferred) · ผลซ้ำได้ (ไม่มีเวลาประมวลผลในไฟล์)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tmd_plain.classify.model_io import load_labeler
from tmd_plain.contract import Issue, SummarizeError
from tmd_plain.extract.advice import Labeler
from tmd_plain.generate.assemble import IssueMeta, default_source_label, issued_at_from_id
from tmd_plain.pipeline import summarize
from tmd_plain.raw_io import RawIssue, load_manifest

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"


def display_issues() -> list[RawIssue]:
    return [i for i in load_manifest(RAW) if i.role == "display_test"]


def meta_for(issue: RawIssue) -> IssueMeta:
    return IssueMeta(
        issue_id=issue.issue_id,
        issued_at=issued_at_from_id(issue.doc_type, issue.issue_id),  # type: ignore[arg-type]
        source_label=issue.label or default_source_label(issue.doc_type, issue.issue_id),  # type: ignore[arg-type]
    )


def run_one(issue: RawIssue, label_of: Labeler) -> Issue | SummarizeError:
    return summarize(issue.preferred(), meta_for(issue), label_of)


def render(issue: Issue) -> str:
    return (
        json.dumps(issue.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, indent=2)
        + "\n"
    )


def out_path(issue: RawIssue) -> Path:
    return OUT / issue.doc_type / f"{issue.issue_id}.json"


def main() -> int:
    label_of = load_labeler(ROOT / "models")
    failed = 0
    count = {"daily": 0, "sevenday": 0}
    for issue in display_issues():
        result = run_one(issue, label_of)
        if isinstance(result, SummarizeError):
            failed += 1
            print(f"FAIL {issue.doc_type}/{issue.issue_id}: {result.error.code}")
            continue
        path = out_path(issue)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(result), encoding="utf-8", newline="\n")
        count[issue.doc_type] += 1
    print(
        f"wrote daily {count['daily']} sevenday {count['sevenday']} -> data/processed · failed {failed}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
