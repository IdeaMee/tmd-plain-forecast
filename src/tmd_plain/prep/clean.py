"""ทำความสะอาดข้อความไทยจาก TMD (ใช้ทั้งข้อความจาก HTML และ PDF).

ลำดับตาม skill thai-text-handling: PUA -> NFC -> normalize ของ PyThaiNLP -> ช่องว่างรอบตัวเลข
ทำทีละบรรทัดเพื่อคงโครงบรรทัดไว้ใช้แยกบล็อกภาค การต่อบรรทัดที่ขาดทำตอนรู้ว่าเป็นย่อหน้า (join_wrapped)
"""

from __future__ import annotations

import re
import unicodedata

from pythainlp.util import normalize as _thai_normalize

# อักษรใน Private Use Area ที่ฟอนต์ไทยบางตัวใช้แทนสระ/วรรณยุกต์รูปเยื้อง -> อักษรไทยจริง
PUA_MAP: dict[str, str] = {
    "\uf700": "\u0e10",  # ฐ ไม่มีเชิง
    "\uf701": "\u0e34",  # ิ
    "\uf702": "\u0e35",  # ี
    "\uf703": "\u0e36",  # ึ
    "\uf704": "\u0e37",  # ื
    "\uf705": "\u0e48",  # ่
    "\uf706": "\u0e49",  # ้
    "\uf707": "\u0e4a",  # ๊
    "\uf708": "\u0e4b",  # ๋
    "\uf709": "\u0e4c",  # ์
    "\uf70a": "\u0e48",  # ่ (ตำแหน่งต่ำ)
    "\uf70b": "\u0e49",  # ้
    "\uf70c": "\u0e4a",  # ๊
    "\uf70d": "\u0e4b",  # ๋
    "\uf70e": "\u0e4c",  # ์
    "\uf70f": "\u0e0d",  # ญ ไม่มีเชิง
    "\uf710": "\u0e31",  # ั
    "\uf711": "\u0e4d",  # ํ
    "\uf712": "\u0e47",  # ็
    "\uf713": "\u0e48",  # ่ (เยื้องซ้าย)
    "\uf714": "\u0e49",  # ้
    "\uf715": "\u0e4a",  # ๊
    "\uf716": "\u0e4b",  # ๋
    "\uf717": "\u0e4c",  # ์
    "\uf718": "\u0e38",  # ุ
    "\uf719": "\u0e39",  # ู
    "\uf71a": "\u0e3a",  # ฺ
}
_PUA_TABLE = str.maketrans(PUA_MAP)
# ข้อความจากหน้าเว็บของ TMD ใช้ non-breaking space (U+00A0) แทนช่องว่างเกือบทุกที่
_SPACE_TABLE = str.maketrans(
    {"\u00a0": " ", "\u2007": " ", "\u2009": " ", "\u202f": " ", "\t": " "}
)

THAI_CHARS = "ก-๛"
# ชั้นข้อความ PDF ทำช่องว่างระหว่างอักษรไทยกับตัวเลขหาย เช่น "ในช่วงวันที่17", "ร้อยละ 30ของ"
_THAI_THEN_DIGIT = re.compile(rf"([{THAI_CHARS}])(\d)")
_DIGIT_THEN_THAI = re.compile(rf"(\d)([{THAI_CHARS}])")
_THAI_END = re.compile(rf"[{THAI_CHARS}]$")
_THAI_START = re.compile(rf"^[{THAI_CHARS}]")


def count_pua(text: str) -> int:
    """นับอักษร PUA ช่วงที่ฟอนต์ไทยใช้ (ไว้ตรวจว่าทำความสะอาดครบ)."""
    return sum(1 for ch in text if "\uf700" <= ch <= "\uf71a")


def fix_digit_spacing(line: str) -> str:
    """ใส่ช่องว่างระหว่างอักษรไทยกับตัวเลขที่ติดกัน (ตัวเลขไม่เปลี่ยน)."""
    return _DIGIT_THEN_THAI.sub(r"\1 \2", _THAI_THEN_DIGIT.sub(r"\1 \2", line))


def clean_text(raw: str) -> str:
    """ทำความสะอาดทีละบรรทัด ตัดบรรทัดว่าง คงลำดับบรรทัดเดิม.

    normalize ของ PyThaiNLP ยุบช่องว่างซ้ำ จึงเรียกทีละบรรทัด ไม่ให้บรรทัดหายไปรวมกัน
    """
    text = unicodedata.normalize("NFC", raw.replace("\r\n", "\n").replace("\r", "\n"))
    lines = []
    for line in text.translate(_PUA_TABLE).translate(_SPACE_TABLE).split("\n"):
        cleaned = _thai_normalize(unicodedata.normalize("NFC", line)).strip()
        if cleaned:
            lines.append(fix_digit_spacing(cleaned))
    return "\n".join(lines)


def join_wrapped(lines: list[str] | tuple[str, ...]) -> str:
    """ต่อบรรทัดที่ PDF ตัดกลางย่อหน้า.

    ไทยต่อไทยต่อกันเลย (ภาษาไทยไม่เว้นวรรคระหว่างคำ และ PDF ตัดบรรทัดกลางคำประสมได้)
    นอกนั้นคั่นด้วยช่องว่าง
    """
    out = ""
    for line in (ln.strip() for ln in lines):
        if not line:
            continue
        if out and not (_THAI_END.search(out) and _THAI_START.search(line)):
            out += " "
        out += line
    return out
