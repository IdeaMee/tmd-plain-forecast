"""แม่แบบประโยคภาษาง่ายจากค่าที่ดึงได้ (ขั้น 3): หนึ่ง SummaryLine ต่อชนิด (ลม/คลื่นแยกตามเขตลม).

กติกา (สเปกหัวข้อ 4 + ADR 0013):
- ตัวเลขและชื่อจังหวัดมาจากค่าใน facts ของบรรทัดต้นฉบับเท่านั้น
- ค่าที่คำนวณ (ร้อยละพื้นที่ -> ราว N ใน 10 ส่วน) อยู่ในวงเล็บหลังตัวเลขต้นฉบับ และเก็บสูตรใน facts
- คำอธิบายระดับใช้อภิธานจากหมายเหตุของ TMD เท่านั้น
- "ร้อยละ N ของพื้นที่" คือสัดส่วนพื้นที่ ห้ามเขียนเป็นโอกาส/ความน่าจะเป็น
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from tmd_plain.contract import DocType, FactValue, LineKind, SummaryLine
from tmd_plain.extract.facts import Fact, Value
from tmd_plain.generate.glossary import cold_terms, glossary, rain_terms

TENTHS_FORMULA = "rain_area_tenths = floor(rain_area_pct / 10 + 0.5)"

_KIND_OF_PREFIX: list[tuple[str, LineKind]] = [
    ("rain_", "rain"),
    ("heavy_rain", "rain"),
    ("very_heavy_rain", "rain"),
    ("light_rain", "rain"),
    ("some_rain", "rain"),
    ("gusts", "rain"),
    ("hail", "rain"),
    ("province", "rain"),
    ("temp_", "temperature"),
    ("peak_", "temperature"),
    ("cold", "temperature"),
    ("wind_", "wind"),
    ("strong_wind", "wind"),
    ("wave", "wave"),
    ("fog", "fog"),
    ("cloud", "other"),
]
_ORDER: tuple[LineKind, ...] = ("rain", "temperature", "wind", "wave", "fog", "other")
_RAIN_PLAIN = {"ฝน/ฝนฟ้าคะนอง": "ฝนหรือฝนฟ้าคะนอง"}
_WAVE_QUAL = {"สูง": "สูง", "สูงประมาณ": "สูงราว", "สูงมากกว่า": "สูงกว่า", "ต่ำกว่า": "ต่ำกว่า"}
_WAVE_WHERE = {
    "wave": "ทะเลมีคลื่น",
    "wave_offshore": "ห่างฝั่งคลื่น",
    "wave_storm": "บริเวณที่มีฝนฟ้าคะนองคลื่น",
}


class GenerateError(ValueError):
    """บล็อกภาคที่สร้างสรุปไม่ได้ (ไม่มีค่าใดเลย) ห้ามเดา."""


def kind_of(name: str) -> LineKind | None:
    for prefix, kind in _KIND_OF_PREFIX:
        if name.startswith(prefix):
            return kind
    return None  # period_*, area_part: ตามส่วนที่อยู่ก่อนหน้า


def _num(v: Value) -> str:
    return str(v)


def _range(lo: Value, hi: Value) -> str:
    return _num(lo) if lo == hi else f"{_num(lo)}-{_num(hi)}"


def _tenths(pct: Value) -> int:
    return int(float(pct) / 10 + 0.5)


def _join_names(names: list[str]) -> str:
    if len(names) == 1:
        return names[0]
    return " ".join(names[:-1]) + " และ" + names[-1]


@dataclass
class _Group:
    kind: LineKind
    area: str = ""
    facts: list[Fact] = field(default_factory=list)


def _group(facts: Sequence[Fact]) -> list[_Group]:
    """แบ่งค่าเป็นกลุ่มตามชนิด ลม/คลื่นแยกตามเขตลม ค่าที่ไม่มีชนิดตามกลุ่มก่อนหน้าในบรรทัดเดียวกัน."""
    groups: dict[tuple[LineKind, str], _Group] = {}
    area = ""
    prev: tuple[int, LineKind] | None = None
    first_in_line: dict[int, str] = {}
    for f in facts:
        first_in_line.setdefault(f.line, f.name)
        if f.name == "wind_area":
            area = str(f.value).rstrip(":").strip()
        kind = kind_of(f.name)
        if kind is None:
            # วลีช่วงวันที่ขึ้นต้นบรรทัดเป็นหัวช่วง (แยกไว้แล้ว) ไม่ใส่ซ้ำ
            if (
                f.name.startswith("period_")
                and first_in_line[f.line] == "period_text"
                and (prev is None or prev[0] != f.line)
            ):
                continue
            kind = prev[1] if prev and prev[0] == f.line else "rain"
        key = (kind, area if kind in ("wind", "wave") else "")
        groups.setdefault(key, _Group(kind, key[1])).facts.append(f)
        prev = (f.line, kind)
    return sorted(groups.values(), key=lambda g: _ORDER.index(g.kind))


def facts_dict(facts: list[Fact]) -> dict[str, FactValue]:
    out: dict[str, FactValue] = {}
    for f in facts:
        if f.name in out:
            old = out[f.name]
            out[f.name] = [*(old if isinstance(old, list) else [str(old)]), str(f.value)]
        elif f.name == "province":
            out[f.name] = [str(f.value)]
        else:
            out[f.name] = f.value
    return out


def _with_glossary(phrase: str, terms: list[str], gl: dict[str, str], used: list[str]) -> str:
    # คำเดียวกับวลีไม่ต้องพูดซ้ำ: "อากาศเย็น (คือ ...)"
    notes = [
        f"คือ {gl[t]}" if t == phrase else f"{t} คือ {gl[t]}"
        for t in terms
        if t in gl and t not in used
    ]
    used += [t for t in terms if t in gl and t not in used]
    return f"{phrase} ({', '.join(notes)})" if notes else phrase


def _rain_text(
    g: _Group, lines: Sequence[str], gl: dict[str, str], used: list[str], area_word: str
) -> str:
    parts: list[str] = []
    by: dict[str, Value] = {}
    i = 0
    facts = g.facts
    while i < len(facts):
        f = facts[i]
        by[f.name] = f.value
        if f.name == "rain_area_pct_high":
            kind = str(by.get("rain_kind", "ฝน"))
            lo, hi = by["rain_area_pct_low"], f.value
            tenths = _range(_tenths(lo), _tenths(hi))
            parts.append(
                f"มี{_RAIN_PLAIN.get(kind, kind)}ร้อยละ {_range(lo, hi)} ของพื้นที่ (ราว {tenths} ใน 10 ส่วนของ{area_word})"
            )
        elif f.name == "province":
            names = [str(f.value)]
            while i + 1 < len(facts) and facts[i + 1].name == "province":
                i += 1
                names.append(str(facts[i].value))
            lead = "ส่วนมากที่จังหวัด" if "ส่วนมาก" in lines[f.line] else "บริเวณจังหวัด"
            parts.append(f"{lead}{_join_names(names)}")
        elif f.name in ("heavy_rain", "very_heavy_rain", "light_rain"):
            parts.append(_with_glossary(f"มี{f.value}", rain_terms(str(f.value)), gl, used))
        elif f.name in ("some_rain", "gusts", "hail"):
            parts.append(f"มี{f.value}")
        elif f.name in ("area_part", "period_text"):
            parts.append(str(f.value))
        i += 1
    return " ".join(parts)


def _temperature_text(g: _Group, gl: dict[str, str], used: list[str]) -> str:
    v = {f.name: f.value for f in g.facts}
    parts: list[str] = []
    for f in g.facts:
        if f.name == "cold":
            parts.append(_with_glossary(str(f.value), cold_terms(str(f.value)), gl, used))
        elif f.name == "temp_trend":
            change = (
                f" {_range(v['temp_change_low'], v['temp_change_high'])} องศาเซลเซียส"
                if "temp_change_low" in v
                else ""
            )
            parts.append(f"อุณหภูมิจะ{f.value}{change}")
        elif f.name == "temp_min_high":
            parts.append(f"อุณหภูมิต่ำสุด {_range(v['temp_min_low'], f.value)} องศาเซลเซียส")
        elif f.name == "temp_max_high":
            lead = "สูงสุด" if "temp_min_high" in v else "อุณหภูมิสูงสุด"
            parts.append(f"{lead} {_range(v['temp_max_low'], f.value)} องศาเซลเซียส")
        elif f.name == "peak_temp_min_high":
            feel = str(v.get("peak_feel", ""))
            head = f"บน{v['peak_place']}" + (
                f" {_with_glossary(feel, cold_terms(feel), gl, used)}" if feel else ""
            )
            parts.append(f"{head} ต่ำสุด {_range(v['peak_temp_min_low'], f.value)} องศาเซลเซียส")
        elif f.name in ("area_part", "period_text"):
            parts.append(str(f.value))
    return " ".join(parts)


def _wind_text(g: _Group) -> str:
    v = {f.name: f.value for f in g.facts}
    parts: list[str] = []
    if g.area:
        parts.append(f"{g.area}:")
    if "wind_dir" in v:
        direction = "ลมแปรปรวน" if v["wind_dir"] == "แปรปรวน" else f"ลมพัดจากทิศ{v['wind_dir']}"
        speed = _range(v["wind_speed_kmh_low"], v["wind_speed_kmh_high"])
        if "wind_speed_kt_low" in v:
            # พยากรณ์เดินเรือให้ทั้งนอตและ กม./ชม. ตามต้นฉบับ (ไม่แปลงหน่วยเอง)
            knots = _range(v["wind_speed_kt_low"], v["wind_speed_kt_high"])
            parts.append(f"{direction} ความเร็ว {knots} นอต ({speed} กม./ชม.)")
        else:
            parts.append(f"{direction} ความเร็ว {speed} กม./ชม.")
    if "strong_wind" in v:
        parts.append("มีลมแรง")
    return " ".join(parts)


def _wave_text(g: _Group) -> str:
    v = {f.name: f.value for f in g.facts}
    parts: list[str] = [f"{g.area}:"] if g.area else []
    for prefix, where in _WAVE_WHERE.items():
        if f"{prefix}_m_low" in v:
            qual = _WAVE_QUAL.get(str(v[f"{prefix}_qualifier"]), str(v[f"{prefix}_qualifier"]))
            parts.append(
                f"{where}{qual} {_range(v[f'{prefix}_m_low'], v[f'{prefix}_m_high'])} เมตร"
            )
    return " ".join(parts)


def build_lines(
    facts: Sequence[Fact],
    lines: Sequence[str],
    doc_type: DocType,
    *,
    gl: dict[str, str] | None = None,
    area_word: str = "พื้นที่ภาค",
) -> list[SummaryLine]:
    """ค่าของบล็อก (หรือของช่วงวัน) -> ประโยคสรุปเรียงตามชนิด ฝน อุณหภูมิ ลม คลื่น หมอก อื่นๆ.

    gl = อภิธานที่ใช้ (ไม่ระบุ = ของชนิดนั้นตามหมายเหตุ TMD) · area_word = คำเรียกพื้นที่ในวงเล็บของร้อยละ
    """
    gl = glossary(doc_type) if gl is None else gl
    out: list[SummaryLine] = []
    for g in _group(facts):
        used: list[str] = []
        if g.kind == "rain":
            text = _rain_text(g, lines, gl, used, area_word)
        elif g.kind == "temperature":
            text = _temperature_text(g, gl, used)
        elif g.kind == "wind":
            text = _wind_text(g)
        elif g.kind == "wave":
            text = _wave_text(g)
        else:
            text = " ".join(f"มี{f.value}" for f in g.facts if f.name in ("fog", "cloud"))
        if not text.strip():
            continue
        facts_out = facts_dict(g.facts)
        for side in ("low", "high"):
            pct = facts_out.get(f"rain_area_pct_{side}")
            if isinstance(pct, list):
                facts_out[f"rain_area_tenths_{side}"] = [str(_tenths(x)) for x in pct]
            elif pct is not None:
                facts_out[f"rain_area_tenths_{side}"] = _tenths(pct)  # type: ignore[arg-type]
        if "rain_area_pct_low" in facts_out:
            facts_out["derived_formula"] = TENTHS_FORMULA
        if used:
            facts_out["glossary_terms"] = used
        out.append(SummaryLine(kind=g.kind, text=text, facts=facts_out))
    if not out:
        raise GenerateError("ไม่มีค่าที่ดึงได้ในบล็อกนี้")
    return out
