"""ท่อประมวลผลทั้งสาย: เอกสาร -> Issue หรือข้อผิดพลาดที่มีรหัส (ไม่ crash ไม่เดา, F7).

ใช้ร่วมกันโดย scripts/run_pipeline.py (ข้อมูลบนเครื่อง) และฟังก์ชัน /api/summarize (Phase 5.1)
"""

from __future__ import annotations

from pydantic import ValidationError

from tmd_plain.contract import Issue, SummarizeError, error_response
from tmd_plain.extract.advice import Labeler
from tmd_plain.generate.assemble import IssueMeta, assemble_issue
from tmd_plain.generate.templates import GenerateError
from tmd_plain.prep.doctype import detect_doc_type
from tmd_plain.prep.extract import SourceDocument, document_from_pdf
from tmd_plain.prep.pdf_text import PdfTextError
from tmd_plain.prep.regions import ParsedIssue, PrepError, parse_issue


def document_from_bytes(data: bytes) -> SourceDocument | SummarizeError:
    """ไฟล์ PDF -> เอกสาร; ไฟล์ว่าง/ไม่ใช่ PDF/ไม่มีชั้นข้อความ -> ข้อผิดพลาด."""
    if not data:
        return error_response("empty_file")
    try:
        return document_from_pdf(data)
    except PdfTextError:
        return error_response("extract_failed")


def parse_or_error(doc: SourceDocument) -> ParsedIssue | SummarizeError:
    if not doc.text.strip():
        return error_response("empty_file")
    if detect_doc_type(doc.text) not in ("daily", "sevenday"):
        return error_response("unsupported_document")
    try:
        return parse_issue(doc)
    except PrepError as exc:
        return error_response(exc.code)


def summarize(doc: SourceDocument, meta: IssueMeta, label_of: Labeler) -> Issue | SummarizeError:
    parsed = parse_or_error(doc)
    if isinstance(parsed, SummarizeError):
        return parsed
    return assemble_or_error(parsed, meta, label_of)


def assemble_or_error(
    parsed: ParsedIssue, meta: IssueMeta, label_of: Labeler
) -> Issue | SummarizeError:
    try:
        return assemble_issue(parsed, meta, label_of)
    except (GenerateError, ValidationError):
        # บล็อกภาคอ่านไม่ออก หรือได้ผลที่ไม่ผ่านสัญญา (เช่น 7 วันที่ทุกช่วงวันของภาคว่าง) ไม่เดาค่า
        return error_response("extract_failed")
