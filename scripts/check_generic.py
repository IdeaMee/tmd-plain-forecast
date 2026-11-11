"""Phase 10.3: รันโหมดทั่วไปกับ PDF ที่เก็บไว้ -> docs/results/generic-check.md (ต้องพิมพ์ errors: 0).

ใช้: .venv/Scripts/python.exe -X utf8 scripts/check_generic.py [--agro-every 10]
ข้อผิดพลาด = crash, ตรวจความถูกต้องไม่ผ่าน, ผลเกิน 1 MB หรือใช้เวลาเกิน 30 วินาที
PDF ภาพล้วนได้ extract_failed เป็นพฤติกรรมที่ตั้งใจ (นับแยก ไม่ใช่ข้อผิดพลาด)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from tmd_plain.classify.model_io import load_classifier, with_label_cache
from tmd_plain.config import load_config
from tmd_plain.contract import SummarizeError
from tmd_plain.generic.build import build_generic
from tmd_plain.generic.fidelity import check_generic
from tmd_plain.pipeline import document_from_bytes

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORT = ROOT / "docs" / "results" / "generic-check.md"
# เอกสารที่ไม่ใช่ของ TMD (มีชั้นข้อความ) ใช้ทดสอบคำเตือน not_tmd_like
NON_TMD = ROOT / "course" / "slides" / "0_MiniProject.pdf"
KINDS = ("generic", "outlook3m", "warning", "weekly", "agro7")
MAX_SECONDS = 30.0
# อินโฟกราฟิกเกษตร 7 วันที่ไม่มีชั้นข้อความ (พบตอนเก็บ 9.1)
IMAGE_ONLY = "agro7_11112026.pdf"


@dataclass
class Stat:
    files: int = 0
    ok: int = 0
    no_text: int = 0
    # จำนวนไฟล์ที่มีข้อผิดพลาด (errors เก็บข้อความ ไฟล์ละได้หลายข้อ)
    failed: int = 0
    errors: list[str] = field(default_factory=list)
    max_seconds: float = 0.0
    max_bytes: int = 0
    units: int = 0
    uncertain: int = 0
    tmd_like: int = 0
    truncated: int = 0
    region_tabs: int = 0


def _files(every: int) -> list[tuple[str, Path]]:
    out: list[tuple[str, Path]] = []
    for kind in KINDS:
        paths = sorted((RAW / kind).glob("*.pdf"))
        if kind == "agro7":
            # สุ่มทุก N ไฟล์ + ไฟล์ภาพล้วนที่รู้จัก ให้กรณีไม่มีชั้นข้อความถูกตรวจทุกครั้ง
            image_only = RAW / kind / IMAGE_ONLY
            paths = sorted({*paths[::every], *([image_only] if image_only.exists() else [])})
        out += [(kind, p) for p in paths]
    if NON_TMD.exists():
        out.append(("non_tmd", NON_TMD))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agro-every", type=int, default=10, help="เกษตร 7 วันมี ~670 ไฟล์ ตรวจทุก N ไฟล์")
    args = ap.parse_args()
    cfg = load_config()["generic"]
    classifier = load_classifier(ROOT / "models")
    stats: dict[str, Stat] = {}
    for kind, path in _files(args.agro_every):
        st = stats.setdefault(kind, Stat())
        st.files += 1
        t0 = time.perf_counter()
        try:
            doc = document_from_bytes(path.read_bytes())
            if isinstance(doc, SummarizeError):
                st.no_text += 1
                continue
            document, details = build_generic(doc, with_label_cache(classifier), cfg)
            if not details.units:
                # มีแค่เลขหน้า/สัญลักษณ์: บริการตอบ extract_failed เหมือนไม่มีชั้นข้อความ
                st.no_text += 1
                continue
            problems = check_generic(document, doc.text)
        # รายงานทุกไฟล์ที่พัง ไม่หยุดทั้งชุด
        except Exception as exc:  # noqa: BLE001
            st.failed += 1
            st.errors.append(f"{path.name}: crash {type(exc).__name__}: {exc}")
            continue
        seconds = time.perf_counter() - t0
        size = len(json.dumps(document.model_dump(mode="json"), ensure_ascii=False).encode("utf-8"))
        file_errors = [f"{path.name}: {p}" for p in problems[:3]]
        if seconds > MAX_SECONDS:
            file_errors.append(f"{path.name}: ใช้เวลา {seconds:.1f} วินาที")
        if size > cfg["max_json_bytes"]:
            file_errors.append(f"{path.name}: ผล {size} ไบต์")
        st.errors += file_errors
        st.failed += bool(file_errors)
        units = [u for s in document.sections for u in s.units]
        st.ok += not file_errors
        st.max_seconds = max(st.max_seconds, seconds)
        st.max_bytes = max(st.max_bytes, size)
        st.units += len(units)
        st.uncertain += sum(u.uncertain for u in units)
        st.tmd_like += document.tmd_like
        st.truncated += document.truncated
        st.region_tabs += document.has_region_headings

    errors = [e for st in stats.values() for e in st.errors]
    lines = [
        "# ตรวจโหมดทั่วไป (Phase 10.3)",
        "",
        "สร้างโดย `scripts/check_generic.py` (อย่าแก้มือ) · เวลาเป็นค่าบนเครื่องทีม รวมอ่าน PDF"
        f" · เกษตร 7 วันตรวจทุก {args.agro_every} ไฟล์ · `non_tmd` = สไลด์วิชา (ไม่ใช่เอกสาร TMD)",
        "",
        "| ชุด | ไฟล์ | ผ่าน | ไม่มีชั้นข้อความ | ไฟล์ที่ผิดพลาด | เวลาสูงสุด (วินาที) | ผลใหญ่สุด (KB) | หน่วย | ไม่แน่ใจ | เหมือน TMD | แท็บภาค | ถูกตัด |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for kind, st in stats.items():
        share = f"{st.uncertain / st.units:.0%}" if st.units else "-"
        lines.append(
            f"| {kind} | {st.files} | {st.ok} | {st.no_text} | {st.failed} | {st.max_seconds:.2f} | "
            f"{st.max_bytes // 1024} | {st.units} | {st.uncertain} ({share}) | {st.tmd_like} | "
            f"{st.region_tabs} | {st.truncated} |"
        )
    lines += [
        "",
        "ไม่แน่ใจ = ความมั่นใจต่ำกว่า `uncertain_below` หรือคำในหน่วยอยู่ในคลังคำของโมเดลน้อยกว่า"
        " `min_known_ratio` (`[generic]` ใน `config.toml`) ตัวจัดประเภทฝึกจากพยากรณ์รายวัน/7 วันเท่านั้น"
        " เอกสารชนิดอื่นจึงไม่แน่ใจมากกว่าปกติ",
    ]
    if errors:
        lines += ["", "## ข้อผิดพลาด", *[f"- {e}" for e in errors]]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for kind, st in stats.items():
        print(
            f"{kind:10} files {st.files:4} ok {st.ok:4} no_text {st.no_text:3} failed {st.failed}"
        )
    for e in errors[:20]:
        print(f"error: {e}")
    print(f"errors: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
