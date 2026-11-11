"""สร้าง/อัปเดต golden file ของโหมดทั่วไป (Phase 10.3): เอกสาร 3 ฉบับ + trace 1 ฉบับ จาก PDF จริง.

รัน: .venv/Scripts/python.exe -X utf8 scripts/make_golden_generic.py
อัปเดตเมื่อจงใจเปลี่ยนกฎของโหมดทั่วไปเท่านั้น และต้องอ่าน diff ก่อนเก็บ
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tmd_plain.classify.model_io import load_classifier
from tmd_plain.contract import SummarizeGenericOk
from tmd_plain.service import summarize_pdf

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "tests" / "golden" / "generic"
# ต่างกันพอให้ครอบกฎ: ความเรียงยาว (ENSO), หัวภาค (สรุปรายสัปดาห์), คำแนะนำมาก (เกษตรราย 15 วัน)
# 11.4: ประกาศเตือนภัยได้ผลชนิดของตัวเองแล้ว จึงเปลี่ยนตัวอย่างคำแนะนำเป็นเกษตรราย 15 วัน (ยังเป็นโหมดทั่วไป)
# 11.5 จะต้องเปลี่ยนตัวอย่างสรุปรายสัปดาห์แบบเดียวกันเมื่อชนิดนั้นมีผลของตัวเอง
SOURCES = {
    "generic_enso_2569_09": RAW / "generic" / "generic_enso_2569_09.pdf",
    "weekly_161120261100": RAW / "weekly" / "weekly_161120261100.pdf",
    "generic_agro_fortnight_16112026": RAW / "generic" / "generic_agro_fortnight_16112026.pdf",
}
TRACE_OF = "generic_enso_2569_09"


def _dump(body: object) -> str:
    return json.dumps(body, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def build() -> dict[str, str]:
    """ชื่อไฟล์ golden -> เนื้อไฟล์ (ใช้ทั้งตอนเขียนและในเทสต์)."""
    classifier = load_classifier(ROOT / "models")
    out: dict[str, str] = {}
    for name, path in SOURCES.items():
        result = summarize_pdf(path.read_bytes(), classifier, trace=name == TRACE_OF)
        if not isinstance(result, SummarizeGenericOk):
            raise SystemExit(f"{name}: ไม่ได้ผลโหมดทั่วไป: {result}")
        out[f"{name}.json"] = _dump(result.document.model_dump(mode="json"))
        if result.trace is not None:
            out[f"{name}.trace.json"] = _dump(result.trace.model_dump(mode="json"))
    return out


def sources_exist() -> bool:
    return all(p.exists() for p in SOURCES.values())


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, body in build().items():
        (OUT / name).write_text(body, encoding="utf-8", newline="\n")
        print(f"wrote {(OUT / name).relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
