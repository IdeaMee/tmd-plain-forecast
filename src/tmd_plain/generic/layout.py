"""โครงเอกสารจากบรรทัดของ PDF ด้วยกฎ: หัวเรื่อง, หัวข้อ, ย่อหน้า (ไม่ใช้ ML).

PDF ตัดบรรทัดตามความกว้างหน้า ย่อหน้าจึงต้องต่อกลับ: บรรทัดที่ยาวเกือบเต็มบรรทัดแปลว่าย่อหน้ายังไม่จบ
ความกว้างต่างกันมากในแต่ละเอกสาร (หน้าเดียว/สองคอลัมน์) จึงวัดจากเอกสารนั้นเอง
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from tmd_plain.prep.clean import join_wrapped

# บรรทัดที่ขึ้นย่อหน้าใหม่แน่ๆ: ข้อที่มีเลข, รายการขีด, ชื่อภาคนำหน้าเนื้อความ
_ITEM_START = re.compile(r"^(?:\d{1,2}[.)]\s|[-•]\s?)")
_REGION_START = re.compile(
    r"^(?:ภาคเหนือ|ภาคตะวันออกเฉียงเหนือ|ภาคกลาง|ภาคตะวันออก|ภาคใต้(?:ฝั่งตะวันออก|ฝั่งตะวันตก)?"
    r"|กรุงเทพมหานคร(?:และปริมณฑล)?)(?=\s|$)"
)
_THAI = re.compile(r"[ก-ฮ]")
# เลขหน้า เช่น "1", "- 1 -"
_PAGE_NO = re.compile(r"^[-\s]*\d{1,3}[-\s]*$")
# คำขึ้นต้นของชื่อเอกสาร TMD ที่พบในชุดตัวอย่าง
_TITLE_PREFIXES = (
    "ประกาศ",
    "พยากรณ์",
    "คาดหมาย",
    "การคาดหมาย",
    "สรุป",
    "การเฝ้าระวัง",
    "รายงาน",
)
TITLE_MAX_CHARS = 100
TITLE_SEARCH_LINES = 15
# บรรทัดที่สั้นกว่าสัดส่วนนี้ของความยาวบรรทัดเต็ม = บรรทัดสุดท้ายของย่อหน้า
FULL_LINE_RATIO = 0.75
# หัวข้อภาคตั้งแต่กี่ภาคขึ้นไปจึงแสดงแท็บภาค
REGION_HEADINGS_MIN = 3


@dataclass(frozen=True)
class Block:
    heading: str | None
    paragraphs: tuple[str, ...]


@dataclass(frozen=True)
class Layout:
    title: str | None
    blocks: tuple[Block, ...]
    region_leads: tuple[str, ...]


def is_page_number(line: str) -> bool:
    """บรรทัดที่มีแค่ตัวเลขสั้นๆ (เลขหน้าที่ PDF แทรกกลางประโยค) ไม่ใช่เนื้อความ จึงข้ามตอนต่อย่อหน้า."""
    return bool(_PAGE_NO.match(line.strip()))


def content_lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.split("\n") if ln.strip() and not is_page_number(ln)]


def _full_width(lines: list[str]) -> int:
    # ความยาวบรรทัดเต็มของเอกสารนี้ = เปอร์เซ็นไทล์ 75 ของบรรทัดที่มีอักษรไทย
    # เอกสารที่ไม่มีอักษรไทยเลยใช้ทุกบรรทัด (ไม่งั้นได้ 0 แล้วทั้งเอกสารกลายเป็นย่อหน้าเดียว)
    lengths = sorted(len(ln) for ln in lines if _THAI.search(ln)) or sorted(len(ln) for ln in lines)
    if not lengths:
        return 0
    return lengths[min(len(lengths) - 1, (len(lengths) * 3) // 4)]


def find_title(lines: list[str]) -> str | None:
    """ชื่อเอกสาร: บรรทัดแรกที่ขึ้นต้นด้วยคำของชื่อเอกสาร TMD ถ้าไม่มี = บรรทัดไทยบรรทัดแรก (คำต่อคำ)."""
    head = [
        ln
        for ln in lines[:TITLE_SEARCH_LINES]
        if _THAI.search(ln) and not _PAGE_NO.match(ln) and len(ln) <= TITLE_MAX_CHARS
    ]
    for ln in head:
        if ln.startswith(_TITLE_PREFIXES):
            return ln
    return head[0] if head else None


def _is_heading(line: str, next_line: str | None, short: int, max_chars: int) -> bool:
    # บรรทัดสั้นที่มีอักษรไทย ตามด้วยบรรทัดเนื้อความยาว (ตารางคือบรรทัดสั้นติดกันหลายบรรทัด ไม่ใช่หัวข้อ)
    if len(line) > max_chars or not _THAI.search(line) or _ITEM_START.match(line):
        return False
    if _PAGE_NO.match(line):
        return False
    return next_line is not None and len(next_line) >= short


def build_layout(text: str, heading_max_chars: int) -> Layout:
    """ข้อความสะอาด (คงบรรทัด) -> หัวเรื่อง + กลุ่มหัวข้อ/ย่อหน้า ทุกย่อหน้าต่อจากบรรทัดเดิมเท่านั้น."""
    lines = content_lines(text)
    title = find_title(lines)
    short = int(_full_width(lines) * FULL_LINE_RATIO)
    blocks: list[Block] = []
    heading: str | None = None
    paragraphs: list[str] = []
    current: list[str] = []

    def end_paragraph() -> None:
        if current:
            paragraphs.append(join_wrapped(current))
            current.clear()

    def end_block() -> None:
        end_paragraph()
        if heading is not None or paragraphs:
            blocks.append(Block(heading, tuple(paragraphs)))
        paragraphs.clear()

    # บรรทัดหัวเรื่องแสดงแยก ไม่ซ้ำเป็นเนื้อความ (ประกาศมีชื่อผู้ลงนามอยู่ก่อนหัวเรื่อง จึงไม่ใช่บรรทัดแรกเสมอ)
    title_index = lines.index(title) if title is not None else -1
    for i, line in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        if i == title_index:
            end_paragraph()
            continue
        if not current and _is_heading(line, nxt, short, heading_max_chars):
            end_block()
            heading = line
            continue
        if current and (_ITEM_START.match(line) or _REGION_START.match(line)):
            end_paragraph()
        current.append(line)
        if len(line) < short:
            end_paragraph()
    end_block()
    leads = []
    for block in blocks:
        for text_ in ([block.heading] if block.heading else []) + list(block.paragraphs):
            m = _REGION_START.match(text_)
            if m and m.group(0) not in leads:
                leads.append(m.group(0))
    return Layout(title=title, blocks=tuple(blocks), region_leads=tuple(leads))


def has_region_headings(layout: Layout) -> bool:
    return len(layout.region_leads) >= REGION_HEADINGS_MIN
