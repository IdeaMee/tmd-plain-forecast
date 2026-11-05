"""Baseline แบบกฎคำสำคัญ (Phase 2.1).

เขียนจากนิยามป้ายในคู่มือหัวข้อ 2 เท่านั้น ก่อนมีป้าย และห้ามปรับโดยดูผลชุดทดสอบ
ลำดับความสำคัญตามคู่มือ: มีคำแนะนำ -> advice เสมอ; แล้วกลไก -> cause; หัวเรื่อง/ไม่ใช่เนื้อหา -> other; ที่เหลือ -> weather
"""

from __future__ import annotations

import re

from tmd_plain.contract import UnitLabel

ADVICE_WORDS = ("ขอให้", "ควร", "ระวัง", "หลีกเลี่ยง", "งดออกจากฝั่ง", "ติดตามประกาศ")
CAUSE_OPENERS = ("ทั้งนี้เนื่องจาก", "เนื่องจาก", "ประกอบกับ", "ในขณะที่", "ส่วนมรสุม")
MECHANISMS = (
    "ความกดอากาศ",
    "มวลอากาศ",
    "มรสุม",
    "ร่องมรสุม",
    "คลื่นกระแสลม",
    "หย่อมความกดอากาศ",
    "ลมฝ่าย",
    "พายุ",
)
MECHANISM_VERBS = ("ปกคลุม", "พัด", "แผ่", "เคลื่อน")
OTHER_OPENERS = ("ออกประกาศ",)
_THAI = re.compile(r"[ก-๙]")


def keyword_label(text: str) -> UnitLabel:
    flat = re.sub(r"\s+", "", text)
    if any(w in flat for w in ADVICE_WORDS):
        return "advice"
    if flat.startswith(CAUSE_OPENERS):
        return "cause"
    if any(m in flat for m in MECHANISMS) and any(v in flat for v in MECHANISM_VERBS):
        return "cause"
    if flat.startswith(OTHER_OPENERS) or not _THAI.search(flat):
        return "other"
    return "weather"
