"""ตัดย่อหน้าภาพรวม/ข้อควรระวังเป็นหน่วย (อนุประโยค) ตามกติกาใน docs/spec/labeling-guideline.md หัวข้อ 3.

ตัดที่: ขึ้นย่อหน้าใหม่ และคำเชื่อมใน SPLIT_MARKERS; "เนื่องจาก" เฉพาะเมื่อตามด้วยกลไกอากาศ;
"ส่งผล(ทำ)ให้" เมื่อหน่วยนั้นพูดถึงกลไกมาก่อน
ไม่ตัดที่: "โดยเฉพาะ", "รวมทั้ง", "ซึ่งอาจทำให้", "สำหรับ", "เนื่องจาก" + สภาพทั่วไป (เหตุผลของคำแนะนำ)
หา marker ได้แม้ไม่มีช่องว่างนำหน้า เพราะ PDF ทำช่องว่างหาย (เช่น "ภาคใต้ขอให้ประชาชน")
"""

from __future__ import annotations

import hashlib
import re

from tmd_plain.prep.periods import is_date_phrase

SPLIT_MARKERS: tuple[str, ...] = (
    "ทั้งนี้เนื่องจาก",
    "ประกอบกับ",
    "ในขณะที่",
    "ส่วนมรสุม",
    "ส่วนประเทศไทย",
    "ส่วนภาค",
    "ส่วนในช่วงวันที่",
    "อนึ่ง",
    "ขอให้",
)
MECHANISMS: tuple[str, ...] = (
    "ความกดอากาศ",
    "มวลอากาศ",
    "มรสุม",
    "ร่องมรสุม",
    "คลื่นกระแสลม",
    "หย่อมความกดอากาศ",
    "ลมฝ่าย",
)
_MARKER_RX = re.compile("|".join(re.escape(m) for m in SPLIT_MARKERS))
# "เนื่องจาก" ที่ตามด้วยกลไก (อาจมี "บริเวณ" คั่น) และไม่ใช่ส่วนของ "ทั้งนี้เนื่องจาก"
_BECAUSE_RX = re.compile(
    r"(?<!ทั้งนี้)เนื่องจาก\s*(?:บริเวณ\s*)?(?=" + "|".join(re.escape(m) for m in MECHANISMS) + ")"
)
_RESULT_RX = re.compile(r"ส่งผล(?:ทำ)?ให้")
MIN_UNIT_CHARS = 4


def _has_mechanism(text: str) -> bool:
    flat = re.sub(r"\s+", "", text)
    return any(m in flat for m in MECHANISMS)


def split_units(paragraph: str) -> list[str]:
    """ตัดหนึ่งย่อหน้าเป็นหน่วย คืนรายการข้อความ (ตัดช่องว่างหัวท้าย ไม่มีหน่วยว่าง)."""
    text = paragraph.strip()
    cuts = {m.start() for m in _MARKER_RX.finditer(text)}
    cuts |= {m.start() for m in _BECAUSE_RX.finditer(text)}
    # "ส่งผลให้" ต้องดูว่าหน่วยที่กำลังอยู่มีกลไกหรือไม่ จึงคำนวณหลังได้จุดตัดอื่นแล้ว
    for m in _RESULT_RX.finditer(text):
        unit_start = max((c for c in cuts if c < m.start()), default=0)
        if _has_mechanism(text[unit_start : m.start()]):
            cuts.add(m.start())
    cuts.discard(0)
    units: list[str] = []
    carry = ""
    prev = 0
    for cut in sorted(cuts) + [len(text)]:
        piece = text[prev:cut].strip()
        prev = cut
        if not piece:
            continue
        # หน่วยที่มีแค่วลีวันที่ (เช่น "ในช่วงวันที่ 5-7 พ.ย.69" ที่ตัดเพราะ "ขอให้" ตามมา) เป็นตัวบอกเวลาของหน่วยถัดไป
        date_only = is_date_phrase(piece)
        if carry:
            piece, carry = f"{carry} {piece}", ""
        if date_only and cut < len(text):
            carry = piece
        elif units and len(piece) < MIN_UNIT_CHARS:
            # ชิ้นสั้นมาก (เช่น เศษคำที่ PDF ตัด) ต่อกับหน่วยก่อนหน้าแทนการเป็นหน่วยเดี่ยว
            units[-1] = f"{units[-1]} {piece}"
        else:
            units.append(piece)
    if carry:
        units.append(carry)
    return units


def split_section(paragraphs: tuple[str, ...] | list[str]) -> list[str]:
    """ตัดทุกย่อหน้าของส่วนหนึ่ง (ภาพรวมหรือข้อควรระวัง) เรียงตามลำดับเดิม."""
    out: list[str] = []
    for para in paragraphs:
        out.extend(split_units(para))
    return out


def unit_id(doc_type: str, text: str) -> str:
    """รหัสหน่วยคงที่: ชนิดเอกสาร + sha1 ของข้อความที่ตัดช่องว่างออก (ถ้อยคำเดียวกัน = รหัสเดียวกัน)."""
    key = re.sub(r"\s+", "", text)
    return f"{doc_type[0]}-{hashlib.sha1(key.encode('utf-8')).hexdigest()[:8]}"
