"""ขั้นต้นของภาพขั้นตอนที่ทุกชนิดมีเหมือนกัน: อ่าน PDF, ทำความสะอาด, ตรวจชนิด."""

from __future__ import annotations

from tmd_plain.doctypes.registry import DocTypeSpec
from tmd_plain.prep.clean import count_pua
from tmd_plain.prep.extract import SourceDocument
from tmd_plain.tracing import StepDraft

SAMPLE_LINES = 5
DOC_TYPE_TH = {
    "daily": "พยากรณ์อากาศรายวัน",
    "sevenday": "พยากรณ์อากาศ 7 วัน",
    "shipping": "พยากรณ์อากาศเพื่อการเดินเรือ",
    "generic": "ไม่ใช่ชนิดที่สรุปเต็ม: ใช้โหมดทั่วไป (แสดงโครงและป้ายประโยค ไม่เขียนข้อความใหม่)",
}


def changed_lines(raw: str, text: str) -> tuple[list[str], list[str]] | None:
    """บรรทัดที่การทำความสะอาดเปลี่ยนจริง (ก่อน, หลัง).

    clean_text ทำทีละบรรทัดและตัดเฉพาะบรรทัดว่าง บรรทัดดิบที่ไม่ว่างจึงจับคู่กับบรรทัดสะอาดได้ทีละคู่
    จับคู่ไม่ได้ (จำนวนไม่เท่า) = None ไม่เดา
    """
    raw_lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    clean_lines = text.split("\n")
    if len(raw_lines) != len(clean_lines):
        return None
    pairs = [(a, b) for a, b in zip(raw_lines, clean_lines, strict=True) if a != b]
    return [a for a, _ in pairs], [b for _, b in pairs]


def pdf_steps(doc: SourceDocument, spec: DocTypeSpec) -> list[StepDraft]:
    """อ่าน PDF และทำความสะอาด จากข้อมูลที่เก็บไว้ตอนอ่านครั้งแรก (ไม่อ่านไฟล์ซ้ำ)."""
    if doc.reader == "pypdfium2":
        read = StepDraft(
            "read_pdf",
            f"pypdfium2 อ่านข้อความได้ {doc.pages} หน้า",
            data={"pages": doc.pages, "chars": len(doc.raw)},
        )
    else:
        read = StepDraft(
            "read_pdf", "pypdfium2 อ่านไม่ได้ ใช้ pdfminer.six แทน", data={"chars": len(doc.raw)}
        )
    data: dict[str, object] = {
        "chars_before": len(doc.raw),
        "chars_after": len(doc.text),
        "pua_fixed": count_pua(doc.raw),
    }
    changed = changed_lines(doc.raw, doc.text)
    if changed is not None:
        before, after = changed
        data |= {
            "changed_lines": len(before),
            "before": before[:SAMPLE_LINES],
            "after": after[:SAMPLE_LINES],
        }
    clean = StepDraft(
        "clean",
        "แก้อักขระพิเศษของฟอนต์ไทย (PUA) จัดสระและช่องว่างรอบตัวเลข"
        + (f": เปลี่ยน {len(changed[0])} บรรทัด" if changed is not None else ""),
        data=data,
    )
    detect = StepDraft(
        "detect_type",
        DOC_TYPE_TH.get(spec.key, spec.key),
        data={"doc_type": spec.key, "kind": spec.kind},
    )
    return [read, clean, detect]
