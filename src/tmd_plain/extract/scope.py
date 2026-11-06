"""คำบอกที่ตั้งในหน่วยคำแนะนำ -> คีย์ภาค ตามตารางแมปภาค v1 (region-scope-map.md หัวข้อ 3, D1-D7).

หลัก: ไม่ตัดคำเตือนทิ้ง ถ้าไม่แน่ใจให้แสดงกว้างไว้ก่อน (D7) · หลายที่ตั้งในหน่วยเดียว = รวมกัน
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from tmd_plain.contract import REGION_KEYS, RegionKey
from tmd_plain.extract.provinces import PROVINCE_RE, province_region

_UPPER: tuple[RegionKey, ...] = ("north", "northeast", "central", "east", "bangkok_vicinity")
_SOUTH: tuple[RegionKey, ...] = ("south_east_coast", "south_west_coast")
_COASTS: tuple[RegionKey, ...] = ("east", "south_east_coast", "south_west_coast")

# คำยาว/เจาะจงก่อน ช่วงที่จับแล้วไม่จับซ้ำ (เช่น "ภาคตะวันออกเฉียงเหนือ" ก่อน "ภาคตะวันออก")
_TERMS: list[tuple[str, tuple[RegionKey, ...]]] = [
    (r"ประเทศไทยตอนบน", _UPPER),  # D3 รวมกรุงเทพฯ
    (r"ภาคใต้ฝั่งตะวันออก", ("south_east_coast",)),
    (r"ภาคใต้ฝั่งตะวันตก", ("south_west_coast",)),
    (r"ภาคใต้(?:ตอนบน|ตอนกลาง|ตอนล่าง)?", _SOUTH),  # D2 ไม่บอกฝั่ง = ทั้งสองฝั่ง
    (r"ภาคตะวันออกเฉียงเหนือ(?:ตอนบน|ตอนล่าง)?", ("northeast",)),
    (r"ภาคเหนือ(?:ตอนบน|ตอนล่าง)?", ("north",)),
    (r"ภาคกลาง(?:ตอนบน|ตอนล่าง)?", ("central", "bangkok_vicinity")),  # D1
    (r"ภาคตะวันออก", ("east",)),
    (r"กรุงเทพมหานคร|กรุงเทพฯ|ปริมณฑล", ("bangkok_vicinity",)),
    (r"อ่าวไทยตอนล่าง", ("south_east_coast",)),
    (r"อ่าวไทย(?:ตอนบน)?", ("east", "south_east_coast")),  # D4
    (r"(?:ทะเล)?อันดามัน(?:ตอนบน|ตอนล่าง)?", ("south_west_coast",)),
    # ทะเลจีนใต้อยู่ในประโยคสาเหตุเกือบทั้งหมด ไม่แมป (จับไว้กันคำอื่นจับซ้ำ)
    (r"ทะเลจีนใต้", ()),
]
_TERM_RES = [(re.compile(p), keys) for p, keys in _TERMS]
_MARINERS = re.compile(r"ชาวเรือ|เรือเล็ก")
# D5: อ้างที่ตั้งของหน่วยก่อนหน้า ("ช่วงเวลาดังกล่าว" เป็นเวลา ไม่ใช่ที่ตั้ง)
_INHERIT = re.compile(r"(?:บริเวณ|พื้นที่)ดังกล่าว")
# หน่วยหนึ่งอาจมีหลายท่อน (คำแนะนำประชาชน + ชาวเรือ + สภาพอากาศ) ตัดท่อนที่คำขึ้นต้นเหล่านี้
_CLAUSE = re.compile(r"(?=ส่วน|สำหรับ|ขอให้(?!ชาวเรือ)|(?<!ขอให้)ชาวเรือ|เรือเล็ก)")
_ADVICE = re.compile(r"ขอให้|ควร|ระวัง|หลีกเลี่ยง|งดออกจากฝั่ง|ติดตาม")


def _overlaps(span: tuple[int, int], taken: list[tuple[int, int]]) -> bool:
    return any(span[0] < b and a < span[1] for a, b in taken)


def locations(text: str) -> set[RegionKey]:
    """ภาคจากคำบอกที่ตั้งในข้อความเดียว (ไม่สืบทอด) ว่าง = ไม่มีคำบอกที่ตั้ง."""
    found: set[RegionKey] = set()
    taken: list[tuple[int, int]] = []
    sea_named = False
    for pattern, keys in _TERM_RES:
        for m in pattern.finditer(text):
            if _overlaps(m.span(), taken):
                continue
            taken.append(m.span())
            found.update(keys)
            sea_named |= "อ่าวไทย" in m.group(0) or "อันดามัน" in m.group(0)
    for m in PROVINCE_RE.finditer(text):
        if not _overlaps(m.span(), taken):
            found.add(province_region(m.group(0)))
    # ชาวเรือ/เรือเล็กไม่บอกชื่อทะเล = ทุกภาคที่มีชายฝั่ง
    if _MARINERS.search(text) and not sea_named:
        found.update(_COASTS)
    return found


def clauses(text: str) -> list[str]:
    return [c for c in _CLAUSE.split(text) if c.strip()]


@dataclass(frozen=True)
class Scope:
    regions: tuple[RegionKey, ...]  # เรียงตาม REGION_KEYS
    general: bool  # True = มีคำแนะนำที่ไม่มีคำบอกที่ตั้ง แสดงเป็นข้อแนะนำทั่วไปทั้ง 7 ภาค (D6)


def advice_scope(text: str, previous: Sequence[str] = ()) -> Scope:
    """ขอบเขตของหน่วยคำแนะนำ; previous = หน่วยก่อนหน้าในย่อหน้าเดียวกัน (ใช้กับ "บริเวณดังกล่าว").

    ทีละท่อน: ท่อนคำแนะนำที่ไม่มีคำบอกที่ตั้ง = ข้อแนะนำทั่วไป (D6) · ท่อนอื่นรวมภาคกัน
    "บริเวณดังกล่าว" รับที่ตั้งของทุกหน่วยก่อนหน้าในย่อหน้า (D5 อ่านคู่กับ D7 แสดงกว้างไว้ก่อน)
    """
    inherited: set[RegionKey] = set()
    for prev in previous:
        inherited |= locations(prev)
    found: set[RegionKey] = set()
    general = False
    for clause in clauses(text):
        here = locations(clause)
        if _INHERIT.search(clause):
            here |= inherited
        if not here and _ADVICE.search(clause):
            general = True
        found |= here
    if general or not found:
        return Scope(REGION_KEYS, general=True)
    return Scope(tuple(k for k in REGION_KEYS if k in found), general=False)
