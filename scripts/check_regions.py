"""Phase 1.3: ตรวจการตรวจชนิดเอกสารและการแยกภาค/ช่วงวันของทุกไฟล์ใน data/raw.

รัน: .venv/Scripts/python.exe -X utf8 scripts/check_regions.py
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

from tmd_plain.contract import REGION_KEYS
from tmd_plain.prep.extract import SourceDocument, document_from_pdf, document_from_txt
from tmd_plain.prep.periods import split_periods
from tmd_plain.prep.regions import ParsedIssue, PrepError, parse_issue
from tmd_plain.raw_io import load_manifest

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
NUM = re.compile(r"\d+(?:\.\d+)?")
NUMERIC_LINE = re.compile(r"^\d+(\.\d+)?$")
ADVICE_WORDS = ("ขอให้", "ควร", "ระวัง", "หลีกเลี่ยง", "งดออกจากฝั่ง")


def numbers(text: str) -> Counter:
    return Counter(NUM.findall(text))


def main() -> int:
    stats: Counter = Counter()
    errors: list[str] = []
    for issue in load_manifest(RAW):
        sources: list[SourceDocument] = []
        if issue.txt:
            sources.append(document_from_txt(issue.txt.read_text(encoding="utf-8")))
        if issue.pdf:
            sources.append(document_from_pdf(issue.pdf.read_bytes()))
        parsed: dict[str, ParsedIssue] = {}
        for doc in sources:
            tag = f"{issue.doc_type}/{doc.kind}"
            stats[f"files {tag}"] += 1
            try:
                p = parse_issue(doc)
            except PrepError as exc:
                stats[f"errors {tag}"] += 1
                errors.append(f"{issue.issue_id} {doc.kind}: {exc}")
                continue
            parsed[doc.kind] = p
            stats[f"doctype ok {tag}"] += p.doc_type == issue.doc_type
            stats[f"7 regions {tag}"] += set(p.regions) == set(REGION_KEYS)
            stats[f"overview found {tag}"] += bool(p.overview)
            for block in p.regions.values():
                stats["numeric-only lines left"] += sum(
                    bool(NUMERIC_LINE.match(x)) for x in block.lines
                )
                stats[f"region lines {issue.doc_type}"] += len(block.lines)
                stats[f"region lines with advice words {issue.doc_type}"] += sum(
                    any(w in x for w in ADVICE_WORDS) for x in block.lines
                )
            if p.doc_type == "sevenday":
                stats[f"issue range parsed {tag}"] += p.issue_range is not None
                periods = [
                    pb for b in p.regions.values() for pb in split_periods(b.lines, p.issue_range)
                ]
                ok = all(pb.start is not None for pb in periods) and any(
                    pb.explicit for pb in periods
                )
                stats[f"periods ok {tag}"] += ok
                if not ok:
                    errors.append(f"{issue.issue_id} {doc.kind}: period not parsed")
        if "txt" in parsed and "pdf" in parsed:
            for key in REGION_KEYS:
                want = numbers("\n".join(parsed["txt"].regions[key].lines))
                have = numbers("\n".join(parsed["pdf"].regions[key].lines))
                stats["pair blocks"] += 1
                stats["pair blocks all HTML numbers in PDF"] += not (want - have)
                stats["pair blocks identical numbers"] += want == have
    for key in sorted(stats):
        print(f"{key}: {stats[key]}")
    print(f"errors: {len(errors)}")
    for line in errors[:20]:
        print("  ", line)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
