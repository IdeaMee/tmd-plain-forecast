"""ปิดชุดป้าย (ADR 0012): final_label = ป้ายที่ผู้ช่วยเสนอ, reviewer = agent-only แล้วบันทึก sha256.

รัน: .venv/Scripts/python.exe -X utf8 scripts/freeze_labels.py
ถ้ามี data/labeled/FROZEN.md แล้ว สคริปต์จะตรวจ sha256 เทียบเท่านั้น ไม่เขียนทับ (ป้ายที่ปิดแล้วห้ามแก้)
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELED = ROOT / "data" / "labeled"
UNITS_LABELED = LABELED / "units_labeled.csv"
SPLIT = LABELED / "split.csv"
FROZEN = LABELED / "FROZEN.md"
# ชุดป้ายประกาศเตือนภัย (Phase 11.3) ปิดด้วย scripts/build_warning_dataset.py แยกต่างหาก ตรวจที่นี่ด้วย
WARNING_FROZEN = LABELED / "warning" / "FROZEN.md"
REVIEWER = "agent-only"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_frozen(frozen: Path = FROZEN) -> int:
    text = frozen.read_text(encoding="utf-8")
    bad = 0
    for name, digest in re.findall(r"`([\w./]+)`: `([0-9a-f]{64})`", text):
        actual = sha256(ROOT / name)
        ok = actual == digest
        bad += not ok
        print(f"{'ok ' if ok else 'BAD'} {name} {actual[:8]}")
    return 1 if bad else 0


def main() -> int:
    if FROZEN.exists():
        bad = check_frozen()
        if WARNING_FROZEN.exists():
            bad |= check_frozen(WARNING_FROZEN)
        return bad
    with UNITS_LABELED.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns = list(reader.fieldnames or [])
        rows = list(reader)
    for r in rows:
        r["final_label"] = r["suggested_label"]
        r["reviewer"] = REVIEWER
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    UNITS_LABELED.write_text("\ufeff" + buf.getvalue(), encoding="utf-8", newline="")
    lines = [
        "# ชุดป้ายที่ปิดแล้ว",
        "",
        f"ปิดเมื่อ: {date.today().isoformat()} · ที่มาของป้าย: ผู้ช่วย (Claude) ติดทุกหน่วย ไม่ได้ผ่านคนตรวจ (ADR 0012)",
        "หลังปิดห้ามแก้ป้าย ตรวจด้วย `scripts/freeze_labels.py` (จะเทียบ sha256 ข้างล่าง)",
        "",
        f"- `data/labeled/units_labeled.csv`: `{sha256(UNITS_LABELED)}`",
        f"- `data/labeled/split.csv`: `{sha256(SPLIT)}`",
        "",
    ]
    FROZEN.write_text("\n".join(lines), encoding="utf-8", newline="")
    print(f"froze {len(rows)} labels -> {FROZEN.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
