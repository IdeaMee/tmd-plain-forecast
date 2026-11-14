"""ชุดข้อมูลติดป้ายของประกาศเตือนภัย (Phase 11.3): หน่วยไม่ซ้ำ + แบ่งชุดตามเหตุการณ์ (ฟังก์ชันบริสุทธิ์).

แบ่งตามเหตุการณ์ (ชุดประกาศจาก series.py) เรียงตามเวลา: ทดสอบ = เหตุการณ์ล่าสุด, dev = ก่อนหน้านั้น, ที่เหลือ = ฝึก
หน่วยอยู่ชุดที่ "เก่าที่สุด" ที่มันปรากฏ (ฝึก < dev < ทดสอบ) ชุด dev/ทดสอบจึงมีแต่ถ้อยคำใหม่ที่ไม่เคยอยู่ในชุดฝึก
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from tmd_plain.doctypes.warning.build import WarningUnit
from tmd_plain.doctypes.warning.parse import ParsedWarning
from tmd_plain.doctypes.warning.series import Series

SPLIT_ORDER = ("train", "dev", "test")
# ชุดป้ายของประกาศ (V7 ทางเลือก ก) ที่เดียว: สคริปต์ติดป้าย ฝึก และรายงาน /model ใช้ร่วมกัน
WARNING_LABELS = ("weather", "advice", "cause")
_SPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class UnitRow:
    unit_id: str
    text: str
    split: str
    # เหตุการณ์ (series_id) และฉบับที่หน่วยนี้ปรากฏ เรียงตามเวลา
    events: tuple[str, ...]
    issues: tuple[str, ...]
    context_prev: str
    context_next: str


def event_splits(series: list[Series], dev_events: int, test_events: int) -> dict[str, str]:
    """series_id -> train/dev/test ตามลำดับเวลาของฉบับแรก (ล่าสุดเป็นชุดทดสอบ)."""
    ordered = sorted(series, key=lambda s: s.notices[0].issued_at)
    if dev_events + test_events >= len(ordered):
        raise ValueError("เหตุการณ์ไม่พอสำหรับชุดฝึก")
    out: dict[str, str] = {}
    for i, s in enumerate(ordered):
        from_end = len(ordered) - i
        out[s.series_id] = (
            "test"
            if from_end <= test_events
            else "dev"
            if from_end <= test_events + dev_events
            else "train"
        )
    return out


def build_rows(
    notices: list[tuple[ParsedWarning, list[WarningUnit]]],
    event_of: dict[str, str],
    split_of_event: dict[str, str],
) -> list[UnitRow]:
    """หน่วยไม่ซ้ำ (เทียบแบบไม่สนช่องว่าง) พร้อมบริบทจากการปรากฏครั้งแรก เรียงตามเวลาที่พบครั้งแรก."""
    first: dict[str, tuple[str, str, str, str]] = {}
    events: dict[str, list[str]] = {}
    issues: dict[str, list[str]] = {}
    for parsed, units in sorted(notices, key=lambda n: (n[0].issued_at, n[0].issue_id)):
        event = event_of[parsed.issue_id]
        for i, unit in enumerate(units):
            key = _SPACE.sub("", unit.text)
            if key not in first:
                prev = units[i - 1].text if i > 0 else ""
                nxt = units[i + 1].text if i + 1 < len(units) else ""
                first[key] = (unit.unit_id, unit.text, prev, nxt)
                events[key], issues[key] = [], []
            if event not in events[key]:
                events[key].append(event)
            if parsed.issue_id not in issues[key]:
                issues[key].append(parsed.issue_id)
    rows: list[UnitRow] = []
    for key, (unit_id, text, prev, nxt) in first.items():
        split = min((split_of_event[e] for e in events[key]), key=SPLIT_ORDER.index)
        rows.append(
            UnitRow(unit_id, text, split, tuple(events[key]), tuple(issues[key]), prev, nxt)
        )
    return rows
