from datetime import datetime
from pathlib import Path

import pytest

from tmd_plain.generate.assemble import BANGKOK, IssueMeta, default_source_label, meta_from_text
from tmd_plain.prep.extract import document_from_pdf
from tmd_plain.raw_io import load_manifest

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
SIGNERS = "นายทดสอบ ผู้พยากรณ์อากาศ\nกองพยากรณ์อากาศ กรมอุตุนิยมวิทยา\nพยากรณ์อากาศ\n"


@pytest.mark.parametrize(
    ("header", "issue_id", "label"),
    [
        (
            "ประจำวันจันทร์ที่ 16 พฤศจิกายน พ.ศ. 2569\nออกประกาศเวลา 1700 น.",
            "161120261800",
            "ประจำวันที่ 16 พฤศจิกายน 2569 17.00 น.",
        ),
        # PDF บางฉบับมีช่องว่างก่อน "ที่"
        (
            "ประจำวันพฤหัสบดี ที่ 12 พฤศจิกายน พ.ศ. 2569\nออกประกาศเวลา 0500 น.",
            "121120260600",
            "ประจำวันที่ 12 พฤศจิกายน 2569 05.00 น.",
        ),
        # PDF ทำช่องว่างหายรอบตัวเลข (known-defects.md 2b)
        (
            "ประจำวันจันทร์ที่16พฤศจิกายนพ.ศ.2569\nออกประกาศเวลา1700 น.",
            "161120261800",
            "ประจำวันที่ 16 พฤศจิกายน 2569 17.00 น.",
        ),
        # รอบ 23.00 น. ข้ามวันและข้ามเดือน: รหัสรอบเป็นเที่ยงคืนของวันถัดไป
        (
            "ประจำวันเสาร์ที่ 31 ตุลาคม พ.ศ. 2569\nออกประกาศเวลา 23.00 น.",
            "011120260000",
            "ประจำวันที่ 31 ตุลาคม 2569 23.00 น.",
        ),
    ],
)
def test_daily_meta_from_pdf_header(header: str, issue_id: str, label: str) -> None:
    meta = meta_from_text("daily", SIGNERS + header + "\nพยากรณ์อากาศ 24 ชั่วโมงข้างหน้า ...")
    assert meta == IssueMeta(
        issue_id=issue_id,
        issued_at=datetime.strptime(issue_id, "%d%m%Y%H%M").replace(tzinfo=BANGKOK),
        source_label=label,
    )


def test_sevenday_meta_from_pdf_header() -> None:
    text = (
        "กองพยากรณ์อากาศ\nพยากรณ์อากาศระยะปานกลาง\n"
        "ระหว่างช่วงวันที่ 16 – 22 พฤศจิกายน พ.ศ. 2569\n"
        "ออกประกาศวันจันทร์ที่ 16 พฤศจิกายน พ.ศ. 2569\nคาดหมายลักษณะอากาศ ..."
    )
    meta = meta_from_text("sevenday", text)
    assert meta == IssueMeta(
        issue_id="261116",
        issued_at=datetime(2026, 11, 16, tzinfo=BANGKOK),
        source_label=default_source_label("sevenday", "261116"),
    )


@pytest.mark.parametrize(
    ("doc_type", "text"),
    [
        ("daily", "พยากรณ์อากาศ\nไม่มีวันที่"),
        ("daily", "ประจำวันจันทร์ที่ 16 พฤศจิกายน พ.ศ. 2569\n(ไม่มีเวลา)"),
        ("daily", "ประจำวันจันทร์ที่ 16 Novem พ.ศ. 2569\nออกประกาศเวลา 1700 น."),
        ("daily", "ประจำวันจันทร์ที่ 31 กุมภาพันธ์ พ.ศ. 2569\nออกประกาศเวลา 1700 น."),
        ("daily", "ประจำวันจันทร์ที่ 16 พฤศจิกายน พ.ศ. 2569\nออกประกาศเวลา 2500 น."),
        ("sevenday", "พยากรณ์อากาศระยะปานกลาง\n(ไม่มีวันออกประกาศ)"),
    ],
)
def test_missing_or_bad_header_gives_none(doc_type: str, text: str) -> None:
    # หาวันเวลาไม่ได้ = ไม่เดา (ผู้เรียกตอบ extract_failed)
    assert meta_from_text(doc_type, text) is None  # type: ignore[arg-type]


def test_meta_matches_manifest_for_every_raw_pdf() -> None:
    if not (RAW / "MANIFEST.csv").exists():
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    issues = [i for i in load_manifest(RAW) if i.pdf is not None]
    if not issues or not issues[0].pdf.exists():  # type: ignore[union-attr]
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    checked_labels = 0
    for issue in issues:
        text = document_from_pdf(issue.pdf.read_bytes()).text  # type: ignore[union-attr]
        meta = meta_from_text(issue.doc_type, text)  # type: ignore[arg-type]
        assert meta is not None, issue.issue_id
        assert meta.issue_id == issue.issue_id
        if issue.label:
            # ป้ายจากหัว PDF ต้องเหมือนป้ายที่หน้าเว็บ TMD เขียน (หน้าหลักใช้ป้ายนี้)
            assert meta.source_label == issue.label, issue.issue_id
            checked_labels += 1
    assert len(issues) == 65 and checked_labels == 46
