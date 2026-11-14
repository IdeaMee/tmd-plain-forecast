"""ทะเบียนชนิดเอกสาร: ชนิดที่ตรวจพบ -> ตัวสร้างผล + ตัวสร้างภาพขั้นตอน.

เพิ่มชนิดใหม่ (แผน 11-12) = เพิ่มคำบอกชนิดใน prep/doctype.py และเพิ่มรายการใน registry() ไม่ต้องแก้ service.py
ชนิดที่ไม่รู้จักไปโหมดทั่วไป (generic_spec) ไม่ปฏิเสธ
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from typing import Any

from tmd_plain.classify.model_io import Classifier
from tmd_plain.contract import DocumentModel, ResultKind, SummarizeError
from tmd_plain.prep.doctype import detect_doc_type
from tmd_plain.prep.extract import SourceDocument
from tmd_plain.tracing import StepDraft


@dataclass(frozen=True)
class DocRun:
    document: DocumentModel
    # ผลระหว่างทางของชนิดนั้น ใช้สร้างภาพขั้นตอนเท่านั้น (ไม่อยู่ในคำตอบ)
    details: Any


Runner = Callable[[SourceDocument, Classifier], DocRun | SummarizeError]
TraceBuilder = Callable[[DocRun, Classifier], list[StepDraft]]


@dataclass(frozen=True)
class DocTypeSpec:
    key: str
    kind: ResultKind
    run: Runner
    trace: TraceBuilder


def _forecast_specs() -> tuple[DocTypeSpec, ...]:
    # นำเข้าในฟังก์ชันเพื่อไม่ให้วนกับ pipeline.py
    from tmd_plain.doctypes.forecast import run_forecast, trace_forecast

    return (
        DocTypeSpec("daily", "issue", run_forecast, trace_forecast),
        DocTypeSpec("sevenday", "issue", run_forecast, trace_forecast),
    )


def _shipping_specs() -> tuple[DocTypeSpec, ...]:
    from tmd_plain.doctypes.shipping.runner import run_shipping, trace_shipping

    return (DocTypeSpec("shipping", "shipping", run_shipping, trace_shipping),)


def _warning_specs() -> tuple[DocTypeSpec, ...]:
    from tmd_plain.doctypes.warning.runner import run_warning, trace_warning

    return (DocTypeSpec("warning", "warning", run_warning, trace_warning),)


@cache
def registry() -> dict[str, DocTypeSpec]:
    return {spec.key: spec for spec in (*_forecast_specs(), *_shipping_specs(), *_warning_specs())}


@cache
def generic_spec() -> DocTypeSpec:
    from tmd_plain.doctypes.generic import run_generic, trace_generic

    return DocTypeSpec("generic", "generic", run_generic, trace_generic)


def spec_for(text: str) -> DocTypeSpec:
    """ชนิดที่รู้จักของข้อความนี้; ไม่รู้จัก = โหมดทั่วไป (ADR 0017, 10.3)."""
    return registry().get(detect_doc_type(text)) or generic_spec()
