"""สร้าง/อัปเดต golden file ของพยากรณ์เดินเรือ (Phase 11.1): 3 ฉบับ + trace 1 ฉบับ จากข้อความหน้าเว็บจริง.

รัน: .venv/Scripts/python.exe -X utf8 scripts/make_golden_shipping.py
อัปเดตเมื่อจงใจเปลี่ยนกฎของพยากรณ์เดินเรือเท่านั้น และต้องอ่าน diff ก่อนเก็บ
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tmd_plain.classify.model_io import load_classifier
from tmd_plain.contract import SummarizeError
from tmd_plain.doctypes.shipping.runner import run_shipping, trace_shipping
from tmd_plain.prep.extract import document_from_txt
from tmd_plain.tracing import build_trace

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "shipping"
OUT = ROOT / "tests" / "golden" / "shipping"
# ต่างกันพอให้ครอบกฎ: "อ่าวไทยตอนบน:" + ลมแปรปรวน, คำแนะนำเรือเล็ก (สองท่อน), ฝนหนัก "ตอนล่าง"
SOURCES = ("161120261300", "101120261900", "251020260000")
TRACE_OF = "101120261900"


def _dump(body: object) -> str:
    return json.dumps(body, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def build() -> dict[str, str]:
    """ชื่อไฟล์ golden -> เนื้อไฟล์ (ใช้ทั้งตอนเขียนและในเทสต์)."""
    classifier = load_classifier(ROOT / "models")
    out: dict[str, str] = {}
    for issue_id in SOURCES:
        doc = document_from_txt((RAW / f"shipping_{issue_id}.txt").read_text(encoding="utf-8"))
        run = run_shipping(doc, classifier)
        if isinstance(run, SummarizeError):
            raise SystemExit(f"{issue_id}: {run.error.code}")
        out[f"{issue_id}.json"] = _dump(run.document.model_dump(mode="json"))
        if issue_id == TRACE_OF:
            trace = build_trace(trace_shipping(run, classifier))
            out[f"{issue_id}.trace.json"] = _dump(trace.model_dump(mode="json"))
    return out


def sources_exist() -> bool:
    return all((RAW / f"shipping_{i}.txt").exists() for i in SOURCES)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, body in build().items():
        (OUT / name).write_text(body, encoding="utf-8", newline="\n")
        print(f"wrote {(OUT / name).relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
