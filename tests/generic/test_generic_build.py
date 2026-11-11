"""ประกอบ GenericDocument + ตรวจความถูกต้อง ด้วยข้อความสังเคราะห์และโมเดลจริงใน models/ (Phase 10.3)."""

from pathlib import Path

from tmd_plain.classify.model_io import load_classifier
from tmd_plain.config import load_config
from tmd_plain.generic.build import build_generic, glossary_for
from tmd_plain.generic.fidelity import check_generic
from tmd_plain.prep.extract import SourceDocument

ROOT = Path(__file__).resolve().parents[2]
CLASSIFIER = load_classifier(ROOT / "models")
CFG = load_config()["generic"]
TEXT = "\n".join(
    [
        "พยากรณ์อากาศเกษตรรายปักษ์",
        "ลักษณะอากาศทั่วไป",
        "บริเวณความกดอากาศสูงจากประเทศจีนจะแผ่ลงมาปกคลุมประเทศไทยตอนบน ทำให้มีอากาศเย็นในตอนเช้า",
        "บริเวณภาคเหนือ อุณหภูมิต่ำสุด 16-18 องศาเซลเซียส",
        "ข้อแนะนำ",
        "ขอให้ประชาชนบริเวณจังหวัดเชียงใหม่ดูแลรักษาสุขภาพเนื่องจากสภาพอากาศที่เปลี่ยนแปลง",
        "กรมอุตุนิยมวิทยา",
    ]
)


def _doc(text: str) -> SourceDocument:
    return SourceDocument(kind="pdf", text=text, raw=text, pages=1, reader="pypdfium2")


def test_build_is_faithful_and_labelled() -> None:
    document, details = build_generic(_doc(TEXT), CLASSIFIER, CFG)
    assert document.title == "พยากรณ์อากาศเกษตรรายปักษ์"
    assert document.tmd_like and document.warnings == []
    assert [s.heading for s in document.sections] == ["ลักษณะอากาศทั่วไป", "ข้อแนะนำ"]
    units = [u for s in document.sections for u in s.units]
    assert len(units) == len(details.units) > 0
    advice = [u for u in units if u.label == "advice"]
    assert advice and "ขอให้ประชาชน" in advice[0].text
    assert "เชียงใหม่" in advice[0].provinces and "north" in advice[0].regions
    assert all(0.0 <= u.confidence <= 1.0 for u in units)
    assert check_generic(document, TEXT) == []
    assert [g.term for g in document.glossary] == ["อากาศเย็น"]


def test_build_is_deterministic() -> None:
    a, _ = build_generic(_doc(TEXT), CLASSIFIER, CFG)
    b, _ = build_generic(_doc(TEXT), CLASSIFIER, CFG)
    assert a.model_dump_json() == b.model_dump_json()


def test_not_tmd_like_gets_warning() -> None:
    text = "Introduction to Machine Learning\nGradient descent minimizes the loss function step by step"
    document, _ = build_generic(_doc(text), CLASSIFIER, CFG)
    assert document.tmd_like is False and document.warnings == ["not_tmd_like"]


def test_fidelity_catches_invented_text_and_numbers() -> None:
    document, _ = build_generic(_doc(TEXT), CLASSIFIER, CFG)
    section = document.sections[0]
    unit = section.units[0]
    fake_unit = unit.model_copy(update={"text": unit.text + " ฝนตกหนักมาก", "numbers": ["99 มม."]})
    fake = document.model_copy(
        update={
            "sections": [section.model_copy(update={"units": [fake_unit]}), *document.sections[1:]]
        }
    )
    problems = check_generic(fake, TEXT)
    assert any("ข้อความไม่อยู่ในต้นฉบับ" in p for p in problems)
    assert any("99 มม." in p for p in problems)


def test_cold_glossary_only_and_guarded() -> None:
    # เกณฑ์ฝนไม่ให้ในโหมดทั่วไป · "อากาศหนาวเย็น" ไม่ใช่ระดับ "อากาศหนาว"
    assert glossary_for("ฝนตกหนักมาก อากาศหนาวเย็น") == []
    assert [g.term for g in glossary_for("มีอากาศหนาวจัด")] == ["อากาศหนาวจัด"]
