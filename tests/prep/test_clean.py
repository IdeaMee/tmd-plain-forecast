import pytest

from tmd_plain.prep.clean import clean_text, count_pua, fix_digit_spacing, join_wrapped
from tmd_plain.prep.extract import document_from_txt, parse_saved_txt
from tmd_plain.prep.pdf_text import PdfTextError, extract_pdf_text


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("ในช่วงวันที่17 - 19 พ.ย. 69", "ในช่วงวันที่ 17 - 19 พ.ย. 69"),
        ("ร้อยละ 30ของพื้นที่", "ร้อยละ 30 ของพื้นที่"),
        ("ส่วนในช่วงวันที่ 6–11 พ.ย. 69ขอให้", "ส่วนในช่วงวันที่ 6–11 พ.ย. 69 ขอให้"),
        ("โทร. 1182", "โทร. 1182"),
        ("พ.ย.69", "พ.ย.69"),
    ],
)
def test_fix_digit_spacing(raw: str, expected: str) -> None:
    assert fix_digit_spacing(raw) == expected


def test_clean_text_applies_all_fixes_and_keeps_lines() -> None:
    raw = "ก\uf70bา\r\n\r\n  ร้อยละ 30ของพื้นที่ \nนํา"
    assert clean_text(raw) == "ก้า\nร้อยละ 30 ของพื้นที่\nนำ"
    assert count_pua(clean_text("\uf701\uf705\uf718")) == 0


def test_clean_text_turns_nbsp_into_single_spaces() -> None:
    assert (
        clean_text("มีฝนฟ้าคะนอง\u00a0ร้อยละ\u00a0\u00a020\u00a0ของพื้นที่")
        == "มีฝนฟ้าคะนอง ร้อยละ 20 ของพื้นที่"
    )


def test_join_wrapped_thai_to_thai_without_space() -> None:
    lines = ["ประกอบกับมรสุม", "ตะวันออกเฉียงเหนือพัดปกคลุม", "มีคลื่นสูง 2 เมตร", "ชาวเรือควรระวัง"]
    assert join_wrapped(lines) == ("ประกอบกับมรสุมตะวันออกเฉียงเหนือพัดปกคลุมมีคลื่นสูง 2 เมตรชาวเรือควรระวัง")


def test_join_wrapped_skips_blank_lines() -> None:
    assert join_wrapped(["", " ก ", "", "1"]) == "ก 1"


def test_parse_saved_txt_splits_header() -> None:
    meta, body = parse_saved_txt("# round_id: 311020261200\n# label: ประจำวันที่ 31\n\nลักษณะอากาศทั่วไป")
    assert meta == {"round_id": "311020261200", "label": "ประจำวันที่ 31"}
    assert body.strip() == "ลักษณะอากาศทั่วไป"


def test_document_from_txt_cleans_body() -> None:
    doc = document_from_txt("# issue_id: 261116\n\n     ในช่วงวันที่17 - 19 พ.ย. 69  \n")
    assert doc.kind == "txt"
    assert doc.meta["issue_id"] == "261116"
    assert doc.text == "ในช่วงวันที่ 17 - 19 พ.ย. 69"


@pytest.mark.parametrize("data", [b"", b"not a pdf at all"])
def test_extract_pdf_text_rejects_bad_input(data: bytes) -> None:
    with pytest.raises(PdfTextError):
        extract_pdf_text(data)
