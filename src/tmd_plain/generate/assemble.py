"""ประกอบผลสรุปทั้งฉบับ (`Issue` ตามสัญญาข้อมูล) จากฉบับที่แยกภาคแล้ว."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from tmd_plain.config import load_config
from tmd_plain.contract import REGION_KEYS, DocType, Issue, Period, RegionSummary
from tmd_plain.extract.advice import Labeler, select_advice
from tmd_plain.extract.facts import extract_block
from tmd_plain.generate.templates import GenerateError, build_lines
from tmd_plain.prep.periods import parse_date_range, split_periods
from tmd_plain.prep.regions import ParsedIssue

BANGKOK = timezone(timedelta(hours=7))


@dataclass(frozen=True)
class IssueMeta:
    issue_id: str
    issued_at: datetime
    source_label: str


def issued_at_from_id(doc_type: DocType, issue_id: str) -> datetime:
    """รายวัน DDMMYYYYHHMM -> เวลาของรอบ; 7 วัน YYMMDD -> เที่ยงคืนของวันนั้น (ไม่มีเวลาในรหัส)."""
    if doc_type == "daily":
        return datetime.strptime(issue_id, "%d%m%Y%H%M").replace(tzinfo=BANGKOK)
    return datetime.strptime(issue_id, "%y%m%d").replace(tzinfo=BANGKOK)


_MONTHS_TH = (
    "มกราคม กุมภาพันธ์ มีนาคม เมษายน พฤษภาคม มิถุนายน กรกฎาคม สิงหาคม กันยายน ตุลาคม พฤศจิกายน ธันวาคม"
).split()


def default_source_label(doc_type: DocType, issue_id: str) -> str:
    """ป้ายวันที่เมื่อต้นฉบับไม่มีป้าย: รายวันตามรูปแบบหน้าเว็บ TMD, 7 วันเป็นวันที่ออกฉบับ (พ.ศ.)."""
    t = issued_at_from_id(doc_type, issue_id)
    day = f"{t.day} {_MONTHS_TH[t.month - 1]} {t.year + 543}"
    if doc_type == "daily":
        # เวลาในรหัสคือรอบ (เช่น 18.00) ไม่ใช่เวลาออกประกาศจริง (เช่น 17.00 น.) จึงเขียนว่า "รอบ"
        return f"ประจำวันที่ {day} รอบ {t.hour:02d}.{t.minute:02d} น."
    return f"ฉบับวันที่ {day}"


# หัว PDF ของ TMD (ดูได้จาก data/raw): "ประจำวันจันทร์ที่ 16 พฤศจิกายน พ.ศ. 2569" / "ออกประกาศเวลา 1700 น."
# บางฉบับมีช่องว่างก่อน "ที่" ("ประจำวันพฤหัสบดี ที่ 12 ...") วันที่หลังคำนำอ่านด้วยตัวอ่านเดียวกับช่วงวัน
_DAILY_DATE = re.compile(r"ประจำวัน\S*?\s*ที่")
_DAILY_TIME = re.compile(r"ออกประกาศเวลา\s*(\d{1,2})\.?(\d{2})\s*น")
_SEVENDAY_DATE = re.compile(r"ออกประกาศวัน\S*?\s*ที่")
META_HEADER_LINES = 15  # ผู้ลงนาม ชื่อหน่วยงาน ชื่อประกาศ วันที่ อยู่ในราว 10 บรรทัดแรก
# รหัสรอบ = เวลาออกประกาศ + 1 ชม. (ออก 23.00/05.00/11.00/17.00 -> รอบ 00/06/12/18 ตรงทั้ง 46 ฉบับใน data/raw)
ROUND_AFTER_ISSUE = timedelta(hours=1)


def _date_after(marker: re.Pattern[str], head: str) -> date | None:
    """วันที่ไทยตัวแรกในบรรทัดหลังคำนำ (ทนช่องว่างที่ PDF ทำหาย); ไม่พบหรือวันเป็นไปไม่ได้ = None."""
    m = marker.search(head)
    if m is None:
        return None
    found = parse_date_range(head[m.end() :].split("\n", 1)[0])
    return found[0] if found else None


def meta_from_text(doc_type: DocType, text: str) -> IssueMeta | None:
    """รหัสฉบับ เวลา และป้ายจากหัวเอกสารเอง (ไฟล์อัปโหลดไม่มีชื่อไฟล์/MANIFEST) หาไม่ได้ = None ไม่เดา."""
    head = "\n".join([ln for ln in text.splitlines() if ln.strip()][:META_HEADER_LINES])
    if doc_type == "sevenday":
        day = _date_after(_SEVENDAY_DATE, head)
        if day is None:
            return None
        issue_id = day.strftime("%y%m%d")
        return IssueMeta(
            issue_id,
            issued_at_from_id("sevenday", issue_id),
            default_source_label("sevenday", issue_id),
        )
    day, time_m = _date_after(_DAILY_DATE, head), _DAILY_TIME.search(head)
    if day is None or time_m is None:
        return None
    try:
        issued = datetime.combine(day, time(int(time_m.group(1)), int(time_m.group(2))))
    except ValueError:
        return None
    issue_id = (issued + ROUND_AFTER_ISSUE).strftime("%d%m%Y%H%M")
    # ป้ายแบบเดียวกับหน้าเว็บ TMD (หน้าหลักใช้ป้ายนี้) ตัวเลขทุกตัวมาจากหัว PDF
    label = f"ประจำวันที่ {issued.day} {_MONTHS_TH[issued.month - 1]} {issued.year + 543} {issued.hour:02d}.{issued.minute:02d} น."
    return IssueMeta(issue_id, issued_at_from_id("daily", issue_id), label)


def _region_summary(parsed: ParsedIssue, key: str) -> RegionSummary:
    block = parsed.regions[key]  # type: ignore[index]
    if parsed.doc_type == "daily":
        return RegionSummary(lines=build_lines(extract_block(block.lines), block.lines, "daily"))
    periods: list[Period] = []
    for pb in split_periods(block.lines, parsed.issue_range):
        if pb.start is None or pb.end is None:
            raise GenerateError(f"หาช่วงวันของบล็อก {key} ไม่ได้")
        try:
            lines = build_lines(extract_block(pb.lines), pb.lines, "sevenday")
        except GenerateError:
            # ช่วงที่มีแต่วลีวันที่ ไม่มีเนื้อหา ข้ามได้
            continue
        periods.append(Period(start=pb.start, end=pb.end, lines=lines))
    return RegionSummary(periods=periods)


def assemble_issue(parsed: ParsedIssue, meta: IssueMeta, label_of: Labeler) -> Issue:
    """7 ภาค (สรุป + คำแนะนำของภาค) + ข้อแนะนำทั่วไป; ไม่มีเวลาประมวลผลในผล (ผลซ้ำได้)."""
    advice = select_advice(parsed, label_of)
    regions = {}
    for key in REGION_KEYS:
        summary = _region_summary(parsed, key)
        regions[key] = summary.model_copy(update={"advice": advice.regional[key]})
    return Issue(
        issue_id=meta.issue_id,
        doc_type=parsed.doc_type,
        issued_at=meta.issued_at,
        source_label=meta.source_label,
        regions=regions,
        general_advice=advice.general,
        pipeline_version=load_config()["pipeline_version"],
    )
