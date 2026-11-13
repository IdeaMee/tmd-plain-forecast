"""แยกพยากรณ์เดินเรือเป็นส่วน (กฎล้วน): ภาพรวม, บรรทัดออกประกาศ, บล็อก 4 พื้นที่ทะเล และตอนบน/ตอนล่าง.

โครงจริง (100/100 ฉบับใน data/raw/shipping):
  ลักษณะอากาศทั่วไป / <วันที่> / ย่อหน้าภาพรวม / ออกประกาศ <วัน> <เดือน> <ปี พ.ศ.> HH:MM น.
  พยากรณ์อากาศสำหรับเรือเดินทะเล ... / <ชื่อพื้นที่> / บรรทัดของพื้นที่ (อ่าวไทยมี "ตอนบน:" "ตอนล่าง:")
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from tmd_plain.contract import SEA_AREA_KEYS, SEA_AREA_LABELS_TH, SeaAreaKey

BANGKOK = timezone(timedelta(hours=7))
_MONTHS_TH = (
    "มกราคม กุมภาพันธ์ มีนาคม เมษายน พฤษภาคม มิถุนายน กรกฎาคม สิงหาคม กันยายน ตุลาคม พฤศจิกายน ธันวาคม"
).split()
_ISSUED = re.compile(
    r"ออกประกาศ\s*(?P<d>\d{1,2})\s*(?P<m>" + "|".join(_MONTHS_TH) + r")\s*(?P<y>\d{4})\s*"
    r"(?P<h>\d{1,2})[:.](?P<mi>\d{2})\s*น\.?"
)
_OVERVIEW_HEAD = "ลักษณะอากาศทั่วไป"
_FORECAST_HEAD = "พยากรณ์อากาศสำหรับเรือเดินทะเล"
# "ตอนบน: ลม...", "ตอนล่าง : ลม..." หรือ "อ่าวไทยตอนบน: ลม..." (16 พ.ย. 13.00 น.) ขึ้นส่วนย่อยของพื้นที่
_PART = re.compile(r"^(?:อ่าวไทย)?(?P<name>ตอนบน|ตอนล่าง)\s*:\s*(?P<rest>.*)$")
_DATE_LINE = re.compile(r"^\d{1,2}\s*(?:" + "|".join(_MONTHS_TH) + r")\s*\d{4}$")
_SPACES = re.compile(r"\s+")


class ShippingParseError(ValueError):
    """โครงไม่ตรงพยากรณ์เดินเรือ (ไม่เดา) ผู้เรียกแปลงเป็นข้อผิดพลาด extract_failed."""


@dataclass(frozen=True)
class SeaPartBlock:
    name_th: str
    lines: tuple[str, ...]


@dataclass(frozen=True)
class SeaBlock:
    key: SeaAreaKey
    name_th: str
    # บรรทัดของทั้งพื้นที่ (ก่อนส่วนย่อยแรก)
    lines: tuple[str, ...]
    parts: tuple[SeaPartBlock, ...]

    def all_lines(self) -> tuple[str, ...]:
        return (*self.lines, *(ln for p in self.parts for ln in p.lines))


@dataclass(frozen=True)
class ParsedShipping:
    overview: str  # ย่อหน้าภาพรวมทั้งหมดต่อกันเป็นก้อนเดียว (หน้าเว็บตัดบรรทัดกลางประโยค)
    issued_line: str  # บรรทัด "ออกประกาศ ..." คำต่อคำ
    issued_at: datetime
    areas: dict[SeaAreaKey, SeaBlock]

    @property
    def issue_id(self) -> str:
        return self.issued_at.strftime("%d%m%Y%H%M")


def _norm(text: str) -> str:
    return _SPACES.sub("", text)


def issued_from(line: str) -> datetime | None:
    """เวลาออกประกาศจากบรรทัด "ออกประกาศ 03 พฤศจิกายน 2569 13:00 น." (ปี พ.ศ.) ไม่ตรงรูป = None."""
    m = _ISSUED.search(line)
    if m is None:
        return None
    try:
        return datetime(
            int(m.group("y")) - 543,
            _MONTHS_TH.index(m.group("m")) + 1,
            int(m.group("d")),
            int(m.group("h")),
            int(m.group("mi")),
            tzinfo=BANGKOK,
        )
    except ValueError:
        return None


def _area_block(key: SeaAreaKey, lines: list[str]) -> SeaBlock:
    own: list[str] = []
    parts: list[tuple[str, list[str]]] = []
    for line in lines:
        m = _PART.match(line)
        if m:
            parts.append(
                (m.group("name"), [m.group("rest").strip()] if m.group("rest").strip() else [])
            )
        elif parts:
            parts[-1][1].append(line)
        else:
            own.append(line)
    if not own and not parts:
        raise ShippingParseError(f"พื้นที่ {key} ไม่มีเนื้อหา")
    if any(not p_lines for _, p_lines in parts):
        raise ShippingParseError(f"ส่วนย่อยของ {key} ไม่มีเนื้อหา")
    return SeaBlock(
        key=key,
        name_th=SEA_AREA_LABELS_TH[key],
        lines=tuple(own),
        parts=tuple(SeaPartBlock(name, tuple(p_lines)) for name, p_lines in parts),
    )


def parse_shipping(text: str) -> ParsedShipping:
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    keys = [_norm(ln) for ln in lines]
    by_name = {_norm(SEA_AREA_LABELS_TH[k]): k for k in SEA_AREA_KEYS}
    try:
        head = keys.index(_norm(_OVERVIEW_HEAD))
        forecast = next(i for i, k in enumerate(keys) if k.startswith(_norm(_FORECAST_HEAD)))
    except (ValueError, StopIteration) as exc:
        raise ShippingParseError("ไม่พบหัวข้อลักษณะอากาศทั่วไปหรือหัวข้อพยากรณ์สำหรับเรือ") from exc
    issued_idx = next((i for i in range(head + 1, forecast) if issued_from(lines[i])), None)
    if issued_idx is None:
        raise ShippingParseError("ไม่พบบรรทัดออกประกาศก่อนหัวข้อพยากรณ์")
    body = lines[head + 1 : issued_idx]
    if body and _DATE_LINE.match(body[0]):
        body = body[1:]
    if not body:
        raise ShippingParseError("ไม่มีย่อหน้าภาพรวม")
    starts = [(i, by_name[k]) for i, k in enumerate(keys) if i > forecast and k in by_name]
    if sorted(k for _, k in starts) != sorted(SEA_AREA_KEYS):
        raise ShippingParseError("หัวข้อพื้นที่ทะเลไม่ครบ 4 หรือซ้ำ")
    areas: dict[SeaAreaKey, SeaBlock] = {}
    for n, (i, key) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        # บรรทัด "ออกประกาศ ..." ท้ายหน้าไม่ใช่เนื้อหาของพื้นที่สุดท้าย
        block = [ln for ln in lines[i + 1 : end] if issued_from(ln) is None]
        areas[key] = _area_block(key, block)
    issued_at = issued_from(lines[issued_idx])
    assert issued_at is not None
    return ParsedShipping(
        overview=" ".join(body),
        issued_line=lines[issued_idx],
        issued_at=issued_at,
        areas=areas,
    )
