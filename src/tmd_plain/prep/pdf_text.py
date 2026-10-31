"""ดึงข้อความจาก PDF ของ TMD.

pypdfium2 เป็นตัวหลัก (ผล Phase 0.2: แยกภาคได้ครบทุกไฟล์) pdfminer.six เป็นตัวสำรองเมื่อ pypdfium2 อ่านไม่ได้
การทำความสะอาดอยู่ใน clean.py (re-export ไว้ที่นี่เพื่อให้โค้ดเดิมใช้ต่อได้)
"""

from __future__ import annotations

import io
from dataclasses import dataclass

import pypdfium2 as pdfium
from pdfminer.high_level import extract_text as _pdfminer_extract_text

from tmd_plain.prep.clean import PUA_MAP, clean_text, count_pua

__all__ = [
    "PUA_MAP",
    "PdfRead",
    "PdfTextError",
    "clean_text",
    "count_pua",
    "extract_pdf_text",
    "extract_pdfium",
    "extract_pdfium_pages",
    "extract_pdfminer",
    "read_pdf",
]


class PdfTextError(ValueError):
    """อ่านข้อความจากไฟล์ไม่ได้ (ไม่ใช่ PDF, ไฟล์เสีย หรือไม่มีชั้นข้อความ)."""


def extract_pdfium_pages(data: bytes) -> list[str]:
    """ข้อความดิบทีละหน้าด้วย pypdfium2 (ยังไม่ทำความสะอาด)."""
    try:
        doc = pdfium.PdfDocument(data)
    except pdfium.PdfiumError as exc:
        raise PdfTextError("ไฟล์ไม่ใช่ PDF ที่อ่านได้") from exc
    try:
        return [doc[i].get_textpage().get_text_range() for i in range(len(doc))]
    finally:
        doc.close()


def extract_pdfium(data: bytes) -> str:
    """ดึงข้อความทุกหน้าด้วย pypdfium2 (ตัวอ่านหลัก)."""
    return "\n".join(extract_pdfium_pages(data))


def extract_pdfminer(data: bytes) -> str:
    """ดึงข้อความด้วย pdfminer.six (ตัวสำรอง)."""
    try:
        return _pdfminer_extract_text(io.BytesIO(data))
    except Exception as exc:  # pdfminer โยนข้อผิดพลาดได้หลายชนิดเมื่อไฟล์เสีย
        raise PdfTextError("ไฟล์ไม่ใช่ PDF ที่อ่านได้") from exc


@dataclass(frozen=True)
class PdfRead:
    # ข้อความดิบก่อนทำความสะอาด (ใช้แสดงในภาพขั้นตอน)
    raw: str
    text: str
    # จำนวนหน้าที่ pypdfium2 อ่านได้ (0 = ใช้ pdfminer.six)
    pages: int
    # "pypdfium2" | "pdfminer.six"
    reader: str


def read_pdf(data: bytes) -> PdfRead:
    """อ่าน PDF ครั้งเดียว: ลอง pypdfium2 ก่อน ถ้าอ่านไม่ได้หรือว่างค่อยใช้ pdfminer.six."""
    if not data:
        raise PdfTextError("ไฟล์ว่าง")
    try:
        pages = extract_pdfium_pages(data)
    except PdfTextError:
        pages = []
    raw = "\n".join(pages)
    text = clean_text(raw)
    if text:
        return PdfRead(raw, text, len(pages), "pypdfium2")
    raw = extract_pdfminer(data)
    text = clean_text(raw)
    if not text:
        raise PdfTextError("ไม่มีชั้นข้อความ (อาจเป็นภาพสแกน)")
    return PdfRead(raw, text, 0, "pdfminer.six")


def extract_pdf_text(data: bytes) -> str:
    """ข้อความสะอาดจาก PDF (ดู read_pdf)."""
    return read_pdf(data).text
