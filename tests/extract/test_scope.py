import pytest

from tmd_plain.contract import REGION_KEYS
from tmd_plain.extract.advice import context_units, select_advice
from tmd_plain.extract.scope import advice_scope, locations
from tmd_plain.prep.regions import ParsedIssue

N, NE, C, E = "north", "northeast", "central", "east"
SE, SW, BKK = "south_east_coast", "south_west_coast", "bangkok_vicinity"
UPPER = {N, NE, C, E, BKK}


# ทุกแถวของตารางแมป (region-scope-map.md หัวข้อ 3)
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ภาคเหนือ", {N}),
        ("ภาคเหนือตอนบน", {N}),
        ("ภาคตะวันออกเฉียงเหนือตอนล่าง", {NE}),
        ("ภาคกลาง", {C, BKK}),  # D1
        ("ภาคกลางตอนล่าง", {C, BKK}),
        ("ภาคตะวันออก", {E}),
        ("กรุงเทพมหานครและปริมณฑล", {BKK}),
        ("ภาคใต้ฝั่งตะวันออก", {SE}),
        ("ภาคใต้ฝั่งตะวันตก", {SW}),
        ("ภาคใต้", {SE, SW}),  # D2
        ("ภาคใต้ตอนล่าง", {SE, SW}),
        ("ประเทศไทยตอนบน", UPPER),  # D3
        ("อ่าวไทยตอนล่าง", {SE}),
        ("อ่าวไทย", {E, SE}),  # D4
        ("อ่าวไทยตอนบน", {E, SE}),
        ("ทะเลอันดามัน", {SW}),
        ("ทะเลอันดามันตอนบน", {SW}),
        ("ชาวเรือควรเดินเรือด้วยความระมัดระวัง", {E, SE, SW}),
        ("เรือเล็กควรงดออกจากฝั่ง", {E, SE, SW}),
        ("ทะเลจีนใต้", set()),
        ("จังหวัดเชียงใหม่", {N}),
        ("จังหวัดภูเก็ต", {SW}),
        ("ขอให้ประชาชนติดตามประกาศจากกรมอุตุนิยมวิทยา", set()),
    ],
)
def test_map_table_rows(text: str, expected: set[str]) -> None:
    assert locations(text) == expected


def test_no_location_is_general_advice() -> None:  # D6
    s = advice_scope("ขอให้ประชาชนดูแลรักษาสุขภาพเนื่องจากสภาพอากาศที่เปลี่ยนแปลง")
    assert s.general and s.regions == REGION_KEYS


def test_several_locations_union() -> None:
    s = advice_scope("ขอให้ประชาชนบริเวณภาคใต้ระวังอันตรายจากฝนตกหนัก ส่วนประเทศไทยตอนบนควรดูแลสุขภาพ")
    assert not s.general and set(s.regions) == UPPER | {SE, SW}


def test_mentioned_area_inherits_from_paragraph() -> None:  # D5 + D7
    previous = ("พยากรณ์อากาศ 24 ชั่วโมงข้างหน้า ภาคใต้มีฝนตกหนัก", "ส่วนประเทศไทยตอนบนมีฝนบางพื้นที่")
    s = advice_scope("ขอให้ประชาชนในบริเวณดังกล่าวระวังอันตรายจากฝนตกหนัก", previous)
    assert set(s.regions) == UPPER | {SE, SW}
    # ไม่มีหน่วยก่อนหน้า = ไม่มีคำบอกที่ตั้ง
    assert advice_scope("ขอให้ประชาชนในบริเวณดังกล่าวระวังอันตราย").general
    # "ช่วงเวลาดังกล่าว" เป็นเวลา ไม่สืบทอดที่ตั้ง
    assert advice_scope("ขอให้ประชาชนวางแผนในช่วงเวลาดังกล่าว", previous).general


def test_clause_without_location_makes_unit_general() -> None:
    text = (
        "ขอให้ประชาชนระวังอันตรายจากฝนตกหนักและฝนตกสะสม"
        "ส่วนชาวเรือบริเวณอ่าวไทยและทะเลอันดามันควรเดินเรือด้วยความระมัดระวัง"
    )
    assert advice_scope(text).general


def test_mariners_without_sea_name_in_their_own_clause() -> None:
    text = "ขอให้ชาวเรือเดินเรือด้วยความระมัดระวัง เรือเล็กบริเวณอ่าวไทยตอนล่างควรงดออกจากฝั่ง"
    assert set(advice_scope(text).regions) == {E, SE, SW}


def _issue(overview: tuple[str, ...]) -> ParsedIssue:
    return ParsedIssue("daily", "txt", overview, (), {}, None)


def test_select_advice_puts_every_advice_somewhere() -> None:
    parsed = _issue(
        (
            "พยากรณ์อากาศ 24 ชั่วโมงข้างหน้า ภาคใต้มีฝนตกหนัก ขอให้ประชาชนในภาคใต้ระวังอันตรายจากฝนตกหนัก",
            "ขอให้ประชาชนติดตามประกาศจากกรมอุตุนิยมวิทยาอย่างต่อเนื่อง",
        )
    )
    units = context_units(parsed)
    assert [u.previous for u in units][1] == (units[0].text,)

    def label_of(text: str) -> str:
        return "advice" if text.startswith("ขอให้") else "weather"

    sel = select_advice(parsed, label_of)
    assert [a.text for a in sel.regional[SE]] == ["ขอให้ประชาชนในภาคใต้ระวังอันตรายจากฝนตกหนัก"]
    assert sel.regional[N] == []
    assert [a.text for a in sel.general] == ["ขอให้ประชาชนติดตามประกาศจากกรมอุตุนิยมวิทยาอย่างต่อเนื่อง"]
    assert all(a.general and a.scope == list(REGION_KEYS) for a in sel.general)
    # ข้อความคำแนะนำคัดจากต้นฉบับตรงๆ
    joined = " ".join(parsed.overview)
    assert all(a.text in joined for items in sel.regional.values() for a in items)
