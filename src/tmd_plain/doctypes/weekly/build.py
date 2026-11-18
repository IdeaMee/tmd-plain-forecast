"""ประกอบ WeeklySummary จากฉบับที่แยกแล้ว + ตรวจความซื่อตรง.

ข้อความของแต่ละภาคและภาพรวมคัดคำต่อคำ (ตัดเป็นท่อนที่ "นอกจากนี้/อีกทั้ง" หรือกติกาหน่วยเดียวกับรายวัน)
พร้อมค่าที่ดึงได้ใน facts ไม่เขียนประโยคใหม่ ไม่มีตัวจัดประเภท (เอกสารชนิดนี้ไม่มีคำแนะนำให้คัดแยก)
ช่องตาราง (ฝนสูงสุด อุณหภูมิสูงสุด/ต่ำสุด) คัดคำต่อคำ ช่องว่างในต้นฉบับ = None (ไม่ใช่ 0)
"""

from __future__ import annotations

import re

from tmd_plain.config import load_config
from tmd_plain.contract import (
    REGION_KEYS,
    LineKind,
    SummaryLine,
    TableCell,
    WeeklyRegion,
    WeeklySummary,
)
from tmd_plain.doctypes.warning.build import WARNING_PATTERNS
from tmd_plain.doctypes.weekly.parse import ParsedRegion, ParsedWeekly, norm
from tmd_plain.extract.facts import extract_line
from tmd_plain.generate.fidelity import CHANCE
from tmd_plain.generate.templates import facts_dict, kind_of
from tmd_plain.generic import spans
from tmd_plain.prep.units import split_units

# ท่อนใหม่เริ่มที่คำเชื่อมเหล่านี้ (ย่อหน้าของภาคอ่านยาก ถ้าฝนกับน้ำท่วมอยู่บรรทัดเดียว)
_PIECE_START = re.compile(r"(?=นอกจากนี้|อีกทั้ง)")
_NUM = re.compile(r"\d+(?:\.\d+)?")
_WS = re.compile(r"\s+")
# ช่องตาราง: "61.5 มม. ที่ อ.แม่สอด จ.ตาก เมื่อวันที่ 26 ส.ค." (อุณหภูมิ "º ซ." หรือ "° ซ." ต้นฉบับใช้ทั้งสองอักขระ)
# อาจตามด้วยค่าที่สองในวงเล็บ (วงเล็บปิดบางฉบับหาย) · ช่องหนึ่งใน 985 ขึ้นต้นด้วยชื่อภาค ("ภาคกลาง 37.9 º ซ. ที่ ...")
_CELL = re.compile(
    r"^(?:ภาค\S*\s+)?(?P<v>-?\d+(?:\.\d+)?)\s*(?P<u>มม\.|[º°]\s*ซ\.)\s*ที่\s*(?P<place>.+?)\s*เมื่อวันที่\s*"
    r"(?P<date>[^()]+?)\s*(?:\((?P<rest>.*?)\)?\s*)?$"
)
_UNIT = {"มม.": "มม."}
_CELL_NAMES = ("rain_max", "temp_max", "temp_min")
# หน่วยที่ควรอยู่ในแต่ละคอลัมน์ตามหัวตารางของ TMD (ต้นฉบับเองมีช่องที่ใส่ค่าผิดคอลัมน์ ดู check_weekly)
_COLUMN_UNIT = {"rain_max": "มม.", "temp_max": "°ซ.", "temp_min": "°ซ."}


def _tidy(text: str) -> str:
    # ช่องไฟกว้างของต้นฉบับ (U+2003 ฯลฯ) เป็นช่องว่างเดียว: เนื้อหาคำต่อคำ ต่างแค่ความกว้างช่องว่าง (ตัวตรวจเทียบแบบไม่สนช่องว่าง)
    return _WS.sub(" ", text).strip()


def _pieces(paragraph: str) -> list[str]:
    return [t for p in _PIECE_START.split(paragraph) if (t := _tidy(p))]


def _line(text: str) -> SummaryLine:
    facts = extract_line(text, 0, WARNING_PATTERNS)
    # ชื่อจังหวัดไม่บอกชนิดของประโยค ใช้ค่าอื่นก่อน
    kinds = [k for f in facts if f.name != "province" and (k := kind_of(f.name)) is not None]
    kinds += [k for f in facts if f.name == "province" and (k := kind_of(f.name)) is not None]
    kind: LineKind = kinds[0] if kinds else "other"
    return SummaryLine(kind=kind, text=text, facts=facts_dict(facts))


def _number(text: str) -> int | float:
    return float(text) if "." in text else int(text)


def cell_facts(text: str) -> dict[str, str | float | bool]:
    """ค่าจากช่องตาราง (ไม่ตรงรูปแบบ = {} ข้อความคำต่อคำยังแสดงได้ แต่ check_weekly จะรายงาน)."""
    m = _CELL.match(text)
    if m is None:
        return {}
    unit = _UNIT.get(m["u"], "°ซ.")
    facts: dict[str, str | float | bool] = {
        "value": float(m["v"]),
        "unit": unit,
        "place": m["place"].strip(),
        "date_text": m["date"].strip(),
    }
    if m["rest"]:
        second = _CELL.match(m["rest"].strip())
        if second is not None:
            facts |= {
                "second_value": float(second["v"]),
                "second_place": second["place"].strip(),
                "second_date_text": second["date"].strip(),
            }
    return facts


def _region(region: ParsedRegion) -> WeeklyRegion:
    lines = [_line(piece) for paragraph in region.paragraphs for piece in _pieces(paragraph)]
    cells: dict[str, TableCell | None] = {}
    for name, text in zip(_CELL_NAMES, region.cells, strict=True):
        if not text:
            cells[name] = None
            continue
        facts = cell_facts(text)
        if facts and facts.get("unit") != _COLUMN_UNIT[name]:
            # คัดตามต้นฉบับ แต่ติดธงให้หน้าเว็บบอกผู้อ่านว่าหน่วยไม่ตรงหัวคอลัมน์ (ไม่เดาว่าตั้งใจหรือพิมพ์ผิด)
            facts["column_unit_mismatch"] = True
        cells[name] = TableCell(text=text, facts=facts)  # type: ignore[arg-type]
    return WeeklyRegion(lines=lines, **cells)  # type: ignore[arg-type]


def assemble_weekly(parsed: ParsedWeekly, issue_id: str | None = None) -> WeeklySummary:
    """ผลทั้งฉบับ; ไม่มีเวลาประมวลผลในผล (ผลซ้ำได้). issue_id ไม่ระบุ = จากบรรทัดออกประกาศ."""
    overview = [
        _line(_tidy(unit)) for paragraph in parsed.overview for unit in split_units(paragraph)
    ]
    return WeeklySummary(
        issue_id=issue_id or parsed.default_issue_id(),
        doc_type="weekly",
        issued_at=parsed.issued_at,
        source_label=parsed.range_line,
        week_start=parsed.week_start,
        week_end=parsed.week_end,
        overview=overview,
        regions={key: _region(parsed.regions[key]) for key in REGION_KEYS},
        pipeline_version=load_config()["pipeline_version"],
    )


def check_weekly(summary: WeeklySummary, parsed: ParsedWeekly) -> list[str]:
    """F: ทุกท่อน/ช่องคัดคำต่อคำและครบ (ข้อมูลไม่หาย) · วันที่มีที่มา · จังหวัดอยู่ในบล็อก · ไม่มีคำว่าโอกาส."""
    errors: list[str] = []
    # ตัวเลขวันในต้นฉบับมีศูนย์นำ ("09 พฤศจิกายน") เทียบเป็นจำนวนเต็ม
    day_numbers = {int(n) for n in _NUM.findall(parsed.range_line) if "." not in n}
    for d in (summary.week_start, summary.week_end):
        if d.day not in day_numbers:
            errors.append(f"วันที่ {d} ไม่อยู่ในบรรทัดช่วงสัปดาห์")
    if summary.issued_at.day not in {
        int(n) for n in _NUM.findall(parsed.issued_line) if "." not in n
    }:
        errors.append("วันประกาศไม่ตรงบรรทัดออกประกาศ")
    if summary.source_label != parsed.range_line:
        errors.append("ป้ายฉบับไม่ตรงบรรทัดช่วงสัปดาห์")
    overview_src = norm("".join(parsed.overview))
    if norm("".join(ln.text for ln in summary.overview)) != overview_src:
        errors.append("ภาพรวมไม่ครบหรือไม่ตรงต้นฉบับ")
    for n, line in enumerate(summary.overview):
        if CHANCE.search(line.text):
            errors.append(f"F4 ภาพรวมท่อน #{n} ใช้คำว่าโอกาส")
    for key, region in summary.regions.items():
        src = parsed.regions[key]
        block = norm("".join(src.paragraphs))
        if norm("".join(ln.text for ln in region.lines)) != block:
            errors.append(f"{key}: ข้อความของภาคไม่ครบหรือไม่ตรงต้นฉบับ")
        for n, line in enumerate(region.lines):
            if CHANCE.search(line.text):
                errors.append(f"F4 {key}#{n} ใช้คำว่าโอกาส")
            for name in spans.provinces(line.text):
                if norm(name) not in block:
                    errors.append(f"F2 {key}: จังหวัด {name} ไม่อยู่ในต้นฉบับ")
        for name, raw in zip(_CELL_NAMES, src.cells, strict=True):
            cell: TableCell | None = getattr(region, name)
            if bool(raw) != (cell is not None):
                errors.append(f"{key}.{name}: ช่องว่าง/มีค่าไม่ตรงต้นฉบับ")
            elif cell is not None:
                if norm(cell.text) != norm(raw):
                    errors.append(f"{key}.{name}: ข้อความช่องไม่ตรงต้นฉบับ")
                value = cell.facts.get("value")
                if value is None:
                    errors.append(f"{key}.{name}: ดึงค่าจากช่องไม่ได้: {cell.text}")
                elif not any(float(n) == abs(float(value)) for n in _NUM.findall(cell.text)):
                    errors.append(f"{key}.{name}: ค่า {value} ไม่อยู่ในช่อง")
    return errors
