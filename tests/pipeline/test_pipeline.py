import sys
from pathlib import Path

import pytest

from tmd_plain.contract import Issue, SummarizeError
from tmd_plain.generate.assemble import IssueMeta, issued_at_from_id
from tmd_plain.pipeline import document_from_bytes, summarize
from tmd_plain.prep.extract import document_from_txt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
META = IssueMeta("161120261800", issued_at_from_id("daily", "161120261800"), "ทดสอบ")
DAILY = ROOT / "data" / "raw" / "daily" / "daily_161120261800.txt"


def label_of(text: str) -> str:
    return "advice" if text.startswith("ขอให้") else "weather"


@pytest.mark.parametrize(
    ("data", "code"),
    [
        (b"", "empty_file"),
        (bytes(range(256)) * 8, "extract_failed"),
        (b"%PDF-1.4 broken", "extract_failed"),
    ],
)
def test_bad_bytes_give_typed_errors(data: bytes, code: str) -> None:
    result = document_from_bytes(data)
    assert isinstance(result, SummarizeError) and result.error.code == code
    assert result.error.message_th


@pytest.mark.parametrize(
    ("text", "code"),
    [
        ("   \n", "empty_file"),
        ("กขค 123 abc ฟหกด\n" * 20, "unsupported_document"),
        (
            "พยากรณ์อากาศสำหรับการเดินเรือ\nลักษณะอากาศทั่วไป\nพยากรณ์อากาศสำหรับประเทศไทย\n",
            "unsupported_document",
        ),
    ],
)
def test_bad_text_gives_typed_errors(text: str, code: str) -> None:
    result = summarize(document_from_txt(text), META, label_of)
    assert isinstance(result, SummarizeError) and result.error.code == code


def test_real_daily_issue_and_truncated_copy() -> None:
    if not DAILY.exists():
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    text = DAILY.read_text(encoding="utf-8")
    assert isinstance(summarize(document_from_txt(text), META, label_of), Issue)
    # เอกสาร TMD ที่หาบล็อกภาคไม่ได้ = อ่านไม่สำเร็จ ไม่เดา
    cut = text.split("พยากรณ์อากาศสำหรับประเทศไทย")[0] + "พยากรณ์อากาศสำหรับประเทศไทย\n"
    result = summarize(document_from_txt(cut), META, label_of)
    assert isinstance(result, SummarizeError) and result.error.code == "extract_failed"


def test_processed_files_follow_the_contract() -> None:
    # ไฟล์ใน data/processed อยู่ใน repo (Q4) ต้องผ่านสัญญาเสมอแม้ไม่มีข้อมูลดิบ
    # พยากรณ์เดินเรือ (11.1) ใช้สัญญา ShippingIssue ตรวจใน tests/shipping
    files = sorted(
        p for d in ("daily", "sevenday") for p in (ROOT / "data" / "processed" / d).glob("*.json")
    )
    if not files:
        pytest.skip("ยังไม่ได้รัน scripts/run_pipeline.py")
    # 11.6: ขึ้นเว็บทุกฉบับที่เก็บ จำนวนโตตามข้อมูล · ชุดแสดงผลเดิม 35 ฉบับต้องยังอยู่ครบ
    assert len(files) >= 35
    if (ROOT / "data" / "raw" / "MANIFEST.csv").exists():
        from run_pipeline import display_issues, out_path

        original = display_issues()
        assert len(original) == 35
        assert all(out_path(i).exists() for i in original)
    for path in files:
        issue = Issue.model_validate_json(path.read_text(encoding="utf-8"))
        assert path.stem == issue.issue_id and path.parent.name == issue.doc_type
