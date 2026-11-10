"""ช่วงข้อความที่ไฮไลต์ในโหมดทั่วไป: วันที่, ตัวเลข(+หน่วย), จังหวัด, ภาค · คืนข้อความคำต่อคำเท่านั้น."""

from __future__ import annotations

import re

from tmd_plain.contract import REGION_KEYS, RegionKey
from tmd_plain.extract.provinces import PROVINCE_RE
from tmd_plain.extract.scope import locations
from tmd_plain.prep.periods import MONTHS

_FULL = [m for m in MONTHS if "." not in m]
_ABBR = [m for m in MONTHS if "." in m]
_FULL_RX = "|".join(re.escape(m) for m in sorted(_FULL, key=len, reverse=True))
_ABBR_RX = "|".join(re.escape(m) for m in sorted(_ABBR, key=len, reverse=True))
_DASH = r"\s*[-–]\s*"
# ปี: 4 หลัก (พ.ศ. หรือ ค.ศ.) หรือ 2 หลักติดเดือนย่อ ("พ.ย.69")
_YEAR = r"(?:\s*(?:พ\.ศ\.)?\s*(?:25|20)\d{2}(?!\d))"
_DATE = re.compile(
    # 16 – 30 พฤศจิกายน พ.ศ. 2569 / 10-12 พ.ย. / 11 พ.ย.69
    rf"\d{{1,2}}(?:{_DASH}\d{{1,2}})?\s*(?:(?:{_FULL_RX}){_YEAR}?|(?:{_ABBR_RX})(?:\d{{2}}(?!\d)|{_YEAR})?)"
    # เดือนพฤศจิกายน 2569 – มกราคม 2570 / มีนาคม – พฤษภาคม 2570
    rf"|(?:เดือน)?(?:{_FULL_RX})(?:{_YEAR})?(?:{_DASH}(?:{_FULL_RX}))?{_YEAR}"
)
_UNITS = (
    "มิลลิเมตร",
    "มม.",
    "องศาเซลเซียส",
    "°ซ.",
    "กิโลเมตร",
    "กม./ชม.",
    "กม.",
    "เมตร",
    "นอต",
    "มิลลิบาร์",
    "%",
    "ของพื้นที่",
    "ชั่วโมง",
    "วัน",
)
_UNIT_RX = "|".join(re.escape(u) for u in sorted(_UNITS, key=len, reverse=True))
_NUM = r"\d+(?:[.,]\d+)?"
_NUMBER = re.compile(rf"(?:ร้อยละ\s*)?{_NUM}(?:{_DASH}{_NUM})?(?:\s*(?:{_UNIT_RX}))?")


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def date_spans(text: str) -> list[tuple[int, int]]:
    return [m.span() for m in _DATE.finditer(text)]


def dates(text: str) -> list[str]:
    return _unique([m.group(0).strip() for m in _DATE.finditer(text)])


def numbers(text: str) -> list[str]:
    """ตัวเลข/ช่วงตัวเลขพร้อมหน่วยที่ตามมา ไม่นับตัวเลขที่เป็นส่วนของวันที่."""
    taken = date_spans(text)
    out = []
    for m in _NUMBER.finditer(text):
        if any(a < m.end() and m.start() < b for a, b in taken):
            continue
        out.append(m.group(0).strip())
    return _unique(out)


# ชื่อจังหวัดที่เป็นคำทั่วไปด้วย ("ไม่เลย", "ตากแดด", "แพร่กระจาย") นับเป็นจังหวัดเฉพาะเมื่อมี "จ." หรือ "จังหวัด" นำ
# พยากรณ์รายวันเขียนชื่อจังหวัดเป็นรายการเสมอจึงไม่ต้องกัน แต่เอกสารอื่นเป็นความเรียง
AMBIGUOUS_PROVINCES = frozenset({"เลย", "ตาก", "แพร่", "น่าน", "ตราด", "ตรัง"})
_PROVINCE_LEAD = re.compile(r"(?:จ\.|จังหวัด)\s*$")


def _province_matches(text: str) -> list[re.Match[str]]:
    out = []
    for m in PROVINCE_RE.finditer(text):
        if m.group(0) in AMBIGUOUS_PROVINCES and not _PROVINCE_LEAD.search(text[: m.start()]):
            continue
        out.append(m)
    return out


def provinces(text: str) -> list[str]:
    # ชื่อตามที่เขียนในต้นฉบับ (รวมคำสะกดผิดที่รู้จัก)
    return _unique([m.group(0) for m in _province_matches(text)])


def regions(text: str) -> list[RegionKey]:
    """ภาคจากคำบอกที่ตั้งในหน่วย ตามตารางแมปภาค v1 (extract/scope.py) เรียงตาม REGION_KEYS.

    ชื่อจังหวัดกำกวมที่ไม่มี "จ." นำ ถูกปิดด้วยช่องว่างก่อนส่งให้ locations ไม่ให้กลายเป็นภาค
    """
    masked = text
    keep = {m.span() for m in _province_matches(text)}
    for m in PROVINCE_RE.finditer(text):
        if m.span() not in keep:
            masked = masked[: m.start()] + " " * (m.end() - m.start()) + masked[m.end() :]
    found = locations(masked)
    return [k for k in REGION_KEYS if k in found]
