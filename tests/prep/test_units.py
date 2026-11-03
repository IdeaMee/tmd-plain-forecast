import pytest

from tmd_plain.prep.tokenize import tokenize
from tmd_plain.prep.units import split_section, split_units

# ตัวอย่างจากคู่มือป้าย (docs/spec/labeling-guideline.md หัวข้อ 2-4) และรูปแบบจริงในชุดข้อมูล


def test_effect_and_mechanism_in_one_sentence_split_in_two() -> None:
    units = split_units(
        "ภาคใต้ตอนล่างมีฝนตกหนักบางแห่ง เนื่องจากมรสุมตะวันออกเฉียงเหนือกำลังปานกลางพัดปกคลุมอ่าวไทยและภาคใต้"
    )
    assert units == [
        "ภาคใต้ตอนล่างมีฝนตกหนักบางแห่ง",
        "เนื่องจากมรสุมตะวันออกเฉียงเหนือกำลังปานกลางพัดปกคลุมอ่าวไทยและภาคใต้",
    ]


def test_advice_with_hazards_and_areas_stays_one_unit() -> None:
    text = (
        "ขอให้ประชาชนในภาคใต้ระวังอันตรายจากฝนตกหนักและฝนที่ตกสะสม ซึ่งอาจทำให้เกิดน้ำท่วมฉับพลันและน้ำป่าไหลหลาก "
        "โดยเฉพาะพื้นที่ลาดเชิงเขาใกล้ทางน้ำไหลผ่านและพื้นที่ลุ่ม"
    )
    assert split_units(text) == [text]


@pytest.mark.parametrize(
    "text",
    [
        "ขอให้ประชาชนดูแลรักษาสุขภาพ เนื่องจากสภาพอากาศที่หนาวเย็นลง",
        "เกษตรกรควรป้องกันความเสียหายต่อผลผลิต เนื่องจากลมแรง",
        "ฝุ่นละอองในระยะนี้ มีการสะสมของฝุ่นละออง เนื่องจากการระบายอากาศในบริเวณดังกล่าวอยู่ในเกณฑ์ไม่ดี",
    ],
)
def test_because_without_mechanism_is_not_a_cut(text: str) -> None:
    assert split_units(text) == [text]


def test_result_phrase_splits_mechanism_from_effect() -> None:
    units = split_units(
        "อนึ่ง ในช่วงวันที่ 8–13 พฤศจิกายน 2569 บริเวณความกดอากาศสูงหรือมวลอากาศเย็นจะแผ่ลงมาปกคลุมประเทศไทยตอนบน "
        "ส่งผลทำให้ประเทศไทยตอนบนมีฝนลดลง"
    )
    assert units == [
        "อนึ่ง ในช่วงวันที่ 8–13 พฤศจิกายน 2569 บริเวณความกดอากาศสูงหรือมวลอากาศเย็นจะแผ่ลงมาปกคลุมประเทศไทยตอนบน",
        "ส่งผลทำให้ประเทศไทยตอนบนมีฝนลดลง",
    ]


def test_result_phrase_without_mechanism_is_not_a_cut() -> None:
    text = "ฝนตกหนักต่อเนื่อง ส่งผลให้เกิดน้ำท่วมขังบางพื้นที่"
    assert split_units(text) == [text]


def test_cause_paragraph_splits_at_connectives_but_not_inside_tangni() -> None:
    units = split_units(
        "ทั้งนี้เนื่องจากลมฝ่ายตะวันออกพัดปกคลุมอ่าวไทย ประเทศไทย และทะเลอันดามัน "
        "ในขณะที่บริเวณความกดอากาศสูงหรือมวลอากาศเย็นจากประเทศจีนมีกำลังอ่อนลง "
        "ประกอบกับคลื่นกระแสลมฝ่ายตะวันตกเคลื่อนผ่านประเทศเมียนมา"
    )
    assert len(units) == 3
    assert units[0].startswith("ทั้งนี้เนื่องจาก")
    assert units[1].startswith("ในขณะที่บริเวณความกดอากาศสูง")
    assert units[2].startswith("ประกอบกับคลื่นกระแสลม")


def test_markers_found_without_leading_space_from_pdf() -> None:
    units = split_units("มีฝนตกหนักบางแห่งบริเวณภาคใต้ขอให้ประชาชนในภาคใต้ระวังอันตรายจากฝนตกหนัก")
    assert units == ["มีฝนตกหนักบางแห่งบริเวณภาคใต้", "ขอให้ประชาชนในภาคใต้ระวังอันตรายจากฝนตกหนัก"]


@pytest.mark.parametrize(
    "text",
    [
        "ประเทศไทยยังคงมีฝนฟ้าคะนอง โดยเฉพาะบริเวณภาคกลาง รวมทั้งกรุงเทพมหานคร และปริมณฑล",
        "สำหรับทะเลอันดามันและอ่าวไทย บริเวณที่มีฝนฟ้าคะนองจะมีคลื่นสูงมากกว่า 2 เมตร",
    ],
)
def test_no_cut_at_specially_including_or_for(text: str) -> None:
    assert split_units(text) == [text]


def test_split_section_keeps_paragraph_breaks_and_order() -> None:
    paragraphs = ("ประเทศไทยตอนบนมีอากาศเย็น", "ทั้งนี้เนื่องจากมวลอากาศเย็นแผ่ลงมาปกคลุม")
    assert split_section(paragraphs) == list(paragraphs)


@pytest.mark.parametrize("word", ["ร้อยละ", "ฝนฟ้าคะนอง", "น้ำป่าไหลหลาก"])
def test_tokenize_keeps_weather_terms_whole(word: str) -> None:
    # พจนานุกรมคำอากาศทำให้ "ฝนฟ้าคะนอง" เป็นคำเดียว (ไม่ถูกตัดเป็น ฟ้า|คะนอง)
    tokens = tokenize("มีฝนฟ้าคะนองร้อยละ 30 ของพื้นที่ ระวังน้ำป่าไหลหลาก")
    assert word in tokens
    assert "คะนอง" not in tokens
    assert " " not in tokens


def test_date_only_fragment_joins_the_next_unit() -> None:
    units = split_units(
        "ในช่วงวันที่ 5-7 พ.ย.69 ขอให้ประชาชนบริเวณประเทศไทยตอนบนระวังอันตรายจากฝนฟ้าคะนอง "
        "ส่วนในช่วงวันที่ 6–11 พ.ย. 69 ขอให้ประชาชนบริเวณภาคใต้ระวังอันตรายจากฝนตกหนัก"
    )
    assert units == [
        "ในช่วงวันที่ 5-7 พ.ย.69 ขอให้ประชาชนบริเวณประเทศไทยตอนบนระวังอันตรายจากฝนฟ้าคะนอง",
        "ส่วนในช่วงวันที่ 6–11 พ.ย. 69 ขอให้ประชาชนบริเวณภาคใต้ระวังอันตรายจากฝนตกหนัก",
    ]
