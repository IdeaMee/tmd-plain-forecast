"""Phase 2.2: รวมป้ายที่ผู้ช่วยเสนอเข้ากับตารางหน่วย แล้วสุ่ม 20% ที่ซ่อนป้ายให้ผู้ใช้ติดซ้ำ.

รัน: .venv/Scripts/python.exe -X utf8 scripts/make_blind_sample.py
อ่าน data/labeled/units.csv + data/labeled/agent_labels.tsv
เขียน data/labeled/units_labeled.csv (suggested_label, scope, note) และ data/labeled/blind_sample.csv
(ไม่มีคอลัมน์ป้ายหรือ scope; ผู้ใช้กรอก human_label, human_scope, human_note)
"""

from __future__ import annotations

import csv
import io
import math
import sys
from collections import Counter
from pathlib import Path

from tmd_plain.classify.labeling import parse_agent_labels, stratified_sample
from tmd_plain.config import load_config

ROOT = Path(__file__).resolve().parents[1]
LABELED = ROOT / "data" / "labeled"
UNITS = LABELED / "units.csv"
AGENT = LABELED / "agent_labels.tsv"
OUT_LABELED = LABELED / "units_labeled.csv"
OUT_BLIND = LABELED / "blind_sample.csv"
BLIND_COLUMNS = [
    "sample_no",
    "unit_id",
    "doc_type",
    "section",
    "context_prev",
    "text",
    "context_next",
    "human_label",
    "human_scope",
    "human_note",
]
HIDDEN = {"suggested_label", "final_label", "scope", "reviewer", "note"}


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    # BOM ให้ Excel เปิดภาษาไทยถูก
    path.write_text("\ufeff" + buf.getvalue(), encoding="utf-8", newline="")


def main() -> int:
    if (LABELED / "FROZEN.md").exists():
        # ปิดชุดป้ายแล้ว (ADR 0012) ห้ามเขียน units_labeled.csv ทับ
        print("ชุดป้ายปิดแล้ว ดู data/labeled/FROZEN.md", file=sys.stderr)
        return 1
    with UNITS.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns = list(reader.fieldnames or [])
        units = list(reader)
    labels = parse_agent_labels(AGENT.read_text(encoding="utf-8"))
    by_id = {a.unit_id: a for a in labels}
    unit_ids = [u["unit_id"] for u in units]
    if len(by_id) != len(labels) or set(by_id) != set(unit_ids):
        missing = sorted(set(unit_ids) - set(by_id))
        extra = sorted(set(by_id) - set(unit_ids))
        print(f"ป้ายไม่ครบหรือซ้ำ: missing={missing} extra={extra}", file=sys.stderr)
        return 1

    for u in units:
        a = by_id[u["unit_id"]]
        u["suggested_label"], u["scope"], u["note"] = a.label, a.scope, a.note
    write_csv(OUT_LABELED, columns, units)

    cfg = load_config()["labeling"]
    ids_by_label: dict[str, list[str]] = {}
    for a in labels:
        ids_by_label.setdefault(a.label, []).append(a.unit_id)
    picked = stratified_sample(ids_by_label, cfg["blind_fraction"], cfg["blind_seed"])
    unit_by_id = {u["unit_id"]: u for u in units}
    blind = [
        {
            "sample_no": str(n),
            **{c: unit_by_id[uid][c] for c in BLIND_COLUMNS[1:7]},
            "human_label": "",
            "human_scope": "",
            "human_note": "",
        }
        for n, uid in enumerate(picked, start=1)
    ]
    write_csv(OUT_BLIND, BLIND_COLUMNS, blind)

    # ตรวจตามแผน: จำนวน = ปัดขึ้น 20%, ไม่มีคอลัมน์ป้าย, ไม่มีหน่วยซ้ำ
    expected = math.ceil(len(units) * cfg["blind_fraction"] - 1e-9)
    assert len(picked) == expected == len(set(picked)), (len(picked), expected)
    assert not HIDDEN & set(BLIND_COLUMNS)

    label_counts = Counter(a.label for a in labels)
    sample_counts = Counter(by_id[uid].label for uid in picked)
    print(f"units: {len(units)} | labels: {dict(sorted(label_counts.items()))}")
    advice = [a for a in labels if a.label == "advice"]
    print(
        f"advice scope: {len(advice)} rows, general(all) "
        f"{sum(a.scope == 'all' for a in advice)}, with note {sum(bool(a.note) for a in labels)}"
    )
    print(f"blind sample: {len(picked)} rows (ceil {cfg['blind_fraction']:.0%} of {len(units)})")
    print(f"sample by label: {dict(sorted(sample_counts.items()))}")
    print(f"wrote {OUT_LABELED.relative_to(ROOT)} and {OUT_BLIND.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
