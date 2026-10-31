"""แปลงไฟล์ต้นฉบับ (ข้อความที่เก็บจากหน้าเว็บ หรือ PDF) เป็นข้อความสะอาดหนึ่งก้อน.

ฟังก์ชันในไฟล์นี้รับเนื้อไฟล์ (str/bytes) ไม่เปิดไฟล์เอง การอ่านดิสก์อยู่ใน raw_io.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from tmd_plain.prep.clean import clean_text
from tmd_plain.prep.pdf_text import read_pdf

SourceKind = Literal["txt", "pdf"]


@dataclass(frozen=True)
class SourceDocument:
    kind: SourceKind
    text: str  # ข้อความสะอาด คงโครงบรรทัด
    meta: dict[str, str] = field(default_factory=dict)  # หัวไฟล์ "# key: value" ของไฟล์ .txt
    # ต่อบรรทัดของ text: บรรทัดในหน้าเว็บขึ้นต้นด้วยการเยื้องไหม (ย่อหน้าจริงเยื้อง; บรรทัดที่หน้าเว็บตัดกลางประโยคไม่เยื้อง)
    indented: tuple[bool, ...] = ()
    # เฉพาะ PDF: ข้อความดิบก่อนทำความสะอาด จำนวนหน้า และตัวอ่านที่ใช้ (ใช้แสดงในภาพขั้นตอนเท่านั้น)
    raw: str = ""
    pages: int = 0
    reader: str = ""


def parse_saved_txt(content: str) -> tuple[dict[str, str], str]:
    """แยกหัวไฟล์ที่ใส่ตอนเก็บข้อมูล (# source / round_id / label / ...) ออกจากเนื้อหา."""
    meta: dict[str, str] = {}
    body: list[str] = []
    for line in content.splitlines():
        if line.startswith("# ") and not body:
            key, _, value = line[2:].partition(":")
            meta[key.strip()] = value.strip()
        else:
            body.append(line)
    return meta, "\n".join(body)


def document_from_txt(content: str) -> SourceDocument:
    meta, body = parse_saved_txt(content)
    lines: list[str] = []
    indented: list[bool] = []
    for raw_line in body.splitlines():
        cleaned = clean_text(raw_line)
        if cleaned:
            lines.append(cleaned)
            indented.append(raw_line[:1].isspace())
    newline = chr(10)
    return SourceDocument(kind="txt", text=newline.join(lines), meta=meta, indented=tuple(indented))


def document_from_pdf(data: bytes) -> SourceDocument:
    read = read_pdf(data)
    return SourceDocument(
        kind="pdf", text=read.text, raw=read.raw, pages=read.pages, reader=read.reader
    )
