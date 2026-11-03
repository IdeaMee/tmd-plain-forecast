"""Phase 2.1: แบ่งหน่วยใน data/labeled/units.csv เป็นชุดฝึก/dev/ทดสอบตามวัน -> data/labeled/split.csv.

รัน: .venv/Scripts/python.exe -X utf8 scripts/make_split.py
คอลัมน์ test_occurrences = จำนวนฉบับในช่วงวันทดสอบที่มีหน่วยนี้ (ใช้รายงานผลแบบ "ทุกหน่วยในวันทดสอบ"
ซึ่งรวมประโยคที่ซ้ำกับชุดฝึก) ส่วนชุด test = หน่วยที่ถ้อยคำไม่เคยปรากฏก่อนช่วงทดสอบ (รายงานแบบ "ถ้อยคำใหม่")
"""

from __future__ import annotations

import csv
import io
import sys
from collections import Counter
from pathlib import Path

from tmd_plain.classify.keyword import keyword_label
from tmd_plain.classify.split import assign_split, issue_date, make_calendar
from tmd_plain.config import load_config

ROOT = Path(__file__).resolve().parents[1]
UNITS = ROOT / "data" / "labeled" / "units.csv"
OUT = ROOT / "data" / "labeled" / "split.csv"
COLUMNS = ["unit_id", "doc_type", "first_seen", "split", "test_occurrences", "keyword_label"]


def main() -> int:
    units = list(csv.DictReader(UNITS.open(encoding="utf-8-sig", newline="")))
    days_by_unit = {
        u["unit_id"]: [issue_date(u["doc_type"], i) for i in u["appears_in"].split(";")]
        for u in units
    }
    last_day = max(d for days in days_by_unit.values() for d in days)
    cfg = load_config()["split"]
    cal = make_calendar(last_day, cfg["test_days"], cfg["dev_days"], cfg["gap_days"])
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(COLUMNS)
    counts: Counter = Counter()
    for u in units:
        days = days_by_unit[u["unit_id"]]
        split = assign_split(days, cal)
        test_occ = sum(d >= cal.test_start for d in days)
        writer.writerow(
            [
                u["unit_id"],
                u["doc_type"],
                u["first_seen"],
                split,
                test_occ,
                keyword_label(u["text"]),
            ]
        )
        counts[(u["doc_type"], split)] += 1
        counts[(u["doc_type"], "in test days")] += test_occ > 0
    OUT.write_text("\ufeff" + buf.getvalue(), encoding="utf-8", newline="")
    print(
        f"calendar: train <= {cal.train_end} | dev {cal.dev_start}..{cal.dev_end} | "
        f"test {cal.test_start}..{cal.test_end}"
    )
    for doc_type in ("daily", "sevenday"):
        parts = ", ".join(f"{s}={counts[(doc_type, s)]}" for s in ("train", "dev", "test", "gap"))
        print(
            f"{doc_type}: {parts}, units appearing on test days={counts[(doc_type, 'in test days')]}"
        )
    print(f"wrote {OUT.relative_to(ROOT).as_posix()} ({len(units)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
