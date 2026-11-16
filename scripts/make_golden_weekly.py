"""สร้าง/อัปเดต golden file ของสรุปรายสัปดาห์ (Phase 11.5): 3 ฉบับจากข้อความหน้าเว็บจริง.

รัน: .venv/Scripts/python.exe -X utf8 scripts/make_golden_weekly.py
อัปเดตเมื่อจงใจเปลี่ยนกฎของสรุปรายสัปดาห์เท่านั้น และต้องอ่าน diff ก่อนเก็บ
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tmd_plain.contract import SummarizeError
from tmd_plain.doctypes.weekly.runner import summarize_weekly

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "weekly"
OUT = ROOT / "tests" / "golden" / "weekly"
# ต่างกันพอให้ครอบกฎ: หน้าร้อนช่องครบ + ค่าที่สองในวงเล็บ (010520262200), ช่องที่ขึ้นต้นชื่อภาค (160320261000),
# ภาพรวม 2 ย่อหน้า + ช่องว่างหลายช่อง (040920261100)
SOURCES = ("010520262200", "160320261000", "040920261100")


def build() -> dict[str, str]:
    """ชื่อไฟล์ golden -> เนื้อไฟล์ (ใช้ทั้งตอนเขียนและในเทสต์)."""
    out: dict[str, str] = {}
    for issue_id in SOURCES:
        summary = summarize_weekly(
            (RAW / f"weekly_{issue_id}.txt").read_text(encoding="utf-8"), issue_id
        )
        if isinstance(summary, SummarizeError):
            raise SystemExit(f"{issue_id}: {summary.error.code}")
        body = json.dumps(
            summary.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, indent=2
        )
        out[f"{issue_id}.json"] = body + "\n"
    return out


def sources_exist() -> bool:
    return all((RAW / f"weekly_{i}.txt").exists() for i in SOURCES)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, body in build().items():
        (OUT / name).write_text(body, encoding="utf-8", newline="\n")
        print(f"wrote {(OUT / name).relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
