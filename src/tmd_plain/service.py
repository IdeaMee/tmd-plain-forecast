"""บริการของหน้า /demo: ไฟล์ที่อัปโหลด -> คำตอบตามสัญญา v2 (ทดสอบได้โดยไม่ต้องมี Vercel, ไม่เก็บไฟล์).

ลำดับ: ไฟล์ว่าง -> ขนาด -> เป็น PDF ไหม -> ดึงข้อความ -> ชนิดเอกสาร (ทะเบียนใน doctypes/) -> ตัวสร้างผลของชนิดนั้น
ภาพขั้นตอนสร้างหลังได้ผลแล้ว จากผลระหว่างทางเท่านั้น จึงเปิดหรือปิดก็ได้ผลสรุปเดียวกันทุกไบต์
"""

from __future__ import annotations

from tmd_plain.classify.model_io import Classifier, with_label_cache
from tmd_plain.config import load_config
from tmd_plain.contract import OkResponse, SummarizeError, error_response, ok_response
from tmd_plain.doctypes.common import pdf_steps
from tmd_plain.doctypes.registry import spec_for
from tmd_plain.pipeline import document_from_bytes
from tmd_plain.tracing import build_trace

PDF_MAGIC = b"%PDF-"
# มาตรฐาน PDF ยอมให้มีไบต์อื่นนำหน้าหัวไฟล์ได้ภายใน 1024 ไบต์แรก
PDF_MAGIC_WINDOW = 1024


def summarize_pdf(
    data: bytes, classifier: Classifier, trace: bool = False
) -> OkResponse | SummarizeError:
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
    if not doc.text.strip():
        return error_response("empty_file")
    # ชนิดที่ไม่รู้จักได้โหมดทั่วไป (10.3) unsupported_document จึงเหลือแค่ไฟล์ที่ไม่ใช่ PDF
    spec = spec_for(doc.text)
    classifier = with_label_cache(classifier)
    run = spec.run(doc, classifier)
    if isinstance(run, SummarizeError):
        return run
    steps = build_trace(pdf_steps(doc, spec) + spec.trace(run, classifier)) if trace else None
    return ok_response(spec.kind, run.document, steps)


def http_status(result: OkResponse | SummarizeError) -> int:
    """200 สำเร็จ, 413 ไฟล์ใหญ่เกิน, 422 ไฟล์ใช้ไม่ได้ (เนื้อคำตอบเป็น JSON ตามสัญญาทุกกรณี)."""
    if not isinstance(result, SummarizeError):
        return 200
    return 413 if result.error.code == "too_large" else 422
