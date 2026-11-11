"""ประกอบภาพขั้นตอน (Trace ตามสัญญา v2) จากข้อมูลย่อของแต่ละขั้น พร้อมตัดให้อยู่ในเพดาน (V4 ข).

trace สร้างหลังท่อประมวลผลทำงานเสร็จ จากผลระหว่างทางเท่านั้น จึงไม่มีทางเปลี่ยนผลสรุป
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from tmd_plain.contract import (
    TRACE_MAX_BYTES,
    TRACE_MAX_ITEMS,
    Trace,
    TraceStatus,
    TraceStep,
    TraceStepId,
)

STEP_TITLES_TH: dict[TraceStepId, str] = {
    "read_pdf": "อ่าน PDF",
    "clean": "ทำความสะอาดข้อความ",
    "detect_type": "ตรวจชนิดเอกสาร",
    "segment": "แบ่งส่วน",
    "units": "แบ่งหน่วยประโยค",
    "tokenize": "ตัดคำ (newmm)",
    "filter_tokens": "คัดคำ",
    "classify": "จัดประเภทประโยค",
    "scope": "แยกตามภาค",
    "extract": "ดึงข้อเท็จจริง (regex)",
    "template": "เขียนตามแม่แบบ",
    "verify": "ตรวจ F1-F5",
    "result": "ผลลัพธ์",
}

# ชื่อโมเดลในข้อความภาพขั้นตอน (หน้าเว็บเป็นภาษาไทย ไม่แสดงชื่อไฟล์โมเดล)
MODEL_NAMES_TH = {"naive_bayes": "Naive Bayes", "knn": "k-NN"}


def model_name_th(name: str) -> str:
    return MODEL_NAMES_TH.get(name, name)


# เผื่อไว้ 10% เพราะฝั่งเว็บนับขนาดด้วย JSON.stringify ซึ่งเขียนตัวเลขต่างจาก Python เล็กน้อย (1.0 / 1)
SIZE_BUDGET = int(TRACE_MAX_BYTES * 0.9)
SIZE_NOTE_TH = " (ตัดข้อมูลของขั้นนี้ออกเพราะภาพขั้นตอนใหญ่เกินเพดาน)"


@dataclass(frozen=True)
class StepDraft:
    id: TraceStepId
    note_th: str = ""
    status: TraceStatus = "done"
    data: dict[str, Any] = field(default_factory=dict)
    # ชื่อขั้นเฉพาะชนิด (เช่น โหมดทั่วไปไม่ได้ตรวจ F1-F5) ว่าง = ใช้ STEP_TITLES_TH
    title_th: str | None = None


def _cap(value: Any) -> tuple[Any, bool]:
    # รายการและแผนที่ยาวเกินเพดานถูกตัดที่ชิ้นแรกๆ ตามลำดับเดิม
    if isinstance(value, (list, tuple)):
        items = list(value)
        return items[:TRACE_MAX_ITEMS], len(items) > TRACE_MAX_ITEMS
    if isinstance(value, dict):
        keys = list(value)[:TRACE_MAX_ITEMS]
        return {k: value[k] for k in keys}, len(value) > TRACE_MAX_ITEMS
    return value, False


def _size(value: Any) -> int:
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return len(text.encode("utf-8"))


def build_trace(drafts: list[StepDraft]) -> Trace:
    """ร่างของแต่ละขั้น -> Trace ที่ผ่านสัญญาเสมอ (ตัดรายการ แล้วตัดข้อมูลของขั้นที่ใหญ่สุดจนพอดีเพดาน)."""
    truncated = False
    steps: list[dict[str, Any]] = []
    for d in drafts:
        data: dict[str, Any] = {}
        for key, value in d.data.items():
            data[key], cut = _cap(value)
            truncated = truncated or cut
        steps.append(
            {
                "id": d.id,
                "title_th": d.title_th or STEP_TITLES_TH[d.id],
                "status": d.status,
                "note_th": d.note_th,
                "data": data,
            }
        )
    # วัดจาก dict ธรรมดา (ถูกกว่าสร้างโมเดลซ้ำ) แล้วสร้างโมเดลครั้งเดียวตอนท้าย
    while _size({"steps": steps, "truncated": True}) > SIZE_BUDGET:
        candidates = [i for i, s in enumerate(steps) if s["data"]]
        if not candidates:
            break
        biggest = max(candidates, key=lambda i: _size(steps[i]))
        steps[biggest] = {
            **steps[biggest],
            "data": {},
            "note_th": steps[biggest]["note_th"] + SIZE_NOTE_TH,
        }
        truncated = True
    return Trace(steps=[TraceStep.model_validate(s) for s in steps], truncated=truncated)
