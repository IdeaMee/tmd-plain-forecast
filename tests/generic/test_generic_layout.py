"""โครงเอกสารของโหมดทั่วไป: หัวเรื่อง หัวข้อ ย่อหน้า และเลขหน้า (Phase 10.3)."""

from tmd_plain.generic.layout import build_layout, content_lines, find_title, has_region_headings

LONG = "ก" * 60
# บรรทัดเต็มยาว 60 ตัว บรรทัดสุดท้ายของย่อหน้าสั้นกว่า 75%
TEXT = "\n".join(
    [
        "- 1 -",
        "ประกาศกรมอุตุนิยมวิทยา",
        "ลักษณะอากาศทั่วไป",
        LONG,
        "ขข",
        "2",
        LONG,
        "คคค",
        "ภาคเหนือ " + "ง" * 51,
        "ภาคกลาง " + "จ" * 52,
        "ภาคใต้ " + "ฉ" * 53,
    ]
)


def test_title_skips_page_number_and_prefers_tmd_title() -> None:
    assert find_title(["- 1 -", "นายสมชาย", "ประกาศกรมอุตุนิยมวิทยา"]) == "ประกาศกรมอุตุนิยมวิทยา"
    assert find_title(["1", "เอกสารอื่น"]) == "เอกสารอื่น"
    assert find_title(["123"]) is None


def test_page_numbers_are_not_content() -> None:
    assert content_lines("- 1 -\nข้อความ\n 2 \nอีก") == ["ข้อความ", "อีก"]


def test_layout_heading_paragraphs_and_join_across_page_number() -> None:
    layout = build_layout(TEXT, heading_max_chars=40)
    assert layout.title == "ประกาศกรมอุตุนิยมวิทยา"
    assert [b.heading for b in layout.blocks] == ["ลักษณะอากาศทั่วไป"]
    paragraphs = layout.blocks[0].paragraphs
    # ย่อหน้าแรกจบที่บรรทัดสั้น "ขข" · ย่อหน้าที่สองต่อข้ามเลขหน้า "2" (ไม่มี "2" อยู่ในข้อความ)
    assert paragraphs[0] == LONG + "ขข"
    assert paragraphs[1] == LONG + "คคค"
    # ชื่อภาคขึ้นต้นบรรทัด = ย่อหน้าใหม่
    assert [p.split()[0] for p in paragraphs[2:]] == ["ภาคเหนือ", "ภาคกลาง", "ภาคใต้"]
    assert layout.region_leads == ("ภาคเหนือ", "ภาคกลาง", "ภาคใต้")
    assert has_region_headings(layout)


def test_short_table_lines_are_not_headings() -> None:
    # บรรทัดสั้นที่ตามด้วยบรรทัดสั้น (ตาราง) ไม่ใช่หัวข้อ
    layout = build_layout(
        "หัวเรื่องรายงาน\n" + LONG + "\nค่าเฉลี่ย\n18 – 20\nน้อยกว่า", heading_max_chars=40
    )
    assert all(b.heading is None for b in layout.blocks)
    assert not has_region_headings(layout)
