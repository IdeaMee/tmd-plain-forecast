"""ดึงค่าจากบรรทัดในบล็อกภาค (ขั้น 2) ด้วย regex; ทุกค่าเก็บข้อความต้นฉบับที่ตรงกันไว้ตรวจย้อนกลับ.

กติกา: ค่าที่เป็นข้อความคัดมาตรงๆ จากต้นฉบับ, ตัวเลขทุกตัวต้องอยู่ใน `source` ของค่านั้น
ยกเว้นวันที่ ISO ของช่วงวัน (แปลงจาก พ.ศ.) ซึ่งเก็บวลีต้นฉบับไว้ใน `period_text`
"ร้อยละ N ของพื้นที่" คือสัดส่วนพื้นที่ที่มีฝน ไม่ใช่โอกาสฝน
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from tmd_plain.extract.provinces import PROVINCE_RE
from tmd_plain.prep.periods import find_date_phrases

Value = str | int | float


@dataclass(frozen=True)
class Fact:
    name: str
    value: Value
    source: str  # ข้อความต้นฉบับที่ให้ค่านี้ (สตริงย่อยของบรรทัด)
    line: int  # ลำดับบรรทัดในบล็อก (เริ่ม 0)


_NUM = r"\d+(?:\.\d+)?"
_RANGE = rf"(?P<lo>{_NUM})(?:\s*[-–]\s*(?P<hi>{_NUM}))?"
# PDF บางฉบับมีช่องว่างแทรก "องศาเซลเซี ยส"
_DEG = r"องศาเซลเซี\s?ยส"


def _num(text: str) -> int | float:
    return float(text) if "." in text else int(text)


def _range_facts(prefix: str, m: re.Match[str]) -> list[tuple[str, Value]]:
    lo = m.group("lo")
    hi = m.group("hi") or lo
    return [(f"{prefix}_low", _num(lo)), (f"{prefix}_high", _num(hi))]


Builder = Callable[[re.Match[str]], list[tuple[str, Value]]]


def _rain(m: re.Match[str]) -> list[tuple[str, Value]]:
    return [("rain_kind", m.group("kind")), *_range_facts("rain_area_pct", m)]


def _peak(m: re.Match[str]) -> list[tuple[str, Value]]:
    feel: list[tuple[str, Value]] = [("peak_feel", m.group("feel"))] if m.group("feel") else []
    return [("peak_place", m.group("place")), *feel, *_range_facts("peak_temp_min", m)]


def _temp(m: re.Match[str]) -> list[tuple[str, Value]]:
    which = "temp_min" if m.group("which") == "ต่ำสุด" else "temp_max"
    return _range_facts(which, m)


def _trend(m: re.Match[str]) -> list[tuple[str, Value]]:
    out: list[tuple[str, Value]] = [("temp_trend", m.group("trend"))]
    if m.group("lo"):
        out += _range_facts("temp_change", m)
    return out


def _wind(m: re.Match[str]) -> list[tuple[str, Value]]:
    out: list[tuple[str, Value]] = []
    if m.group("area"):
        out.append(("wind_area", m.group("area").strip()))
    return [*out, ("wind_dir", m.group("dir")), *_range_facts("wind_speed_kmh", m)]


def _wave(m: re.Match[str]) -> list[tuple[str, Value]]:
    where = m.group("where")
    prefix = "wave_offshore" if "ห่างฝั่ง" in where else "wave_storm" if "ฟ้าคะนอง" in where else "wave"
    return [(f"{prefix}_qualifier", m.group("qual")), *_range_facts(f"{prefix}_m", m)]


def _phrase(name: str) -> Builder:
    return lambda m: [(name, m.group(0))]


# ลำดับสำคัญ: รูปแบบที่ยาว/เจาะจงก่อน ช่วงที่จับแล้วจะไม่ถูกจับซ้ำ
_PATTERNS: list[tuple[re.Pattern[str], Builder]] = [
    (
        re.compile(
            rf"(?P<area>ตั้งแต่จังหวัด\s*\S+?\s*(?:ขึ้นมา|ลงไป)\s*:)?\s*ลม(?P<dir>ตะวันออกเฉียงเหนือ|ตะวันออกเฉียงใต้|"
            rf"ตะวันตกเฉียงเหนือ|ตะวันตกเฉียงใต้|ตะวันออก|ตะวันตก|เหนือ|ใต้|แปรปรวน)\s*ความเร็ว\s*{_RANGE}\s*กม\./ชม\."
        ),
        _wind,
    ),
    (
        re.compile(
            rf"บริเวณ(?P<place>ยอด(?:ดอย|ภู))(?P<feel>อากาศ\S*)?\s*อุณหภูมิต่ำสุด\s*{_RANGE}\s*{_DEG}"
        ),
        _peak,
    ),
    (re.compile(rf"อุณหภูมิ(?P<which>ต่ำสุด|สูงสุด)\s*{_RANGE}\s*{_DEG}"), _temp),
    (
        re.compile(rf"อุณหภูมิจะ(?P<trend>สูงขึ้น|ลดลง)(?:อีก)?(?:เล็กน้อย)?(?:\s*{_RANGE}\s*{_DEG})?"),
        _trend,
    ),
    (
        re.compile(rf"(?P<kind>ฝน(?:/ฝนฟ้าคะนอง|ฟ้าคะนอง)?)\s*ร้อยละ\s*{_RANGE}\s*ของพื้นที่"),
        _rain,
    ),
    (
        re.compile(
            rf"(?P<where>ห่างฝั่ง(?:คลื่น)?|บริเวณที่มีฝนฟ้าคะนอง(?:คลื่น)?|ทะเลมีคลื่น|คลื่น)\s*"
            rf"(?P<qual>สูงประมาณ|สูงมากกว่า|สูง|ต่ำกว่า)\s*{_RANGE}\s*เมตร"
        ),
        _wave,
    ),
    (re.compile(r"ฝนตกหนัก(?:ถึงหนักมาก|มาก)(?:บางแห่ง|บางพื้นที่|หลายพื้นที่)?"), _phrase("very_heavy_rain")),
    (re.compile(r"ฝนตกหนัก(?:บางแห่ง|บางพื้นที่|หลายพื้นที่)?"), _phrase("heavy_rain")),
    (re.compile(r"ลมกระโชกแรง(?:บางแห่ง)?"), _phrase("gusts")),
    (re.compile(r"ลูกเห็บตก(?:บางแห่ง)?"), _phrase("hail")),
    (re.compile(r"ฝนเล็กน้อย(?:บางแห่ง)?"), _phrase("light_rain")),
    (re.compile(r"ฝน(?:/ฝนฟ้าคะนอง|ฟ้าคะนอง)?(?:บางแห่ง|บางพื้นที่)"), _phrase("some_rain")),
    (re.compile(r"หมอก(?:บาง)?"), _phrase("fog")),
    (re.compile(r"อากาศ(?:เย็นถึงหนาว|หนาวเย็น|หนาว|เย็น)"), _phrase("cold")),
    (re.compile(r"ลมแรง"), _phrase("strong_wind")),
    (re.compile(r"เมฆ(?:เป็นส่วนมาก|บางส่วน)"), _phrase("cloud")),
    (re.compile(r"ทางตอน(?:บน|ล่าง)(?:ของภาค)?"), _phrase("area_part")),
    (PROVINCE_RE, _phrase("province")),
]


def _overlaps(span: tuple[int, int], taken: list[tuple[int, int]]) -> bool:
    return any(span[0] < b and a < span[1] for a, b in taken)


Pattern = tuple[re.Pattern[str], Builder]


def extract_line(text: str, line: int = 0, extra: Sequence[Pattern] = ()) -> list[Fact]:
    """ค่าทั้งหมดในบรรทัดเดียว เรียงตามตำแหน่งในบรรทัด.

    extra = รูปแบบเฉพาะชนิดเอกสาร (เช่น ลมเป็นนอตของพยากรณ์เดินเรือ) ลองก่อนรูปแบบกลาง
    """
    found: list[tuple[int, Fact]] = []
    taken: list[tuple[int, int]] = []
    for phrase, start, end in find_date_phrases(text):
        taken.append((phrase.start, phrase.end))
        found.append((phrase.start, Fact("period_text", phrase.text, phrase.text, line)))
        found.append((phrase.start, Fact("period_start", start.isoformat(), phrase.text, line)))
        found.append((phrase.start, Fact("period_end", end.isoformat(), phrase.text, line)))
    for pattern, build in (*extra, *_PATTERNS):
        for m in pattern.finditer(text):
            span = m.span()
            if _overlaps(span, taken):
                continue
            taken.append(span)
            source = m.group(0).strip()
            found += [(span[0], Fact(name, value, source, line)) for name, value in build(m)]
    found.sort(key=lambda t: t[0])
    return [f for _, f in found]


def extract_block(lines: Sequence[str], extra: Sequence[Pattern] = ()) -> list[Fact]:
    """ค่าของทุกบรรทัดในบล็อกภาค (บรรทัดที่ไม่มีค่าไม่ใช่ข้อผิดพลาด ต้องดูในรายงานความครอบคลุม)."""
    return [f for i, text in enumerate(lines) for f in extract_line(text, i, extra)]
