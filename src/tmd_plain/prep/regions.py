"""แยกฉบับพยากรณ์เป็นย่อหน้าภาพรวม ข้อควรระวัง และบล็อก 7 ภาค (รองรับข้อความหน้าเว็บและ PDF).

โครงของแต่ละแบบอยู่ใน .claude/skills/thai-text-handling/references/known-defects.md หัวข้อ 2b
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from tmd_plain.contract import DocType, ErrorCode, RegionKey
from tmd_plain.prep.clean import join_wrapped
from tmd_plain.prep.doctype import detect_doc_type
from tmd_plain.prep.extract import SourceDocument, SourceKind
from tmd_plain.prep.periods import parse_date_range

# หัวข้อภาคเรียงตามลำดับในฉบับ (ฉบับ 7 วันจาก PDF ไม่มีคำว่า "ภาค")
REGION_HEADINGS: tuple[tuple[RegionKey, re.Pattern[str]], ...] = (
    ("north", re.compile(r"^(ภาค)?เหนือ(?=\s|$)")),
    ("northeast", re.compile(r"^(ภาค)?ตะวันออกเฉียงเหนือ(?=\s|$)")),
    ("central", re.compile(r"^(ภาค)?กลาง(?=\s|$)")),
    ("east", re.compile(r"^(ภาค)?ตะวันออก(?=\s|$)")),
    ("south_east_coast", re.compile(r"^(ภาค)?ใต้\s*\(?ฝั่งตะวันออก\)?")),
    ("south_west_coast", re.compile(r"^(ภาค)?ใต้\s*\(?ฝั่งตะวันตก\)?")),
    ("bangkok_vicinity", re.compile(r"^กรุงเทพ(มหานคร|ฯ)?(\s*และปริมณฑล)?")),
)
# บรรทัดที่สองของหัวข้อภาคใน PDF
_HEADING_TAIL = re.compile(r"^(รวมทั้งชายฝั่ง|\(ฝั่งอ่าวไทย\)|\(ฝั่งอันดามัน\)|และปริมณฑล)\s*")
_END_PREFIXES = (
    "หมายเหตุ",
    "ออกประกาศ",
    "ผู้พยากรณ์",
    "ผู้อำนวยการ",
    "นาย",
    "นาง",
    "ส่วนพยากรณ์อากาศ",
    "สอบถาม",
)
# ย่อหน้าใหม่ใน PDF (PDF ไม่เก็บการขึ้นย่อหน้า จึงเดาจากคำขึ้นต้นบรรทัด)
_PARA_OPENERS = ("ทั้งนี้", "สำหรับ", "อนึ่ง")
_DATE_LINE = re.compile(r"^\d{1,2}\s*([-–]\s*\d{1,2}\s*)?[ก-๙.]+\s*(พ\.ศ\.)?\s*\d{4}$")
_NUMERIC_LINE = re.compile(r"^\d+(\.\d+)?$")


class PrepError(ValueError):
    """เตรียมข้อความไม่สำเร็จ code ตรงกับรหัสข้อผิดพลาดในสัญญาข้อมูล."""

    def __init__(self, code: ErrorCode, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code: ErrorCode = code


@dataclass(frozen=True)
class RegionBlock:
    key: RegionKey
    lines: tuple[str, ...]  # เนื้อหาไม่รวมหัวข้อภาค และตัดตารางอุณหภูมิรายจังหวัดของ PDF ออกแล้ว


@dataclass(frozen=True)
class ParsedIssue:
    doc_type: DocType
    source_kind: SourceKind
    overview: tuple[str, ...]  # ย่อหน้า
    caution: tuple[str, ...]  # ย่อหน้า "ข้อควรระวัง" (เฉพาะ 7 วัน)
    regions: dict[RegionKey, RegionBlock]
    issue_range: tuple[date, date] | None  # ช่วงของฉบับ 7 วัน


def _find(lines: list[str], prefixes: tuple[str, ...], start: int = 0) -> int | None:
    return next((i for i in range(start, len(lines)) if lines[i].startswith(prefixes)), None)


def _strip_prefix(line: str, prefix: str) -> str:
    return line[len(prefix) :].strip() if line.startswith(prefix) else line


def _paragraphs(
    lines: list[str], kind: SourceKind, indented: tuple[bool, ...] | list[bool] = ()
) -> tuple[str, ...]:
    """แบ่งย่อหน้า.

    หน้าเว็บ: ย่อหน้าจริงขึ้นต้นด้วยการเยื้อง บรรทัดที่ไม่เยื้องต่อจากย่อหน้าก่อนคือหน้าเว็บตัดกลางประโยค
    PDF: ไม่เก็บการขึ้นย่อหน้า จึงต่อบรรทัดที่ขาดและเริ่มย่อหน้าใหม่ที่คำขึ้นต้น (_PARA_OPENERS)
    """
    flags = list(indented) if len(indented) == len(lines) else [True] * len(lines)
    kept = [(ln, f) for ln, f in zip(lines, flags, strict=True) if ln and not _DATE_LINE.match(ln)]
    paras: list[list[str]] = []
    for line, is_indented in kept:
        if kind == "txt":
            # บางฉบับไม่เยื้องย่อหน้า "สำหรับ..." จึงให้คำขึ้นต้นย่อหน้าเริ่มย่อหน้าใหม่ด้วย
            new_para = not paras or is_indented or line.startswith(_PARA_OPENERS)
        else:
            new_para = not paras or line.startswith(_PARA_OPENERS)
        if new_para:
            paras.append([line])
        else:
            paras[-1].append(line)
    return tuple(join_wrapped(p) for p in paras)


def _drop_station_table(lines: list[str]) -> list[str]:
    """ตัดตารางอุณหภูมิรายจังหวัดท้ายบล็อกของ PDF รายวัน: ชื่อจังหวัด N บรรทัด ตามด้วยตัวเลข 2N บรรทัด."""
    k = 0
    while k < len(lines) and _NUMERIC_LINE.match(lines[-1 - k]):
        k += 1
    if k < 2 or k % 2:
        return lines
    names = lines[len(lines) - k - k // 2 : len(lines) - k]
    if len(names) == k // 2 and all(" " not in n and not _NUMERIC_LINE.match(n) for n in names):
        return lines[: len(lines) - k - k // 2]
    return lines


def split_regions(lines: list[str], start: int) -> dict[RegionKey, RegionBlock]:
    """หาหัวข้อ 7 ภาคตามลำดับตั้งแต่ start; ไม่ครบโยน PrepError(extract_failed)."""
    heads: list[tuple[RegionKey, int, str]] = []
    pos = start
    for key, rx in REGION_HEADINGS:
        hit = next(((i, m) for i in range(pos, len(lines)) if (m := rx.match(lines[i]))), None)
        if hit is None:
            raise PrepError("extract_failed", f"ไม่พบหัวข้อภาค {key}")
        i, m = hit
        heads.append((key, i, lines[i][m.end() :].strip()))
        pos = i + 1
    end = _find(lines, _END_PREFIXES, heads[-1][1] + 1) or len(lines)
    blocks: dict[RegionKey, RegionBlock] = {}
    for n, (key, i, rest) in enumerate(heads):
        stop = heads[n + 1][1] if n + 1 < len(heads) else end
        body = ([rest] if rest else []) + lines[i + 1 : stop]
        while body and _HEADING_TAIL.match(body[0]):
            body[0] = _HEADING_TAIL.sub("", body[0], count=1)
            if not body[0]:
                body.pop(0)
        blocks[key] = RegionBlock(key=key, lines=tuple(_drop_station_table(body)))
    return blocks


def parse_issue(doc: SourceDocument) -> ParsedIssue:
    """แยกฉบับเป็นส่วนต่างๆ; ไม่ใช่พยากรณ์ที่รองรับโยน PrepError(unsupported_document)."""
    doc_type = detect_doc_type(doc.text)
    if doc_type not in ("daily", "sevenday"):
        raise PrepError("unsupported_document", "ไม่พบคำบอกชนิดพยากรณ์รายวัน/7 วัน")
    lines = doc.text.split("\n")
    caution: tuple[str, ...] = ()
    issue_range = None
    if doc_type == "daily":
        if doc.kind == "txt":
            ov_start = (_find(lines, ("ลักษณะอากาศทั่วไป",)) or 0) + 1
            ov_end = _find(lines, ("ออกประกาศ",), ov_start)
        else:
            ov_start = (_find(lines, ("ออกประกาศเวลา",)) or 0) + 1
            ov_end = _find(lines, ("พยากรณ์อากาศสำหรับประเทศไทย",), ov_start)
        reg_start = _find(lines, ("พยากรณ์อากาศสำหรับประเทศไทย",))
        if ov_end is None or reg_start is None:
            raise PrepError("extract_failed", "ไม่พบส่วนภาพรวมหรือส่วนรายภาค")
        overview = _paragraphs(lines[ov_start:ov_end], doc.kind, doc.indented[ov_start:ov_end])
    else:
        if doc.kind == "txt":
            ov_start = _find(lines, ("คาดหมายอากาศทั่วไป",))
            cau_start = _find(lines, ("ข้อควรระวัง",))
            cau_end = _find(lines, ("ออกประกาศ",), (cau_start or 0) + 1)
            reg_start = _find(lines, ("คาดหมายอากาศรายภาค",))
            head = lines[(ov_start or 0) + 1] if ov_start is not None else ""
        else:
            ov_start = _find(lines, ("คาดหมายลักษณะอากาศ",))
            cau_start = _find(lines, ("ข้อควรระวัง",))
            cau_end = reg_start = _find(lines, ("สภาวะอากาศ",))
            head = next((ln for ln in lines if ln.startswith("ระหว่างช่วงวันที่")), "")
        if None in (ov_start, cau_start, cau_end, reg_start):
            raise PrepError("extract_failed", "ไม่พบส่วนภาพรวม ข้อควรระวัง หรือส่วนรายภาค")
        ov = lines[ov_start:cau_start]  # type: ignore[misc]
        ov[0] = _strip_prefix(_strip_prefix(ov[0], "คาดหมายลักษณะอากาศ"), "คาดหมายอากาศทั่วไป")
        cau = lines[cau_start:cau_end]  # type: ignore[misc]
        cau[0] = _strip_prefix(cau[0], "ข้อควรระวัง")
        overview = _paragraphs(ov, doc.kind, doc.indented[ov_start:cau_start])  # type: ignore[misc]
        caution = _paragraphs(cau, doc.kind, doc.indented[cau_start:cau_end])  # type: ignore[misc]
        issue_range = parse_date_range(head)
    regions = split_regions(lines, reg_start + 1)
    return ParsedIssue(
        doc_type=doc_type,
        source_kind=doc.kind,
        overview=overview,
        caution=caution,
        regions=regions,
        issue_range=issue_range,
    )
