"""คำอธิบายระดับฝน/ความหนาวตามเกณฑ์ในหมายเหตุท้ายฉบับของ TMD (resources/glossary.toml)."""

from __future__ import annotations

import tomllib
from functools import cache
from importlib.resources import files

from tmd_plain.contract import DocType


@cache
def _raw() -> dict:
    text = files("tmd_plain").joinpath("resources/glossary.toml").read_text(encoding="utf-8")
    return tomllib.loads(text)


def glossary(doc_type: DocType) -> dict[str, str]:
    """คำ -> คำอธิบาย; เกณฑ์ฝนของรายวันกับ 7 วันต่างกันตามหมายเหตุของแต่ละชนิด."""
    data = _raw()
    return {**data["rain"][doc_type], **data["cold"]}


def cold_glossary() -> dict[str, str]:
    """เกณฑ์ความหนาว (ชุดเดียวของ TMD) ใช้กับเอกสารชนิดอื่นในโหมดทั่วไป.

    เกณฑ์ฝนไม่ให้ เพราะรายวันกับ 7 วันใช้เกณฑ์ต่างกัน เอกสารชนิดอื่นจึงเลือกชุดที่ถูกไม่ได้ (ไม่เดา)
    """
    return dict(_raw()["cold"])


def rain_terms(phrase: str) -> list[str]:
    """คำในอภิธานที่ตรงกับวลีฝนจากต้นฉบับ เช่น "ฝนตกหนักถึงหนักมาก" -> ฝนหนัก, ฝนหนักมาก."""
    if "หนักถึงหนักมาก" in phrase:
        return ["ฝนหนัก", "ฝนหนักมาก"]
    if "หนักมาก" in phrase:
        return ["ฝนหนักมาก"]
    if "หนัก" in phrase:
        return ["ฝนหนัก"]
    if "เล็กน้อย" in phrase:
        return ["ฝนเล็กน้อย"]
    return []


def cold_terms(phrase: str) -> list[str]:
    """คำในอภิธานที่ตรงกับวลีความเย็น เช่น "อากาศเย็นถึงหนาว" -> อากาศเย็น, อากาศหนาว."""
    if "หนาวจัด" in phrase:
        return ["อากาศหนาวจัด"]
    if "เย็นถึงหนาว" in phrase:
        return ["อากาศเย็น", "อากาศหนาว"]
    if "หนาวเย็น" in phrase:
        # "หนาวเย็น" ไม่ใช่ระดับในหมายเหตุ ไม่อธิบายด้วยตัวเลข
        return []
    if "หนาว" in phrase:
        return ["อากาศหนาว"]
    if "เย็น" in phrase:
        return ["อากาศเย็น"]
    return []
