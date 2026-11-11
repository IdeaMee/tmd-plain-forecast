"""วัดเวลาที่ภาพขั้นตอน (trace) เพิ่ม บน PDF ชุดแสดงผล (Phase 10.2 เกณฑ์ < 20%).

รัน: .venv/Scripts/python.exe -X utf8 scripts/measure_trace.py
สร้างตัวจัดประเภทใหม่ทุกไฟล์ (แคชป้ายไม่ข้ามไฟล์ เหมือนคำขอแรกของแต่ละไฟล์) สลับปิด/เปิดหลายรอบแล้วใช้มัธยฐาน
"""

from __future__ import annotations

import statistics
import sys
import time
from pathlib import Path

from tmd_plain.classify.model_io import load_classifier
from tmd_plain.raw_io import load_manifest
from tmd_plain.service import summarize_pdf

ROOT = Path(__file__).resolve().parents[1]
ROUNDS = 5


def _run(datas: list[bytes], trace: bool) -> float:
    total = 0.0
    for data in datas:
        classifier = load_classifier(ROOT / "models")
        start = time.perf_counter()
        summarize_pdf(data, classifier, trace=trace)
        total += time.perf_counter() - start
    return total


def main() -> int:
    issues = load_manifest(ROOT / "data" / "raw")
    datas = [i.pdf.read_bytes() for i in issues if i.role == "display_test" and i.pdf]
    _run(datas, False)
    _run(datas, True)
    off: list[float] = []
    on: list[float] = []
    for _ in range(ROUNDS):
        off.append(_run(datas, False))
        on.append(_run(datas, True))
    a, b = statistics.median(off), statistics.median(on)
    overhead = 100 * (b - a) / a
    print(
        f"pdfs {len(datas)} · off {a * 1000 / len(datas):.1f} ms/pdf · "
        f"on {b * 1000 / len(datas):.1f} ms/pdf · overhead {overhead:.1f}%"
    )
    return 0 if overhead < 20 else 1


if __name__ == "__main__":
    sys.exit(main())
