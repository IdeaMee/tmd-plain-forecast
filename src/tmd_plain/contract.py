"""สัญญาข้อมูล v1 (docs/spec/data-contract.md): ต้นฉบับของรูปข้อมูลที่ทุกขั้นและฝั่งเว็บใช้ร่วม.

เปลี่ยนไฟล์นี้ต้องเขียน ADR ก่อน แล้วรัน scripts/export_schema.py ให้ JSON Schema ฝั่งเว็บตรงกัน
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

CONTRACT_VERSION = "1"

RegionKey = Literal[
    "north",
    "northeast",
    "central",
    "east",
    "south_east_coast",
    "south_west_coast",
    "bangkok_vicinity",
]
REGION_KEYS: tuple[RegionKey, ...] = (
    "north",
    "northeast",
    "central",
    "east",
    "south_east_coast",
    "south_west_coast",
    "bangkok_vicinity",
)
REGION_LABELS_TH: dict[RegionKey, str] = {
    "north": "ภาคเหนือ",
    "northeast": "ภาคตะวันออกเฉียงเหนือ",
    "central": "ภาคกลาง",
    "east": "ภาคตะวันออก",
    "south_east_coast": "ภาคใต้ฝั่งตะวันออก (อ่าวไทย)",
    "south_west_coast": "ภาคใต้ฝั่งตะวันตก (อันดามัน)",
    "bangkok_vicinity": "กรุงเทพมหานครและปริมณฑล",
}

UnitLabel = Literal["weather", "advice", "cause", "other"]
LABELS: tuple[UnitLabel, ...] = ("weather", "advice", "cause", "other")

DocType = Literal["daily", "sevenday"]
DOC_TYPES: tuple[DocType, ...] = ("daily", "sevenday")

LineKind = Literal["rain", "temperature", "wind", "wave", "fog", "other"]

ErrorCode = Literal["unsupported_document", "too_large", "extract_failed", "empty_file"]
ERROR_MESSAGES_TH: dict[ErrorCode, str] = {
    "unsupported_document": "ไฟล์นี้ไม่ใช่พยากรณ์อากาศรายวันหรือพยากรณ์ 7 วันของกรมอุตุนิยมวิทยา กรุณาเลือกไฟล์ PDF พยากรณ์จากเว็บไซต์กรมอุตุนิยมวิทยา",
    "too_large": "ไฟล์ใหญ่เกิน 4 MB กรุณาเลือกไฟล์พยากรณ์ฉบับเดียว",
    "extract_failed": "อ่านข้อความในไฟล์ไม่สำเร็จ ไฟล์อาจเสียหรือเป็นภาพสแกน กรุณาลองไฟล์อื่น",
    "empty_file": "ไฟล์ว่างเปล่า กรุณาเลือกไฟล์ใหม่",
}

# ค่าที่ดึงได้ (ใช้ตรวจ F1-F5) เก็บเป็นชนิดพื้นฐานเท่านั้นเพื่อให้ JSON ฝั่งเว็บตรวจง่าย
FactValue = str | int | float | bool | list[str]

_DAILY_ID = re.compile(r"\d{12}")  # รหัสรอบ DDMMYYYYHHMM (ปี ค.ศ.)
_SEVENDAY_ID = re.compile(r"\d{6}")  # YYMMDD ตามชื่อไฟล์ t_YYMMDD.pdf


class _Model(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SummaryLine(_Model):
    kind: LineKind
    text: str = Field(min_length=1)
    facts: dict[str, FactValue] = Field(default_factory=dict)


class Period(_Model):
    start: date
    end: date
    lines: list[SummaryLine] = Field(min_length=1)

    @model_validator(mode="after")
    def _start_not_after_end(self) -> Period:
        if self.start > self.end:
            raise ValueError("start ต้องไม่หลัง end")
        return self


class AdviceItem(_Model):
    text: str = Field(min_length=1)  # คัดจากต้นฉบับตรงๆ ห้ามเขียนเอง
    scope: list[RegionKey] = Field(min_length=1)
    general: bool
    source_unit_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def _general_means_all_regions(self) -> AdviceItem:
        if self.general and set(self.scope) != set(REGION_KEYS):
            raise ValueError("ข้อแนะนำทั่วไปต้องมี scope ครบ 7 ภาค")
        if len(set(self.scope)) != len(self.scope):
            raise ValueError("scope มีภาคซ้ำ")
        return self


class RegionSummary(_Model):
    lines: list[SummaryLine] = Field(default_factory=list)
    periods: list[Period] = Field(default_factory=list)
    advice: list[AdviceItem] = Field(default_factory=list)


class Issue(_Model):
    issue_id: str
    doc_type: DocType
    issued_at: datetime
    source_label: str = Field(min_length=1)
    regions: dict[RegionKey, RegionSummary]
    general_advice: list[AdviceItem] = Field(default_factory=list)
    pipeline_version: str = Field(min_length=1)

    @model_validator(mode="after")
    def _check_shape(self) -> Issue:
        if set(self.regions) != set(REGION_KEYS):
            raise ValueError("regions ต้องมีครบ 7 ภาคพอดี")
        if self.issued_at.tzinfo is None:
            raise ValueError("issued_at ต้องมีเขตเวลา (+07:00)")
        pattern = _DAILY_ID if self.doc_type == "daily" else _SEVENDAY_ID
        if not pattern.fullmatch(self.issue_id):
            raise ValueError(f"issue_id ไม่ตรงรูปแบบของ {self.doc_type}")
        for key, region in self.regions.items():
            if self.doc_type == "daily" and region.periods:
                raise ValueError(f"พยากรณ์รายวันต้องไม่มี periods ({key})")
            if self.doc_type == "sevenday" and not region.periods:
                raise ValueError(f"พยากรณ์ 7 วันต้องมี periods ({key})")
            if self.doc_type == "daily" and not region.lines:
                raise ValueError(f"พยากรณ์รายวันต้องมี lines ({key})")
            for item in region.advice:
                if key not in item.scope:
                    raise ValueError(f"คำแนะนำในภาค {key} ต้องมี {key} ใน scope")
        if any(not item.general for item in self.general_advice):
            raise ValueError("general_advice รับเฉพาะรายการที่ general=true")
        return self


class ErrorDetail(_Model):
    code: ErrorCode
    message_th: str = Field(min_length=1)


class SummarizeOk(_Model):
    ok: Literal[True]
    issue: Issue


class SummarizeError(_Model):
    ok: Literal[False]
    error: ErrorDetail


def error_response(code: ErrorCode) -> SummarizeError:
    """สร้างคำตอบข้อผิดพลาดพร้อมข้อความภาษาไทยมาตรฐาน."""
    return SummarizeError(
        ok=False, error=ErrorDetail(code=code, message_th=ERROR_MESSAGES_TH[code])
    )
