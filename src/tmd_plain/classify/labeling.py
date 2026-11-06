"""ป้ายที่ผู้ช่วยเสนอ (Phase 2.2): อ่านไฟล์ป้าย แปลง scope และสุ่มตัวอย่างแบบแบ่งชั้นให้คนติดซ้ำ."""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass

from tmd_plain.contract import LABELS, REGION_KEYS

# รหัสย่อในไฟล์ป้าย -> คีย์ภาคในสัญญาข้อมูล
SCOPE_CODES: dict[str, str] = {
    "N": "north",
    "NE": "northeast",
    "C": "central",
    "E": "east",
    "SE": "south_east_coast",
    "SW": "south_west_coast",
    "BKK": "bangkok_vicinity",
}
# ไม่มีคำบอกที่ตั้งเลย = ข้อแนะนำทั่วไป แสดงทั้ง 7 ภาค (D6)
GENERAL_CODE = "ALL"
GENERAL_SCOPE = "all"


@dataclass(frozen=True)
class AgentLabel:
    unit_id: str
    label: str
    scope: str
    note: str


def parse_scope(codes: str) -> str:
    """แปลงรหัสย่อเป็นคีย์ภาคคั่นด้วย ; เรียงตาม REGION_KEYS ("all" = ข้อแนะนำทั่วไป)."""
    parts = codes.split()
    if parts == [GENERAL_CODE]:
        return GENERAL_SCOPE
    unknown = [p for p in parts if p not in SCOPE_CODES]
    if not parts or unknown:
        raise ValueError(f"scope ไม่ถูกต้อง: {codes!r}")
    keys = {SCOPE_CODES[p] for p in parts}
    return ";".join(k for k in REGION_KEYS if k in keys)


def parse_agent_labels(text: str) -> list[AgentLabel]:
    """อ่านไฟล์ TSV: unit_id, label, scope (เฉพาะ advice), note; ข้ามบรรทัด # และบรรทัดว่าง."""
    out: list[AgentLabel] = []
    for n, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.startswith("#"):
            continue
        cells = (line.split("\t") + ["", "", ""])[:4]
        unit_id, label, codes, note = (c.strip() for c in cells)
        if label not in LABELS:
            raise ValueError(f"บรรทัด {n}: ป้าย {label!r} ไม่อยู่ใน {LABELS}")
        if label == "advice":
            scope = parse_scope(codes)
        elif codes:
            raise ValueError(f"บรรทัด {n}: มี scope แต่ไม่ใช่ advice")
        else:
            scope = ""
        out.append(AgentLabel(unit_id, label, scope, note))
    return out


def stratum_quotas(counts: dict[str, int], fraction: float) -> dict[str, int]:
    """จำนวนที่สุ่มต่อชั้น: รวม = ปัดขึ้น fraction ของทั้งหมด, เศษมากได้ก่อน, ทุกชั้นได้อย่างน้อย 1."""
    total = math.ceil(sum(counts.values()) * fraction - 1e-9)
    exact = {k: v * fraction for k, v in counts.items()}
    quotas = {k: min(counts[k], math.floor(x)) for k, x in exact.items()}
    by_remainder = sorted(counts, key=lambda k: (-(exact[k] - math.floor(exact[k])), k))
    i = 0
    while sum(quotas.values()) < total:
        k = by_remainder[i % len(by_remainder)]
        if quotas[k] < counts[k]:
            quotas[k] += 1
        i += 1
    # ชั้นเล็กมาก (เช่น other) ต้องมีตัวแทนให้คนตรวจ เอามาจากชั้นที่ใหญ่สุด
    for k in sorted(counts):
        if counts[k] and quotas[k] == 0:
            biggest = max(quotas, key=lambda j: (quotas[j], j))
            quotas[biggest] -= 1
            quotas[k] = 1
    return quotas


def stratified_sample(
    ids_by_label: dict[str, Sequence[str]], fraction: float, seed: int
) -> list[str]:
    """สุ่มแบบแบ่งชั้นตามป้าย แล้วสลับลำดับ (ไม่ให้ลำดับบอกป้าย) ผลซ้ำได้ด้วย seed เดิม."""
    rng = random.Random(seed)
    quotas = stratum_quotas({k: len(v) for k, v in ids_by_label.items()}, fraction)
    picked: list[str] = []
    for label in sorted(ids_by_label):
        picked += rng.sample(sorted(ids_by_label[label]), quotas[label])
    rng.shuffle(picked)
    return picked
