import json
import re
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from tmd_plain.config import load_config
from tmd_plain.contract import (
    ERROR_MESSAGES_TH,
    LABELS,
    REGION_KEYS,
    AdviceItem,
    Issue,
    SummaryLine,
    error_response,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "contract"
RAW = ROOT / "data" / "raw"
sys.path.insert(0, str(ROOT / "scripts"))
import export_schema  # noqa: E402


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", ["issue-daily-example.json", "issue-sevenday-example.json"])
def test_examples_validate(name: str) -> None:
    issue = Issue.model_validate(_load(name))
    assert set(issue.regions) == set(REGION_KEYS)


def test_missing_region_is_rejected() -> None:
    data = _load("issue-daily-example.json")
    del data["regions"]["east"]
    with pytest.raises(ValidationError):
        Issue.model_validate(data)


def test_unknown_region_is_rejected() -> None:
    data = _load("issue-daily-example.json")
    data["regions"]["south"] = data["regions"].pop("south_west_coast")
    with pytest.raises(ValidationError):
        Issue.model_validate(data)


def test_daily_must_not_have_periods() -> None:
    data = _load("issue-daily-example.json")
    data["regions"]["north"]["periods"] = [
        {"start": "2026-10-31", "end": "2026-11-01", "lines": [{"kind": "other", "text": "x"}]}
    ]
    with pytest.raises(ValidationError):
        Issue.model_validate(data)


def test_issue_id_format_follows_doc_type() -> None:
    data = _load("issue-sevenday-example.json")
    data["issue_id"] = "311020261200"
    with pytest.raises(ValidationError):
        Issue.model_validate(data)


def test_advice_in_region_must_include_that_region() -> None:
    data = _load("issue-daily-example.json")
    data["regions"]["north"]["advice"] = data["regions"]["central"]["advice"]
    with pytest.raises(ValidationError):
        Issue.model_validate(data)


def test_general_advice_needs_all_regions() -> None:
    with pytest.raises(ValidationError):
        AdviceItem(text="x", scope=["north"], general=True, source_unit_id="u")
    ok = AdviceItem(text="x", scope=list(REGION_KEYS), general=True, source_unit_id="u")
    assert ok.general


def test_unknown_line_kind_is_rejected() -> None:
    with pytest.raises(ValidationError):
        SummaryLine.model_validate({"kind": "probability", "text": "x"})


def test_constants() -> None:
    assert LABELS == ("weather", "advice", "cause", "other")
    assert len(REGION_KEYS) == 7
    err = error_response("too_large")
    assert err.ok is False and err.error.message_th == ERROR_MESSAGES_TH["too_large"]


def test_config_loads() -> None:
    cfg = load_config()
    assert cfg["max_upload_bytes"] == 4 * 1024 * 1024
    assert cfg["paths"]["raw"] == "data/raw"


def test_schema_export_is_deterministic_and_committed() -> None:
    first = {k: export_schema.render(v) for k, v in export_schema.build_schemas().items()}
    second = {k: export_schema.render(v) for k, v in export_schema.build_schemas().items()}
    assert first == second
    for filename, text in first.items():
        committed = ROOT / "lib" / "contract" / filename
        assert committed.read_text(encoding="utf-8") == text, (
            f"รัน scripts/export_schema.py ใหม่ ({filename})"
        )


def _numbers(text: str) -> set[str]:
    return set(re.findall(r"\d+", text))


@pytest.mark.parametrize(
    ("name", "source"),
    [
        ("issue-daily-example.json", RAW / "daily" / "daily_311020261200.txt"),
        ("issue-sevenday-example.json", RAW / "sevenday" / "sevenday_261116.txt"),
    ],
)
def test_example_numbers_and_advice_come_from_source(name: str, source: Path) -> None:
    # ตัวอย่างต้องไม่มีตัวเลขหรือคำแนะนำที่ไม่มีในต้นฉบับ (แนวเดียวกับ F1/F3)
    if not source.exists():
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    src = source.read_text(encoding="utf-8")
    src_flat = re.sub(r"\s+", "", src)
    issue = Issue.model_validate(_load(name))
    for region in issue.regions.values():
        lines = list(region.lines) + [ln for p in region.periods for ln in p.lines]
        for line in lines:
            assert _numbers(line.text) <= _numbers(src), line.text
        for item in region.advice:
            assert re.sub(r"\s+", "", item.text) in src_flat, item.text
