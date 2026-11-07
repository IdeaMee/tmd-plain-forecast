import json
import re
import sys
from datetime import date
from pathlib import Path

import pytest

from tmd_plain.extract.facts import extract_block, extract_line
from tmd_plain.extract.provinces import canonical, province_region
from tmd_plain.prep.periods import find_date_phrases

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import make_golden_facts as golden  # noqa: E402


def facts_of(text: str) -> dict[str, object]:
    return {f.name: f.value for f in extract_line(text)}


def test_rain_area_is_share_of_area_with_kind() -> None:
    got = facts_of("มีฝนฟ้าคะนอง ร้อยละ 40 ของพื้นที่ และมีฝนตกหนักบางแห่ง")
    assert got == {
        "rain_kind": "ฝนฟ้าคะนอง",
        "rain_area_pct_low": 40,
        "rain_area_pct_high": 40,
        "heavy_rain": "ฝนตกหนักบางแห่ง",
    }
    assert facts_of("โดยมีฝน/ฝนฟ้าคะนองร้อยละ 10 – 30 ของพื้นที่")["rain_area_pct_high"] == 30


def test_temperatures_peak_and_trend() -> None:
    got = facts_of("อุณหภูมิต่ำสุด 21 – 26 องศาเซลเซียส อุณหภูมิสูงสุด 30 - 33 องศาเซลเซี ยส")
    assert (got["temp_min_low"], got["temp_min_high"]) == (21, 26)
    assert (got["temp_max_low"], got["temp_max_high"]) == (30, 33)
    peak = facts_of("บริเวณยอดดอยอากาศหนาว อุณหภูมิต่ำสุด 9-15 องศาเซลเซียส")
    # ยอดดอยไม่ใช่อุณหภูมิต่ำสุดของภาค
    assert "temp_min_low" not in peak
    assert (peak["peak_place"], peak["peak_feel"], peak["peak_temp_min_low"]) == (
        "ยอดดอย",
        "อากาศหนาว",
        9,
    )
    trend = facts_of("อากาศเย็นในตอนเช้ากับมีลมแรง และอุณหภูมิจะลดลง 1-2 องศาเซลเซียส")
    assert trend["temp_trend"] == "ลดลง" and trend["temp_change_high"] == 2
    assert trend["strong_wind"] == "ลมแรง" and trend["cold"] == "อากาศเย็น"


def test_wind_with_area_and_waves() -> None:
    got = facts_of("ตั้งแต่จังหวัดนครศรีธรรมราช ลงไป: ลมตะวันออก ความเร็ว 20-35 กม./ชม.")
    assert got["wind_area"] == "ตั้งแต่จังหวัดนครศรีธรรมราช ลงไป:"
    assert (got["wind_dir"], got["wind_speed_kmh_low"], got["wind_speed_kmh_high"]) == (
        "ตะวันออก",
        20,
        35,
    )
    # จังหวัดในวลีบอกเขตลมไม่ใช่จังหวัดที่มีฝน
    assert "province" not in got
    waves = facts_of("ทะเลมีคลื่นต่ำกว่า 1 เมตร ห่างฝั่งสูงมากกว่า 2 เมตร บริเวณที่มีฝนฟ้าคะนองคลื่นสูงมากกว่า 3 เมตร")
    assert (waves["wave_qualifier"], waves["wave_m_high"]) == ("ต่ำกว่า", 1)
    assert (waves["wave_offshore_qualifier"], waves["wave_offshore_m_low"]) == ("สูงมากกว่า", 2)
    assert waves["wave_storm_m_low"] == 3
    # "ฝนฟ้าคะนอง" ในวลีคลื่นไม่ใช่ข้อมูลฝน
    assert "rain_kind" not in waves


def test_provinces_keep_source_spelling() -> None:
    facts = extract_line("บริเวณจังหวัดเพชรบุรีนครศรีธรรมราช พัทลุง และสุราษฏร์ธานี")
    names = [f.value for f in facts if f.name == "province"]
    assert names == ["เพชรบุรี", "นครศรีธรรมราช", "พัทลุง", "สุราษฏร์ธานี"]
    assert canonical("สุราษฏร์ธานี") == "สุราษฎร์ธานี"
    assert province_region("สุราษฏร์ธานี") == "south_east_coast"
    assert province_region("นครพนม") == "northeast"


@pytest.mark.parametrize(
    ("text", "phrase", "start", "end"),
    [
        (
            "ส่วนในช่วงวันที่ 17 - 18 พ.ย. 69 มีฝน",
            "ส่วนในช่วงวันที่ 17 - 18 พ.ย. 69",
            date(2026, 11, 17),
            date(2026, 11, 18),
        ),
        (
            "ในช่วงวันที่ 30 - 31 ต.ค. และ 1 – 2 พ.ย. 69 มี",
            "ในช่วงวันที่ 30 - 31 ต.ค. และ 1 – 2 พ.ย. 69",
            date(2026, 10, 30),
            date(2026, 11, 2),
        ),
        (
            "ในช่วงวันที่ 31 ต.ค. 69 – 2 พ.ย. 69 มี",
            "ในช่วงวันที่ 31 ต.ค. 69 – 2 พ.ย. 69",
            date(2026, 10, 31),
            date(2026, 11, 2),
        ),
        (
            "ในช่วงวันที่ 16 และ 18 - 19 พ.ย. 69 อุณ",
            "ในช่วงวันที่ 16 และ 18 - 19 พ.ย. 69",
            date(2026, 11, 16),
            date(2026, 11, 19),
        ),
        (
            "อุณหภูมิจะลดลง ช่วงวันที่ 18 - 19 พ.ย. 69",
            "ช่วงวันที่ 18 - 19 พ.ย. 69",
            date(2026, 11, 18),
            date(2026, 11, 19),
        ),
        (
            "ในวันที่ 30 ธ.ค. – 2 ม.ค. 70",
            "ในวันที่ 30 ธ.ค. – 2 ม.ค. 70",
            date(2026, 12, 30),
            date(2027, 1, 2),
        ),
    ],
)
def test_find_date_phrases(text: str, phrase: str, start: date, end: date) -> None:
    [(p, s, e)] = find_date_phrases(text)
    assert (p.text, s, e) == (phrase, start, end)


def test_every_line_gets_line_index() -> None:
    facts = extract_block(["อุณหภูมิต่ำสุด 20-24 องศาเซลเซียส", "ลมตะวันออก ความเร็ว 10-20 กม./ชม."])
    assert {f.line for f in facts if f.name.startswith("temp")} == {0}
    assert {f.line for f in facts if f.name.startswith("wind")} == {1}


@pytest.mark.parametrize("name", sorted(golden.CASES))
def test_golden_facts(name: str) -> None:
    source = golden.CASES[name]
    if not source.exists():
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    expected = (ROOT / "tests" / "golden" / "facts" / f"{name}.json").read_text(encoding="utf-8")
    assert golden.render(golden.facts_to_dict(golden.parse_path(source))) == expected


@pytest.mark.parametrize("name", sorted(golden.CASES))
def test_golden_values_trace_back_to_source(name: str) -> None:
    # ตรวจจากไฟล์ golden ที่ commit แล้ว (ไม่ต้องมีข้อมูลดิบ): source อยู่ในบรรทัด, ตัวเลขของค่าอยู่ใน source
    data = json.loads(
        (ROOT / "tests" / "golden" / "facts" / f"{name}.json").read_text(encoding="utf-8")
    )
    for lines in data["regions"].values():
        for item in lines:
            assert item["facts"], item["text"]
            for fact_name, value, source in item["facts"]:
                assert source in item["text"]
                if fact_name in ("period_start", "period_end"):
                    continue
                if isinstance(value, str):
                    assert value in source
                else:
                    assert re.search(rf"(?<![\d.]){value}(?![\d.])", source), (
                        fact_name,
                        value,
                        source,
                    )
