"""อ่านชุดข้อมูลดิบใน data/raw ตาม MANIFEST.csv (ส่วน I/O ที่สคริปต์ใช้ร่วมกัน)."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

from tmd_plain.prep.extract import SourceDocument, document_from_pdf, document_from_txt


@dataclass(frozen=True)
class RawIssue:
    issue_id: str  # รายวัน DDMMYYYYHHMM, 7 วัน YYMMDD
    doc_type: str  # "daily" | "sevenday"
    role: str  # "display_test" | "train_pool"
    pdf: Path | None
    txt: Path | None
    label: str = ""  # ป้ายวันที่จาก MANIFEST เช่น "ประจำวันที่ 1 พฤศจิกายน 2569 17.00 น." (บางฉบับว่าง)

    def preferred(self) -> SourceDocument:
        """ข้อความจากหน้าเว็บก่อน (สะอาดกว่า PDF) ถ้าไม่มีค่อยใช้ PDF."""
        if self.txt is not None:
            return document_from_txt(self.txt.read_text(encoding="utf-8"))
        if self.pdf is not None:
            return document_from_pdf(self.pdf.read_bytes())
        raise FileNotFoundError(self.issue_id)


# ชนิดที่ไปป์ไลน์อ่านได้ตอนนี้ ไฟล์ชนิดอื่นที่เก็บไว้ล่วงหน้า (ADR 0015) ข้ามจนกว่าแผน 10-12 จะรองรับ
SUPPORTED_DOC_TYPES = frozenset({"daily", "sevenday"})
# บทบาทเดิมของไปป์ไลน์ ไฟล์ที่เก็บรอบ v2 (เช่น sample_v2) ยังไม่เข้าชุดฝึก/แสดงผลเดิม
PIPELINE_ROLES = frozenset({"display_test", "train_pool"})
# ฉบับรายวัน/7 วันที่ขึ้นเว็บ (11.6): ชุดเดิม + ที่เก็บรอบ v2 (archive_v2) · ชุดฝึก/วัดผลยังใช้ PIPELINE_ROLES เท่านั้น
WEB_ROLES = frozenset({"display_test", "train_pool", "archive_v2"})
# ป้ายของฉบับที่เก็บรอบ v2 ใช้เมื่อเป็นป้ายวันที่เท่านั้น (ฉบับ 7 วันเก็บป้ายรวมๆ "พยากรณ์อากาศ 7 วัน")
_DATE_LABEL = re.compile(r"^(?:ประจำวันที่|ฉบับวันที่|ออกประกาศ)\s+\d")


def load_manifest(raw_dir: Path, roles: frozenset[str] = PIPELINE_ROLES) -> list[RawIssue]:
    """รวมแถว MANIFEST เป็นฉบับละหนึ่งรายการ เรียงตามชนิดแล้วตามรหัสฉบับ (roles ไม่ระบุ = ชุดเดิมของไปป์ไลน์)."""
    rows: dict[tuple[str, str], dict[str, object]] = {}
    with (raw_dir / "MANIFEST.csv").open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["type"] not in SUPPORTED_DOC_TYPES or row["role"] not in roles:
                continue
            key = (row["type"], row["issue_id"])
            item = rows.setdefault(
                key, {"role": row["role"], "pdf": None, "txt": None, "label": ""}
            )
            item[row["format"]] = raw_dir / row["file"]
            label = row.get("label") or ""
            # ชุดเดิมใช้ป้ายตามที่เก็บ (ผลเดิมเท่าเดิมทุกไบต์) ชุดใหม่กรองเฉพาะป้ายวันที่
            if label and (row["role"] in PIPELINE_ROLES or _DATE_LABEL.match(label)):
                item["label"] = label
    issues = [
        RawIssue(
            issue_id=k[1],
            doc_type=k[0],
            role=str(v["role"]),
            pdf=v["pdf"],  # type: ignore[arg-type]
            txt=v["txt"],  # type: ignore[arg-type]
            label=str(v["label"]),
        )
        for k, v in rows.items()
    ]
    return sorted(issues, key=lambda i: (i.doc_type, issue_sort_key(i)))


@dataclass(frozen=True)
class RawShipping:
    issue_id: str  # รหัสรอบจากหน้าเว็บ DDMMYYYYHHMM
    txt: Path


def load_shipping(raw_dir: Path) -> list[RawShipping]:
    """พยากรณ์เดินเรือทุกฉบับที่เก็บ (แผน 11.1; มีแต่ข้อความหน้าเว็บ ไม่มี PDF) เรียงตามเวลา."""
    with (raw_dir / "MANIFEST.csv").open(encoding="utf-8-sig", newline="") as fh:
        rows = [
            RawShipping(row["issue_id"], raw_dir / row["file"])
            for row in csv.DictReader(fh)
            if row["type"] == "shipping" and row["format"] == "txt"
        ]
    return sorted(rows, key=lambda r: round_sort_key(r.issue_id))


@dataclass(frozen=True)
class RawWarning:
    issue_id: str  # "<ปี พ.ศ.>_<เลขประกาศ>" เช่น 2569_315
    txt: Path


def _warning_sort_key(issue_id: str) -> tuple[int, int]:
    year, number = issue_id.split("_")
    return int(year), int(number)


def load_warnings(raw_dir: Path) -> list[RawWarning]:
    """ประกาศเตือนภัยทุกฉบับที่เก็บ (แผน 11.4; ใช้ข้อความหน้าเว็บ) เรียงตามเลขประกาศ."""
    with (raw_dir / "MANIFEST.csv").open(encoding="utf-8-sig", newline="") as fh:
        rows = [
            RawWarning(row["issue_id"], raw_dir / row["file"])
            for row in csv.DictReader(fh)
            if row["type"] == "warning" and row["format"] == "txt"
        ]
    return sorted(rows, key=lambda r: _warning_sort_key(r.issue_id))


@dataclass(frozen=True)
class RawWeekly:
    issue_id: str  # รหัสรอบจากหน้าเว็บ DDMMYYYYHHMM (ชั่วโมงอาจต่างจากเวลาออกประกาศ 4/100 ฉบับ)
    txt: Path


def load_weekly(raw_dir: Path) -> list[RawWeekly]:
    """สรุปรายสัปดาห์ทุกฉบับที่เก็บ (แผน 11.5; ใช้ข้อความหน้าเว็บ PDF เป็นแผนที่คนละเลย์เอาต์) เรียงตามเวลา."""
    with (raw_dir / "MANIFEST.csv").open(encoding="utf-8-sig", newline="") as fh:
        rows = [
            RawWeekly(row["issue_id"], raw_dir / row["file"])
            for row in csv.DictReader(fh)
            if row["type"] == "weekly" and row["format"] == "txt"
        ]
    return sorted(rows, key=lambda r: round_sort_key(r.issue_id))


def round_sort_key(issue_id: str) -> str:
    """รหัสรอบ DDMMYYYYHHMM -> YYYYMMDDHHMM (เรียงตามเวลา)."""
    return issue_id[4:8] + issue_id[2:4] + issue_id[0:2] + issue_id[8:12]


def issue_sort_key(issue: RawIssue) -> str:
    """เรียงตามเวลา: รายวัน DDMMYYYYHHMM -> YYYYMMDDHHMM, 7 วัน YYMMDD -> 20YYMMDD."""
    if issue.doc_type == "daily":
        return round_sort_key(issue.issue_id)
    return "20" + issue.issue_id
