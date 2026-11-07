"""Phase 1.2: ตรวจการดึงและทำความสะอาดข้อความของทุกไฟล์ใน data/raw.

รัน: .venv/Scripts/python.exe -X utf8 scripts/check_extract.py
ตรวจ (1) ทุกไฟล์อ่านได้และไม่มีอักษร PUA เหลือ (2) ตัวเลขทุกตัวในข้อความหน้าเว็บของรอบเดียวกันมีในข้อความจาก PDF
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

from tmd_plain.prep.clean import count_pua
from tmd_plain.prep.extract import document_from_pdf, document_from_txt
from tmd_plain.raw_io import load_manifest

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
NUM = re.compile(r"\d+(?:\.\d+)?")


def main() -> int:
    issues = load_manifest(RAW)
    files = pua = failed = 0
    pairs = want_total = found_total = 0
    worst: list[tuple[float, str]] = []
    for issue in issues:
        txt = document_from_txt(issue.txt.read_text(encoding="utf-8")) if issue.txt else None
        pdf = None
        if issue.pdf:
            try:
                pdf = document_from_pdf(issue.pdf.read_bytes())
            except ValueError as exc:
                failed += 1
                print(f"FAIL {issue.pdf.name}: {exc}")
        for doc in (txt, pdf):
            if doc is not None:
                files += 1
                pua += count_pua(doc.text)
        if txt and pdf:
            want, have = Counter(NUM.findall(txt.text)), Counter(NUM.findall(pdf.text))
            got = sum(min(c, have[n]) for n, c in want.items())
            total = sum(want.values())
            pairs += 1
            want_total += total
            found_total += got
            worst.append((got / total, issue.issue_id))
    print(f"files read: {files} (failed PDFs: {failed})")
    print(f"PUA characters left after cleaning: {pua}")
    print(
        f"HTML numbers found in PDF text: {found_total}/{want_total} "
        f"= {found_total / want_total:.4f} over {pairs} txt+pdf pairs"
    )
    for ratio, issue_id in sorted(worst)[:3]:
        print(f"  lowest: {issue_id} {ratio:.4f}")
    return 0 if failed == 0 and pua == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
