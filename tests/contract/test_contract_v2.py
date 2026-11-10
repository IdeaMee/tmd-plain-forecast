import json
import re
from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError

from tmd_plain.contract import (
    SEA_AREA_KEYS,
    SEA_AREA_LABELS_TH,
    TRACE_MAX_BYTES,
    TRACE_MAX_ITEMS,
    GenericDocument,
    Issue,
    ShippingIssue,
    SummarizeOk,
    Trace,
    WarningNotice,
    WeeklySummary,
)
from tmd_plain.prep.extract import document_from_pdf

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "contract"
RAW = ROOT / "data" / "raw"
OK_V2: TypeAdapter = TypeAdapter(SummarizeOk)


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _flat(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _numbers(text: str) -> set[str]:
    return set(re.findall(r"\d+", text))


@pytest.mark.parametrize(
    ("name", "model"),
    [
        ("shipping-example.json", ShippingIssue),
        ("warning-example.json", WarningNotice),
        ("weekly-example.json", WeeklySummary),
    ],
)
def test_document_examples_validate(name: str, model: type) -> None:
    model.model_validate(_load(name))


def test_generic_response_example_validates() -> None:
    result = OK_V2.validate_python(_load("summarize-v2-generic-example.json"))
    assert result.kind == "generic"
    assert isinstance(result.document, GenericDocument)
    assert result.trace is not None and result.trace.steps[0].id == "read_pdf"


def test_issue_response_without_trace() -> None:
    data = {"ok": True, "kind": "issue", "document": _load("issue-daily-example.json")}
    result = OK_V2.validate_python(data)
    assert isinstance(result.document, Issue)
    assert result.trace is None


def test_kind_must_match_document() -> None:
    data = {"ok": True, "kind": "shipping", "document": _load("issue-daily-example.json")}
    with pytest.raises(ValidationError):
        OK_V2.validate_python(data)


def test_v2_response_round_trips_through_json() -> None:
    data = _load("summarize-v2-generic-example.json")
    dumped = OK_V2.dump_python(OK_V2.validate_python(data), mode="json")
    assert OK_V2.validate_python(dumped) == OK_V2.validate_python(data)


def test_shipping_needs_all_sea_areas() -> None:
    data = _load("shipping-example.json")
    del data["areas"]["ca_mau_cape"]
    with pytest.raises(ValidationError):
        ShippingIssue.model_validate(data)


def test_shipping_area_name_must_match_source_heading() -> None:
    data = _load("shipping-example.json")
    data["areas"]["gulf_of_thailand"]["name_th"] = "อ่าวไทย"
    with pytest.raises(ValidationError):
        ShippingIssue.model_validate(data)
    assert set(SEA_AREA_LABELS_TH) == set(SEA_AREA_KEYS)


def test_warning_id_must_match_notice_no() -> None:
    data = _load("warning-example.json")
    data["notice_no"] = "314/2569"
    with pytest.raises(ValidationError):
        WarningNotice.model_validate(data)


def test_warning_effect_dates_may_be_open() -> None:
    data = _load("warning-example.json")
    data["effect"] = {
        "text": "มีผลกระทบจนถึงวันที่ 22 พฤศจิกายน 2569",
        "start": None,
        "end": "2026-11-22",
    }
    assert WarningNotice.model_validate(data).effect.start is None
    data["effect"] = {"text": "x", "start": "2026-11-23", "end": "2026-11-22"}
    with pytest.raises(ValidationError):
        WarningNotice.model_validate(data)


def test_warning_next_issue_after_issue_time() -> None:
    data = _load("warning-example.json")
    data["next_issue_at"] = "2026-11-18T04:00:00+07:00"
    with pytest.raises(ValidationError):
        WarningNotice.model_validate(data)


def test_weekly_needs_all_regions() -> None:
    data = _load("weekly-example.json")
    del data["regions"]["east"]
    with pytest.raises(ValidationError):
        WeeklySummary.model_validate(data)


def test_generic_warning_follows_tmd_like() -> None:
    doc = _load("summarize-v2-generic-example.json")["document"]
    doc["tmd_like"] = False
    with pytest.raises(ValidationError):
        GenericDocument.model_validate(doc)
    doc["warnings"] = ["not_tmd_like"]
    assert GenericDocument.model_validate(doc).warnings == ["not_tmd_like"]


def test_generic_confidence_in_range() -> None:
    doc = _load("summarize-v2-generic-example.json")["document"]
    doc["sections"][0]["units"][0]["confidence"] = 1.2
    with pytest.raises(ValidationError):
        GenericDocument.model_validate(doc)


def test_trace_item_limit() -> None:
    step = {
        "id": "tokenize",
        "title_th": "ตัดคำ",
        "status": "done",
        "data": {"tokens": ["ก"] * TRACE_MAX_ITEMS},
    }
    Trace.model_validate({"steps": [step]})
    step["data"] = {"tokens": ["ก"] * (TRACE_MAX_ITEMS + 1)}
    with pytest.raises(ValidationError):
        Trace.model_validate({"steps": [step]})


def test_trace_byte_limit_and_unique_steps() -> None:
    big = "ก" * 1000
    steps = [
        {"id": sid, "title_th": "x", "status": "done", "data": {"tokens": [big] * TRACE_MAX_ITEMS}}
        for sid in ("tokenize", "filter_tokens")
    ]
    # สองขั้น x 50 ชิ้น x 3,000 ไบต์ เกินเพดาน 256 KB
    assert 2 * TRACE_MAX_ITEMS * 3000 > TRACE_MAX_BYTES
    with pytest.raises(ValidationError):
        Trace.model_validate({"steps": steps})
    small = {"id": "clean", "title_th": "x", "status": "done"}
    with pytest.raises(ValidationError):
        Trace.model_validate({"steps": [small, small]})


def _lines(obj: object) -> list[dict]:
    # เก็บทุก SummaryLine (มี kind + text; facts ไม่บังคับ) จากโครง JSON
    if isinstance(obj, dict):
        if "kind" in obj and "text" in obj:
            return [obj]
        return [ln for v in obj.values() for ln in _lines(v)]
    if isinstance(obj, list):
        return [ln for v in obj for ln in _lines(v)]
    return []


@pytest.mark.parametrize(
    ("name", "source", "quoted_keys"),
    [
        ("shipping-example.json", RAW / "shipping" / "shipping_311020261900.txt", ("advice",)),
        ("warning-example.json", RAW / "warning" / "warning_2569_315.txt", ("precautions",)),
        ("weekly-example.json", RAW / "weekly" / "weekly_310820261200.txt", ()),
    ],
)
def test_examples_come_from_source(name: str, source: Path, quoted_keys: tuple[str, ...]) -> None:
    # แนวเดียวกับ F1/F3: ตัวเลขในประโยคแม่แบบมีในต้นฉบับ ข้อความที่คัดมาตรงกับต้นฉบับคำต่อคำ
    if not source.exists():
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    src = source.read_text(encoding="utf-8")
    data = _load(name)
    for line in _lines(data):
        assert _numbers(line["text"]) <= _numbers(src), line["text"]
    quoted = [item["text"] for key in quoted_keys for item in data[key]]
    if name == "warning-example.json":
        quoted += [data["title"], data["effect"]["text"]]
    if name == "shipping-example.json":
        quoted += [area["name_th"] for area in data["areas"].values()]
    if name == "weekly-example.json":
        quoted += [
            cell["text"]
            for region in data["regions"].values()
            for cell in (region["rain_max"], region["temp_max"], region["temp_min"])
            if cell
        ]
    assert quoted
    for text in quoted:
        assert _flat(text) in _flat(src), text


def test_generic_example_units_are_verbatim() -> None:
    source = RAW / "generic" / "generic_outlook_monthly_2569_12.pdf"
    if not source.exists():
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    src = _flat(document_from_pdf(source.read_bytes()).text)
    doc = _load("summarize-v2-generic-example.json")["document"]
    for section in doc["sections"]:
        if section["heading"]:
            assert _flat(section["heading"]) in src
        for unit in section["units"]:
            assert _flat(unit["text"]) in src, unit["text"]
            for span in unit["numbers"] + unit["dates"] + unit["provinces"]:
                assert span in unit["text"], span
