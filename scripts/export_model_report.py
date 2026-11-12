"""Phase 8.1: รายงานโมเดลสำหรับหน้า /model -> lib/generated/model-report.json (+ schema).

รัน: .venv/Scripts/python.exe -X utf8 scripts/export_model_report.py (ผลซ้ำได้ทุกไบต์)
อ่าน data/labeled และ data/labeled/warning (ชุดป้ายที่ปิดแล้ว) เท่านั้น ไม่แก้ models/ และไม่จูนค่าใหม่ (ใช้ [classify] เดิม)
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from tmd_plain.classify.features import bag_of_words
from tmd_plain.config import load_config
from tmd_plain.labeled_io import load_labeled_rows
from tmd_plain.model_report import ModelReport, build_report

ROOT = Path(__file__).resolve().parents[1]
LABELED = ROOT / "data" / "labeled"
WARNING_LABELED = LABELED / "warning" / "units_labeled.csv"
OUT_DIR = ROOT / "lib" / "generated"
REPORT = OUT_DIR / "model-report.json"
SCHEMA = OUT_DIR / "model-report.schema.json"


def _dump(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def build() -> dict[str, str]:
    """ชื่อไฟล์ -> เนื้อไฟล์ (ใช้ทั้งตอนเขียนและในเทสต์ตรวจไฟล์เก่า)."""
    rows = load_labeled_rows(LABELED)
    bags = {r["unit_id"]: bag_of_words(r["text"]) for r in rows}
    with WARNING_LABELED.open(encoding="utf-8", newline="") as f:
        warning_rows = list(csv.DictReader(f))
    report = build_report(rows, bags, load_config()["classify"], warning_rows)
    schema = ModelReport.model_json_schema()
    schema["$comment"] = "สร้างโดย scripts/export_model_report.py ห้ามแก้มือ"
    return {
        REPORT.name: _dump(report.model_dump(mode="json")),
        SCHEMA.name: _dump(schema),
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, body in build().items():
        (OUT_DIR / name).write_text(body, encoding="utf-8", newline="\n")
        print(f"wrote {(OUT_DIR / name).relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
