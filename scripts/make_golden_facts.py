"""สร้าง/อัปเดต golden file ของการดึงค่า (Phase 3.1) จากฉบับจริง 5 ฉบับ (รายวัน 3, 7 วัน 2).

รัน: .venv/Scripts/python.exe -X utf8 scripts/make_golden_facts.py
อัปเดตเมื่อจงใจเปลี่ยนตัวดึงค่าเท่านั้น และต้องอ่าน diff ก่อนเก็บ
"""

from __future__ import annotations

import json
from pathlib import Path

from tmd_plain.extract.facts import extract_block
from tmd_plain.prep.extract import document_from_pdf, document_from_txt
from tmd_plain.prep.regions import ParsedIssue, parse_issue

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "tests" / "golden" / "facts"
CASES = {
    "daily_101120260000_txt": RAW / "daily" / "daily_101120260000.txt",
    "daily_131120261200_pdf": RAW / "daily" / "daily_131120261200.pdf",
    "daily_161120261800_txt": RAW / "daily" / "daily_161120261800.txt",
    "sevenday_261112_pdf": RAW / "sevenday" / "sevenday_261112.pdf",
    "sevenday_261116_txt": RAW / "sevenday" / "sevenday_261116.txt",
}


def parse_path(path: Path) -> ParsedIssue:
    if path.suffix == ".txt":
        return parse_issue(document_from_txt(path.read_text(encoding="utf-8")))
    return parse_issue(document_from_pdf(path.read_bytes()))


def facts_to_dict(p: ParsedIssue) -> dict:
    regions = {}
    for key, block in p.regions.items():
        facts = extract_block(block.lines)
        regions[key] = [
            {
                "text": text,
                "facts": [[f.name, f.value, f.source] for f in facts if f.line == i],
            }
            for i, text in enumerate(block.lines)
        ]
    return {"doc_type": p.doc_type, "source_kind": p.source_kind, "regions": regions}


def render(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, path in CASES.items():
        (OUT / f"{name}.json").write_text(
            render(facts_to_dict(parse_path(path))), encoding="utf-8", newline="\n"
        )
        print(f"wrote tests/golden/facts/{name}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
