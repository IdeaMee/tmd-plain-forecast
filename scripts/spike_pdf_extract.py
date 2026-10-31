"""Phase 0.2: วัดคุณภาพข้อความจาก PDF ของ TMD เทียบตัวอ่านสองตัว (pypdfium2, pdfminer.six).

รัน: .venv/Scripts/python.exe -X utf8 scripts/spike_pdf_extract.py
อ่านเฉพาะไฟล์ใน data/raw/ (ห้ามดึงเว็บ TMD) ผลพิมพ์ออกหน้าจอเป็นตาราง markdown
ตัวแยกบล็อกภาคในไฟล์นี้เป็นแบบง่ายเพื่อวัดผลเท่านั้น ตัวจริงอยู่ใน Phase 1.3
"""

from __future__ import annotations

import re
import sys
import time
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from tmd_plain.prep.pdf_text import clean_text, count_pua, extract_pdfium, extract_pdfminer

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
REGIONS = [
    ("north", r"(ภาค)?เหนือ(\s|$)"),
    ("northeast", r"(ภาค)?ตะวันออกเฉียงเหนือ(\s|$)"),
    ("central", r"(ภาค)?กลาง(\s|$)"),
    ("east", r"(ภาค)?ตะวันออก(\s|$)"),
    ("south_east_coast", r"(ภาค)?ใต้\s*\(?ฝั่งตะวันออก"),
    ("south_west_coast", r"(ภาค)?ใต้\s*\(?ฝั่งตะวันตก"),
    ("bangkok_vicinity", r"กรุงเทพ"),
]
START_MARKERS = ("พยากรณ์อากาศสำหรับประเทศไทย", "สภาวะอากาศ", "คาดหมายอากาศรายภาค")
END_MARKERS = ("หมายเหตุ", "ออกประกาศ", "ผู้พยากรณ์")
NUM = re.compile(r"\d+(?:\.\d+)?")
EXTRACTORS = {"pypdfium2": extract_pdfium, "pdfminer.six": extract_pdfminer}


def read_txt(path: Path) -> str:
    # ตัดหัวไฟล์ "# source ..." ที่ใส่ตอนเก็บข้อมูล
    lines = path.read_text(encoding="utf-8").splitlines()
    return clean_text("\n".join(line for line in lines if not line.startswith("# ")))


def split_regions(text: str) -> dict[str, str] | None:
    """หาหัวข้อ 7 ภาคตามลำดับหลังเครื่องหมายเริ่มส่วนรายภาค; คืน None ถ้าไม่ครบ."""
    lines = text.split("\n")
    start = next((i for i, ln in enumerate(lines) if ln.startswith(START_MARKERS)), None)
    if start is None:
        return None
    pos, heads = start + 1, []
    for key, pat in REGIONS:
        rx = re.compile(pat)
        hit = next((i for i in range(pos, len(lines)) if rx.match(lines[i])), None)
        if hit is None:
            return None
        heads.append((key, hit))
        pos = hit + 1
    last = heads[-1][1]
    end = next(
        (i for i in range(last + 1, len(lines)) if lines[i].startswith(END_MARKERS)), len(lines)
    )
    blocks = {}
    for n, (key, i) in enumerate(heads):
        j = heads[n + 1][1] if n + 1 < len(heads) else end
        blocks[key] = "\n".join(lines[i:j])
    return blocks


def number_recall(ref: str, got: str) -> float:
    """สัดส่วนตัวเลขของต้นฉบับ HTML ที่พบในบล็อกจาก PDF (นับซ้ำได้)."""
    want, have = Counter(NUM.findall(ref)), Counter(NUM.findall(got))
    total = sum(want.values())
    if total == 0:
        return 1.0
    return sum(min(c, have[n]) for n, c in want.items()) / total


def similarity(ref: str, got: str) -> float:
    # ตัดบรรทัดที่เป็นตัวเลขล้วน (ตารางอุณหภูมิรายจังหวัดที่มีเฉพาะใน PDF) และช่องว่างก่อนเทียบ
    got = "\n".join(ln for ln in got.split("\n") if not NUM.fullmatch(ln.strip()))
    a, b = re.sub(r"\s+", "", ref), re.sub(r"\s+", "", got)
    return SequenceMatcher(None, a, b, autojunk=False).ratio()


def main() -> int:
    pdfs = sorted(RAW.glob("daily/*.pdf")) + sorted(RAW.glob("sevenday/*.pdf"))
    if not pdfs:
        print("ไม่พบไฟล์ใน data/raw/", file=sys.stderr)
        return 1
    summary: dict[tuple[str, str], Counter] = {}
    sims: dict[tuple[str, str], list[float]] = {}
    print(
        "| file | extractor | 7 regions | blocks numbers 100% | mean sim | period phrase | PUA | ms |"
    )
    print("|---|---|---|---|---|---|---|---|")
    for pdf in pdfs:
        doc_type = pdf.parent.name
        txt = pdf.with_suffix(".txt")
        ref_blocks = split_regions(read_txt(txt)) if txt.exists() else None
        data = pdf.read_bytes()
        for name, fn in EXTRACTORS.items():
            t0 = time.perf_counter()
            raw = fn(data)
            ms = (time.perf_counter() - t0) * 1000
            text = clean_text(raw)
            blocks = split_regions(text)
            c = summary.setdefault((doc_type, name), Counter())
            c["files"] += 1
            c["ms"] += ms
            c["pua_raw"] += count_pua(raw)
            c["pua_clean"] += count_pua(text)
            c["regions_ok"] += blocks is not None
            period = bool(re.search(r"ในช่วงวันที่", "\n".join(blocks.values()))) if blocks else False
            c["period_ok"] += period
            num_cell = sim_cell = "-"
            if ref_blocks is not None and blocks is not None:
                rec = [number_recall(ref_blocks[k], blocks[k]) for k, _ in REGIONS]
                sm = [similarity(ref_blocks[k], blocks[k]) for k, _ in REGIONS]
                c["pair_blocks"] += len(rec)
                c["pair_blocks_full"] += sum(r == 1.0 for r in rec)
                sims.setdefault((doc_type, name), []).extend(sm)
                num_cell = f"{sum(r == 1.0 for r in rec)}/7"
                sim_cell = f"{sum(sm) / len(sm):.3f}"
            elif ref_blocks is not None:
                c["pair_blocks"] += 7
                num_cell = "0/7 (no split)"
            print(
                f"| {pdf.name} | {name} | {'yes' if blocks else 'NO'} | {num_cell} | {sim_cell} "
                f"| {'yes' if period else 'no'} | {count_pua(raw)} | {ms:.0f} |"
            )
    print("\n## Summary\n")
    print(
        "| doc type | extractor | files | 7 regions found | period phrase | blocks with all HTML numbers "
        "| mean block similarity | PUA raw/clean | mean ms/file |"
    )
    print("|---|---|---|---|---|---|---|---|---|")
    for (doc_type, name), c in summary.items():
        s = sims.get((doc_type, name), [])
        sim = f"{sum(s) / len(s):.3f}" if s else "-"
        print(
            f"| {doc_type} | {name} | {c['files']} | {c['regions_ok']}/{c['files']} "
            f"| {c['period_ok']}/{c['files']} | {c['pair_blocks_full']}/{c['pair_blocks']} | {sim} "
            f"| {c['pua_raw']}/{c['pua_clean']} | {c['ms'] / c['files']:.0f} |"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
