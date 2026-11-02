"""ตรวจชนิดเอกสาร (ด่านแรกของท่อประมวลผล): พยากรณ์รายวัน / 7 วัน / เดินเรือ / ประกาศเตือนภัย / ไม่รองรับ."""

from __future__ import annotations

import re
from typing import Literal

from tmd_plain.contract import SEA_AREA_LABELS_TH

DetectedType = Literal["daily", "sevenday", "shipping", "warning", "unsupported"]

# คำบอกชนิดที่ต้องพบ (หน้าเว็บหรือ PDF อย่างใดอย่างหนึ่ง) ดูโครงจริงใน known-defects.md
_SEVENDAY = ("คาดหมายอากาศรายภาค", "พยากรณ์อากาศระยะปานกลาง")
_DAILY = ("พยากรณ์อากาศสำหรับประเทศไทย",)
_DAILY_HEADER = ("ลักษณะอากาศทั่วไป", "ประจำวัน")
# ชื่อประกาศที่มีคำนี้ไม่ใช่พยากรณ์รายวัน (เดินเรือเป็นชนิดของตัวเอง ตรวจด้วยโครงด้านล่าง)
_REJECT_IN_HEADER = ("เดินเรือ",)
# พยากรณ์เดินเรือ (แผน 11.1): หัวข้อพยากรณ์สำหรับเรือ + หัวข้อพื้นที่ทะเลครบ 4 บรรทัด
# โครงไม่ครบ (เช่น PDF ที่จัดหน้าต่าง) ไม่เดา ไปโหมดทั่วไป
_SHIPPING = "พยากรณ์อากาศสำหรับเรือเดินทะเล"
_SPACES = re.compile(r"\s+")
TITLE_MAX_CHARS = 60
HEADER_LINES = 8  # หัวเอกสาร (ชื่อหน่วยงาน ชื่อประกาศ วันที่) ไม่รวมเนื้อหาที่อาจพูดถึง "ชาวเรือควรเดินเรือ..."


# ประกาศเตือนภัย (แผน 11.2): บรรทัดหัว "ประกาศกรมอุตุนิยมวิทยา" + "เรื่อง ..." + "ฉบับที่ N (เลข/ปี)" ใกล้กัน
# PDF มีบล็อกผู้พยากรณ์ราว 8 บรรทัดก่อนหัวประกาศ จึงดู 30 บรรทัดแรก
_WARNING_NUMBER = re.compile(r"^ฉบับที่\s*\d+\s*\(\s*\d+\s*/\s*\d{4}\s*\)")
WARNING_HEAD_LINES = 30


def is_warning(text: str) -> bool:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()][:WARNING_HEAD_LINES]
    if "ประกาศกรมอุตุนิยมวิทยา" not in lines:
        return False
    start = lines.index("ประกาศกรมอุตุนิยมวิทยา")
    near = lines[start + 1 : start + 6]
    return (
        bool(near) and near[0].startswith("เรื่อง") and any(_WARNING_NUMBER.match(ln) for ln in near)
    )


def is_shipping(text: str) -> bool:
    lines = {_SPACES.sub("", ln) for ln in text.splitlines()}
    return _SPACES.sub("", _SHIPPING) in _SPACES.sub("", text) and all(
        _SPACES.sub("", name) in lines for name in SEA_AREA_LABELS_TH.values()
    )


def detect_doc_type(text: str) -> DetectedType:
    if is_shipping(text):
        return "shipping"
    if is_warning(text):
        return "warning"
    header_lines = [ln for ln in text.splitlines() if ln.strip()][:HEADER_LINES]
    # บรรทัดชื่อประกาศสั้น (ย่อหน้าเนื้อหาที่ขึ้นต้น "พยากรณ์อากาศ 24 ชั่วโมง..." ยาวกว่านี้มาก)
    titles = [
        ln
        for ln in header_lines
        if len(ln) <= TITLE_MAX_CHARS and ln.startswith(("พยากรณ์อากาศ", "ประกาศ", "คาดหมาย"))
    ]
    if any(word in title for title in titles for word in _REJECT_IN_HEADER):
        return "unsupported"
    if any(marker in text for marker in _SEVENDAY):
        return "sevenday"
    if any(m in text for m in _DAILY) and any(h in text for h in _DAILY_HEADER):
        return "daily"
    return "unsupported"
