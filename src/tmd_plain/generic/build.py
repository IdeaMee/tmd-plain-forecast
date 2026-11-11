"""ประกอบ GenericDocument: โครงเอกสาร -> หน่วยประโยค -> ป้าย + ความมั่นใจ -> ช่วงข้อความที่ไฮไลต์.

ไม่มีข้อความที่เขียนใหม่: ทุกหน่วยคือข้อความต้นฉบับที่ต่อบรรทัดกลับแล้วตัดตามกติกาหน่วยเดิม (prep/units.py)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from tmd_plain.classify.features import bag_of_words
from tmd_plain.classify.model_io import Classifier, Explanation
from tmd_plain.contract import GenericDocument, GenericSection, GenericUnit, GlossaryEntry
from tmd_plain.generate.glossary import cold_glossary
from tmd_plain.generic import spans
from tmd_plain.generic.layout import Layout, build_layout, has_region_headings
from tmd_plain.prep.extract import SourceDocument
from tmd_plain.prep.units import split_units, unit_id

# คำบอกว่าเป็นเอกสารของกรมอุตุนิยมวิทยา (ชื่อกรมหรือโดเมน) ไม่พบ = แสดงพร้อมคำเตือน not_tmd_like
_TMD_MARKERS = ("กรมอุตุนิยมวิทยา", "tmd.go.th", "thai meteorological department")
# "อากาศหนาว" ที่เป็นส่วนของ "อากาศหนาวจัด" หรือ "อากาศหนาวเย็น" ไม่ใช่ระดับอากาศหนาว
_TERM_GUARD = {"อากาศหนาว": "(?!จัด|เย็น)"}
CONFIDENCE_DIGITS = 4


@dataclass(frozen=True)
class UnitRun:
    unit: GenericUnit
    section: int
    explanation: Explanation
    known_ratio: float


@dataclass(frozen=True)
class GenericDetails:
    layout: Layout
    units: tuple[UnitRun, ...]
    dropped_units: int


def is_tmd_like(text: str, ratios: list[float], cfg: dict[str, Any]) -> bool:
    """มีชื่อกรม/โดเมน หรือคำส่วนใหญ่อยู่ในคลังคำพยากรณ์ของ TMD (เอกสารบางชนิด เช่น แผนที่สรุปรายสัปดาห์ ไม่มีชื่อกรม)."""
    lowered = text.lower()
    if any(m in lowered for m in _TMD_MARKERS):
        return True
    if len(ratios) < cfg["tmd_vocab_min_units"]:
        return False
    return sum(ratios) / len(ratios) >= cfg["tmd_vocab_ratio"]


def known_ratio(text: str, explanation: Explanation) -> float:
    """สัดส่วนคำของหน่วยที่อยู่ในคลังคำของโมเดล (คำนอกคลังถูกข้ามตอนคำนวณ)."""
    bag = bag_of_words(text)
    total = sum(bag.values())
    if not total:
        return 0.0
    unknown = sum(bag[w] for w in explanation.unknown_words)
    return (total - unknown) / total


def glossary_for(text: str) -> list[GlossaryEntry]:
    out = []
    for term, explanation in cold_glossary().items():
        if re.search(re.escape(term) + _TERM_GUARD.get(term, ""), text):
            out.append(GlossaryEntry(term=term, explanation=explanation))
    return out


def _unique_id(text: str, seen: set[str]) -> str:
    # รหัสคงที่จากข้อความ (เหมือนหน่วยของรายวัน) ข้อความซ้ำในเอกสารเดียวต่อท้ายลำดับ
    base = unit_id("generic", text)
    uid, n = base, 1
    while uid in seen:
        n += 1
        uid = f"{base}-{n}"
    seen.add(uid)
    return uid


def _make_unit(
    text: str, uid: str, explanation: Explanation, ratio: float, cfg: dict[str, Any]
) -> GenericUnit:
    confidence = round(explanation.scores.get(explanation.label, 0.0), CONFIDENCE_DIGITS)
    return GenericUnit(
        unit_id=uid,
        text=text,
        label=explanation.label,  # type: ignore[arg-type]
        confidence=confidence,
        uncertain=confidence < cfg["uncertain_below"] or ratio < cfg["min_known_ratio"],
        regions=spans.regions(text),
        provinces=spans.provinces(text),
        numbers=spans.numbers(text),
        dates=spans.dates(text),
    )


def _document(
    doc: SourceDocument, layout: Layout, runs: list[UnitRun], truncated: bool, tmd_like: bool
) -> GenericDocument:
    sections = [
        GenericSection(heading=block.heading, units=[r.unit for r in runs if r.section == i])
        for i, block in enumerate(layout.blocks)
    ]
    return GenericDocument(
        title=layout.title,
        tmd_like=tmd_like,
        warnings=[] if tmd_like else ["not_tmd_like"],
        page_count=max(doc.pages, 1),
        char_count=len(doc.text),
        has_region_headings=has_region_headings(layout),
        sections=[s for s in sections if s.heading is not None or s.units],
        glossary=glossary_for(doc.text),
        truncated=truncated,
    )


def _size(model: GenericDocument) -> int:
    return len(json.dumps(model.model_dump(mode="json"), ensure_ascii=False).encode("utf-8"))


def build_generic(
    doc: SourceDocument, classifier: Classifier, cfg: dict[str, Any]
) -> tuple[GenericDocument, GenericDetails]:
    layout = build_layout(doc.text, cfg["heading_max_chars"])
    seen: set[str] = set()
    runs: list[UnitRun] = []
    total = 0
    for i, block in enumerate(layout.blocks):
        for paragraph in block.paragraphs:
            for text in split_units(paragraph):
                total += 1
                if len(runs) >= cfg["max_units"]:
                    continue
                explanation = classifier.explain(text)
                ratio = known_ratio(text, explanation)
                unit = _make_unit(text, _unique_id(text, seen), explanation, ratio, cfg)
                runs.append(UnitRun(unit, i, explanation, ratio))
    truncated = total > len(runs)
    # ตัดสินจากหน่วยทั้งหมดที่วิเคราะห์ ก่อนตัดเพราะขนาด ผลจึงไม่ขึ้นกับเพดาน
    tmd_like = is_tmd_like(doc.text, [r.known_ratio for r in runs], cfg)
    document = _document(doc, layout, runs, truncated, tmd_like)
    # ผลใหญ่เกินเพดาน: ตัดหน่วยท้ายทีละ 10% จนพอดี
    while runs and _size(document) > cfg["max_json_bytes"]:
        runs = runs[: max(1, len(runs) * 9 // 10)] if len(runs) > 1 else []
        truncated = True
        document = _document(doc, layout, runs, truncated, tmd_like)
    return document, GenericDetails(layout, tuple(runs), total - len(runs))
