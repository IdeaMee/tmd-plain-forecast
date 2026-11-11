"""ช่วงข้อความที่ไฮไลต์ในโหมดทั่วไป: ทุกค่าเป็นข้อความต้นฉบับคำต่อคำ (Phase 10.3)."""

import pytest

from tmd_plain.generic import spans


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ระหว่างวันที่ 16 – 30 พฤศจิกายน พ.ศ. 2569 นี้", ["16 – 30 พฤศจิกายน พ.ศ. 2569"]),
        ("ในช่วงวันที่ 10-12 พ.ย. มีฝน", ["10-12 พ.ย."]),
        ("ตั้งแต่ 11 พ.ย.69 เป็นต้นไป", ["11 พ.ย.69"]),
        ("ช่วงเดือนมีนาคม – พฤษภาคม 2570", ["เดือนมีนาคม – พฤษภาคม 2570"]),
        ("ไม่มีวันที่ในประโยคนี้", []),
    ],
)
def test_dates(text: str, expected: list[str]) -> None:
    assert spans.dates(text) == expected
    assert all(d in text for d in spans.dates(text))


def test_numbers_keep_units_and_skip_dates() -> None:
    text = "คลื่นสูง 2 - 4 เมตร ฝนร้อยละ 30-70 ของพื้นที่ วันที่ 11 พ.ย. อุณหภูมิ 1.0 - 2.0 องศาเซลเซียส"
    assert spans.numbers(text) == ["2 - 4 เมตร", "ร้อยละ 30-70 ของพื้นที่", "1.0 - 2.0 องศาเซลเซียส"]


def test_ambiguous_province_needs_prefix() -> None:
    # "เลย" เป็นคำทั่วไป นับเป็นจังหวัดเมื่อมี จ./จังหวัด นำ
    assert spans.provinces("ไม่เคยเกิดขึ้นเลย") == []
    assert spans.regions("ไม่เคยเกิดขึ้นเลย") == []
    assert spans.provinces("ฝนตกที่ จ.เลย และเชียงใหม่") == ["เลย", "เชียงใหม่"]
    assert spans.regions("ฝนตกที่ จ.เลย") == ["northeast"]


def test_regions_follow_scope_map() -> None:
    assert spans.regions("ภาคใต้ฝั่งตะวันตกมีฝน") == ["south_west_coast"]
    assert spans.regions("ภาคตะวันออกเฉียงเหนือและภาคตะวันออก") == ["northeast", "east"]
