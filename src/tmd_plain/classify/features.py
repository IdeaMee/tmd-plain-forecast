"""คุณลักษณะของหน่วย: bag of words (นับความถี่) บนผลตัดคำ newmm.

เลือกนับความถี่ดิบ ไม่ใช้ TF-IDF (สไลด์ NLP 4-1 ให้สูตร TF-IDF ขัดกันเอง และ Naive Bayes แบบข้อความในสไลด์ ML 08 ใช้ความถี่)
ตัวเลขทุกตัวรวมเป็นโทเคนเดียว เพื่อให้วันที่/ความสูงคลื่นต่างกันไม่กลายเป็นคำใหม่
"""

from __future__ import annotations

import re
from collections import Counter

from tmd_plain.prep.tokenize import tokenize

NUM_TOKEN = "<num>"
_NUM = re.compile(r"^[0-9๐-๙.,]+$")
# โทเคนที่มีแต่เครื่องหมาย (วงเล็บ ขีด จุด) ไม่มีความหมายต่อป้าย
_PUNCT_ONLY = re.compile(r"^[\W_]+$")


def normalize_tokens(tokens: list[str]) -> list[str]:
    out: list[str] = []
    for tok in tokens:
        if _NUM.match(tok):
            out.append(NUM_TOKEN)
        elif not _PUNCT_ONLY.match(tok):
            out.append(tok)
    return out


def bag_of_words(text: str) -> Counter[str]:
    return Counter(normalize_tokens(tokenize(text)))
