"""ประกอบ WarningNotice จากประกาศที่แยกแล้ว + ตรวจความซื่อตรง.

เนื้อหาตัดเป็นหน่วย (กติกาเดียวกับรายวัน) แล้วเป็นท่อนที่ "สำหรับ/ชาวเรือ/เรือเล็ก/ขอให้" ตัวจัดประเภทประโยค
(NB/k-NN ที่เขียนเอง) แยกคำแนะนำ -> precautions คัดคำต่อคำ ท่อนอื่น -> lines คำต่อคำพร้อมค่าที่ดึงได้
ไม่เขียนเนื้อหาใหม่: ภาษาของประกาศอ่านเข้าใจได้อยู่แล้ว และการเขียนใหม่เสี่ยงทำให้ช่วงเวลา/พื้นที่ของคำเตือนเพี้ยน
ระดับความรุนแรงคือคำในหัวเรื่องของ TMD เอง (ไม่สร้างสเกลสี)
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from tmd_plain.config import load_config
from tmd_plain.contract import (
    REGION_KEYS,
    EffectPeriod,
    LineKind,
    QuotedAdvice,
    SummaryLine,
    WarningNotice,
)
from tmd_plain.doctypes.shipping.build import SHIPPING_PATTERNS
from tmd_plain.doctypes.warning.parse import ParsedWarning, effect_dates, norm
from tmd_plain.extract.facts import Pattern, Value, extract_line
from tmd_plain.extract.scope import clauses, locations
from tmd_plain.generate.fidelity import CHANCE
from tmd_plain.generate.templates import facts_dict, kind_of
from tmd_plain.generic import spans
from tmd_plain.prep.units import split_units, unit_id

_NUM = re.compile(r"\d+")


def _trend(m: re.Match[str]) -> list[tuple[str, Value]]:
    out: list[tuple[str, Value]] = [("temp_trend", m.group("trend"))]
    if m.group("lo"):
        out += [
            ("temp_change_low", int(m.group("lo"))),
            ("temp_change_high", int(m.group("hi") or m.group("lo"))),
        ]
    return out


# รูปแบบเฉพาะประกาศ: ประกาศเขียน "จะมีอุณหภูมิลดลง 1-3 องศาเซลเซียส" (รูปแบบกลางต้องมี "อุณหภูมิจะ")
# ใช้เฉพาะประกาศ เพื่อไม่ให้ผลของรายวัน/7 วันเปลี่ยน
WARNING_PATTERNS: tuple[Pattern, ...] = (
    *SHIPPING_PATTERNS,
    (
        re.compile(
            r"อุณหภูมิ(?P<trend>สูงขึ้น|ลดลง)(?:อีก)?(?:เล็กน้อย)?"
            r"(?:\s*(?P<lo>\d+)(?:\s*[-–]\s*(?P<hi>\d+))?\s*องศาเซลเซี\s?ยส)?"
        ),
        _trend,
    ),
)


@dataclass(frozen=True)
class WarningUnit:
    # ท่อนคำต่อคำ
    text: str
    unit_id: str
    # ป้ายจากตัวจัดประเภท (weather / cause / advice / other)
    label: str


def warning_unit_id(text: str) -> str:
    # unit_id ใช้อักษรแรกของชนิด ("w" จะชนกับสรุปรายสัปดาห์ weekly) จึงใช้ "wn"
    return "wn" + unit_id("w", text)[1:]


# ท่อนที่เหลือแค่คำเชื่อม ("สำหรับเรือเล็ก..." ถูกตัดทั้งที่ "สำหรับ" และ "เรือเล็ก") ต่อเข้ากับท่อนถัดไป
CONNECTORS = frozenset({"ส่วน", "สำหรับ"})


def _pieces(unit: str) -> list[str]:
    out: list[str] = []
    carry = ""
    for piece in clauses(unit):
        text = piece.strip()
        if not text:
            continue
        if text in CONNECTORS:
            carry += piece
            continue
        out.append((carry + piece).strip())
        carry = ""
    if carry.strip():
        out.append(carry.strip())
    return out


def warning_units(parsed: ParsedWarning, label_of: Callable[[str], str]) -> list[WarningUnit]:
    out: list[WarningUnit] = []
    for paragraph in parsed.paragraphs:
        for unit in split_units(paragraph):
            for text in _pieces(unit):
                out.append(WarningUnit(text, warning_unit_id(text), label_of(text)))
    return out


def _provinces(body: str) -> list[str]:
    # "กรุงเทพมหานคร" ที่มีแค่ในชื่อภาค "กรุงเทพมหานครและปริมณฑล" ไม่ใช่การกล่าวถึงจังหวัด
    region_only = body.count("กรุงเทพมหานคร") == body.count("กรุงเทพมหานครและปริมณฑล")
    return [p for p in spans.provinces(body) if not (p == "กรุงเทพมหานคร" and region_only)]


# คำเชื่อมที่การตัดหน่วยที่ "ขอให้" ทิ้งไว้ท้ายท่อน ("...อย่างระมัดระวัง จึง" + "ขอให้ประชาชนติดตาม...")
_TRAILING_JOIN = re.compile(r"\s*จึง$")
# วลีบอกจุดประสงค์ท้ายท่อน เป็นของคำแนะนำที่ตามมา ("ทั้งนี้ เพื่อความปลอดภัย..." + "ขอให้ประชาชน...")
_PURPOSE = re.compile(r"(?:ทั้งนี้\s*)?เพื่อความปลอดภัย")
_ADVICE_WORD = re.compile(r"ขอให้|ควร")


# "ส่วนมาก"/"ส่วนใหญ่" เป็นส่วนขยายของประโยคก่อนหน้า (ตัวตัดท่อนตัดที่คำ "ส่วน" ทุกที่)
_FRAGMENT = re.compile(r"^ส่วน(?:มาก|ใหญ่)")


def display_texts(texts: list[str], body: str, labels: list[str] | None = None) -> list[str]:
    """ข้อความที่แสดงของแต่ละท่อน: ย้ายคำเชื่อม/วลีจุดประสงค์ที่ค้างท้ายท่อนไปต้นท่อนถัดไป.

    ย้ายเฉพาะเมื่อข้อความที่ต่อแล้วอยู่ติดกันในต้นฉบับจริง (body = เนื้อหาที่ตัดช่องว่างแล้ว) จึงยังคำต่อคำ
    ท่อนที่ส่งให้ตัวจัดประเภทไม่เปลี่ยน เพราะป้ายที่ปิดไว้ใน 11.3 ผูกกับข้อความท่อนเดิม
    """
    out = list(texts)
    for i in range(len(out) - 1):
        found = list(_PURPOSE.finditer(out[i]))
        if found:
            start = found[-1].start()
            tail = out[i][start:].strip()
            joined = f"{tail} {out[i + 1]}"
            if out[i][:start].strip() and not _ADVICE_WORD.search(tail) and norm(joined) in body:
                out[i], out[i + 1] = out[i][:start].strip(), joined
        m = _TRAILING_JOIN.search(out[i])
        if m and out[i][: m.start()].strip():
            joined = "จึง" + out[i + 1]
            if norm(joined) in body:
                out[i], out[i + 1] = out[i][: m.start()].strip(), joined
    # ต่อท่อนส่วนขยายกลับท่อนก่อนหน้า (ป้ายเดียวกัน ติดกันในต้นฉบับ) ท่อนที่ถูกต่อไปแล้วเป็น "" (ผู้เรียกข้าม)
    for i in range(1, len(out)):
        same = labels is None or labels[i] == labels[i - 1]
        if out[i] and _FRAGMENT.match(out[i]) and out[i - 1] and same:
            joined = f"{out[i - 1]} {out[i]}"
            if norm(joined) in body:
                out[i - 1], out[i] = joined, ""
    return out


def _line(unit: WarningUnit, text: str) -> SummaryLine:
    facts = extract_line(text, 0, WARNING_PATTERNS)
    # ชื่อจังหวัดไม่บอกชนิดของประโยค (รูปแบบกลางนับเป็นฝน) ใช้ค่าอื่นก่อน
    kinds = [k for f in facts if f.name != "province" and (k := kind_of(f.name)) is not None]
    kinds += [k for f in facts if f.name == "province" and (k := kind_of(f.name)) is not None]
    kind: LineKind = kinds[0] if kinds else "other"
    return SummaryLine(kind=kind, text=text, facts={**facts_dict(facts), "unit_role": unit.label})


def assemble_warning(
    parsed: ParsedWarning, units: list[WarningUnit], source_label: str | None = None
) -> WarningNotice:
    """ผลทั้งฉบับ; ไม่มีเวลาประมวลผลในผล (ผลซ้ำได้)."""
    lines: list[SummaryLine] = []
    precautions: list[QuotedAdvice] = []
    seen: set[str] = set()
    texts = display_texts([u.text for u in units], norm(parsed.body()), [u.label for u in units])
    for unit, text in zip(units, texts, strict=True):
        if not text:
            continue
        if unit.label != "advice":
            lines.append(_line(unit, text))
        elif unit.unit_id not in seen:
            seen.add(unit.unit_id)
            here = locations(text)
            precautions.append(
                QuotedAdvice(
                    text=text,
                    regions=[k for k in REGION_KEYS if k in here],
                    source_unit_id=unit.unit_id,
                )
            )
    start, end = effect_dates(parsed.effect_text)
    effect = (
        EffectPeriod(text=parsed.effect_text, start=start, end=end) if parsed.effect_text else None
    )
    body = parsed.body()
    return WarningNotice(
        issue_id=parsed.issue_id,
        doc_type="warning",
        issued_at=parsed.issued_at,
        source_label=source_label or f"{parsed.title} ฉบับที่ {parsed.series_no} ({parsed.notice_no})",
        title=parsed.title,
        series_no=parsed.series_no,
        notice_no=parsed.notice_no,
        effect=effect,
        next_issue_at=parsed.next_issue_at,
        regions=spans.regions(f"{parsed.title}\n{body}"),
        provinces=_provinces(body),
        lines=lines,
        precautions=precautions,
        pipeline_version=load_config()["pipeline_version"],
    )


def _date_numbers_present(day_text: str, d: date) -> bool:
    # วัน (ตัวเลข) ของวันที่ที่อ่านได้ต้องอยู่ในข้อความต้นฉบับ (เดือน/ปีตรวจผ่าน parse_date_range แล้ว)
    return str(d.day) in _NUM.findall(day_text)


def check_warning(notice: WarningNotice, parsed: ParsedWarning) -> list[str]:
    """F: หัวเรื่อง ช่วงที่มีผล ทุกท่อน คำแนะนำ จังหวัด มาจากต้นฉบับคำต่อคำ · วันที่มีที่มา · ไม่มีคำว่าโอกาส."""
    errors: list[str] = []
    header = norm(" ".join(parsed.header_lines))
    body = norm(parsed.body())
    if norm(notice.title) not in header:
        errors.append("หัวเรื่องไม่อยู่ในต้นฉบับ")
    if f"({notice.notice_no})" not in header:
        errors.append("เลขประกาศไม่อยู่ในหัวประกาศ")
    if f"ฉบับที่{notice.series_no}(" not in header:
        errors.append("ฉบับที่ไม่อยู่ในหัวประกาศ")
    if notice.effect is not None:
        if norm(notice.effect.text) not in header:
            errors.append("ช่วงที่มีผลไม่อยู่ในต้นฉบับ")
        for d in (notice.effect.start, notice.effect.end):
            if d is not None and not _date_numbers_present(notice.effect.text, d):
                errors.append(f"วันที่ {d} ไม่มีในข้อความช่วงที่มีผล")
    if not _date_numbers_present(parsed.issued_line, notice.issued_at):
        errors.append("วันประกาศไม่ตรงบรรทัดประกาศ ณ วันที่")
    if notice.next_issue_at is not None and not _date_numbers_present(
        parsed.next_line, notice.next_issue_at
    ):
        errors.append("วันฉบับต่อไปไม่ตรงต้นฉบับ")
    for n, line in enumerate(notice.lines):
        if norm(line.text) not in body:
            errors.append(f"F3 ท่อน #{n} ไม่อยู่ในเนื้อหาต้นฉบับ")
        if CHANCE.search(line.text):
            errors.append(f"F4 ท่อน #{n} ใช้คำว่าโอกาส")
    for item in notice.precautions:
        if norm(item.text) not in body:
            errors.append(f"F3 ข้อควรระวังไม่อยู่ในต้นฉบับ {item.source_unit_id}")
        if CHANCE.search(item.text):
            errors.append(f"F4 ข้อควรระวังใช้คำว่าโอกาส {item.source_unit_id}")
    for name in notice.provinces:
        if norm(name) not in body:
            errors.append(f"F2 จังหวัด {name} ไม่อยู่ในต้นฉบับ")
    said = norm(
        "".join(ln.text for ln in notice.lines) + "".join(p.text for p in notice.precautions)
    )
    # ข้อมูลไม่หาย: ทุกท่อนของเนื้อหาต้องไปอยู่ใน lines หรือ precautions
    if not set(_NUM.findall(body)) <= set(_NUM.findall(said)):
        errors.append("ตัวเลขในเนื้อหาบางตัวหายจากผล")
    if notice.issue_id != parsed.issue_id:
        errors.append("รหัสฉบับไม่ตรงเลขประกาศ")
    return errors
