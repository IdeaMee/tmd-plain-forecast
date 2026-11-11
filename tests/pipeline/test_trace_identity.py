import json
import sys
from pathlib import Path

import pytest

from tmd_plain.classify.model_io import load_classifier
from tmd_plain.contract import TRACE_MAX_BYTES, TRACE_MAX_ITEMS, SummarizeError
from tmd_plain.raw_io import load_manifest
from tmd_plain.service import summarize_pdf

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
GOLDEN = ROOT / "tests" / "golden" / "trace" / "daily_161120261800_pdf.json"
CLASSIFIER = load_classifier(ROOT / "models")
sys.path.insert(0, str(ROOT / "scripts"))
import make_golden_trace  # noqa: E402
import run_pipeline  # noqa: E402


def _display_pdfs() -> list[Path]:
    if not (RAW / "MANIFEST.csv").exists():
        return []
    return [i.pdf for i in load_manifest(RAW) if i.role == "display_test" and i.pdf is not None]


def test_processed_files_are_unchanged() -> None:
    # ท่อประมวลผลบนเครื่อง (ไม่มี trace) ต้องเขียนไฟล์เดิมทุกไบต์
    issues = run_pipeline.display_issues() if (RAW / "MANIFEST.csv").exists() else []
    if not issues:
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    for issue in issues:
        result = run_pipeline.run_one(issue, CLASSIFIER.label)
        assert not isinstance(result, SummarizeError), issue.issue_id
        expected = run_pipeline.out_path(issue).read_text(encoding="utf-8")
        assert run_pipeline.render(result) == expected, issue.issue_id


def test_trace_never_changes_the_summary() -> None:
    # ทุก PDF ของชุดแสดงผล: เปิด/ปิด trace ได้ document เดียวกันทุกไบต์ และ trace อยู่ในเพดาน
    pdfs = _display_pdfs()
    if not pdfs:
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    for pdf in pdfs:
        data = pdf.read_bytes()
        plain = summarize_pdf(data, CLASSIFIER)
        traced = summarize_pdf(data, CLASSIFIER, trace=True)
        if isinstance(plain, SummarizeError):
            assert traced == plain, pdf.name
            continue
        assert not isinstance(traced, SummarizeError), pdf.name
        assert plain.trace is None and traced.trace is not None
        dump = lambda r: json.dumps(r.document.model_dump(mode="json"), ensure_ascii=False)  # noqa: E731
        assert dump(plain) == dump(traced), pdf.name
        body = json.dumps(
            traced.trace.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":")
        )
        assert len(body.encode("utf-8")) <= TRACE_MAX_BYTES
        for step in traced.trace.steps:
            for value in step.data.values():
                if isinstance(value, (list, dict)):
                    assert len(value) <= TRACE_MAX_ITEMS


def test_golden_trace() -> None:
    if not make_golden_trace.SOURCE.exists():
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    expected = GOLDEN.read_text(encoding="utf-8")
    assert make_golden_trace.build() == expected, "รัน scripts/make_golden_trace.py แล้วอ่าน diff"
