"""แยกโครงประกาศเตือนภัย: หัวเรื่อง ช่วงที่มีผล ฉบับที่/เลขประกาศ เนื้อหา วันเวลาประกาศ ฉบับต่อไป.

โครงจริง (155 ฉบับที่เก็บใน 9.2 ทั้งข้อความหน้าเว็บและ PDF):
  ประกาศกรมอุตุนิยมวิทยา / เรื่อง ... (อาจสองบรรทัด) / (มีผลกระทบ...) (ไม่มี 1 ฉบับ) / ฉบับที่ N (X/ปี) / -----
  เนื้อหา / ประกาศ ณ วันที่ ... เวลา HH.MM น. / ฉบับต่อไป ... หรือ "ฉบับสุดท้าย" / (ลงชื่อ) ...
PDF มีบล็อกผู้พยากรณ์ก่อนหัวประกาศ และตารางจังหวัดรายวันหลังลงชื่อ ใช้เฉพาะส่วนหัวถึงบรรทัดประกาศ ณ วันที่
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from tmd_plain.prep.clean import join_wrapped
from tmd_plain.prep.periods import parse_date_range

BANGKOK = timezone(timedelta(hours=7))
HEADER = "ประกาศกรมอุตุนิยมวิทยา"
_SPACE = re.compile(r"\s+")
_NUMBER_LINE = re.compile(r"^ฉบับที่\s*(?P<series>\d+)\s*\(\s*(?P<no>\d+)\s*/\s*(?P<year>\d{4})\s*\)")
_EFFECT_LINE = re.compile(r"^\(\s*(?P<text>มีผล[^)]*?)\s*\)$")
_DASHES = re.compile(r"^-{5,}$")
_ISSUED = re.compile(r"^ประกาศ\s*ณ\s*วันที่(?P<date>.+?)เวลา\s*(?P<h>\d{1,2})[.:](?P<m>\d{2})\s*น\.")
_NEXT = re.compile(r"ฉบับต่อไปในวันที่(?P<date>.+?)เวลา\s*(?P<h>\d{1,2})[.:](?P<m>\d{2})\s*น\.")
_FINAL = re.compile(r"ฉบับสุดท้าย")
_SIGN = re.compile(r"^\(ลงชื่อ\)")


class WarningParseError(ValueError):
    """โครงไม่ตรงประกาศเตือนภัย (ไม่เดาค่า)."""


@dataclass(frozen=True)
class ParsedWarning:
    title: str
    # ข้อความในวงเล็บคำต่อคำ เช่น "มีผลกระทบจนถึงวันที่ 30 สิงหาคม 2569" (ไม่มี = None)
    effect_text: str | None
    series_no: int
    notice_no: str
    issued_at: datetime
    issued_line: str
    next_issue_at: datetime | None
    # บรรทัดฉบับต่อไป/ฉบับสุดท้ายคำต่อคำ (ไม่มี = "")
    next_line: str
    final: bool
    header_lines: tuple[str, ...]
    paragraphs: tuple[str, ...]

    @property
    def issue_id(self) -> str:
        number, year = self.notice_no.split("/")
        return f"{year}_{number}"

    def body(self) -> str:
        return "\n".join(self.paragraphs)


def norm(text: str) -> str:
    return _SPACE.sub("", text)


def _datetime(date_text: str, hour: str, minute: str) -> datetime | None:
    found = parse_date_range(date_text)
    if found is None:
        return None
    day: date = found[0]
    try:
        return datetime.combine(day, time(int(hour), int(minute))).replace(tzinfo=BANGKOK)
    except ValueError:
        return None


def _paragraphs(lines: list[str]) -> tuple[str, ...]:
    # ทั้งหน้าเว็บและ PDF ต่อเนื้อหาเป็นก้อนเดียวแล้วให้ split_units/clauses ตัดเอง:
    # หน้าเว็บก็ตัดบรรทัดกลางประโยคได้ (เช่น "เรือเล็กบริเวณอ่าวไทยตอนล่าง" / "ควรงดออกจากฝั่ง...")
    # และสองแหล่งได้หน่วยแบบเดียวกัน
    joined = join_wrapped(lines)
    return (joined,) if joined else ()


def parse_warning(text: str) -> ParsedWarning:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    try:
        start = lines.index(HEADER)
    except ValueError as exc:
        raise WarningParseError("ไม่พบหัว ประกาศกรมอุตุนิยมวิทยา") from exc
    number_at = next((i for i in range(start, len(lines)) if _NUMBER_LINE.match(lines[i])), None)
    if number_at is None:
        raise WarningParseError("ไม่พบบรรทัด ฉบับที่ N (เลข/ปี)")
    head = lines[start + 1 : number_at]
    if not head or not head[0].startswith("เรื่อง"):
        raise WarningParseError("ไม่พบบรรทัด เรื่อง")
    effect_text: str | None = None
    title_lines = head
    effect = _EFFECT_LINE.match(head[-1])
    if effect:
        effect_text = effect.group("text")
        title_lines = head[:-1]
    title = join_wrapped(title_lines)[len("เรื่อง") :].strip()
    if not title:
        raise WarningParseError("หัวเรื่องว่าง")
    m = _NUMBER_LINE.match(lines[number_at])
    assert m is not None
    body_start = number_at + 1
    if body_start < len(lines) and _DASHES.match(lines[body_start]):
        body_start += 1
    issued_at_idx = next(
        (i for i in range(body_start, len(lines)) if _ISSUED.match(lines[i])), None
    )
    if issued_at_idx is None:
        raise WarningParseError("ไม่พบบรรทัด ประกาศ ณ วันที่")
    im = _ISSUED.match(lines[issued_at_idx])
    assert im is not None
    issued_at = _datetime(im.group("date"), im.group("h"), im.group("m"))
    if issued_at is None:
        raise WarningParseError("อ่านวันเวลาประกาศไม่ได้")
    after = lines[issued_at_idx + 1 : issued_at_idx + 4]
    next_line = next((ln for ln in after if "ฉบับต่อไป" in ln or _FINAL.search(ln)), "")
    next_issue_at: datetime | None = None
    nm = _NEXT.search(next_line)
    if nm:
        next_issue_at = _datetime(nm.group("date"), nm.group("h"), nm.group("m"))
    body = [ln for ln in lines[body_start:issued_at_idx] if not _SIGN.match(ln)]
    paragraphs = _paragraphs(body)
    if not paragraphs:
        raise WarningParseError("ไม่มีเนื้อหาประกาศ")
    return ParsedWarning(
        title=title,
        effect_text=effect_text,
        series_no=int(m.group("series")),
        notice_no=f"{int(m.group('no'))}/{m.group('year')}",
        issued_at=issued_at,
        issued_line=lines[issued_at_idx],
        next_issue_at=next_issue_at,
        next_line=next_line,
        final=bool(_FINAL.search(next_line)),
        header_lines=tuple(lines[start:body_start]),
        paragraphs=paragraphs,
    )


def effect_dates(effect_text: str | None) -> tuple[date | None, date | None]:
    """ช่วงที่มีผลจากข้อความคำต่อคำ: "จนถึง" = มีแต่วันสิ้นสุด, "ตั้งแต่" วันเดียว = มีแต่วันเริ่ม, ช่วง = ทั้งคู่."""
    if not effect_text:
        return None, None
    found = parse_date_range(effect_text)
    if found is None:
        return None, None
    first, last = found
    if "จนถึง" in effect_text:
        return None, last
    if first == last and "ตั้งแต่" in effect_text:
        return first, None
    return first, last
