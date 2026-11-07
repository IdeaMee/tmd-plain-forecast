"""Phase 3.2: เทียบกฎแมปภาคกับ scope ในชุดป้าย และเลือกคำแนะนำของทุกฉบับ -> docs/results/scope-map-check.md.

รัน: .venv/Scripts/python.exe -X utf8 scripts/check_scope.py (ต้องพิมพ์ errors: 0)
- เทียบ: หน่วย advice ทุกหน่วยในชุดป้าย ใช้บริบทย่อหน้าจากฉบับแรกที่หน่วยปรากฏ (ตรงกับตอนติดป้าย)
- ท่อจริง: ทุกฉบับ display_test จัดประเภทด้วยโมเดลที่อนุมัติ แล้วเลือกคำแนะนำ ทุกคำแนะนำต้องไปที่ภาคหรือข้อแนะนำทั่วไป
"""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

from tmd_plain.classify.model_io import load_labeler
from tmd_plain.contract import REGION_KEYS
from tmd_plain.extract.advice import context_units, select_advice
from tmd_plain.extract.scope import Scope, advice_scope
from tmd_plain.prep.regions import parse_issue
from tmd_plain.raw_io import issue_sort_key, load_manifest

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORT = ROOT / "docs" / "results" / "scope-map-check.md"
CODE = {
    "north": "N",
    "northeast": "NE",
    "central": "C",
    "east": "E",
    "south_east_coast": "SE",
    "south_west_coast": "SW",
    "bangkok_vicinity": "BKK",
}
# คำอธิบายของหน่วยที่กฎไม่ตรงกับป้าย (เขียนหลังอ่านผล ไม่ได้ใช้ปรับกฎ)
EXPLAIN = {
    "d-eaa9cda2": '"ช่วงเวลาดังกล่าว" เป็นเวลา กฎจึงเป็นข้อแนะนำทั่วไป (D6) ส่วนป้ายสืบทอดพื้นที่จากหน่วยก่อนหน้า ภาคที่แสดงเท่ากัน (ครบ 7 ภาค) ต่างแค่ป้าย "ข้อแนะนำทั่วไป"',
}


def show(scope: Scope) -> str:
    return "ทั่วไป (7 ภาค)" if scope.general else " ".join(CODE[k] for k in scope.regions)


def main() -> int:
    labels = {
        r["unit_id"]: r
        for r in csv.DictReader(
            (ROOT / "data" / "labeled" / "units_labeled.csv").open(encoding="utf-8-sig")
        )
    }
    issues = sorted(load_manifest(RAW), key=lambda i: (issue_sort_key(i), i.doc_type))
    first: dict[str, Scope] = {}
    variants: dict[str, set[Scope]] = defaultdict(set)
    errors: list[str] = []
    label_of = load_labeler(ROOT / "models")
    stats: Counter[str] = Counter()
    for issue in issues:
        parsed = parse_issue(issue.preferred())
        for unit in context_units(parsed):
            row = labels.get(unit.unit_id)
            if row is None:
                errors.append(f"หน่วยไม่อยู่ในชุดป้าย {unit.unit_id} ({issue.issue_id})")
                continue
            if row["final_label"] == "advice":
                scope = advice_scope(unit.text, unit.previous)
                first.setdefault(unit.unit_id, scope)
                variants[unit.unit_id].add(scope)
        if issue.role != "display_test":
            continue
        sel = select_advice(parsed, label_of)
        placed = {a.source_unit_id for items in sel.regional.values() for a in items}
        placed |= {a.source_unit_id for a in sel.general}
        advice_ids = {u.unit_id for u in context_units(parsed) if label_of(u.text) == "advice"}
        if advice_ids - placed:
            errors.append(f"คำแนะนำหาย {sorted(advice_ids - placed)} ({issue.issue_id})")
        stats["issues"] += 1
        stats["advice placed"] += len(placed)
        stats["general advice"] += len(sel.general)
        for key in REGION_KEYS:
            stats[f"region {key}"] += len(sel.regional[key])
        joined = " ".join((*parsed.overview, *parsed.caution))
        for items in (*sel.regional.values(), sel.general):
            for a in items:
                if a.text not in joined:
                    errors.append(f"ข้อความคำแนะนำไม่อยู่ในต้นฉบับ {a.source_unit_id}")

    rows = []
    match = 0
    for uid, scope in first.items():
        r = labels[uid]
        expected = Scope(REGION_KEYS, True) if r["scope"] == "all" else None
        lab_regions = set(REGION_KEYS) if r["scope"] == "all" else set(r["scope"].split(";"))
        same = set(scope.regions) == lab_regions and scope.general == (r["scope"] == "all")
        match += same
        if not same:
            lab = (
                show(expected)
                if expected
                else " ".join(CODE[k] for k in REGION_KEYS if k in lab_regions)
            )
            rows.append(f"| {uid} | {show(scope)} | {lab} | {EXPLAIN.get(uid, '')} |")
    region_match = sum(
        set(s.regions)
        == (set(REGION_KEYS) if labels[u]["scope"] == "all" else set(labels[u]["scope"].split(";")))
        for u, s in first.items()
    )
    multi = sorted(u for u, v in variants.items() if len(v) > 1)
    lines = [
        "# ตรวจตารางแมปภาค (Phase 3.2)",
        "",
        "คำสั่ง: `.venv/Scripts/python.exe -X utf8 scripts/check_scope.py` · ไฟล์นี้สร้างโดยสคริปต์",
        "",
        "**ชุดอ้างอิง:** `scope` ในชุดป้ายซึ่งผู้ช่วยติดเอง ไม่ได้ผ่านคนตรวจ (ADR 0012) การตรงกันจึงบอกว่ากฎทำซ้ำการตัดสินของผู้ติดป้ายได้ ไม่ได้พิสูจน์ว่าถูกตามภูมิศาสตร์",
        "",
        "## กฎแมป เทียบ scope ของชุดป้าย",
        f'- หน่วย advice ในชุดป้าย: {len(first)} · ตรงทั้งภาคและป้าย "ทั่วไป": **{match}/{len(first)}** · ตรงเฉพาะภาค: {region_match}/{len(first)}',
        "",
        "| unit_id | กฎ | ชุดป้าย | คำอธิบาย |",
        "|---|---|---|---|",
        *rows,
        "",
        f'หน่วยที่ได้ขอบเขตต่างกันในแต่ละฉบับ (บริบทย่อหน้าต่างกัน สำหรับ "บริเวณดังกล่าว"): {len(multi)} หน่วย {", ".join(multi)}',
        "",
        "## ท่อจริงบนฉบับที่แสดงบนเว็บ (จัดประเภทด้วยโมเดลที่อนุมัติ)",
        f"- ฉบับ: {stats['issues']} · คำแนะนำที่วาง: {stats['advice placed']} · ข้อแนะนำทั่วไป: {stats['general advice']}",
        "- จำนวนคำแนะนำต่อภาค (รวมทุกฉบับ): "
        + ", ".join(f"{CODE[k]} {stats[f'region {k}']}" for k in REGION_KEYS),
        f"- ข้อผิดพลาด (หน่วยไม่อยู่ในชุดป้าย, คำแนะนำหาย, ข้อความไม่อยู่ในต้นฉบับ): {len(errors)}",
        *[f"  - {e}" for e in errors],
        "",
        "## กติกาที่ใช้ (ตาม region-scope-map.md v1)",
        '- ตัดหน่วยเป็นท่อนที่ "ส่วน / สำหรับ / ขอให้ / ชาวเรือ / เรือเล็ก" · ท่อนคำแนะนำที่ไม่มีคำบอกที่ตั้ง = ทั้งหน่วยเป็นข้อแนะนำทั่วไป (D6) · ท่อนอื่นรวมภาค (union)',
        '- "บริเวณดังกล่าว / พื้นที่ดังกล่าว" รับที่ตั้งของทุกหน่วยก่อนหน้าในย่อหน้าเดียวกัน (D5 อ่านคู่กับ D7 แสดงกว้างไว้ก่อน) · "ช่วงเวลาดังกล่าว" ไม่สืบทอด',
        "- ชาวเรือ/เรือเล็กในท่อนที่ไม่บอกชื่อทะเล = E SE SW",
        '- หน่วย `weather` ในย่อหน้าภาพรวม (เช่น "อนึ่ง ในช่วงวันที่ …") ไม่แสดงในภาคในเวอร์ชันแรก (ผู้ใช้ยืนยัน 2026-11-17)',
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"label match {match}/{len(first)} (regions {region_match}) multi-variant {len(multi)}")
    print(
        f"display issues {stats['issues']} advice placed {stats['advice placed']} general {stats['general advice']}"
    )
    for e in errors[:20]:
        print(e)
    print(f"errors: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
