"""พยากรณ์รายวันและ 7 วันใน /demo: สร้าง Issue (ท่อประมวลผลเดิม) และภาพขั้นตอนจากผลระหว่างทาง."""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass

from tmd_plain.classify.features import NUM_TOKEN, normalize_tokens
from tmd_plain.classify.model_io import Classifier
from tmd_plain.contract import REGION_KEYS, REGION_LABELS_TH, Issue, SummarizeError, error_response
from tmd_plain.doctypes.registry import DocRun
from tmd_plain.extract.advice import context_units
from tmd_plain.extract.facts import Fact, extract_block
from tmd_plain.generate.assemble import meta_from_text
from tmd_plain.generate.fidelity import check_issue
from tmd_plain.pipeline import assemble_or_error, parse_or_error
from tmd_plain.prep.extract import SourceDocument
from tmd_plain.prep.periods import split_periods
from tmd_plain.prep.regions import ParsedIssue
from tmd_plain.prep.tokenize import tokenize
from tmd_plain.tracing import StepDraft, model_name_th

logger = logging.getLogger(__name__)

SCORE_DIGITS = 4

CHECKS_TH = [
    "F1 ตัวเลขทุกตัวมีที่มาในบล็อกของภาค",
    "F2 ชื่อจังหวัดอยู่ในต้นฉบับ",
    "F3 คำแนะนำคัดจากต้นฉบับคำต่อคำ",
    "F4 ไม่แปลงร้อยละของพื้นที่เป็นโอกาสฝน",
    "F5 ไม่มีตัวเลขข้ามภาค (ตามมาจาก F1)",
]


@dataclass(frozen=True)
class ForecastDetails:
    parsed: ParsedIssue


def run_forecast(doc: SourceDocument, classifier: Classifier) -> DocRun | SummarizeError:
    """ท่อประมวลผลเดิม + วันเวลาจากหัว PDF + ตรวจ F1-F5 ซ้ำ (ไม่ผ่าน = ข้อผิดพลาด ไม่แสดงค่าที่ไม่มีที่มา)."""
    parsed = parse_or_error(doc)
    if isinstance(parsed, SummarizeError):
        return parsed
    meta = meta_from_text(parsed.doc_type, doc.text)
    if meta is None:
        return error_response("extract_failed")
    issue = assemble_or_error(parsed, meta, classifier.label)
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
    return DocRun(document=issue, details=ForecastDetails(parsed))


def _facts(parsed: ParsedIssue, key: str) -> list[Fact]:
    # แบบเดียวกับตอนประกอบผล: รายวันทั้งบล็อก, 7 วันทีละช่วงวัน
    lines = parsed.regions[key].lines  # type: ignore[index]
    if parsed.doc_type == "daily":
        return extract_block(lines)
    return [f for pb in split_periods(lines, parsed.issue_range) for f in extract_block(pb.lines)]


def _line_texts(issue: Issue, key: str) -> list[str]:
    region = issue.regions[key]  # type: ignore[index]
    return [ln.text for ln in (*region.lines, *(ln for p in region.periods for ln in p.lines))]


def trace_forecast(run: DocRun, classifier: Classifier) -> list[StepDraft]:
    """ขั้นที่ท่อประมวลผลรายวัน/7 วันทำจริง คำนวณซ้ำจากผลระหว่างทาง (เรียกเฉพาะเมื่อขอ trace)."""
    parsed: ParsedIssue = run.details.parsed
    issue: Issue = run.document  # type: ignore[assignment]
    units = context_units(parsed)
    labels = [classifier.label(u.text) for u in units]
    by_region = {key: len(parsed.regions[key].lines) for key in REGION_KEYS}
    steps = [
        StepDraft(
            "segment",
            f"แยกภาพรวม {len(parsed.overview)} ย่อหน้า ข้อควรระวัง {len(parsed.caution)} ย่อหน้า และบล็อก 7 ภาค",
            data={
                "regions": [REGION_LABELS_TH[k] for k in REGION_KEYS],
                "lines_by_region": by_region,
                "overview_paragraphs": len(parsed.overview),
                "caution_paragraphs": len(parsed.caution),
            },
        ),
        StepDraft(
            "units",
            f"ตัดภาพรวมและข้อควรระวังเป็น {len(units)} หน่วยประโยค",
            data={"count": len(units), "units": [u.text for u in units]},
        ),
    ]
    advice_first = [u for u, label in zip(units, labels, strict=True) if label == "advice"]
    sample = (advice_first or units or [None])[0]
    if sample is None:
        steps += [
            StepDraft(sid, "ไม่มีหน่วยให้จัดประเภท", "skipped")
            for sid in ("tokenize", "filter_tokens", "classify")
        ]
    else:
        tokens = tokenize(sample.text)
        explained = classifier.explain(sample.text)
        steps += [
            StepDraft(
                "tokenize",
                "ตัวอย่างจากหน่วยแรกที่เป็นคำแนะนำ" if advice_first else "ตัวอย่างจากหน่วยแรก",
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
                f"{model_name_th(classifier.name)} จัด {len(units)} หน่วย หน่วยที่เป็นคำแนะนำไปขั้นแยกตามภาค",
                data={
                    "unit": sample.text,
                    "label": explained.label,
                    # ปัดเพื่อแสดงผล (ค่าจริงอย่าง 5e-52 อ่านไม่ได้) ป้ายที่เลือกมาจากคะแนนก่อนปัด
                    "scores": {c: round(v, SCORE_DIGITS) for c, v in explained.scores.items()},
                    "top_words": list(explained.top_words),
                    "label_counts": dict(sorted(Counter(labels).items())),
                },
            ),
        ]
    regional = {a.source_unit_id: a.text for r in issue.regions.values() for a in r.advice}
    steps.append(
        StepDraft(
            "scope",
            "คำแนะนำที่มีชื่อภาคไปภาคนั้น ไม่มีชื่อภาคเป็นข้อแนะนำทั่วไป",
            data={
                "general": len(issue.general_advice),
                "regional": len(regional),
                "advice_by_region": {k: len(issue.regions[k].advice) for k in REGION_KEYS},
                "advice": [a.text for a in issue.general_advice] + list(regional.values()),
            },
        )
    )
    facts = {key: _facts(parsed, key) for key in REGION_KEYS}
    first = next((k for k in REGION_KEYS if facts[k]), REGION_KEYS[0])
    steps.append(
        StepDraft(
            "extract",
            f"ตัวอย่างค่าที่ดึงได้ของ{REGION_LABELS_TH[first]}",
            data={
                "facts_by_region": {k: len(v) for k, v in facts.items()},
                "sample": [f"{f.name} = {f.value} ← {f.source}" for f in facts[first]],
            },
        )
    )
    lines = {key: _line_texts(issue, key) for key in REGION_KEYS}
    steps += [
        StepDraft(
            "template",
            f"ตัวอย่างประโยคของ{REGION_LABELS_TH[first]}",
            data={"lines_by_region": {k: len(v) for k, v in lines.items()}, "sample": lines[first]},
        ),
        StepDraft(
            "verify", "ผ่านทุกข้อ (ถ้าไม่ผ่านจะไม่แสดงผล)", data={"problems": 0, "checks": CHECKS_TH}
        ),
        StepDraft(
            "result",
            "ผลสรุป 7 ภาค",
            data={
                "doc_type": issue.doc_type,
                "issue_id": issue.issue_id,
                "lines": sum(len(v) for v in lines.values()),
                "advice": len(issue.general_advice) + len(regional),
            },
        ),
    ]
    return steps
