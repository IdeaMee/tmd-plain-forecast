"""Phase 9.1: ตรวจ data/raw กับ MANIFEST.csv (อ่านอย่างเดียว) -> docs/results/raw-inventory.md.

ใช้: .venv/Scripts/python.exe -X utf8 scripts/check_raw.py  (ต้องพิมพ์ errors: 0)
"""

from __future__ import annotations

import csv
import hashlib
import sys
from collections import Counter
from pathlib import Path

import pypdfium2 as pdfium

from tmd_plain.prep.pdf_text import PdfTextError, extract_pdfium
from tmd_plain.raw_batch import DiskFile, check_inventory, text_layer_level

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORT = ROOT / "docs" / "results" / "raw-inventory.md"
# ไฟล์ประกอบในโฟลเดอร์ ไม่ใช่ข้อมูล
NOT_DATA = {"README.md", "MANIFEST.csv"}


def pdf_info(data: bytes) -> tuple[int, int]:
    """(จำนวนหน้า, จำนวนอักษรไทยที่ดึงได้) อ่านไม่ได้ = (0, 0)."""
    try:
        pages = len(pdfium.PdfDocument(data))
    except pdfium.PdfiumError:
        return 0, 0
    try:
        text = extract_pdfium(data)
    except PdfTextError:
        return pages, 0
    return pages, sum(1 for ch in text if "฀" <= ch <= "๿")


def main() -> int:
    if not (RAW / "MANIFEST.csv").exists():
        print("ไม่มี data/raw/MANIFEST.csv (ข้อมูลดิบไม่อยู่ใน repo)")
        return 1
    with (RAW / "MANIFEST.csv").open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    disk: list[DiskFile] = []
    levels: dict[str, tuple[int, int, str]] = {}
    for p in sorted(RAW.rglob("*")):
        if not p.is_file() or p.name in NOT_DATA:
            continue
        data = p.read_bytes()
        rel = p.relative_to(RAW).as_posix()
        disk.append(DiskFile(rel, len(data), hashlib.sha256(data).hexdigest()))
        if p.suffix == ".pdf":
            pages, thai = pdf_info(data)
            levels[rel] = (pages, thai, text_layer_level(thai))

    errors = check_inventory(rows, disk)

    count = Counter((r["type"], r["format"], r["role"]) for r in rows)
    lines = [
        "# คลังข้อมูลดิบ (`data/raw`)",
        "",
        "สร้างโดย `scripts/check_raw.py` (อย่าแก้มือ) · ที่มาและวิธีเก็บ: "
        "ADR 0015, `docs/research/collection-procedure.md`",
        "",
        f"ไฟล์ข้อมูล {len(disk)} ไฟล์ · แถว MANIFEST {len(rows)} แถว · ข้อผิดพลาด {len(errors)}",
        "",
        "## จำนวนต่อชนิด",
        "| ชนิด | รูปแบบ | บทบาท | ไฟล์ |",
        "|---|---|---|---|",
    ]
    lines += [f"| {t} | {f} | {r} | {n} |" for (t, f, r), n in sorted(count.items())]
    lines += [
        "",
        "## ชั้นข้อความของ PDF ที่เก็บรอบ v2",
        "นับอักษรไทยที่ pypdfium2 ดึงได้ทั้งไฟล์ (yes ≥ 200, low 1-199, none 0)"
        " เป็นการคัดกรองคร่าว ๆ เท่านั้น ประตูจริงของรอบ 2 อยู่ใน Phase 12.1",
        "",
        "| ไฟล์ | หน้า | อักษรไทย | ชั้นข้อความ |",
        "|---|---|---|---|",
    ]
    v2 = {r["file"] for r in rows if r["role"] not in {"display_test", "train_pool"}}
    for rel in sorted(levels):
        if rel in v2:
            pages, thai, level = levels[rel]
            lines.append(f"| `{rel}` | {pages} | {thai} | {level} |")
    if errors:
        lines += ["", "## ข้อผิดพลาด", *[f"- {e}" for e in errors]]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for (t, f, r), n in sorted(count.items()):
        print(f"{t:9} {f:4} {r:13} {n}")
    for e in errors:
        print(f"error: {e}")
    print(f"files: {len(disk)} rows: {len(rows)}")
    print(f"errors: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
