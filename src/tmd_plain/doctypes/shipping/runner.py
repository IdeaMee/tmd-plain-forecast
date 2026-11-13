"""พยากรณ์เดินเรือใน /demo และ run_pipeline: ท่อประมวลผลเต็ม + ภาพขั้นตอนจากผลระหว่างทาง."""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass

from pydantic import ValidationError

from tmd_plain.classify.features import NUM_TOKEN, normalize_tokens
from tmd_plain.classify.model_io import Classifier
from tmd_plain.contract import (
    SEA_AREA_KEYS,
    SEA_AREA_LABELS_TH,
    ShippingIssue,
    SummarizeError,
    error_response,
)
from tmd_plain.doctypes.registry import DocRun
from tmd_plain.doctypes.shipping.build import (
    OverviewUnit,
    area_facts,
    assemble_shipping,
    check_shipping,
    overview_units,
)
from tmd_plain.doctypes.shipping.parse import ParsedShipping, ShippingParseError, parse_shipping
from tmd_plain.extract.advice import Labeler
from tmd_plain.generate.templates import GenerateError
from tmd_plain.prep.extract import SourceDocument
from tmd_plain.prep.tokenize import tokenize
from tmd_plain.tracing import StepDraft, model_name_th

logger = logging.getLogger(__name__)

SCORE_DIGITS = 4
CHECKS_TH = [
    "F1 ตัวเลขทุกตัวมีที่มาในบล็อกของพื้นที่ทะเล (หรือส่วนตอนบน/ตอนล่าง) นั้น",
    "F2 ชื่อจังหวัดอยู่ในต้นฉบับ",
    "F3 ภาพรวมและคำแนะนำคัดจากต้นฉบับคำต่อคำ",
    "F4 ไม่แปลงร้อยละของพื้นที่เป็นโอกาสฝน",
]


@dataclass(frozen=True)
class ShippingDetails:
    parsed: ParsedShipping
    units: tuple[OverviewUnit, ...]


def summarize_shipping(
    text: str, label_of: Labeler, source_label: str | None = None
) -> DocRun | SummarizeError:
    """ข้อความสะอาด -> ShippingIssue ที่ผ่าน F1-F4; โครงไม่ตรง/ไม่ผ่านตรวจ = extract_failed (ไม่เดา)."""
    try:
        parsed = parse_shipping(text)
    except ShippingParseError as exc:
        logger.warning("shipping parse failed: %s", exc)
        return error_response("extract_failed")
    units = overview_units(parsed, label_of)
    try:
        issue = assemble_shipping(parsed, units, source_label)
    except (GenerateError, ValidationError) as exc:
        logger.warning("shipping assemble failed issue=%s: %s", parsed.issue_id, exc)
        return error_response("extract_failed")
    problems = check_shipping(issue, parsed)
    if problems:
        logger.warning(
            "shipping fidelity failed issue=%s count=%d first=%s",
            issue.issue_id,
            len(problems),
            problems[0],
        )
        return error_response("extract_failed")
    return DocRun(document=issue, details=ShippingDetails(parsed, tuple(units)))


def run_shipping(doc: SourceDocument, classifier: Classifier) -> DocRun | SummarizeError:
    return summarize_shipping(doc.text, classifier.label)


def _area_texts(issue: ShippingIssue, key: str) -> list[str]:
    area = issue.areas[key]  # type: ignore[index]
    return [ln.text for ln in (*area.lines, *(ln for p in area.parts for ln in p.lines))]


def trace_shipping(run: DocRun, classifier: Classifier) -> list[StepDraft]:
    """ขั้นที่ท่อประมวลผลเดินเรือทำจริง คำนวณซ้ำจากผลระหว่างทาง (เรียกเฉพาะเมื่อขอ trace)."""
    details: ShippingDetails = run.details
    parsed, units = details.parsed, list(details.units)
    issue: ShippingIssue = run.document  # type: ignore[assignment]
    names = [SEA_AREA_LABELS_TH[k] for k in SEA_AREA_KEYS]
    steps = [
        StepDraft(
            "segment",
            f"แยกภาพรวม บรรทัดออกประกาศ และ {len(parsed.areas)} พื้นที่ทะเล (อ่าวไทยแยกตอนบน/ตอนล่าง)",
            data={
                "areas": names,
                "lines_by_area": {
                    SEA_AREA_LABELS_TH[k]: len(b.all_lines()) for k, b in parsed.areas.items()
                },
                "issued": parsed.issued_line,
            },
        ),
        StepDraft(
            "units",
            f"ตัดภาพรวมเป็น {len(units)} ท่อน (ตัดที่ สำหรับ/ชาวเรือ/เรือเล็ก/ขอให้)",
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
                f"{model_name_th(classifier.name)} จัด {len(units)} ท่อน ท่อนที่เป็นคำแนะนำคัดคำต่อคำ ที่เหลือเป็นภาพรวม",
                data={
                    "unit": sample.text,
                    "label": explained.label,
                    "scores": {c: round(v, SCORE_DIGITS) for c, v in explained.scores.items()},
                    "top_words": list(explained.top_words),
                    "label_counts": dict(sorted(Counter(u.label for u in units).items())),
                },
            ),
        ]
    steps.append(
        StepDraft(
            "scope",
            "คำแนะนำของชาวเรือคัดคำต่อคำ ภาคที่เกี่ยวข้องดูจากชื่อทะเล/ภาคในประโยค",
            data={"advice": [a.text for a in issue.advice], "count": len(issue.advice)},
        )
    )
    facts = {k: area_facts(b) for k, b in parsed.areas.items()}
    first = next((k for k in SEA_AREA_KEYS if facts[k]), SEA_AREA_KEYS[0])
    steps.append(
        StepDraft(
            "extract",
            f"ตัวอย่างค่าที่ดึงได้ของ{SEA_AREA_LABELS_TH[first]} (ลมทั้งนอตและ กม./ชม. ตามต้นฉบับ)",
            data={
                "facts_by_area": {SEA_AREA_LABELS_TH[k]: len(v) for k, v in facts.items()},
                "sample": [f"{f.name} = {f.value} ← {f.source}" for f in facts[first]],
            },
        )
    )
    lines = {k: _area_texts(issue, k) for k in SEA_AREA_KEYS}
    steps += [
        StepDraft(
            "template",
            f"ตัวอย่างประโยคของ{SEA_AREA_LABELS_TH[first]}",
            data={
                "lines_by_area": {SEA_AREA_LABELS_TH[k]: len(v) for k, v in lines.items()},
                "sample": lines[first],
            },
        ),
        StepDraft(
            "verify", "ผ่านทุกข้อ (ถ้าไม่ผ่านจะไม่แสดงผล)", data={"problems": 0, "checks": CHECKS_TH}
        ),
        StepDraft(
            "result",
            f"ผลสรุป {len(SEA_AREA_KEYS)} พื้นที่ทะเล",
            data={
                "doc_type": "shipping",
                "issue_id": issue.issue_id,
                "lines": sum(len(v) for v in lines.values()),
                "advice": len(issue.advice),
            },
        ),
    ]
    return steps
