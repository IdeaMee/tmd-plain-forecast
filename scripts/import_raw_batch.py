"""นำไฟล์ชุด JSON ที่เก็บด้วย Claude in Chrome (ADR 0015) เข้า data/raw + ต่อแถวใน MANIFEST.csv.

ใช้: .venv/Scripts/python.exe -X utf8 scripts/import_raw_batch.py <batch.json> --role sample_v2
ไฟล์ที่มีอยู่แล้วและ sha256 ตรงกันจะข้าม ถ้าไม่ตรงจะไม่เขียนทับ (นับเป็นข้อผิดพลาด)
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from tmd_plain.raw_batch import MANIFEST_FIELDS, manifest_row, parse_batch

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=Path)
    ap.add_argument("--role", required=True)
    ap.add_argument("--raw-dir", type=Path, default=RAW)
    args = ap.parse_args()

    entries = json.loads(args.batch.read_text(encoding="utf-8"))
    if not isinstance(entries, dict):
        print("errors: 1 (batch is not an object)")
        return 1
    files, errors = parse_batch(entries)

    manifest = args.raw_dir / "MANIFEST.csv"
    with manifest.open(encoding="utf-8-sig", newline="") as fh:
        known = {row["file"]: row["sha256"] for row in csv.DictReader(fh)}

    new_rows: list[dict[str, str]] = []
    skipped = 0
    for f in files:
        target = args.raw_dir / f.rel_path
        if f.rel_path in known or target.exists():
            if known.get(f.rel_path) == f.sha256:
                skipped += 1
            else:
                errors.append(f"exists with different content: {f.rel_path}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(f.data)
        new_rows.append(manifest_row(f, args.role))

    if new_rows:
        with manifest.open("a", encoding="utf-8", newline="") as fh:
            # ไฟล์เดิมใช้ CRLF (มี BOM อยู่ต้นไฟล์แล้ว ต่อท้ายจึงไม่ใส่ BOM ซ้ำ)
            w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, lineterminator="\r\n")
            w.writerows(new_rows)

    kinds: dict[str, int] = {}
    for r in new_rows:
        kinds[r["type"]] = kinds.get(r["type"], 0) + 1
    print(f"written: {len(new_rows)} {kinds}")
    print(f"skipped (same): {skipped}")
    for e in errors:
        print(f"error: {e}")
    print(f"errors: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
