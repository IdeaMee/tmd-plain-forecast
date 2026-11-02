"""แปลงวลีช่วงวันแบบไทย (พ.ศ.) เป็นวันที่ ISO และแบ่งบล็อกภาคของพยากรณ์ 7 วันตามช่วงวัน.

ตัวอย่าง: "ในช่วงวันที่ 17 - 19 พ.ย. 69", "ส่วนในช่วงวันที่ 30 ต.ค. - 1 พ.ย. 69", "16 – 22 พฤศจิกายน พ.ศ. 2569"
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

MONTHS: dict[str, int] = {
    "ม.ค.": 1, "ก.พ.": 2, "มี.ค.": 3, "เม.ย.": 4, "พ.ค.": 5, "มิ.ย.": 6,
    "ก.ค.": 7, "ส.ค.": 8, "ก.ย.": 9, "ต.ค.": 10, "พ.ย.": 11, "ธ.ค.": 12,
    "มกราคม": 1, "กุมภาพันธ์": 2, "มีนาคม": 3, "เมษายน": 4, "พฤษภาคม": 5, "มิถุนายน": 6,
    "กรกฎาคม": 7, "สิงหาคม": 8, "กันยายน": 9, "ตุลาคม": 10, "พฤศจิกายน": 11, "ธันวาคม": 12,
}  # fmt: skip
_MONTH = "|".join(re.escape(m) for m in sorted(MONTHS, key=len, reverse=True))
# วันเริ่มอาจมีเดือนและปีของตัวเอง เช่น "31 ต.ค. 69 – 2 พ.ย. 69"
_RANGE = re.compile(
    rf"(?P<d1>\d{{1,2}})(?:\s*(?P<m1>{_MONTH})(?:\s*(?:พ\.ศ\.)?\s*(?P<y1>\d{{2,4}}))?)?"
    rf"\s*[-–]\s*(?P<d2>\d{{1,2}})\s*(?P<m2>{_MONTH})\s*(?:พ\.ศ\.)?\s*(?P<y2>\d{{2,4}})"
)
_SINGLE = re.compile(rf"(\d{{1,2}})\s*(?P<m>{_MONTH})\s*(?:พ\.ศ\.)?\s*(\d{{2,4}})")
PERIOD_START = re.compile(r"^(ส่วน)?ในช่วงวันที่")


def _ce_year(text: str) -> int:
    # ปี พ.ศ. 2 หลัก (69) หรือ 4 หลัก (2569) -> ค.ศ.
    year = int(text)
    if year < 100:
        year += 2500
    return year - 543


def parse_date_range(text: str) -> tuple[date, date] | None:
    """ช่วงวันแรกที่พบในข้อความ; วันเดียวคืน (d, d); ไม่พบคืน None."""
    m = _RANGE.search(text)
    if m:
        d1, d2 = int(m.group("d1")), int(m.group("d2"))
        year = _ce_year(m.group("y2"))
        m2 = MONTHS[m.group("m2")]
        if m.group("m1"):
            m1 = MONTHS[m.group("m1")]
        else:
            m1 = m2 - 1 if d1 > d2 else m2  # "30 - 2 พ.ย." = 30 ต.ค. ถึง 2 พ.ย.
            m1 = m1 or 12
        if m.group("y1"):
            start_year = _ce_year(m.group("y1"))
        else:
            start_year = year - 1 if m1 > m2 else year  # ข้ามปี เช่น 30 ธ.ค. - 2 ม.ค.
        try:
            return date(start_year, m1, d1), date(year, m2, d2)
        except ValueError:
            return None
    m = _SINGLE.search(text)
    if m:
        try:
            d = date(_ce_year(m.group(3)), MONTHS[m.group("m")], int(m.group(1)))
        except ValueError:
            return None
        return d, d
    return None


_DATE_LEAD = re.compile(r"^(ส่วน)?ใน(ช่วง)?วันที่\s*")


def is_date_phrase(text: str) -> bool:
    """ข้อความเป็นแค่วลีวันที่ล้วน เช่น "ส่วนในช่วงวันที่ 6–11 พ.ย. 69" (ไม่มีเนื้อหาอื่นต่อท้าย)."""
    lead = _DATE_LEAD.match(text.strip())
    if not lead:
        return False
    rest = text.strip()[lead.end() :]
    m = _RANGE.match(rest) or _SINGLE.match(rest)
    return bool(m) and not rest[m.end() :].strip()


@dataclass(frozen=True)
class PeriodBlock:
    start: date | None
    end: date | None
    lines: tuple[str, ...]
    explicit: bool  # True = ขึ้นต้นด้วยวลีช่วงวัน; False = บรรทัดก่อนวลีแรก (ใช้ทั้งช่วงของฉบับ)


def split_periods(
    lines: tuple[str, ...] | list[str], issue_range: tuple[date, date] | None
) -> tuple[PeriodBlock, ...]:
    """แบ่งบรรทัดของบล็อกภาค 7 วัน: เริ่มช่วงใหม่เมื่อบรรทัดขึ้นต้นด้วย "(ส่วน)ในช่วงวันที่".

    วลีช่วงวันที่อยู่กลางบรรทัด (เช่น "...โดยมีฝนตกหนักมากในช่วงวันที่ 20 - 22 พ.ย. 69") เป็นแค่ข้อความ ไม่ใช่ช่วงใหม่
    """
    blocks: list[PeriodBlock] = []
    current: list[str] = []
    start: date | None = issue_range[0] if issue_range else None
    end: date | None = issue_range[1] if issue_range else None
    explicit = False
    for line in lines:
        if PERIOD_START.match(line):
            if current:
                blocks.append(PeriodBlock(start, end, tuple(current), explicit))
            parsed = parse_date_range(line)
            start, end = parsed if parsed else (None, None)
            explicit = True
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(PeriodBlock(start, end, tuple(current), explicit))
    return tuple(blocks)


@dataclass(frozen=True)
class DatePhrase:
    text: str
    start: int
    end: int


# วลีช่วงวันกลางบรรทัด เช่น "หลังจากนั้นในช่วงวันที่ 19 – 20 พ.ย. 69", "ในช่วงวันที่ 16 และ 18 - 19 พ.ย. 69",
# "ในช่วงวันที่ 30 - 31 ต.ค. และ 1 – 2 พ.ย. 69", "31 ต.ค. 69 – 2 พ.ย. 69", "ช่วงวันที่ 18 - 19 พ.ย. 69"
_FILL = rf"(?:[0-9\s,\-–]|และ|{_MONTH})"
_END = rf"(?:{_MONTH})\s*(?:พ\.ศ\.)?\s*\d{{2,4}}"
_PHRASE = re.compile(
    rf"(?:(?:ส่วน|หลังจากนั้น)?ใน)?(?:ช่วงวันที่|ช่วง|วันที่)\s*\d{{1,2}}{_FILL}*?{_END}(?:\s*(?:และ|[-–]){_FILL}*?{_END})*"
)
_TOKEN = re.compile(rf"\d+|{_MONTH}")


def _phrase_dates(text: str) -> tuple[date, date] | None:
    """วันแรกและวันสุดท้ายของวลี: วันที่ยังไม่มีเดือนใช้เดือนถัดไปที่พบ ตัวเลขเกิน 31 คือปี พ.ศ."""
    days: list[int] = []
    pairs: list[tuple[int, int]] = []
    year: int | None = None
    for tok in _TOKEN.findall(text):
        if tok in MONTHS:
            pairs += [(MONTHS[tok], d) for d in days]
            days = []
        elif int(tok) > 31:
            year = _ce_year(tok)
        else:
            days.append(int(tok))
    if year is None or not pairs:
        return None
    last_month = pairs[-1][0]
    try:
        # เดือนที่มากกว่าเดือนสุดท้าย = ปีก่อน (ข้ามปี ธ.ค. -> ม.ค.)
        dates = [date(year - (m > last_month), m, d) for m, d in pairs]
    except ValueError:
        return None
    return min(dates), max(dates)


def find_date_phrases(text: str) -> list[tuple[DatePhrase, date, date]]:
    """วลีช่วงวันทุกวลีในข้อความ พร้อมวันเริ่ม/วันสิ้นสุด (ข้ามวลีที่แปลงวันที่ไม่ได้)."""
    out: list[tuple[DatePhrase, date, date]] = []
    for m in _PHRASE.finditer(text):
        dates = _phrase_dates(m.group(0))
        if dates is not None:
            out.append((DatePhrase(m.group(0).strip(), m.start(), m.end()), *dates))
    return out
