import csv
import math
from pathlib import Path

import pytest

from tmd_plain.classify.labeling import (
    parse_agent_labels,
    parse_scope,
    stratified_sample,
    stratum_quotas,
)
from tmd_plain.contract import LABELS, REGION_KEYS

ROOT = Path(__file__).resolve().parents[2]
LABELED = ROOT / "data" / "labeled"


def test_parse_scope_orders_keys_and_handles_general() -> None:
    assert parse_scope("SW SE") == "south_east_coast;south_west_coast"
    assert parse_scope("ALL") == "all"
    with pytest.raises(ValueError):
        parse_scope("XX")
    with pytest.raises(ValueError):
        parse_scope("")


def test_parse_agent_labels_rules() -> None:
    text = "# หัว\nu1\tweather\t\t\nu2\tadvice\tN NE\tหมายเหตุ\n\n"
    rows = parse_agent_labels(text)
    assert [(r.unit_id, r.label, r.scope, r.note) for r in rows] == [
        ("u1", "weather", "", ""),
        ("u2", "advice", "north;northeast", "หมายเหตุ"),
    ]
    with pytest.raises(ValueError):
        parse_agent_labels("u3\tadvice\t\t")  # advice ต้องมี scope
    with pytest.raises(ValueError):
        parse_agent_labels("u4\tcause\tN\t")  # ป้ายอื่นห้ามมี scope
    with pytest.raises(ValueError):
        parse_agent_labels("u5\twarning\t\t")


def test_quotas_sum_to_ceiling_and_cover_small_strata() -> None:
    q = stratum_quotas({"weather": 123, "cause": 111, "advice": 57, "other": 1}, 0.2)
    assert sum(q.values()) == math.ceil(292 * 0.2) == 59
    assert q["other"] == 1
    assert all(q[k] <= n for k, n in {"weather": 123, "cause": 111, "advice": 57}.items())


def test_stratified_sample_is_deterministic() -> None:
    ids = {"a": [f"a{i}" for i in range(10)], "b": [f"b{i}" for i in range(5)]}
    first = stratified_sample(ids, 0.2, seed=1)
    assert first == stratified_sample(ids, 0.2, seed=1)
    assert len(first) == len(set(first)) == 3


def test_labeled_files_are_consistent() -> None:
    labeled = LABELED / "units_labeled.csv"
    blind = LABELED / "blind_sample.csv"
    if not labeled.exists() or not blind.exists():
        pytest.skip("ยังไม่ได้รัน scripts/make_blind_sample.py")
    rows = list(csv.DictReader(labeled.open(encoding="utf-8-sig")))
    units = list(csv.DictReader((LABELED / "units.csv").open(encoding="utf-8-sig")))
    assert [r["unit_id"] for r in rows] == [u["unit_id"] for u in units]
    for r in rows:
        assert r["suggested_label"] in LABELS
        if r["suggested_label"] == "advice":
            assert r["scope"] == "all" or set(r["scope"].split(";")) <= set(REGION_KEYS)
        else:
            assert r["scope"] == ""
    sample = list(csv.DictReader(blind.open(encoding="utf-8-sig")))
    assert len(sample) == math.ceil(len(rows) * 0.2)
    header = set(sample[0])
    assert not header & {"suggested_label", "final_label", "scope", "note", "reviewer"}
    assert all(not s["human_label"] for s in sample)
