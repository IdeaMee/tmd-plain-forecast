"""ตรวจความถูกต้องของโหมดทั่วไป (แบบ F1-F3): ทุกข้อความ ตัวเลข วันที่ จังหวัด มาจากต้นฉบับคำต่อคำ."""

from __future__ import annotations

import re

from tmd_plain.contract import GenericDocument
from tmd_plain.generate.glossary import cold_glossary
from tmd_plain.generic import spans
from tmd_plain.generic.layout import content_lines

_WS = re.compile(r"\s+")


def _flat(text: str) -> str:
    # ย่อหน้าถูกต่อจากหลายบรรทัด เทียบโดยไม่สนช่องว่าง
    return _WS.sub("", text)


def check_generic(document: GenericDocument, source_text: str) -> list[str]:
    """รายการปัญหา (ว่าง = ผ่าน)."""
    problems: list[str] = []
    # เทียบกับต้นฉบับที่ตัดบรรทัดเลขหน้าออก (layout ต่อย่อหน้าข้ามเลขหน้าที่ PDF แทรกกลางประโยค)
    flat_source = _flat("\n".join(content_lines(source_text)))
    glossary = cold_glossary()
    if document.title is not None and document.title not in source_text:
        problems.append(f"title ไม่อยู่ในต้นฉบับ: {document.title}")
    for section in document.sections:
        if section.heading is not None and section.heading not in source_text:
            problems.append(f"heading ไม่อยู่ในต้นฉบับ: {section.heading}")
        for unit in section.units:
            if _flat(unit.text) not in flat_source:
                problems.append(f"{unit.unit_id} ข้อความไม่อยู่ในต้นฉบับ")
            for name, values in (
                ("numbers", unit.numbers),
                ("dates", unit.dates),
                ("provinces", unit.provinces),
            ):
                problems += [
                    f"{unit.unit_id} {name} {v!r} ไม่อยู่ในหน่วย" for v in values if v not in unit.text
                ]
            if unit.regions != spans.regions(unit.text):
                problems.append(f"{unit.unit_id} regions ไม่ตรงกับคำบอกที่ตั้งในหน่วย")
    for entry in document.glossary:
        if glossary.get(entry.term) != entry.explanation:
            problems.append(f"glossary {entry.term} ไม่ตรงกับ glossary.toml")
        if entry.term not in source_text:
            problems.append(f"glossary {entry.term} ไม่อยู่ในต้นฉบับ")
    return problems
