"""สร้าง/อัปเดต golden file ของการแยกภาค (Phase 1.3) จากไฟล์จริง 3 ฉบับ.

รัน: .venv/Scripts/python.exe -X utf8 scripts/make_golden_regions.py
อัปเดตเมื่อจงใจเปลี่ยนตัวแยกภาคเท่านั้น และต้องอ่าน diff ก่อนเก็บ
"""

from __future__ import annotations

import json
from pathlib import Path

from tmd_plain.prep.extract import document_from_pdf, document_from_txt
from tmd_plain.prep.periods import split_periods
from tmd_plain.prep.regions import ParsedIssue, parse_issue

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "tests" / "golden" / "regions"
CASES = {
    "daily_311020261200_txt": RAW / "daily" / "daily_311020261200.txt",
    "daily_151120261800_pdf": RAW / "daily" / "daily_151120261800.pdf",
    "sevenday_261105_pdf": RAW / "sevenday" / "sevenday_261105.pdf",
}


def parsed_to_dict(p: ParsedIssue) -> dict:
    regions = {}
    for key, block in p.regions.items():
        item: dict = {"lines": list(block.lines)}
        if p.doc_type == "sevenday":
            item["periods"] = [
                {
                    "start": pb.start.isoformat() if pb.start else None,
                    "end": pb.end.isoformat() if pb.end else None,
                    "explicit": pb.explicit,
                    "n_lines": len(pb.lines),
                }
                for pb in split_periods(block.lines, p.issue_range)
            ]
        regions[key] = item
    return {
        "doc_type": p.doc_type,
        "source_kind": p.source_kind,
        "issue_range": [d.isoformat() for d in p.issue_range] if p.issue_range else None,
        "overview": list(p.overview),
        "caution": list(p.caution),
        "regions": regions,
    }


def parse_path(path: Path) -> ParsedIssue:
    if path.suffix == ".txt":
        return parse_issue(document_from_txt(path.read_text(encoding="utf-8")))
    return parse_issue(document_from_pdf(path.read_bytes()))


def render(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, path in CASES.items():
        (OUT / f"{name}.json").write_text(
            render(parsed_to_dict(parse_path(path))), encoding="utf-8", newline="\n"
        )
        print(f"wrote tests/golden/regions/{name}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
