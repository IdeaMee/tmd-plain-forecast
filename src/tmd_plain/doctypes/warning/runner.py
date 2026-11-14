"""ประกาศเตือนภัยใน /demo และสคริปต์บนเครื่อง: ท่อประมวลผลเต็ม + ภาพขั้นตอนจากผลระหว่างทาง."""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass

from pydantic import ValidationError

from tmd_plain.classify.features import NUM_TOKEN, normalize_tokens
from tmd_plain.classify.model_io import Classifier
from tmd_plain.contract import REGION_LABELS_TH, SummarizeError, WarningNotice, error_response
from tmd_plain.doctypes.registry import DocRun
from tmd_plain.doctypes.warning.build import (
    WarningUnit,
    assemble_warning,
    check_warning,
    warning_units,
)
from tmd_plain.doctypes.warning.parse import ParsedWarning, WarningParseError, parse_warning
from tmd_plain.extract.advice import Labeler
from tmd_plain.prep.extract import SourceDocument
from tmd_plain.prep.tokenize import tokenize
from tmd_plain.tracing import StepDraft, model_name_th

logger = logging.getLogger(__name__)

SCORE_DIGITS = 4
CHECKS_TH = [
    "หัวเรื่อง ฉบับที่ เลขประกาศ และช่วงที่มีผล คัดจากหัวประกาศคำต่อคำ",
    "วันที่อ่านได้ตรงกับตัวเลขในต้นฉบับ (วันประกาศ ช่วงที่มีผล ฉบับต่อไป)",
    "ทุกท่อนและข้อควรระวังคัดจากเนื้อหาคำต่อคำ",
    "ชื่อจังหวัดอยู่ในต้นฉบับ",
    "ไม่แปลงร้อยละของพื้นที่เป็นโอกาสฝน",
]


def _trained_on(classifier: Classifier) -> str:
    if classifier.doc_type == "warning":
        return "ที่ฝึกจากประกาศเตือนภัย (ป้าย weather/cause/advice)"
    return "ที่ฝึกจากพยากรณ์รายวัน/7 วัน"


@dataclass(frozen=True)
class WarningDetails:
    parsed: ParsedWarning
    units: tuple[WarningUnit, ...]


def summarize_warning(
    text: str, label_of: Labeler, source_label: str | None = None
) -> DocRun | SummarizeError:
    """ข้อความสะอาด -> WarningNotice ที่ผ่านตัวตรวจ; โครงไม่ตรง/ไม่ผ่านตรวจ = extract_failed (ไม่เดา)."""
    try:
        parsed = parse_warning(text)
    except WarningParseError as exc:
        logger.warning("warning parse failed: %s", exc)
        return error_response("extract_failed")
    units = warning_units(parsed, label_of)
    try:
        notice = assemble_warning(parsed, units, source_label)
    except ValidationError as exc:
        logger.warning("warning assemble failed issue=%s: %s", parsed.issue_id, exc)
        return error_response("extract_failed")
    problems = check_warning(notice, parsed)
    if problems:
        logger.warning(
            "warning fidelity failed issue=%s count=%d first=%s",
            notice.issue_id,
            len(problems),
            problems[0],
        )
        return error_response("extract_failed")
    return DocRun(document=notice, details=WarningDetails(parsed, tuple(units)))


def run_warning(doc: SourceDocument, classifier: Classifier) -> DocRun | SummarizeError:
    # ตัวจัดประเภทของประกาศ (11.3) ถ้ามี ไม่มีใช้ตัวของรายวัน
    return summarize_warning(doc.text, classifier.for_doc("warning").label)


def trace_warning(run: DocRun, classifier: Classifier) -> list[StepDraft]:
    """ขั้นที่ท่อประมวลผลประกาศเตือนภัยทำจริง (ไม่มีขั้นแม่แบบ: เนื้อหาคัดคำต่อคำ)."""
    details: WarningDetails = run.details
    classifier = classifier.for_doc("warning")
    parsed, units = details.parsed, list(details.units)
    notice: WarningNotice = run.document  # type: ignore[assignment]
    steps = [
        StepDraft(
            "segment",
            "แยกหัวประกาศ (เรื่อง ช่วงที่มีผล ฉบับที่) เนื้อหา และบรรทัดประกาศ ณ วันที่",
            data={
                "title": parsed.title,
                "effect": parsed.effect_text or "ไม่มีในต้นฉบับ",
                "number": f"ฉบับที่ {parsed.series_no} ({parsed.notice_no})",
                "issued": parsed.issued_line,
                "next": parsed.next_line or "ไม่มีในต้นฉบับ",
                "paragraphs": len(parsed.paragraphs),
            },
        ),
        StepDraft(
            "units",
            f"ตัดเนื้อหาเป็น {len(units)} ท่อน (กติกาเดียวกับรายวัน + ตัดที่ สำหรับ/ชาวเรือ/เรือเล็ก/ขอให้)",
            data={"count": len(units), "units": [u.text for u in units]},
        ),
    ]
    advice_first = [u for u in units if u.label == "advice"]
    sample = (advice_first or units)[0] if units else None
    if sample is None:
        steps += [
            StepDraft(sid, "ไม่มีท่อนให้จัดประเภท", "skipped")
            for sid in ("tokenize", "filter_tokens", "classify")
        ]
    else:
        tokens = tokenize(sample.text)
        explained = classifier.explain(sample.text)
        steps += [
            StepDraft(
                "tokenize",
                "ตัวอย่างจากท่อนแรกที่เป็นคำแนะนำ" if advice_first else "ตัวอย่างจากท่อนแรก",
                data={"unit": sample.text, "tokens": tokens},
            ),
            StepDraft(
                "filter_tokens",
                f"ทิ้งเครื่องหมาย ตัวเลขเป็น {NUM_TOKEN} และข้ามคำที่ไม่อยู่ในคลังคำของโมเดล (ไม่มีการตัด stop word)",
                data={
                    "kept": normalize_tokens(tokens),
                    "dropped": [t for t in tokens if not normalize_tokens([t])],
                    "numbers": [t for t in tokens if normalize_tokens([t]) == [NUM_TOKEN]],
                    "unknown": list(explained.unknown_words),
                },
            ),
            StepDraft(
                "classify",
                f"{model_name_th(classifier.name)} {_trained_on(classifier)} จัด {len(units)} ท่อน "
                "ท่อนที่เป็นคำแนะนำ (advice) เป็นข้อควรระวัง",
                data={
                    "unit": sample.text,
                    "label": explained.label,
                    "scores": {c: round(v, SCORE_DIGITS) for c, v in explained.scores.items()},
                    "top_words": list(explained.top_words),
                    "label_counts": dict(sorted(Counter(u.label for u in units).items())),
                },
            ),
        ]
    steps += [
        StepDraft(
            "scope",
            "ภาคจากชื่อภาค/จังหวัดในหัวเรื่องและเนื้อหา (ตารางแมปภาค v1) จังหวัดคำต่อคำ",
            data={
                "regions": [REGION_LABELS_TH[k] for k in notice.regions],
                "provinces": list(notice.provinces),
                "precautions": len(notice.precautions),
            },
        ),
        StepDraft(
            "extract",
            "วันที่จากหัวประกาศ (ช่วงที่มีผล วันประกาศ ฉบับต่อไป)",
            data={
                "effect_start": str(notice.effect.start)
                if notice.effect and notice.effect.start
                else "-",
                "effect_end": str(notice.effect.end)
                if notice.effect and notice.effect.end
                else "-",
                "issued_at": notice.issued_at.isoformat(),
                "next_issue_at": notice.next_issue_at.isoformat() if notice.next_issue_at else "-",
            },
        ),
        StepDraft(
            "verify", "ผ่านทุกข้อ (ถ้าไม่ผ่านจะไม่แสดงผล)", data={"problems": 0, "checks": CHECKS_TH}
        ),
        StepDraft(
            "result",
            f"ประกาศฉบับที่ {notice.series_no} ({notice.notice_no})",
            data={
                "doc_type": "warning",
                "issue_id": notice.issue_id,
                "lines": len(notice.lines),
                "precautions": len(notice.precautions),
            },
        ),
    ]
    return steps
