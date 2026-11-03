"""อ่านชุดข้อมูลดิบใน data/raw ตาม MANIFEST.csv (ส่วน I/O ที่สคริปต์ใช้ร่วมกัน)."""

from __future__ import annotations

import csv
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


def load_manifest(raw_dir: Path) -> list[RawIssue]:
    """รวมแถว MANIFEST เป็นฉบับละหนึ่งรายการ เรียงตามชนิดแล้วตามรหัสฉบับ."""
    rows: dict[tuple[str, str], dict[str, object]] = {}
    with (raw_dir / "MANIFEST.csv").open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            key = (row["type"], row["issue_id"])
            item = rows.setdefault(
                key, {"role": row["role"], "pdf": None, "txt": None, "label": ""}
            )
            item[row["format"]] = raw_dir / row["file"]
            if row.get("label"):
                item["label"] = row["label"]
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


def issue_sort_key(issue: RawIssue) -> str:
    """เรียงตามเวลา: รายวัน DDMMYYYYHHMM -> YYYYMMDDHHMM, 7 วัน YYMMDD -> 20YYMMDD."""
    i = issue.issue_id
    if issue.doc_type == "daily":
        return i[4:8] + i[2:4] + i[0:2] + i[8:12]
    return "20" + i
