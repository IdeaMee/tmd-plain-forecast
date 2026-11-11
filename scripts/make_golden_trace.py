"""สร้าง/อัปเดต golden file ของภาพขั้นตอน (Phase 10.2) จาก PDF รายวันจริง 1 ฉบับ.

รัน: .venv/Scripts/python.exe -X utf8 scripts/make_golden_trace.py
อัปเดตเมื่อจงใจเปลี่ยนขั้นของ trace เท่านั้น และต้องอ่าน diff ก่อนเก็บ
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tmd_plain.classify.model_io import load_classifier
from tmd_plain.contract import SummarizeError
from tmd_plain.service import summarize_pdf

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "daily" / "daily_161120261800.pdf"
OUT = ROOT / "tests" / "golden" / "trace" / "daily_161120261800_pdf.json"


def build() -> str:
    result = summarize_pdf(SOURCE.read_bytes(), load_classifier(ROOT / "models"), trace=True)
    if isinstance(result, SummarizeError) or result.trace is None:
        raise SystemExit(f"สร้าง trace ไม่ได้: {result}")
    body = result.trace.model_dump(mode="json")
    return json.dumps(body, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
