"""แบ่งชุดข้อมูลตามวัน (docs/spec/labeling-guideline.md หัวข้อ 6, ADR 0007).

ปฏิทิน: ทดสอบ = วันล่าสุด N วัน, เว้น, dev, เว้น, ที่เหลือ = ฝึก (ค่าใน config.toml [split])
หน่วยถ้อยคำเดียวกันอยู่ชุดเดียว: ใช้ชุดของวันแรกที่หน่วยนั้นปรากฏ (ถ้าเคยอยู่ในชุดฝึก ก็อยู่ชุดฝึก)
หน่วยที่ปรากฏครั้งแรกในวันที่เว้นไว้ได้ชุด "gap" และไม่ถูกใช้ทั้งฝึกและวัดผล
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

SplitName = Literal["train", "dev", "test", "gap"]


@dataclass(frozen=True)
class SplitCalendar:
    train_end: date
    dev_start: date
    dev_end: date
    test_start: date
    test_end: date

    def split_of(self, day: date) -> SplitName:
        if day >= self.test_start:
            return "test"
        if self.dev_start <= day <= self.dev_end:
            return "dev"
        if day <= self.train_end:
            return "train"
        return "gap"


def make_calendar(last_day: date, test_days: int, dev_days: int, gap_days: int) -> SplitCalendar:
    test_start = last_day - timedelta(days=test_days - 1)
    dev_end = test_start - timedelta(days=gap_days + 1)
    dev_start = dev_end - timedelta(days=dev_days - 1)
    train_end = dev_start - timedelta(days=gap_days + 1)
    return SplitCalendar(train_end, dev_start, dev_end, test_start, last_day)


def issue_date(doc_type: str, issue_id: str) -> date:
    """วันของฉบับจากรหัส: รายวัน DDMMYYYYHHMM, 7 วัน YYMMDD (ปี ค.ศ.)."""
    if doc_type == "daily":
        return date(int(issue_id[4:8]), int(issue_id[2:4]), int(issue_id[0:2]))
    return date(2000 + int(issue_id[0:2]), int(issue_id[2:4]), int(issue_id[4:6]))


def assign_split(days: list[date], calendar: SplitCalendar) -> SplitName:
    """ชุดของหน่วย = ชุดของวันแรกที่ปรากฏ."""
    return calendar.split_of(min(days))
