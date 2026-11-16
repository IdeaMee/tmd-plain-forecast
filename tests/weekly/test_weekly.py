"""สรุปรายสัปดาห์ (Phase 11.5): แยกโครง (แท็บของตาราง) ข้อความคำต่อคำ ช่องตาราง ตรวจ F และ golden."""

import json
import sys
from datetime import date
from pathlib import Path

import pytest

from tmd_plain.contract import REGION_KEYS, SummarizeError, WeeklySummary
from tmd_plain.doctypes.weekly.build import assemble_weekly, cell_facts, check_weekly
from tmd_plain.doctypes.weekly.parse import WeeklyParseError, issued_from, parse_weekly
from tmd_plain.doctypes.weekly.runner import summarize_weekly

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "tests" / "golden" / "weekly"
PROCESSED = ROOT / "data" / "processed" / "weekly"
sys.path.insert(0, str(ROOT / "scripts"))
import make_golden_weekly  # noqa: E402

HEAD = "ปริมาณฝนสูงสุด\tอุณหภูมิสูงสุด\tอุณหภูมิต่ำสุด"
REGIONS = [
    "ภาคเหนือ",
    "ภาคตะวันออกเฉียงเหนือ",
    "ภาคกลาง",
    "ภาคตะวันออก",
    "ภาคใต้(ฝั่งตะวันออก)",
    "ภาคใต้(ฝั่งตะวันตก)",
    "กรุงเทพและปริมณฑล",
]
RAIN = "61.5 มม. ที่ อ.แม่สอด จ.ตาก เมื่อวันที่ 26 ส.ค."
TEMP = "38.5 º ซ. ที่ อ.ชัยบาดาล จ.ลพบุรี เมื่อวันที่ 12 เม.ย. (40.0 ° ซ. ที่ อ.ลับแล จ.อุตรดิตถ์ เมื่อวันที่ 11 เม.ย.)"


def _sample(
    rows: dict[str, str] | None = None, issued: str = "ออกประกาศ 31 สิงหาคม 2569 12:04 น."
) -> str:
    # rows: ชื่อภาค -> แถวค่า (3 ช่องคั่นด้วยแท็บ) ที่ไม่ระบุใช้ช่องฝนอย่างเดียว
    lines = [
        "# source: https://example.invalid/x",
        "# round_id: 310820261200",
        "",
        "ประเทศไทย",
        "24 สิงหาคม 2569 - 30 สิงหาคม 2569",
        "        ร่องมรสุมพาดผ่านภาคเหนือ ประกอบกับมรสุมตะวันตกเฉียงใต้พัดปกคลุมประเทศไทย",
        "        อนึ่งพายุโซนร้อนเคลื่อนขึ้นฝั่งในวันที่ 26 ส.ค.",
        "ลักษณะอากาศรายภาค",
        "24 สิงหาคม 2569 - 30 สิงหาคม 2569",
    ]
    for name in REGIONS:
        lines += [
            name,
            "มีฝนร้อยละ 30-55 ของพื้นที่ นอกจากนี้มีรายงานน้ำท่วมบริเวณจังหวัดสุโขทัย ในวันที่ 24 ส.ค. ",
            HEAD,
            (rows or {}).get(name, f"{RAIN}\t\t"),
        ]
    lines.append(issued)
    return "\n".join(lines)


def test_parse_structure_and_cell_positions() -> None:
    parsed = parse_weekly(_sample({"ภาคกลาง": f"\t{TEMP}\t", "ภาคตะวันออก": f"\t\t{TEMP}"}))
    assert parsed.week_start == date(2026, 8, 24) and parsed.week_end == date(2026, 8, 30)
    assert parsed.range_line == "24 สิงหาคม 2569 - 30 สิงหาคม 2569"
    assert parsed.issued_line == "ออกประกาศ 31 สิงหาคม 2569 12:04 น."
    assert parsed.default_issue_id() == "310820261200"
    assert len(parsed.overview) == 2 and set(parsed.regions) == set(REGION_KEYS)
    # ช่องว่างในตารางมีความหมาย: ตำแหน่งแท็บต้องรักษาไว้ (ข้อความสะอาดทั่วไปทำแท็บหาย)
    assert parsed.regions["north"].cells == (RAIN, "", "")
    assert parsed.regions["central"].cells == ("", TEMP, "")
    assert parsed.regions["east"].cells == ("", "", TEMP)


@pytest.mark.parametrize(
    "broken",
    [
        _sample().replace("ประเทศไทย\n", "", 1),
        _sample().replace("ลักษณะอากาศรายภาค", "อื่นๆ"),
        _sample().replace("ภาคกลาง\n", "ภาคกลางตอนบน\n"),
        _sample().replace("ภาคเหนือ\n", "ภาคกลาง\n", 1),
        _sample().replace(f"\n{RAIN}\t\t", f"\n{RAIN}\t", 1),
        _sample().rsplit("\n", 1)[0],
        _sample(issued="ออกประกาศ 31 กุมภาพันธ์ 2569 12:04 น."),
    ],
)
def test_parse_rejects_broken_structure(broken: str) -> None:
    with pytest.raises(WeeklyParseError):
        parse_weekly(broken)


def test_issued_from() -> None:
    assert (
        issued_from("ออกประกาศ 31 สิงหาคม 2569 12:04 น.").isoformat() == "2026-08-31T12:04:00+07:00"
    )  # type: ignore[union-attr]
    assert issued_from("ออกประกาศ 31 กุมภาพันธ์ 2569 12:04 น.") is None
    assert issued_from("ไม่มีเวลา") is None


def test_assemble_pieces_cells_and_defaults() -> None:
    parsed = parse_weekly(_sample({"ภาคกลาง": f"\t{TEMP}\t"}))
    summary = assemble_weekly(parsed)
    assert summary.issue_id == "310820261200" and summary.source_label == parsed.range_line
    north = summary.regions["north"]
    # ย่อหน้าตัดที่ "นอกจากนี้" ท่อนที่สองขึ้นต้นด้วยคำเชื่อมคำต่อคำ
    assert [ln.text.split()[0] for ln in north.lines] == [
        "มีฝนร้อยละ",
        "นอกจากนี้มีรายงานน้ำท่วมบริเวณจังหวัดสุโขทัย",
    ]
    assert north.lines[0].facts["rain_area_pct_low"] == 30
    assert north.rain_max is not None and north.rain_max.text == RAIN
    assert north.temp_max is None and north.temp_min is None
    central = summary.regions["central"]
    assert central.rain_max is None and central.temp_max is not None
    assert (
        central.temp_max.facts["value"] == 38.5 and central.temp_max.facts["second_value"] == 40.0
    )
    assert check_weekly(summary, parsed) == []
    # รหัสที่ระบุมาก่อนรหัสจากบรรทัดออกประกาศ (หน้าเว็บ 4/100 ฉบับใช้ชั่วโมงต่าง)
    assert assemble_weekly(parsed, "310820262300").issue_id == "310820262300"


@pytest.mark.parametrize(
    ("text", "value", "unit"),
    [
        (RAIN, 61.5, "มม."),
        ("19.0 ° ซ. ที่ กกษ.นครสรรค์ อ.ตากฟ้า จ.นครสวรรค์ เมื่อวันที่ 12 พ.ย.", 19.0, "°ซ."),
        ("37.9 º ซ. ที่ อ.เมืองนครสวรรค์ จ.นครสวรรค์ เมื่อวันที่ 9 มี.ค.", 37.9, "°ซ."),
        # ช่องที่ขึ้นต้นด้วยชื่อภาค และค่าที่สองไม่มีวงเล็บปิด
        (
            "ภาคกลาง 37.9 º ซ. ที่ อ.เมืองนครสวรรค์ จ.นครสวรรค์ เมื่อวันที่ 9 มี.ค. (25.5 มม. ที่ อ.ก จ.ข เมื่อวันที่ 24 เม.ย.",
            37.9,
            "°ซ.",
        ),
    ],
)
def test_cell_facts(text: str, value: float, unit: str) -> None:
    facts = cell_facts(text)
    assert facts["value"] == value and facts["unit"] == unit and facts["date_text"]


def test_cell_facts_unknown_shape_is_empty() -> None:
    assert cell_facts("ไม่มีตัวเลขในช่องนี้") == {}


def test_fidelity_catches_tampering() -> None:
    parsed = parse_weekly(_sample())
    summary = assemble_weekly(parsed)
    north = summary.regions["north"]
    # ช่องตารางถูกแก้ค่า
    cell = north.rain_max.model_copy(
        update={
            "text": RAIN.replace("61.5", "99.9"),
            "facts": {**north.rain_max.facts, "value": 99.9},
        }
    )  # type: ignore[union-attr]
    bad = summary.model_copy(
        update={
            "regions": {**summary.regions, "north": north.model_copy(update={"rain_max": cell})}
        }
    )
    assert any("ข้อความช่องไม่ตรง" in e for e in check_weekly(bad, parsed))
    # ท่อนหาย (ข้อมูลไม่หาย)
    short = north.model_copy(update={"lines": north.lines[:1]})
    bad = summary.model_copy(update={"regions": {**summary.regions, "north": short}})
    assert any("ไม่ครบ" in e for e in check_weekly(bad, parsed))
    # ช่องว่างในต้นฉบับถูกเติมค่า
    filled = north.model_copy(update={"temp_max": north.rain_max})
    bad = summary.model_copy(update={"regions": {**summary.regions, "north": filled}})
    assert any("ช่องว่าง/มีค่า" in e for e in check_weekly(bad, parsed))
    # คำว่าโอกาส
    chance = north.lines[0].model_copy(update={"text": "มีโอกาสฝน 30 %"})
    bad = summary.model_copy(
        update={
            "regions": {
                **summary.regions,
                "north": north.model_copy(update={"lines": [chance, *north.lines[1:]]}),
            }
        }
    )
    assert any(e.startswith("F4") for e in check_weekly(bad, parsed))


def test_summarize_weekly_error_is_typed() -> None:
    result = summarize_weekly("ไม่ใช่สรุปรายสัปดาห์")
    assert isinstance(result, SummarizeError) and result.error.code == "extract_failed"
    ok = summarize_weekly(_sample())
    assert isinstance(ok, WeeklySummary)


def test_golden_weekly() -> None:
    if not make_golden_weekly.sources_exist():
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    built = make_golden_weekly.build()
    assert sorted(built) == sorted(p.name for p in GOLDEN.glob("*.json"))
    for name, body in built.items():
        assert body == (GOLDEN / name).read_text(encoding="utf-8"), (
            f"{name}: รัน scripts/make_golden_weekly.py แล้วอ่าน diff"
        )


def test_processed_files_follow_contract() -> None:
    files = sorted(PROCESSED.glob("*.json"))
    if not files:
        pytest.skip("ยังไม่ได้รัน scripts/run_pipeline.py")
    for path in files:
        summary = WeeklySummary.model_validate(json.loads(path.read_text(encoding="utf-8")))
        assert summary.issue_id == path.stem
