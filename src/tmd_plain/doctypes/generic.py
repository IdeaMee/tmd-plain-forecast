"""โหมดทั่วไปใน /demo: เอกสาร TMD ที่ไม่ใช่ชนิดที่สรุปเต็ม (ADR 0017) และภาพขั้นตอนของโหมดนี้."""

from __future__ import annotations

import logging
from collections import Counter

from tmd_plain.classify.features import NUM_TOKEN, normalize_tokens
from tmd_plain.classify.model_io import Classifier
from tmd_plain.config import load_config
from tmd_plain.contract import (
    REGION_KEYS,
    REGION_LABELS_TH,
    GenericDocument,
    SummarizeError,
    error_response,
)
from tmd_plain.doctypes.registry import DocRun
from tmd_plain.generic.build import GenericDetails, build_generic
from tmd_plain.generic.fidelity import check_generic
from tmd_plain.prep.extract import SourceDocument
from tmd_plain.prep.tokenize import tokenize
from tmd_plain.tracing import StepDraft, model_name_th

logger = logging.getLogger(__name__)

SCORE_DIGITS = 4
CHECKS_TH = [
    "ทุกหน่วยเป็นข้อความต้นฉบับ (ไม่เขียนใหม่)",
    "ตัวเลข วันที่ และจังหวัดที่ไฮไลต์อยู่ในหน่วยนั้นจริง",
    "ภาคมาจากคำบอกที่ตั้งในหน่วย ตามตารางแมปภาค",
    "คำอธิบายศัพท์มาจากหมายเหตุของกรมอุตุนิยมวิทยาเท่านั้น",
]


def run_generic(doc: SourceDocument, classifier: Classifier) -> DocRun | SummarizeError:
    """โครง + ป้ายประโยค + ไฮไลต์ แล้วตรวจว่าทุกอย่างมาจากต้นฉบับ (ไม่ผ่าน = ข้อผิดพลาด ไม่แสดงค่าที่ไม่มีที่มา)."""
    document, details = build_generic(doc, classifier, load_config()["generic"])
    if not details.units:
        # มีแค่เลขหน้า/สัญลักษณ์ (เช่น ภาพสแกนที่มีเลขหน้าพิมพ์ไว้) = อ่านข้อความไม่ได้ ไม่ส่งผลว่างเปล่า
        return error_response("extract_failed")
    problems = check_generic(document, doc.text)
    if problems:
        logger.warning("generic check failed count=%d first=%s", len(problems), problems[0])
        return error_response("extract_failed")
    return DocRun(document=document, details=details)


def trace_generic(run: DocRun, classifier: Classifier) -> list[StepDraft]:
    """ขั้นที่โหมดทั่วไปทำจริง (ไม่มีขั้นแม่แบบ เพราะไม่เขียนข้อความใหม่)."""
    details: GenericDetails = run.details
    document: GenericDocument = run.document  # type: ignore[assignment]
    units = list(details.units)
    headings = [b.heading for b in details.layout.blocks if b.heading]
    steps = [
        StepDraft(
            "segment",
            f"ต่อบรรทัดของ PDF กลับเป็นย่อหน้า แบ่งตามหัวข้อได้ {len(document.sections)} ส่วน",
            data={
                "title": document.title or "",
                "headings": headings,
                "region_leads": list(details.layout.region_leads),
                "has_region_headings": document.has_region_headings,
            },
        ),
        StepDraft(
            "units",
            f"ตัดย่อหน้าเป็น {len(units)} หน่วยประโยค"
            + (
                f" (ตัดส่วนท้าย {details.dropped_units} หน่วยเพราะเกินเพดาน)"
                if details.dropped_units
                else ""
            ),
            data={"count": len(units), "units": [r.unit.text for r in units]},
        ),
    ]
    advice = [r for r in units if r.unit.label == "advice"]
    sample = (advice or units or [None])[0]
    if sample is None:
        steps += [
            StepDraft(sid, "ไม่มีหน่วยให้จัดประเภท", "skipped")
            for sid in ("tokenize", "filter_tokens", "classify")
        ]
    else:
        tokens = tokenize(sample.unit.text)
        ex = sample.explanation
        steps += [
            StepDraft(
                "tokenize",
                "ตัวอย่างจากหน่วยแรกที่เป็นคำแนะนำ" if advice else "ตัวอย่างจากหน่วยแรก",
                data={"unit": sample.unit.text, "tokens": tokens},
            ),
            StepDraft(
                "filter_tokens",
                f"ทิ้งเครื่องหมาย ตัวเลขเป็น {NUM_TOKEN} และข้ามคำที่ไม่อยู่ในคลังคำของโมเดล (ไม่มีการตัด stop word)",
                data={
                    "kept": normalize_tokens(tokens),
                    "dropped": [t for t in tokens if not normalize_tokens([t])],
                    "numbers": [t for t in tokens if normalize_tokens([t]) == [NUM_TOKEN]],
                    "unknown": list(ex.unknown_words),
                    "known_ratio": round(sample.known_ratio, SCORE_DIGITS),
                },
            ),
            StepDraft(
                "classify",
                f"{model_name_th(classifier.name)} ที่ฝึกจากพยากรณ์รายวัน/7 วัน: ไม่แน่ใจ {sum(r.unit.uncertain for r in units)} จาก {len(units)} หน่วย",
                data={
                    "unit": sample.unit.text,
                    "label": ex.label,
                    "scores": {c: round(v, SCORE_DIGITS) for c, v in ex.scores.items()},
                    "top_words": list(ex.top_words),
                    "label_counts": dict(sorted(Counter(r.unit.label for r in units).items())),
                    "uncertain": sum(r.unit.uncertain for r in units),
                },
            ),
        ]
    by_region = {k: sum(k in r.unit.regions for r in units) for k in REGION_KEYS}
    steps.append(
        StepDraft(
            "scope",
            "ภาคจากชื่อภาค ชื่อทะเล และชื่อจังหวัดในแต่ละหน่วย (ตารางแมปภาค v1)",
            data={
                "units_with_region": sum(bool(r.unit.regions) for r in units),
                "units_by_region": {REGION_LABELS_TH[k]: v for k, v in by_region.items()},
            },
        )
    )
    numbers = [n for r in units for n in r.unit.numbers]
    dates = [d for r in units for d in r.unit.dates]
    provinces = list(dict.fromkeys(p for r in units for p in r.unit.provinces))
    steps += [
        StepDraft(
            "extract",
            f"ไฮไลต์ตัวเลข {len(numbers)} จุด วันที่ {len(dates)} จุด จังหวัด {len(provinces)} จังหวัด (regex)",
            data={"numbers": numbers, "dates": dates, "provinces": provinces},
        ),
        StepDraft(
            "verify",
            "ผ่านทุกข้อ (ถ้าไม่ผ่านจะไม่แสดงผล)",
            data={"problems": 0, "checks": CHECKS_TH},
            title_th="ตรวจว่าทุกอย่างมาจากต้นฉบับ",
        ),
        StepDraft(
            "result",
            "เอกสารของกรมอุตุนิยมวิทยา"
            if document.tmd_like
            else "ไม่พบชื่อกรมอุตุนิยมวิทยาในเอกสาร แสดงพร้อมคำเตือน",
            data={
                "sections": len(document.sections),
                "units": len(units),
                "advice": len(advice),
                "glossary": [g.term for g in document.glossary],
                "truncated": document.truncated,
            },
        ),
    ]
    return steps
