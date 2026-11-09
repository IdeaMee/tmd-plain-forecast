import io
from pathlib import Path

import pypdfium2 as pdfium
import pytest

from tmd_plain import pipeline
from tmd_plain.classify.model_io import load_classifier
from tmd_plain.config import load_config
from tmd_plain.contract import (
    REGION_KEYS,
    Issue,
    SummarizeError,
    SummarizeGenericOk,
    SummarizeIssueOk,
)
from tmd_plain.doctypes import forecast
from tmd_plain.doctypes import generic as generic_doctype
from tmd_plain.generate.fidelity import check_issue
from tmd_plain.generic.fidelity import check_generic
from tmd_plain.pipeline import parse_or_error
from tmd_plain.prep.extract import document_from_pdf
from tmd_plain.service import http_status, summarize_pdf

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
CLASSIFIER = load_classifier(ROOT / "models")
MAX = load_config()["max_upload_bytes"]


def _raw(name: str) -> bytes:
    path = RAW / name
    if not path.exists():
        pytest.skip(f"ไม่มีข้อมูลดิบ {name} (data/raw ไม่อยู่ใน repo)")
    return path.read_bytes()


def _blank_pdf() -> bytes:
    # PDF จริงที่ไม่มีชั้นข้อความ (เหมือนภาพสแกน)
    doc = pdfium.PdfDocument.new()
    doc.new_page(200, 200)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


@pytest.mark.parametrize(
    ("name", "doc_type", "issue_id"),
    [
        ("daily/daily_161120261800.pdf", "daily", "161120261800"),
        ("sevenday/sevenday_261116.pdf", "sevenday", "261116"),
    ],
)
def test_real_pdf_gives_faithful_issue(name: str, doc_type: str, issue_id: str) -> None:
    data = _raw(name)
    result = summarize_pdf(data, CLASSIFIER)
    assert isinstance(result, SummarizeIssueOk), result
    assert result.trace is None
    issue = result.document
    assert (issue.doc_type, issue.issue_id) == (doc_type, issue_id)
    assert set(issue.regions) == set(REGION_KEYS)
    parsed = parse_or_error(document_from_pdf(data))
    assert check_issue(issue, parsed) == []  # type: ignore[arg-type]
    assert http_status(result) == 200


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        (b"", "empty_file"),
        (b"hello, this is not a pdf", "unsupported_document"),
        (b"%PDF-1.4" + b"\0" * (MAX + 1), "too_large"),
        (b"%PDF-1.4 broken", "extract_failed"),
    ],
)
def test_bad_upload_gives_contract_error(payload: bytes, code: str) -> None:
    result = summarize_pdf(payload, CLASSIFIER)
    assert isinstance(result, SummarizeError) and result.error.code == code
    assert http_status(result) == (413 if code == "too_large" else 422)


def test_fidelity_guard_rejects_unfaithful_output(monkeypatch: pytest.MonkeyPatch) -> None:
    # ถ้าตรวจ F1-F5 ไม่ผ่าน ต้องไม่แสดงผล (ตอบ extract_failed แทน)
    data = _raw("daily/daily_161120261800.pdf")
    monkeypatch.setattr(forecast, "check_issue", lambda issue, parsed: ["F1 ทดสอบ"])
    result = summarize_pdf(data, CLASSIFIER)
    assert isinstance(result, SummarizeError) and result.error.code == "extract_failed"


def test_issue_that_breaks_contract_is_extract_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    # ผลที่ไม่ผ่านโมเดล Issue (ValidationError) ต้องเป็นข้อผิดพลาดตามสัญญา ไม่ crash
    data = _raw("sevenday/sevenday_261116.pdf")
    monkeypatch.setattr(pipeline, "assemble_issue", lambda *a: Issue.model_validate({}))
    result = summarize_pdf(data, CLASSIFIER)
    assert isinstance(result, SummarizeError) and result.error.code == "extract_failed"


def test_pdf_without_text_layer_is_extract_failed() -> None:
    result = summarize_pdf(_blank_pdf(), CLASSIFIER)
    assert isinstance(result, SummarizeError) and result.error.code == "extract_failed"


def test_non_tmd_pdf_gets_generic_with_warning() -> None:
    # 10.3: PDF ที่มีข้อความแต่ไม่ใช่ของ TMD (สไลด์วิชา) แสดงแบบโหมดทั่วไปพร้อมคำเตือน ไม่ปฏิเสธ
    path = ROOT / "course" / "slides" / "0_MiniProject.pdf"
    if not path.exists():
        pytest.skip("ไม่มีสไลด์วิชาในเครื่อง")
    result = summarize_pdf(path.read_bytes(), CLASSIFIER)
    assert isinstance(result, SummarizeGenericOk), result
    assert result.document.tmd_like is False
    assert result.document.warnings == ["not_tmd_like"]


@pytest.mark.parametrize(
    "name",
    [
        "generic/generic_enso_2569_09.pdf",
        "generic/generic_agro_fortnight_16112026.pdf",
        "weekly/weekly_161120261100.pdf",
        "outlook3m/outlook3m_112026-012027.pdf",
    ],
)
def test_other_tmd_pdf_gets_faithful_generic(name: str) -> None:
    data = _raw(name)
    result = summarize_pdf(data, CLASSIFIER)
    assert isinstance(result, SummarizeGenericOk), result
    doc = result.document
    assert doc.tmd_like and doc.warnings == []
    assert sum(len(s.units) for s in doc.sections) > 0
    assert check_generic(doc, document_from_pdf(data).text) == []
    # เปิด trace แล้วเอกสารต้องเหมือนเดิมทุกไบต์ และมีเฉพาะขั้นที่ทำจริง (ไม่มีขั้นแม่แบบ)
    traced = summarize_pdf(data, CLASSIFIER, trace=True)
    assert isinstance(traced, SummarizeGenericOk) and traced.trace is not None
    assert traced.document.model_dump_json() == doc.model_dump_json()
    ids = [s.id for s in traced.trace.steps]
    assert ids[:3] == ["read_pdf", "clean", "detect_type"] and "template" not in ids


def test_image_only_tmd_pdf_is_extract_failed() -> None:
    # อินโฟกราฟิกเกษตร 7 วันที่เป็นภาพล้วน (ไม่มีชั้นข้อความ) ปฏิเสธ ไม่เดา
    result = summarize_pdf(_raw("agro7/agro7_11112026.pdf"), CLASSIFIER)
    assert isinstance(result, SummarizeError) and result.error.code == "extract_failed"


def test_generic_fidelity_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    # ตรวจความถูกต้องของโหมดทั่วไปไม่ผ่าน = ไม่แสดงผล
    data = _raw("generic/generic_enso_2569_09.pdf")
    monkeypatch.setattr(generic_doctype, "check_generic", lambda doc, text: ["ทดสอบ"])
    result = summarize_pdf(data, CLASSIFIER)
    assert isinstance(result, SummarizeError) and result.error.code == "extract_failed"


def test_warning_pdf_gets_full_summary_with_trace() -> None:
    # 11.4: PDF ประกาศเตือนภัยได้ผลสรุปเต็ม (kind "warning") ใช้ตัวจัดประเภทของประกาศ ไม่ใช่โหมดทั่วไป
    data = _raw("warning/warning_2569_315.pdf")
    result = summarize_pdf(data, CLASSIFIER)
    assert not isinstance(result, SummarizeError) and result.kind == "warning", result
    doc = result.document
    assert doc.issue_id == "2569_315" and doc.series_no == 7 and doc.precautions
    traced = summarize_pdf(data, CLASSIFIER, trace=True)
    assert not isinstance(traced, SummarizeError) and traced.trace is not None
    assert traced.document.model_dump_json() == doc.model_dump_json()
    classify = next(s for s in traced.trace.steps if s.id == "classify")
    assert "ที่ฝึกจากประกาศเตือนภัย" in classify.note_th
