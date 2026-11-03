"""แปลงไฟล์ชุดที่เก็บจากเบราว์เซอร์ (JSON หนึ่งไฟล์ต่อชุด, ADR 0015) เป็นไฟล์ดิบ + แถว MANIFEST.

ส่วนนี้เป็นฟังก์ชันล้วน การอ่าน/เขียนไฟล์อยู่ใน scripts/import_raw_batch.py และ scripts/check_raw.py
"""

from __future__ import annotations

import base64
import hashlib
import re
from dataclasses import dataclass

# ลำดับคอลัมน์เดิมของ data/raw/MANIFEST.csv
MANIFEST_FIELDS = (
    "file",
    "type",
    "issue_id",
    "format",
    "role",
    "label",
    "source_url",
    "bytes",
    "sha256",
)

# ชื่อชนิดที่เก็บได้ (ชนิดที่ไปป์ไลน์รองรับจริงอยู่ใน raw_io.SUPPORTED_DOC_TYPES)
KNOWN_KINDS = frozenset(
    {"daily", "sevenday", "shipping", "warning", "weekly", "agro7", "outlook3m", "generic"}
)

# คีย์มาจากข้อมูลที่ไม่น่าไว้ใจ: บังคับรูปแบบ <ชนิด>/<ชนิด>_<รหัส>.<txt|pdf> กัน path แปลก
_KEY = re.compile(r"^([a-z0-9]+)/\1_([0-9A-Za-z][0-9A-Za-z_\-]{0,80})\.(txt|pdf)$")
_LABEL = re.compile(r"^# label: (.*)$", re.MULTILINE)


class BatchError(ValueError):
    """รายการในไฟล์ชุดผิดรูปแบบ."""


@dataclass(frozen=True)
class BatchFile:
    rel_path: str
    kind: str
    issue_id: str
    fmt: str
    data: bytes
    label: str
    source_url: str

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest()


def parse_entry(key: str, value: object) -> BatchFile:
    """หนึ่งรายการ {key: {text|b64, source}} -> BatchFile หรือ BatchError."""
    m = _KEY.match(key)
    if m is None or m.group(1) not in KNOWN_KINDS:
        raise BatchError(f"bad key: {key!r}")
    if not isinstance(value, dict):
        raise BatchError(f"bad value for {key}")
    kind, issue_id, fmt = m.group(1), m.group(2), m.group(3)
    source = str(value.get("source", ""))
    if not source.startswith("https://www.tmd.go.th/"):
        raise BatchError(f"source not tmd.go.th: {key}")
    if fmt == "txt":
        text = value.get("text")
        if not isinstance(text, str) or not text.startswith("# source: "):
            raise BatchError(f"bad text: {key}")
        # ไฟล์ข้อความเดิมใช้ \n และไม่มีบรรทัดว่างท้ายไฟล์
        data = text.replace("\r\n", "\n").encode("utf-8")
        lm = _LABEL.search(text)
        label = lm.group(1).strip() if lm else ""
    else:
        raw = value.get("b64")
        if not isinstance(raw, str):
            raise BatchError(f"bad pdf: {key}")
        data = base64.b64decode(raw, validate=True)
        if not data.startswith(b"%PDF-"):
            raise BatchError(f"not a pdf: {key}")
        label = ""
    return BatchFile(f"{kind}/{kind}_{issue_id}.{fmt}", kind, issue_id, fmt, data, label, source)


def parse_batch(entries: dict[str, object]) -> tuple[list[BatchFile], list[str]]:
    """ทั้งชุด -> (ไฟล์ที่ใช้ได้ เรียงตาม path, ข้อผิดพลาด) รายการเสียข้ามแต่นับไว้."""
    files: list[BatchFile] = []
    errors: list[str] = []
    for key in sorted(entries):
        try:
            files.append(parse_entry(key, entries[key]))
        except (BatchError, ValueError) as exc:
            errors.append(str(exc))
    return files, errors


@dataclass(frozen=True)
class DiskFile:
    rel_path: str
    size: int
    sha256: str


def check_inventory(rows: list[dict[str, str]], disk: list[DiskFile]) -> list[str]:
    """เทียบ MANIFEST กับไฟล์จริง: ไฟล์ไม่มีแถว, แถวไม่มีไฟล์, ขนาด/sha256 ไม่ตรง, แถวซ้ำ, เนื้อหาซ้ำ."""
    errors: list[str] = []
    by_path: dict[str, dict[str, str]] = {}
    for row in rows:
        if row["file"] in by_path:
            errors.append(f"duplicate row: {row['file']}")
        by_path[row["file"]] = row
    on_disk = {d.rel_path: d for d in disk}
    for path in sorted(set(on_disk) - set(by_path)):
        errors.append(f"file without manifest row: {path}")
    for path in sorted(set(by_path) - set(on_disk)):
        errors.append(f"manifest row without file: {path}")
    seen: dict[str, str] = {}
    for path in sorted(set(by_path) & set(on_disk)):
        row, d = by_path[path], on_disk[path]
        if row["sha256"] != d.sha256 or row["bytes"] != str(d.size):
            errors.append(f"size/sha256 mismatch: {path}")
        if d.sha256 in seen:
            errors.append(f"same content as {seen[d.sha256]}: {path}")
        seen.setdefault(d.sha256, path)
    return errors


def text_layer_level(thai_chars: int) -> str:
    """ระดับชั้นข้อความของ PDF จากจำนวนอักษรไทยที่ดึงได้ (ประตูของแผน 12.1 ใช้เกณฑ์ละเอียดกว่า)."""
    if thai_chars >= 200:
        return "yes"
    return "low" if thai_chars > 0 else "none"


def manifest_row(f: BatchFile, role: str) -> dict[str, str]:
    return {
        "file": f.rel_path,
        "type": f.kind,
        "issue_id": f.issue_id,
        "format": f.fmt,
        "role": role,
        "label": f.label,
        "source_url": f.source_url,
        "bytes": str(len(f.data)),
        "sha256": f.sha256,
    }
