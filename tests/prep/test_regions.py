import sys
from datetime import date
from pathlib import Path

import pytest

from tmd_plain.prep.doctype import detect_doc_type
from tmd_plain.prep.extract import SourceDocument
from tmd_plain.prep.periods import parse_date_range, split_periods
from tmd_plain.prep.regions import PrepError, _drop_station_table, parse_issue

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import make_golden_regions as golden  # noqa: E402


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ลักษณะอากาศทั่วไป\n...\nพยากรณ์อากาศสำหรับประเทศไทย", "daily"),
        ("พยากรณ์อากาศ\nประจำวันเสาร์ที่ 31\nพยากรณ์อากาศสำหรับประเทศไทย", "daily"),
        ("คาดหมายอากาศทั่วไป\nคาดหมายอากาศรายภาค", "sevenday"),
        ("พยากรณ์อากาศระยะปานกลาง\nสภาวะอากาศ", "sevenday"),
        ("พยากรณ์อากาศสำหรับการเดินเรือ\nพยากรณ์อากาศสำหรับประเทศไทย ลักษณะอากาศทั่วไป", "unsupported"),
        # 11.1: โครงเดินเรือครบ (หัวข้อพยากรณ์สำหรับเรือ + 4 พื้นที่) เป็นชนิดของตัวเอง
        (
            "พยากรณ์อากาศสำหรับเรือเดินทะเล\nอ่าวไทยทั้งสองฝั่ง\nทะเลอันดามันและช่องแคบมะละกา\n"
            "เส้นทางเดินเรือโกตาบารูถึงสิงคโปร์\nปลายแหลมญวน",
            "shipping",
        ),
        ("Introduction to Machine Learning", "unsupported"),
        ("", "unsupported"),
    ],
)
def test_detect_doc_type(text: str, expected: str) -> None:
    assert detect_doc_type(text) == expected


@pytest.mark.parametrize("text", ["", "ข้อความอื่นที่ไม่ใช่พยากรณ์"])
def test_parse_issue_rejects_non_forecast(text: str) -> None:
    with pytest.raises(PrepError) as err:
        parse_issue(SourceDocument(kind="txt", text=text))
    assert err.value.code == "unsupported_document"


def test_parse_issue_reports_missing_regions_as_extract_failed() -> None:
    text = "ลักษณะอากาศทั่วไป\nฝนตก\nออกประกาศ 1\nพยากรณ์อากาศสำหรับประเทศไทย\nภาคเหนือ\nฝน"
    with pytest.raises(PrepError) as err:
        parse_issue(SourceDocument(kind="txt", text=text))
    assert err.value.code == "extract_failed"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ในช่วงวันที่ 17 - 19 พ.ย. 69", (date(2026, 11, 17), date(2026, 11, 19))),
        ("ส่วนในช่วงวันที่ 20 – 22 พ.ย. 69", (date(2026, 11, 20), date(2026, 11, 22))),
        ("ในช่วงวันที่ 31 ต.ค. 69 – 2 พ.ย. 69", (date(2026, 10, 31), date(2026, 11, 2))),
        ("ในช่วงวันที่ 30 - 2 พ.ย. 69", (date(2026, 10, 30), date(2026, 11, 2))),
        ("16 – 22 พฤศจิกายน พ.ศ. 2569", (date(2026, 11, 16), date(2026, 11, 22))),
        ("ในช่วงวันที่ 30 ธ.ค. 69 - 2 ม.ค. 70", (date(2026, 12, 30), date(2027, 1, 2))),
        ("ในวันที่ 5 พ.ย. 69", (date(2026, 11, 5), date(2026, 11, 5))),
        ("ไม่มีวันที่", None),
    ],
)
def test_parse_date_range(text: str, expected) -> None:
    assert parse_date_range(text) == expected


def test_split_periods_ignores_mid_line_mentions() -> None:
    lines = (
        "มีฝนฟ้าคะนอง ร้อยละ 60 – 70 ของพื้นที่ โดยมีฝนตกหนักมากในช่วงวันที่ 20 - 22 พ.ย. 69",
        "ในช่วงวันที่ 16 - 17 พ.ย. 69",
        "ลมตะวันออกเฉียงเหนือ",
        "ส่วนในช่วงวันที่ 18 - 22 พ.ย. 69",
        "ลมตะวันออก",
    )
    blocks = split_periods(lines, (date(2026, 11, 16), date(2026, 11, 22)))
    assert [(b.start, b.end, b.explicit, len(b.lines)) for b in blocks] == [
        (date(2026, 11, 16), date(2026, 11, 22), False, 1),
        (date(2026, 11, 16), date(2026, 11, 17), True, 2),
        (date(2026, 11, 18), date(2026, 11, 22), True, 2),
    ]


def test_drop_station_table() -> None:
    body = ["ลมตะวันออก ความเร็ว 10-20 กม./ชม.", "ปทุมธานี", "นนทบุรี", "26", "27", "36", "34"]
    assert _drop_station_table(body) == ["ลมตะวันออก ความเร็ว 10-20 กม./ชม."]
    assert _drop_station_table(["ทะเลมีคลื่นสูง 1 เมตร"]) == ["ทะเลมีคลื่นสูง 1 เมตร"]


@pytest.mark.parametrize("name", sorted(golden.CASES))
def test_golden_regions(name: str) -> None:
    source = golden.CASES[name]
    if not source.exists():
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    expected = (ROOT / "tests" / "golden" / "regions" / f"{name}.json").read_text(encoding="utf-8")
    assert golden.render(golden.parsed_to_dict(golden.parse_path(source))) == expected


def test_web_text_line_broken_mid_sentence_joins_its_paragraph() -> None:
    # หน้าเว็บของ TMD ขึ้นบรรทัดใหม่กลางประโยค ("ควรงด" / "ออกจากฝั่ง...") ย่อหน้าจริงขึ้นต้นด้วยการเยื้อง
    from tmd_plain.prep.extract import document_from_txt

    content = (
        "ลักษณะอากาศทั่วไป\n13 พฤศจิกายน 2569\n\n"
        "\u2003พยากรณ์อากาศ 24 ชั่วโมงข้างหน้า มีฝนบางแห่ง\n\n"
        "\u2003สำหรับคลื่นลมบริเวณอ่าวไทยตอนล่าง เรือเล็กควรงด\nออกจากฝั่งต่อไปอีก 1 วัน\n\n"
        "ออกประกาศ 13 พฤศจิกายน 2569\nพยากรณ์อากาศสำหรับประเทศไทย\n"
        "ภาคเหนือ\nฝน\nภาคตะวันออกเฉียงเหนือ\nฝน\nภาคกลาง\nฝน\nภาคตะวันออก\nฝน\n"
        "ภาคใต้(ฝั่งตะวันออก)\nฝน\nภาคใต้(ฝั่งตะวันตก)\nฝน\nกรุงเทพและปริมณฑล\nฝน\nออกประกาศ 13"
    )
    parsed = parse_issue(document_from_txt(content))
    assert parsed.overview == (
        "พยากรณ์อากาศ 24 ชั่วโมงข้างหน้า มีฝนบางแห่ง",
        "สำหรับคลื่นลมบริเวณอ่าวไทยตอนล่าง เรือเล็กควรงดออกจากฝั่งต่อไปอีก 1 วัน",
    )
    assert parsed.regions["bangkok_vicinity"].lines == ("ฝน",)


def test_web_paragraph_opener_starts_a_paragraph_even_without_indent() -> None:
    from tmd_plain.prep.extract import document_from_txt

    content = (
        "ลักษณะอากาศทั่วไป\n\n"
        "\u2003ทั้งนี้เนื่องจากมีร่องมรสุมพาดผ่านภาคใต้ตอนกลาง\n"
        "สำหรับทะเลอันดามันและอ่าวไทย ชาวเรือควรเดินเรือด้วยความระมัดระวัง\n\n"
        "ออกประกาศ 1\nพยากรณ์อากาศสำหรับประเทศไทย\n"
        "ภาคเหนือ\nฝน\nภาคตะวันออกเฉียงเหนือ\nฝน\nภาคกลาง\nฝน\nภาคตะวันออก\nฝน\n"
        "ภาคใต้(ฝั่งตะวันออก)\nฝน\nภาคใต้(ฝั่งตะวันตก)\nฝน\nกรุงเทพและปริมณฑล\nฝน\nออกประกาศ 1"
    )
    parsed = parse_issue(document_from_txt(content))
    assert parsed.overview == (
        "ทั้งนี้เนื่องจากมีร่องมรสุมพาดผ่านภาคใต้ตอนกลาง",
        "สำหรับทะเลอันดามันและอ่าวไทย ชาวเรือควรเดินเรือด้วยความระมัดระวัง",
    )
