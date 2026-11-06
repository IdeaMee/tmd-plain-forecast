"""เลือกคำแนะนำจากย่อหน้าภาพรวม/ข้อควรระวังให้แต่ละภาค (ขั้น 2) คำแนะนำคัดจากต้นฉบับตรงๆ."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from tmd_plain.contract import REGION_KEYS, AdviceItem, RegionKey
from tmd_plain.extract.scope import advice_scope
from tmd_plain.prep.regions import ParsedIssue
from tmd_plain.prep.units import split_units, unit_id

# ข้อความหน่วย -> ป้าย (weather / advice / cause / other) จากตัวจัดประเภทที่อนุมัติ
Labeler = Callable[[str], str]


@dataclass(frozen=True)
class ContextUnit:
    text: str
    unit_id: str
    previous: tuple[str, ...]  # หน่วยก่อนหน้าในย่อหน้าเดียวกัน


def context_units(parsed: ParsedIssue) -> list[ContextUnit]:
    """หน่วยของภาพรวมและข้อควรระวัง ตามลำดับเดิม พร้อมหน่วยก่อนหน้าในย่อหน้า."""
    out: list[ContextUnit] = []
    for paragraph in (*parsed.overview, *parsed.caution):
        units = split_units(paragraph)
        for n, text in enumerate(units):
            out.append(ContextUnit(text, unit_id(parsed.doc_type, text), tuple(units[:n])))
    return out


@dataclass(frozen=True)
class AdviceSelection:
    regional: dict[RegionKey, list[AdviceItem]]
    general: list[AdviceItem]


def select_advice(parsed: ParsedIssue, label_of: Labeler) -> AdviceSelection:
    """หน่วยที่จัดเป็น advice -> ภาคตามตารางแมป; ไม่มีคำบอกที่ตั้ง -> ข้อแนะนำทั่วไป (ทุกหน่วยต้องไปที่ใดที่หนึ่ง)."""
    regional: dict[RegionKey, list[AdviceItem]] = {k: [] for k in REGION_KEYS}
    general: list[AdviceItem] = []
    seen: set[str] = set()
    for unit in context_units(parsed):
        if unit.unit_id in seen or label_of(unit.text) != "advice":
            continue
        seen.add(unit.unit_id)
        scope = advice_scope(unit.text, unit.previous)
        item = AdviceItem(
            text=unit.text,
            scope=list(scope.regions),
            general=scope.general,
            source_unit_id=unit.unit_id,
        )
        if scope.general:
            general.append(item)
        else:
            for key in scope.regions:
                regional[key].append(item)
    return AdviceSelection(regional, general)
