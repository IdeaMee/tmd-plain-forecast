import csv
from datetime import date
from pathlib import Path

import pytest

from tmd_plain.classify.split import assign_split, issue_date, make_calendar

ROOT = Path(__file__).resolve().parents[2]
CAL = make_calendar(date(2026, 11, 16), test_days=7, dev_days=2, gap_days=1)


def test_calendar_matches_spec() -> None:
    # ฝึก 14 วันเก่าสุด (ถึง 5 พ.ย.), เว้น 6 พ.ย., dev 7-8 พ.ย., เว้น 9 พ.ย., ทดสอบ 10-16 พ.ย.
    assert CAL.train_end == date(2026, 11, 5)
    assert (CAL.dev_start, CAL.dev_end) == (date(2026, 11, 7), date(2026, 11, 8))
    assert (CAL.test_start, CAL.test_end) == (date(2026, 11, 10), date(2026, 11, 16))
    assert CAL.split_of(date(2026, 11, 6)) == "gap"
    assert CAL.split_of(date(2026, 11, 9)) == "gap"
    assert CAL.split_of(date(2026, 10, 23)) == "train"


def test_unit_goes_to_the_split_of_its_first_day() -> None:
    assert assign_split([date(2026, 11, 14), date(2026, 11, 1)], CAL) == "train"
    assert assign_split([date(2026, 11, 8), date(2026, 11, 12)], CAL) == "dev"
    assert assign_split([date(2026, 11, 12)], CAL) == "test"
    assert assign_split([date(2026, 11, 9), date(2026, 11, 12)], CAL) == "gap"


@pytest.mark.parametrize(
    ("doc_type", "issue_id", "expected"),
    [("daily", "311020261200", date(2026, 10, 31)), ("sevenday", "261116", date(2026, 11, 16))],
)
def test_issue_date(doc_type: str, issue_id: str, expected: date) -> None:
    assert issue_date(doc_type, issue_id) == expected


def test_split_file_is_consistent_with_units() -> None:
    split_path = ROOT / "data" / "labeled" / "split.csv"
    units_path = ROOT / "data" / "labeled" / "units.csv"
    if not split_path.exists():
        pytest.skip("ยังไม่ได้รัน scripts/make_split.py")
    units = {r["unit_id"]: r for r in csv.DictReader(units_path.open(encoding="utf-8-sig"))}
    rows = list(csv.DictReader(split_path.open(encoding="utf-8-sig")))
    assert [r["unit_id"] for r in rows] == list(units)  # ทุกหน่วยมีชุดเดียว เรียงเหมือนตารางหน่วย
    for r in rows:
        first = min(
            issue_date(r["doc_type"], i) for i in units[r["unit_id"]]["appears_in"].split(";")
        )
        assert r["split"] == CAL.split_of(first)
        if r["split"] == "test":
            # หน่วยชุดทดสอบต้องไม่เคยปรากฏก่อนช่วงทดสอบ (กันข้อมูลรั่ว)
            assert first >= CAL.test_start
