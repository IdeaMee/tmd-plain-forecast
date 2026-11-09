"""บริการของหน้า /demo: ไฟล์ที่อัปโหลด -> คำตอบตามสัญญา (ทดสอบได้โดยไม่ต้องมี Vercel, ไม่เก็บไฟล์).

ลำดับ: ไฟล์ว่าง -> ขนาด -> เป็น PDF ไหม -> ดึงข้อความ -> ชนิดเอกสาร -> วันเวลาจากหัวเอกสาร -> ท่อประมวลผล
-> ตรวจ F1-F5 ซ้ำ (PDF ที่ไม่เคยเห็นอาจอ่านเพี้ยน ถ้าไม่ผ่านตอบข้อผิดพลาดแทนการแสดงค่าที่ไม่มีที่มา)
"""

from __future__ import annotations

import logging

from tmd_plain.config import load_config
from tmd_plain.contract import SummarizeError, SummarizeOk, error_response
from tmd_plain.extract.advice import Labeler
from tmd_plain.generate.assemble import meta_from_text
from tmd_plain.generate.fidelity import check_issue
from tmd_plain.pipeline import assemble_or_error, document_from_bytes, parse_or_error

logger = logging.getLogger(__name__)

PDF_MAGIC = b"%PDF-"
# มาตรฐาน PDF ยอมให้มีไบต์อื่นนำหน้าหัวไฟล์ได้ภายใน 1024 ไบต์แรก
PDF_MAGIC_WINDOW = 1024


def summarize_pdf(data: bytes, label_of: Labeler) -> SummarizeOk | SummarizeError:
    if not data:
        return error_response("empty_file")
    if len(data) > load_config()["max_upload_bytes"]:
        return error_response("too_large")
    if PDF_MAGIC not in data[:PDF_MAGIC_WINDOW]:
        # ไม่ใช่ PDF เลย: ข้อความของ unsupported_document บอกให้เลือก PDF พยากรณ์ของ TMD
        return error_response("unsupported_document")
    doc = document_from_bytes(data)
    if isinstance(doc, SummarizeError):
        return doc
    parsed = parse_or_error(doc)
    if isinstance(parsed, SummarizeError):
        return parsed
    meta = meta_from_text(parsed.doc_type, doc.text)
    if meta is None:
        return error_response("extract_failed")
    issue = assemble_or_error(parsed, meta, label_of)
    if isinstance(issue, SummarizeError):
        return issue
    problems = check_issue(issue, parsed)
    if problems:
        logger.warning(
            "fidelity check failed issue=%s count=%d first=%s",
            issue.issue_id,
            len(problems),
            problems[0],
        )
        return error_response("extract_failed")
    return SummarizeOk(ok=True, issue=issue)


def http_status(result: SummarizeOk | SummarizeError) -> int:
    """200 สำเร็จ, 413 ไฟล์ใหญ่เกิน, 422 ไฟล์ใช้ไม่ได้ (เนื้อคำตอบเป็น JSON ตามสัญญาทุกกรณี)."""
    if isinstance(result, SummarizeOk):
        return 200
    return 413 if result.error.code == "too_large" else 422
