"""แยกโครงสรุปรายสัปดาห์ (กฎล้วน) จากข้อความหน้าเว็บดิบ.

โครงจริง (100/100 ฉบับใน data/raw/weekly):
  ประเทศไทย / <ช่วงสัปดาห์> / ย่อหน้าภาพรวม (1-2) / ลักษณะอากาศรายภาค / <ช่วงสัปดาห์>
  7 ภาค: <ชื่อภาค> / ย่อหน้า (1-2) / "ปริมาณฝนสูงสุด<TAB>อุณหภูมิสูงสุด<TAB>อุณหภูมิต่ำสุด" / แถวค่า 3 ช่องคั่นด้วยแท็บ
  ออกประกาศ <วัน> <เดือน> <ปี พ.ศ.> HH:MM น.
ต้องแยกจากข้อความดิบ: การทำความสะอาดข้อความ (clean_text) แทนแท็บเป็นช่องว่างแล้วตัดท้ายบรรทัด ช่องว่างของตารางจึงหายตำแหน่ง
(ช่องว่างมีความหมาย: ฉบับหนึ่งอาจมีแค่อุณหภูมิต่ำสุด) แถวตารางจึงแยกตามแท็บก่อน แล้วค่อยทำความสะอาดทีละช่อง
(PDF ของหมวดนี้เป็นแผนที่คนละเลย์เอาต์ ไม่ผ่านตัวแยกนี้ ไปโหมดทั่วไปของ /demo)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from tmd_plain.contract import REGION_KEYS, RegionKey
from tmd_plain.prep.clean import clean_text

BANGKOK = timezone(timedelta(hours=7))
_MONTHS_TH = (
    "มกราคม กุมภาพันธ์ มีนาคม เมษายน พฤษภาคม มิถุนายน กรกฎาคม สิงหาคม กันยายน ตุลาคม พฤศจิกายน ธันวาคม"
).split()
_MONTH_RX = "|".join(_MONTHS_TH)
_RANGE = re.compile(
    rf"^(?P<d1>\d{{1,2}})\s*(?P<m1>{_MONTH_RX})\s*(?P<y1>\d{{4}})\s*-\s*"
    rf"(?P<d2>\d{{1,2}})\s*(?P<m2>{_MONTH_RX})\s*(?P<y2>\d{{4}})$"
)
_ISSUED = re.compile(
    rf"^ออกประกาศ\s*(?P<d>\d{{1,2}})\s*(?P<m>{_MONTH_RX})\s*(?P<y>\d{{4}})\s*"
    r"(?P<h>\d{1,2})[:.](?P<mi>\d{2})\s*น\.?$"
)
_SPACE = re.compile(r"\s+")

TOP = "ประเทศไทย"
REGION_SECTION = "ลักษณะอากาศรายภาค"
TABLE_HEAD = ("ปริมาณฝนสูงสุด", "อุณหภูมิสูงสุด", "อุณหภูมิต่ำสุด")
# หัวภาคตามที่หน้าเว็บเขียน (เทียบแบบไม่สนช่องว่าง)
REGION_HEADS: dict[str, RegionKey] = {
    "ภาคเหนือ": "north",
    "ภาคตะวันออกเฉียงเหนือ": "northeast",
    "ภาคกลาง": "central",
    "ภาคตะวันออก": "east",
    "ภาคใต้(ฝั่งตะวันออก)": "south_east_coast",
    "ภาคใต้(ฝั่งตะวันตก)": "south_west_coast",
    "กรุงเทพและปริมณฑล": "bangkok_vicinity",
}


class WeeklyParseError(ValueError):
    """โครงไม่ตรงสรุปรายสัปดาห์ (ไม่เดาค่า)."""


@dataclass(frozen=True)
class ParsedRegion:
    key: RegionKey
    head: str  # หัวภาคคำต่อคำ
    paragraphs: tuple[str, ...]
    # ช่องตารางคำต่อคำ: (ฝนสูงสุด, อุณหภูมิสูงสุด, อุณหภูมิต่ำสุด) ช่องว่าง = ""
    cells: tuple[str, str, str]


@dataclass(frozen=True)
class ParsedWeekly:
    week_start: date
    week_end: date
    range_line: str
    overview: tuple[str, ...]
    regions: dict[RegionKey, ParsedRegion]
    issued_at: datetime
    issued_line: str

    def default_issue_id(self) -> str:
        """รหัส DDMMYYYYHH00 จากบรรทัดออกประกาศ (รหัสรอบจริงของหน้าเว็บอาจต่างที่ชั่วโมง ดู check_weekly)."""
        return self.issued_at.strftime("%d%m%Y%H00")


def norm(text: str) -> str:
    return _SPACE.sub("", text)


def _date(day: str, month: str, year: str) -> date | None:
    try:
        return date(int(year) - 543, _MONTHS_TH.index(month) + 1, int(day))
    except ValueError:
        return None


def issued_from(line: str) -> datetime | None:
    m = _ISSUED.match(line)
    if m is None:
        return None
    day = _date(m["d"], m["m"], m["y"])
    if day is None or int(m["h"]) > 23 or int(m["mi"]) > 59:
        return None
    return datetime(day.year, day.month, day.day, int(m["h"]), int(m["mi"]), tzinfo=BANGKOK)


def _range(line: str) -> tuple[date, date] | None:
    m = _RANGE.match(line)
    if m is None:
        return None
    a, b = _date(m["d1"], m["m1"], m["y1"]), _date(m["d2"], m["m2"], m["y2"])
    return (a, b) if a and b and a <= b else None


def _cells(raw_row: str) -> tuple[str, str, str] | None:
    parts = raw_row.split("\t")
    if len(parts) != 3:
        return None
    a, b, c = (clean_text(p) for p in parts)
    return a, b, c


def parse_weekly(raw: str) -> ParsedWeekly:
    """ข้อความดิบของไฟล์ที่เก็บ (มีหัว # และแท็บ) -> โครงที่แยกแล้ว; โครงไม่ตรงโยน WeeklyParseError."""
    raw_lines = [ln for ln in raw.replace("\r\n", "\n").split("\n") if not ln.startswith("# ")]
    # (ข้อความสะอาด, บรรทัดดิบ) เฉพาะบรรทัดที่มีเนื้อหา; บรรทัดที่มีแต่แท็บ/ช่องว่างข้าม
    rows = [(clean_text(ln), ln) for ln in raw_lines]
    rows = [(c, ln) for c, ln in rows if c]
    cleaned = [c for c, _ in rows]
    if not cleaned or cleaned[0] != TOP:
        raise WeeklyParseError("ไม่ขึ้นต้นด้วย ประเทศไทย")
    if len(cleaned) < 3 or (week := _range(cleaned[1])) is None:
        raise WeeklyParseError("ไม่พบช่วงสัปดาห์หลังหัว ประเทศไทย")
    try:
        sec = cleaned.index(REGION_SECTION)
    except ValueError as exc:
        raise WeeklyParseError("ไม่พบหัวข้อ ลักษณะอากาศรายภาค") from exc
    overview = tuple(cleaned[2:sec])
    if not overview:
        raise WeeklyParseError("ไม่มีย่อหน้าภาพรวม")
    issued = issued_from(cleaned[-1])
    if issued is None:
        raise WeeklyParseError("บรรทัดสุดท้ายไม่ใช่ออกประกาศ")
    if sec + 1 >= len(cleaned) - 1 or _range(cleaned[sec + 1]) is None:
        raise WeeklyParseError("ไม่พบช่วงสัปดาห์หลังหัวข้อรายภาค")
    by_name = {norm(name): key for name, key in REGION_HEADS.items()}
    regions: dict[RegionKey, ParsedRegion] = {}
    i = sec + 2
    end = len(rows) - 1
    while i < end:
        key = by_name.get(norm(cleaned[i]))
        if key is None or key in regions:
            raise WeeklyParseError(f"หัวภาคไม่รู้จักหรือซ้ำ: {cleaned[i]}")
        head = cleaned[i]
        i += 1
        paragraphs: list[str] = []
        while i < end and tuple(c.strip() for c in rows[i][1].split("\t")) != TABLE_HEAD:
            if by_name.get(norm(cleaned[i])) is not None:
                raise WeeklyParseError(f"{head}: ไม่พบหัวตารางก่อนภาคถัดไป")
            paragraphs.append(cleaned[i])
            i += 1
        if i + 1 >= end:
            # ไม่เจอหัวตาราง หรือหัวตารางเป็นบรรทัดท้ายสุดก่อนออกประกาศ (ไม่มีแถวค่า)
            raise WeeklyParseError(f"{head}: ไม่พบหัวตารางหรือแถวค่าของตาราง")
        cells = _cells(rows[i + 1][1])
        if not paragraphs or cells is None:
            raise WeeklyParseError(f"{head}: ไม่มีย่อหน้าหรือแถวตารางไม่ครบ 3 ช่อง")
        regions[key] = ParsedRegion(key, head, tuple(paragraphs), cells)
        i += 2
    if set(regions) != set(REGION_KEYS):
        raise WeeklyParseError("ภาคไม่ครบ 7")
    return ParsedWeekly(
        week_start=week[0],
        week_end=week[1],
        range_line=cleaned[1],
        overview=overview,
        regions=regions,
        issued_at=issued,
        issued_line=cleaned[-1],
    )
