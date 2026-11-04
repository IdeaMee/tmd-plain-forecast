"""อ่านชุดป้ายที่ปิดแล้ว (data/labeled) เป็นแถวเดียวต่อหน่วย (ส่วน I/O ที่สคริปต์วัดผลใช้ร่วมกัน)."""

from __future__ import annotations

import csv
from pathlib import Path


def load_labeled_rows(labeled_dir: Path) -> list[dict[str, str]]:
    """units_labeled.csv รวมกับ split.csv ตาม unit_id (ต้องปิดชุดป้ายแล้ว ทุกแถวมี final_label)."""
    with (labeled_dir / "units_labeled.csv").open(encoding="utf-8-sig", newline="") as fh:
        units = list(csv.DictReader(fh))
    with (labeled_dir / "split.csv").open(encoding="utf-8-sig", newline="") as fh:
        split = {r["unit_id"]: r for r in csv.DictReader(fh)}
    if any(not u["final_label"] for u in units):
        raise SystemExit("ยังไม่ได้ปิดชุดป้าย: รัน scripts/freeze_labels.py ก่อน")
    return [{**u, **split[u["unit_id"]]} for u in units]
