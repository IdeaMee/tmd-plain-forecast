import re
from pathlib import Path

import pytest

from tmd_plain.prep.pdf_text import (
    PdfTextError,
    clean_text,
    count_pua,
    extract_pdfium,
    extract_pdfminer,
)

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
FIXTURES = sorted((ROOT / "tests" / "fixtures" / "pdf").glob("*__*.txt"))


def _squash(text: str) -> str:
    # ชั้นข้อความ PDF ทำช่องว่างหาย/เกิน และ "–" กับ "-" แยกจากภาพไม่ได้ จึงไม่นับสองอย่างนี้
    return re.sub(r"\s+", "", text.replace("–", "-"))


def test_clean_text_maps_pua_to_thai_marks() -> None:
    assert clean_text("ก\uf70bา") == "ก้า"
    assert count_pua(clean_text("\uf701\uf705\uf718")) == 0


def test_clean_text_fixes_nikhahit_sara_aa() -> None:
    assert clean_text("นํา") == "นำ"


def test_clean_text_keeps_lines_and_drops_blank_lines() -> None:
    assert clean_text("a\r\n\r\n  b  c \n") == "a\nb c"


@pytest.mark.parametrize("extract", [extract_pdfium, extract_pdfminer])
def test_not_a_pdf_raises_typed_error(extract) -> None:
    with pytest.raises(PdfTextError):
        extract(b"not a pdf")


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.stem)
def test_pdfium_text_contains_hand_checked_block(fixture: Path) -> None:
    source_name = fixture.stem.split("__")[0]
    folder = "daily" if source_name.startswith("daily") else "sevenday"
    pdf = RAW / folder / f"{source_name}.pdf"
    if not pdf.exists():
        pytest.skip(f"ไม่มีข้อมูลดิบ {pdf.name} (data/raw ไม่อยู่ใน repo)")
    got = clean_text(extract_pdfium(pdf.read_bytes()))
    expected = fixture.read_text(encoding="utf-8")
    assert _squash(expected) in _squash(got)


def test_five_fixtures_exist() -> None:
    assert len(FIXTURES) == 5
