"""Phase 11.3: ตารางหน่วยไม่ซ้ำของประกาศเตือนภัย + ชุดตามเหตุการณ์ + รวมป้ายของผู้ช่วย.

รัน: .venv/Scripts/python.exe -X utf8 scripts/build_warning_dataset.py
ผล: data/labeled/warning/units.csv (ผลซ้ำได้) และถ้ามี agent_labels.tsv (แก้ด้วยมือ: unit_id<TAB>ป้าย)
-> units_labeled.csv (ทุกหน่วยต้องมีป้ายจากชุด weather/cause/advice)
หลังปิดป้าย (data/labeled/warning/FROZEN.md) สคริปต์ไม่เขียนทับไฟล์ที่ปิดแล้ว ตรวจด้วย scripts/freeze_labels.py
"""

from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

from tmd_plain.config import load_config
from tmd_plain.doctypes.warning.build import warning_units
from tmd_plain.doctypes.warning.dataset import WARNING_LABELS, UnitRow, build_rows, event_splits
from tmd_plain.doctypes.warning.parse import parse_warning
from tmd_plain.doctypes.warning.series import NoticeKey, link_series
from tmd_plain.prep.extract import document_from_txt

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "warning"
OUT = ROOT / "data" / "labeled" / "warning"
LABELS = WARNING_LABELS
COLUMNS = ["unit_id", "split", "events", "issues", "text", "context_prev", "context_next"]


def build() -> list[UnitRow]:
    cfg = load_config()["warning_split"]
    notices = []
    for path in sorted(RAW.glob("warning_*.txt")):
        parsed = parse_warning(document_from_txt(path.read_text(encoding="utf-8")).text)
        # ป้ายยังไม่ใช้ตรงนี้ (ติดป้ายด้วยมือใน agent_labels.tsv)
        notices.append((parsed, warning_units(parsed, lambda _t: "")))
    keys = [
        NoticeKey(p.issue_id, p.series_no, p.title, p.issued_at, p.next_issue_at, p.final)
        for p, _ in notices
    ]
    series = link_series(keys)
    event_of = {n.issue_id: s.series_id for s in series for n in s.notices}
    return build_rows(
        notices, event_of, event_splits(series, cfg["dev_events"], cfg["test_events"])
    )


def render(rows: list[UnitRow], labels: dict[str, str] | None = None) -> str:
    buf = io.StringIO()
    cols = COLUMNS + (["final_label", "reviewer"] if labels is not None else [])
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(cols)
    for r in rows:
        row = [
            r.unit_id,
            r.split,
            ";".join(r.events),
            ";".join(r.issues),
            r.text,
            r.context_prev,
            r.context_next,
        ]
        if labels is not None:
            row += [labels[r.unit_id], "agent-only"]
        writer.writerow(row)
    return buf.getvalue()


def read_labels(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        unit_id, label = line.split("\t")[:2]
        out[unit_id.strip()] = label.strip()
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = build()
    frozen = (OUT / "FROZEN.md").exists()
    units_text = render(rows)
    units_path = OUT / "units.csv"
    if frozen and units_path.read_text(encoding="utf-8") != units_text:
        print("units.csv ไม่ตรงกับที่ปิดไว้ (ห้ามเขียนทับหลังปิดป้าย)")
        return 1
    units_path.write_text(units_text, encoding="utf-8", newline="\n")
    counts = {s: sum(r.split == s for r in rows) for s in ("train", "dev", "test")}
    print(f"units {len(rows)} · " + " · ".join(f"{k} {v}" for k, v in counts.items()))
    labels_path = OUT / "agent_labels.tsv"
    if not labels_path.exists():
        print("ยังไม่มี agent_labels.tsv")
        return 0
    labels = read_labels(labels_path)
    ids = {r.unit_id for r in rows}
    missing = sorted(ids - set(labels))
    extra = sorted(set(labels) - ids)
    bad = sorted(u for u, lab in labels.items() if lab not in LABELS)
    if missing or extra or bad:
        print(
            f"ป้ายไม่ครบ/เกิน/ผิดชุด: missing {len(missing)} extra {len(extra)} bad {len(bad)} {missing[:3]} {bad[:3]}"
        )
        return 1
    labeled_text = render(rows, labels)
    labeled_path = OUT / "units_labeled.csv"
    if frozen and labeled_path.read_text(encoding="utf-8") != labeled_text:
        print("units_labeled.csv ไม่ตรงกับที่ปิดไว้ (ห้ามแก้ป้ายหลังปิด)")
        return 1
    labeled_path.write_text(labeled_text, encoding="utf-8", newline="\n")
    table = {
        s: {
            lab: sum(1 for r in rows if r.split == s and labels[r.unit_id] == lab) for lab in LABELS
        }
        for s in counts
    }
    print(
        "labels "
        + " · ".join(
            f"{s}: " + ", ".join(f"{k} {v}" for k, v in t.items()) for s, t in table.items()
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
