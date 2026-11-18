"""ประกาศเตือนภัย (Phase 11.2): แยกโครง ช่วงที่มีผล ตรวจ F เชื่อมชุด และ golden."""

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from tmd_plain.classify.model_io import load_classifier
from tmd_plain.contract import SummarizeError, WarningNotice
from tmd_plain.doctypes.warning.build import (
    assemble_warning,
    check_warning,
    display_texts,
    warning_units,
)
from tmd_plain.doctypes.warning.parse import WarningParseError, effect_dates, parse_warning
from tmd_plain.doctypes.warning.runner import summarize_warning
from tmd_plain.doctypes.warning.series import NoticeKey, link_series
from tmd_plain.prep.doctype import detect_doc_type
from tmd_plain.prep.extract import document_from_pdf, document_from_txt

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "warning"
GOLDEN = ROOT / "tests" / "golden" / "warning"
sys.path.insert(0, str(ROOT / "scripts"))
import make_golden_warnings  # noqa: E402

CLASSIFIER = load_classifier(ROOT / "models").for_doc("warning")
BKK = timezone(timedelta(hours=7))

SAMPLE = """ประกาศกรมอุตุนิยมวิทยา
เรื่อง อากาศแปรปรวนบริเวณประเทศไทยตอนบน
และฝนตกหนักถึงหนักมากบริเวณภาคใต้
(มีผลกระทบในช่วงวันที่ 5-9 พฤศจิกายน 2569)
ฉบับที่ 2 (285/2569)
-------------------
ในช่วงวันที่ 5-7 พฤศจิกายน 2569 บริเวณประเทศไทยตอนบนจะมีพายุฝนฟ้าคะนอง ส่วนภาคใต้มีฝนตกหนักบางแห่งที่จังหวัดสงขลา
ขอให้ประชาชนระวังอันตรายจากพายุฝนฟ้าคะนอง เรือเล็กบริเวณอ่าวไทยตอนล่าง
ควรงดออกจากฝั่งในช่วงวันดังกล่าว
ประกาศ ณ วันที่ 2 พฤศจิกายน พ.ศ. 2569 เวลา 05.00 น.
กรมอุตุนิยมวิทยาจะออกประกาศฉบับต่อไปในวันที่ 2 พฤศจิกายน พ.ศ. 2569 เวลา 17.00 น.
(ลงชื่อ) ชื่อผู้ลงนาม
"""


def _raw(name: str) -> Path:
    path = RAW / name
    if not path.exists():
        pytest.skip(f"ไม่มีข้อมูลดิบ {name} (data/raw ไม่อยู่ใน repo)")
    return path


def test_parse_sample_header_body_and_times() -> None:
    p = parse_warning(SAMPLE)
    assert p.title == "อากาศแปรปรวนบริเวณประเทศไทยตอนบนและฝนตกหนักถึงหนักมากบริเวณภาคใต้"
    assert p.effect_text == "มีผลกระทบในช่วงวันที่ 5-9 พฤศจิกายน 2569"
    assert (p.series_no, p.notice_no, p.issue_id) == (2, "285/2569", "2569_285")
    assert p.issued_at == datetime(2026, 11, 2, 5, 0, tzinfo=BKK)
    assert p.next_issue_at == datetime(2026, 11, 2, 17, 0, tzinfo=BKK)
    assert not p.final
    # ลงชื่อไม่อยู่ในเนื้อหา และบรรทัดที่หน้าเว็บตัดกลางประโยคถูกต่อ
    assert "ลงชื่อ" not in p.body()
    assert "อ่าวไทยตอนล่างควรงดออกจากฝั่ง" in p.body()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("มีผลกระทบในช่วงวันที่ 5-9 พฤศจิกายน 2569", (date(2026, 11, 5), date(2026, 11, 9))),
        ("มีผลกระทบจนถึงวันที่ 30 สิงหาคม 2569", (None, date(2026, 8, 30))),
        ("มีผลกระทบจนถึงวันที่ 10-12 ตุลาคม 2569", (None, date(2026, 10, 12))),
        ("มีผลกระทบตั้งแต่วันที่ 29 สิงหาคม – 2 กันยายน 2569", (date(2026, 8, 29), date(2026, 9, 2))),
        ("มีผลกระทบตั้งแต่วันที่ 5 ตุลาคม 2569", (date(2026, 10, 5), None)),
        (None, (None, None)),
    ],
)
def test_effect_dates(text: str | None, expected: tuple[date | None, date | None]) -> None:
    assert effect_dates(text) == expected


@pytest.mark.parametrize(
    ("broken", "why"),
    [
        (SAMPLE.replace("ประกาศกรมอุตุนิยมวิทยา\n", ""), "หัว"),
        (SAMPLE.replace("ฉบับที่ 2 (285/2569)", "ฉบับที่สอง"), "ฉบับที่"),
        (SAMPLE.replace("ประกาศ ณ วันที่", "ประกาศวันที่"), "ประกาศ ณ"),
    ],
)
def test_broken_structure_is_an_error_not_a_guess(broken: str, why: str) -> None:
    with pytest.raises(WarningParseError):
        parse_warning(broken)


def test_final_notice_and_missing_effect() -> None:
    text = SAMPLE.replace("(มีผลกระทบในช่วงวันที่ 5-9 พฤศจิกายน 2569)\n", "").replace(
        "กรมอุตุนิยมวิทยาจะออกประกาศฉบับต่อไปในวันที่ 2 พฤศจิกายน พ.ศ. 2569 เวลา 17.00 น.",
        "กรมอุตุนิยมวิทยาจะออกประกาศฉบับนี้เป็นฉบับสุดท้ายของเหตุการณ์นี้",
    )
    p = parse_warning(text)
    assert p.effect_text is None and p.final and p.next_issue_at is None
    run = summarize_warning(text, CLASSIFIER.label)
    assert not isinstance(run, SummarizeError)
    notice: WarningNotice = run.document  # type: ignore[assignment]
    assert notice.effect is None and notice.next_issue_at is None


def test_detection() -> None:
    assert detect_doc_type(SAMPLE) == "warning"
    # หัวประกาศอื่นของกรมที่ไม่มี "ฉบับที่ N (เลข/ปี)" ไม่ใช่ประกาศเตือนภัย
    assert detect_doc_type(SAMPLE.replace("ฉบับที่ 2 (285/2569)", "")) != "warning"


def test_sample_output_is_verbatim_and_scoped() -> None:
    run = summarize_warning(SAMPLE, CLASSIFIER.label)
    assert not isinstance(run, SummarizeError)
    n: WarningNotice = run.document  # type: ignore[assignment]
    assert n.provinces == ["สงขลา"]
    assert "south_east_coast" in n.regions and "north" in n.regions
    texts = [ln.text for ln in n.lines] + [p.text for p in n.precautions]
    assert any("เรือเล็กบริเวณอ่าวไทยตอนล่างควรงดออกจากฝั่ง" in t for t in texts)
    assert n.effect is not None and n.effect.start == date(2026, 11, 5)


def test_fidelity_check_catches_changed_output() -> None:
    parsed = parse_warning(SAMPLE)
    units = warning_units(parsed, CLASSIFIER.label)
    notice = assemble_warning(parsed, units)
    assert check_warning(notice, parsed) == []
    bad_title = notice.model_copy(update={"title": "ฝนตกหนักมากทั่วประเทศ"})
    assert check_warning(bad_title, parsed)
    bad_line = notice.model_copy(
        update={"lines": [notice.lines[0].model_copy(update={"text": "มีโอกาสฝน 60%"})]}
    )
    errs = check_warning(bad_line, parsed)
    assert any("F3" in e for e in errs) and any("F4" in e for e in errs)
    bad_prov = notice.model_copy(update={"provinces": ["เชียงใหม่"]})
    assert any("F2" in e for e in check_warning(bad_prov, parsed))


def _key(
    issue_id: str,
    series_no: int,
    hours: int,
    title: str = "ฝน",
    nxt: int | None = None,
    final: bool = False,
):
    t0 = datetime(2026, 11, 1, 5, tzinfo=BKK)
    return NoticeKey(
        issue_id=issue_id,
        series_no=series_no,
        title=title,
        issued_at=t0 + timedelta(hours=hours),
        next_issue_at=t0 + timedelta(hours=nxt) if nxt is not None else None,
        final=final,
    )


def test_series_links_consecutive_notices_and_closes_on_final() -> None:
    keys = [
        _key("2569_10", 1, 0, nxt=12),
        _key("2569_11", 2, 12, title="ฝน (ขยายพื้นที่)", nxt=24),
        _key("2569_12", 3, 24, final=True),
        _key("2569_13", 1, 36),
    ]
    series = link_series(keys)
    assert [[n.issue_id for n in s.notices] for s in series] == [
        ["2569_10", "2569_11", "2569_12"],
        ["2569_13"],
    ]
    assert series[0].closed and series[0].complete_start


def test_series_picks_the_chain_whose_next_time_matches() -> None:
    # สองเหตุการณ์พร้อมกัน ฉบับที่ 2 ของแต่ละชุดไปต่อชุดที่บอกเวลาฉบับต่อไปตรง
    keys = [
        _key("2569_20", 1, 0, title="ก", nxt=12),
        _key("2569_21", 1, 1, title="ข", nxt=13),
        _key("2569_22", 2, 12, title="ก"),
        _key("2569_23", 2, 13, title="ข"),
    ]
    series = link_series(keys)
    assert [[n.issue_id for n in s.notices] for s in series] == [
        ["2569_20", "2569_22"],
        ["2569_21", "2569_23"],
    ]


def test_series_gap_too_long_starts_a_new_partial_series() -> None:
    series = link_series([_key("2569_30", 1, 0), _key("2569_31", 2, 72)])
    assert len(series) == 2 and not series[1].complete_start


def test_pdf_and_web_text_give_the_same_header() -> None:
    txt = summarize_warning(
        document_from_txt(_raw("warning_2569_315.txt").read_text(encoding="utf-8")).text,
        CLASSIFIER.label,
    )
    pdf = summarize_warning(
        document_from_pdf(_raw("warning_2569_315.pdf").read_bytes()).text, CLASSIFIER.label
    )
    assert not isinstance(txt, SummarizeError) and not isinstance(pdf, SummarizeError)
    a, b = txt.document, pdf.document
    assert (a.title, a.notice_no, a.effect, a.issued_at, a.next_issue_at) == (
        b.title,
        b.notice_no,
        b.effect,
        b.issued_at,
        b.next_issue_at,
    )


def test_golden_warnings() -> None:
    if not make_golden_warnings.sources_exist():
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    built = make_golden_warnings.build()
    assert set(built) == {p.name for p in GOLDEN.glob("*.json")}
    for name, body in built.items():
        assert (GOLDEN / name).read_text(encoding="utf-8") == body, (
            f"{name}: รัน scripts/make_golden_warnings.py แล้วอ่าน diff"
        )


def test_warning_classifier_is_loaded_and_labels_advice() -> None:
    # 11.3: ตัวเฉพาะของประกาศโหลดจาก models/warning_selected.json และคืนป้ายชุด weather/cause/advice
    assert CLASSIFIER.doc_type == "warning"
    base = load_classifier(ROOT / "models")
    assert base.doc_type == "" and base.for_doc("shipping") is base
    units = warning_units(parse_warning(SAMPLE), CLASSIFIER.label)
    assert {u.label for u in units} <= {"weather", "cause", "advice"}
    assert any(u.label == "advice" and "งดออกจากฝั่ง" in u.text for u in units)


def test_display_texts_rejoins_connectors_verbatim() -> None:
    # 11.4: ตัดหน่วยที่ "ขอให้" ทิ้ง "จึง" และวลีจุดประสงค์ไว้ท้ายท่อนก่อน ตอนแสดงผลย้ายไปต้นท่อนถัดไป
    source = (
        "ลมแรงขึ้น ทั้งนี้ เพื่อความปลอดภัยและลดผลกระทบที่อาจเกิดขึ้น "
        "ขอให้ประชาชนวางแผนการเดินทางอย่างระมัดระวัง จึงขอให้ประชาชนติดตามประกาศ"
    )
    body = "".join(source.split())
    pieces = [
        "ลมแรงขึ้น ทั้งนี้ เพื่อความปลอดภัยและลดผลกระทบที่อาจเกิดขึ้น",
        "ขอให้ประชาชนวางแผนการเดินทางอย่างระมัดระวัง จึง",
        "ขอให้ประชาชนติดตามประกาศ",
    ]
    assert display_texts(pieces, body) == [
        "ลมแรงขึ้น",
        "ทั้งนี้ เพื่อความปลอดภัยและลดผลกระทบที่อาจเกิดขึ้น ขอให้ประชาชนวางแผนการเดินทางอย่างระมัดระวัง",
        "จึงขอให้ประชาชนติดตามประกาศ",
    ]
    # ไม่ติดกันในต้นฉบับ = ไม่ย้าย (คงคำต่อคำ)
    assert display_texts(pieces[1:], "อื่น") == pieces[1:]


def test_display_texts_reattaches_extension_fragments() -> None:
    # "ส่วนมาก..." เป็นส่วนขยายของประโยคก่อนหน้า (ตัวตัดท่อนตัดที่คำ "ส่วน" ทุกที่) ต่อกลับตอนแสดงเมื่อป้ายเดียวกันและติดกันในต้นฉบับ
    source = "ฝนฟ้าคะนองเกิดขึ้นได้บางพื้นที่ ส่วนมากบริเวณด้านตะวันตกของภาคเหนือ ขอให้ประชาชนระวัง"
    body = "".join(source.split())
    texts = ["ฝนฟ้าคะนองเกิดขึ้นได้บางพื้นที่", "ส่วนมากบริเวณด้านตะวันตกของภาคเหนือ", "ขอให้ประชาชนระวัง"]
    out = display_texts(texts, body, ["weather", "weather", "advice"])
    assert out == ["ฝนฟ้าคะนองเกิดขึ้นได้บางพื้นที่ ส่วนมากบริเวณด้านตะวันตกของภาคเหนือ", "", "ขอให้ประชาชนระวัง"]
    # ป้ายต่างกัน = ไม่ต่อ
    assert display_texts(texts, body, ["weather", "advice", "advice"])[1] == texts[1]


def test_next_issue_line_must_be_readable() -> None:
    # ไม่มีทั้งวันเวลาฉบับต่อไปและคำว่าฉบับสุดท้าย = ข้อผิดพลาด ไม่ใช่ "ฉบับสุดท้าย" ที่ไม่มีหลักฐาน
    assert parse_warning(SAMPLE).next_issue_at is not None
    broken = SAMPLE.replace(
        "กรมอุตุนิยมวิทยาจะออกประกาศฉบับต่อไปในวันที่ 2 พฤศจิกายน พ.ศ. 2569 เวลา 17.00 น.",
        "กรมอุตุนิยมวิทยาจะติดตามสถานการณ์อย่างใกล้ชิด",
    )
    assert broken != SAMPLE
    with pytest.raises(WarningParseError):
        parse_warning(broken)
