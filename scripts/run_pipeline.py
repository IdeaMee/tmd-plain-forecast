"""Phase 3.4: รันท่อประมวลผลกับทุกฉบับที่แสดงบนเว็บ -> data/processed/<doc_type>/<issue_id>.json.

ตั้งแต่ 11.1: พยากรณ์เดินเรือทุกฉบับที่เก็บ -> data/processed/shipping/ (รายวัน/7 วันเหมือนเดิมทุกไบต์)
ตั้งแต่ 11.4: ประกาศเตือนภัยทุกฉบับที่เก็บ -> data/processed/warning/ (ใช้ตัวจัดประเภทของประกาศ ชนิดอื่นไม่เปลี่ยน)
ตั้งแต่ 11.5: สรุปรายสัปดาห์ทุกฉบับที่เก็บ -> data/processed/weekly/ (ไม่มีตัวจัดประเภท ข้อความคัดคำต่อคำ)
ตั้งแต่ 11.6: รายวัน/7 วันประมวลผลทุกฉบับที่เก็บ (WEB_ROLES รวม train_pool และ archive_v2) ไม่ใช่แค่ display_test · ฉบับที่ไม่ผ่านตัวตรวจ F
ไม่เขียนไฟล์และบันทึกใน docs/results/pipeline-run.md (35 ไฟล์เดิมต้องเท่าเดิมทุกไบต์)

รัน: .venv/Scripts/python.exe -X utf8 scripts/run_pipeline.py
แหล่งข้อความ: หน้าเว็บ (.txt) ก่อน ถ้าไม่มีใช้ PDF (RawIssue.preferred) · ผลซ้ำได้ (ไม่มีเวลาประมวลผลในไฟล์)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tmd_plain.classify.model_io import load_classifier
from tmd_plain.contract import (
    Issue,
    ShippingIssue,
    SummarizeError,
    WarningNotice,
    WeeklySummary,
    error_response,
)
from tmd_plain.doctypes.shipping.runner import summarize_shipping
from tmd_plain.doctypes.warning.runner import summarize_warning
from tmd_plain.doctypes.weekly.runner import summarize_weekly
from tmd_plain.extract.advice import Labeler
from tmd_plain.generate.assemble import IssueMeta, default_source_label, issued_at_from_id
from tmd_plain.pipeline import summarize
from tmd_plain.prep.extract import document_from_txt
from tmd_plain.raw_io import (
    WEB_ROLES,
    RawIssue,
    RawShipping,
    RawWarning,
    RawWeekly,
    load_manifest,
    load_shipping,
    load_warnings,
    load_weekly,
)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"


def display_issues() -> list[RawIssue]:
    """ชุดแสดงผลเดิม 35 ฉบับ (ใช้กับ check_fidelity F7, make_review_sheet และเทสต์ที่ตรึงชุดนี้)."""
    return [i for i in load_manifest(RAW) if i.role == "display_test"]


def web_issues() -> list[RawIssue]:
    """ทุกฉบับรายวัน/7 วันที่ขึ้นเว็บ (11.6): ชุดเดิมและที่เก็บรอบ v2 ทั้งหมด."""
    return load_manifest(RAW, WEB_ROLES)


def meta_for(issue: RawIssue) -> IssueMeta:
    return IssueMeta(
        issue_id=issue.issue_id,
        issued_at=issued_at_from_id(issue.doc_type, issue.issue_id),  # type: ignore[arg-type]
        source_label=issue.label or default_source_label(issue.doc_type, issue.issue_id),  # type: ignore[arg-type]
    )


def run_one(issue: RawIssue, label_of: Labeler) -> Issue | SummarizeError:
    return summarize(issue.preferred(), meta_for(issue), label_of)


def render(issue: Issue | ShippingIssue | WarningNotice | WeeklySummary) -> str:
    return (
        json.dumps(issue.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, indent=2)
        + "\n"
    )


def out_path(issue: RawIssue) -> Path:
    return OUT / issue.doc_type / f"{issue.issue_id}.json"


def run_shipping(raw: RawShipping, label_of: Labeler) -> ShippingIssue | SummarizeError:
    run = summarize_shipping(document_from_txt(raw.txt.read_text(encoding="utf-8")).text, label_of)
    if isinstance(run, SummarizeError):
        return run
    issue: ShippingIssue = run.document  # type: ignore[assignment]
    if issue.issue_id != raw.issue_id:
        # รหัสจากบรรทัดออกประกาศต้องตรงรหัสรอบของหน้าเว็บ (ตรง 100/100 ฉบับ) ไม่ตรง = ไม่เขียน
        return error_response("extract_failed")
    return issue


def run_warning(raw: RawWarning, label_of: Labeler) -> WarningNotice | SummarizeError:
    run = summarize_warning(document_from_txt(raw.txt.read_text(encoding="utf-8")).text, label_of)
    if isinstance(run, SummarizeError):
        return run
    notice: WarningNotice = run.document  # type: ignore[assignment]
    if notice.issue_id != raw.issue_id:
        # รหัสจากเลขประกาศในเนื้อหาต้องตรงชื่อไฟล์ (ตรง 155/155 ฉบับ) ไม่ตรง = ไม่เขียน
        return error_response("extract_failed")
    return notice


def run_weekly(raw: RawWeekly) -> WeeklySummary | SummarizeError:
    summary = summarize_weekly(raw.txt.read_text(encoding="utf-8"), raw.issue_id)
    if isinstance(summary, SummarizeError):
        return summary
    # วัน เดือน ปีของรหัสรอบต้องตรงบรรทัดออกประกาศ (ชั่วโมงต่างได้ 4/100 ฉบับ ดู RawWeekly) ไม่ตรง = ไม่เขียน
    if raw.issue_id[:8] != summary.issued_at.strftime("%d%m%Y"):
        return error_response("extract_failed")
    return summary


REPORT = ROOT / "docs" / "results" / "pipeline-run.md"
TYPE_ORDER = ("daily", "sevenday", "shipping", "warning", "weekly")
TYPE_TH = {
    "daily": "พยากรณ์รายวัน",
    "sevenday": "พยากรณ์ 7 วัน",
    "shipping": "พยากรณ์เดินเรือ",
    "warning": "ประกาศเตือนภัย",
    "weekly": "สรุปรายสัปดาห์",
}


class Stats:
    """นับต่อชนิด: ฉบับที่ลอง เขียนได้ และที่ไม่ผ่าน (รหัสข้อผิดพลาด) ใช้เขียนรายงาน."""

    def __init__(self) -> None:
        self.tried: dict[str, int] = {t: 0 for t in TYPE_ORDER}
        self.written: dict[str, list[str]] = {t: [] for t in TYPE_ORDER}
        self.failed: dict[str, list[tuple[str, str]]] = {t: [] for t in TYPE_ORDER}

    def ok(self, doc_type: str, issue_id: str) -> None:
        self.tried[doc_type] += 1
        self.written[doc_type].append(issue_id)

    def fail(self, doc_type: str, issue_id: str, code: str) -> None:
        self.tried[doc_type] += 1
        self.failed[doc_type].append((issue_id, code))
        print(f"FAIL {doc_type}/{issue_id}: {code}")

    @property
    def total_failed(self) -> int:
        return sum(len(v) for v in self.failed.values())


def write_report(stats: Stats, removed: list[str]) -> None:
    lines = [
        "# รายงานการรันท่อประมวลผลทุกฉบับ (Phase 11.6)",
        "",
        "สร้างโดย `scripts/run_pipeline.py` (อย่าแก้ด้วยมือ) · ฉบับที่ไม่ผ่านตัวตรวจ F ไม่ถูกเขียนลง `data/processed` จึงไม่ขึ้นเว็บ",
        "",
        "| ชนิด | ฉบับที่ลอง | เขียนได้ | ไม่ผ่าน | ช่วงรหัสที่เขียนได้ (เรียงตามเวลา) |",
        "|---|---|---|---|---|",
    ]
    for t in TYPE_ORDER:
        ids = stats.written[t]
        span = f"`{ids[0]}` ถึง `{ids[-1]}`" if ids else "-"
        lines.append(
            f"| {TYPE_TH[t]} | {stats.tried[t]} | {len(ids)} | {len(stats.failed[t])} | {span} |"
        )
    lines += ["", "## ฉบับที่ไม่ผ่าน", ""]
    failures = [
        f"- {TYPE_TH[t]} `{i}`: `{code}`" for t in TYPE_ORDER for i, code in stats.failed[t]
    ]
    lines += failures or ["- ไม่มี"]
    lines += ["", "## ไฟล์ค้างที่ลบออกจาก data/processed (ไม่ผ่านรอบนี้)", ""]
    lines += [f"- `{r}`" for r in removed] or ["- ไม่มี"]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def prune_stale(stats: Stats) -> list[str]:
    """ลบไฟล์ใน data/processed ที่รอบนี้ไม่ได้เขียน (ฉบับที่เคยผ่านแต่ตอนนี้ไม่ผ่านตัวตรวจ ห้ามค้างไปขึ้นเว็บ)."""
    removed: list[str] = []
    for doc_type in TYPE_ORDER:
        folder = OUT / doc_type
        if not folder.exists():
            continue
        keep = set(stats.written[doc_type])
        for path in sorted(folder.glob("*.json")):
            if path.stem not in keep:
                path.unlink()
                removed.append(f"{doc_type}/{path.stem}")
                print(f"REMOVED stale {doc_type}/{path.stem}")
    return removed


def write_json(path: Path, doc: Issue | ShippingIssue | WarningNotice | WeeklySummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(doc), encoding="utf-8", newline="\n")


def main() -> int:
    classifier = load_classifier(ROOT / "models")
    label_of = classifier.label
    stats = Stats()
    for issue in web_issues():
        result = run_one(issue, label_of)
        if isinstance(result, SummarizeError):
            stats.fail(issue.doc_type, issue.issue_id, result.error.code)
            continue
        write_json(out_path(issue), result)
        stats.ok(issue.doc_type, issue.issue_id)
    for raw in load_shipping(RAW):
        shipping = run_shipping(raw, label_of)
        if isinstance(shipping, SummarizeError):
            stats.fail("shipping", raw.issue_id, shipping.error.code)
            continue
        write_json(OUT / "shipping" / f"{raw.issue_id}.json", shipping)
        stats.ok("shipping", raw.issue_id)
    warning_label_of = classifier.for_doc("warning").label
    for raw_warning in load_warnings(RAW):
        notice = run_warning(raw_warning, warning_label_of)
        if isinstance(notice, SummarizeError):
            stats.fail("warning", raw_warning.issue_id, notice.error.code)
            continue
        write_json(OUT / "warning" / f"{raw_warning.issue_id}.json", notice)
        stats.ok("warning", raw_warning.issue_id)
    for raw_weekly in load_weekly(RAW):
        weekly = run_weekly(raw_weekly)
        if isinstance(weekly, SummarizeError):
            stats.fail("weekly", raw_weekly.issue_id, weekly.error.code)
            continue
        write_json(OUT / "weekly" / f"{raw_weekly.issue_id}.json", weekly)
        stats.ok("weekly", raw_weekly.issue_id)
    removed = prune_stale(stats)
    write_report(stats, removed)
    print(
        "wrote "
        + " ".join(f"{t} {len(stats.written[t])}" for t in TYPE_ORDER)
        + f" -> data/processed · failed {stats.total_failed}"
    )
    return 1 if stats.total_failed else 0


if __name__ == "__main__":
    sys.exit(main())
