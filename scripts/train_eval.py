"""Phase 2.4: ฝึก Naive Bayes และ k-NN (เขียนเอง) ปรับค่าบน dev วัดบนชุดทดสอบเทียบกฎ keyword.

รัน: .venv/Scripts/python.exe -X utf8 scripts/train_eval.py
อ่าน data/labeled/units_labeled.csv (final_label, ปิดแล้วตาม FROZEN.md) + data/labeled/split.csv
เขียน models/eval/*.json (ฝึกด้วยชุดฝึกเท่านั้น ใช้วัดผล), models/*.json (ฝึกด้วยป้ายทั้งหมด ใช้ในท่อประมวลผล)
และ docs/results/classifier-evaluation.md
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from tmd_plain.classify.evaluate import (
    ERROR_NOTES,
    Predict,
    accuracy,
    fit_knn,
    fit_nb,
    tune,
    vocabulary_size,
)
from tmd_plain.classify.features import bag_of_words
from tmd_plain.classify.keyword import keyword_label
from tmd_plain.config import load_config
from tmd_plain.contract import LABELS
from tmd_plain.labeled_io import load_labeled_rows

ROOT = Path(__file__).resolve().parents[1]
LABELED = ROOT / "data" / "labeled"
MODELS = ROOT / "models"
REPORT = ROOT / "docs" / "results" / "classifier-evaluation.md"


def dump_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2)
    path.write_text(text + "\n", encoding="utf-8", newline="\n")


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def main() -> int:
    rows = load_labeled_rows(LABELED)
    bags = {r["unit_id"]: bag_of_words(r["text"]) for r in rows}
    text_of = {r["unit_id"]: r["text"] for r in rows}

    train = [r for r in rows if r["split"] == "train"]
    dev = [r for r in rows if r["split"] == "dev"]
    test_new = [r for r in rows if r["split"] == "test"]
    test_all = [r for r in rows if int(r["test_occurrences"]) > 0]

    # ปรับค่าบน dev เท่านั้น ค่าดีเท่ากันเลือกค่าแรกในรายการ
    tuning = tune(train, dev, bags, load_config()["classify"])
    vocab_train = tuning.vocab_train
    nb_tuning, knn_tuning = tuning.nb, tuning.knn
    best_f, best_k = tuning.best_m_factor, tuning.best_k

    nb_eval = fit_nb(train, bags, best_f * vocab_train)
    knn_eval = fit_knn(train, bags, best_k)
    predictors: dict[str, Predict] = {
        "Naive Bayes": lambda u: nb_eval.predict(bags[u]),
        "k-NN": lambda u: knn_eval.predict(bags[u]),
        "กฎ keyword (baseline)": lambda u: keyword_label(text_of[u]),
    }
    results = {
        name: {
            "dev": accuracy(dev, p),
            "test_all": accuracy(test_all, p),
            "test_all_weighted": accuracy(test_all, p, "test_occurrences"),
            "test_new": accuracy(test_new, p),
        }
        for name, p in predictors.items()
    }
    # เลือกจาก dev (ห้ามเลือกจากชุดทดสอบ) เสมอกันเลือก Naive Bayes เพราะไฟล์เล็กและอธิบายได้
    chosen = "Naive Bayes" if results["Naive Bayes"]["dev"] >= results["k-NN"]["dev"] else "k-NN"

    dump_json(MODELS / "eval" / "naive_bayes.json", nb_eval.to_json())
    dump_json(MODELS / "eval" / "knn.json", knn_eval.to_json())
    vocab_all = vocabulary_size(rows, bags)
    nb_final = fit_nb(rows, bags, best_f * vocab_all)
    knn_final = fit_knn(rows, bags, best_k)
    dump_json(MODELS / "naive_bayes.json", nb_final.to_json())
    dump_json(MODELS / "knn.json", knn_final.to_json())
    dump_json(
        MODELS / "selected.json",
        {"model": "naive_bayes" if chosen == "Naive Bayes" else "knn", "chosen_on": "dev accuracy"},
    )

    kw_agree = sum(keyword_label(r["text"]) == r["final_label"] for r in rows)
    chosen_predict = predictors[chosen]
    confusion: Counter[tuple[str, str]] = Counter(
        (r["final_label"], chosen_predict(r["unit_id"])) for r in test_new
    )
    wrong = [r for r in test_new if chosen_predict(r["unit_id"]) != r["final_label"]]

    label_count = Counter(r["final_label"] for r in train)
    lines = [
        "# ผลวัดตัวจัดประเภทหน่วย (Phase 2.4)",
        "",
        "คำสั่ง: `.venv/Scripts/python.exe -X utf8 scripts/train_eval.py` (รันซ้ำได้ผลเดิม) · ไฟล์นี้สร้างโดยสคริปต์ ห้ามแก้มือ",
        "",
        "**ที่มาของป้าย:** ติดโดยโมเดลภาษา (Claude) ไม่ได้ผ่านคนตรวจ ([ADR 0012](../decisions/0012-agent-labels-without-human-review.md)) "
        "accuracy ข้างล่างจึงวัดว่าโมเดลทำซ้ำป้ายชุดนี้ได้แค่ไหน ไม่ใช่เทียบกับป้ายที่คนยืนยัน",
        "",
        "## ข้อมูล",
        f"- ฝึก {len(train)} หน่วย ({', '.join(f'{c} {label_count[c]}' for c in LABELS)}) · dev {len(dev)} · "
        f"ทดสอบ (ก) ทุกหน่วยที่ปรากฏในวันทดสอบ {len(test_all)} หน่วย ({sum(int(r['test_occurrences']) for r in test_all)} ครั้งที่ปรากฏ) · "
        f"(ข) เฉพาะถ้อยคำใหม่ {len(test_new)} หน่วย",
        f"- คุณลักษณะ: bag of words (นับความถี่) บนผลตัดคำ newmm + พจนานุกรมคำอากาศ ตัวเลขรวมเป็นโทเคน `<num>` · Vocabulary ชุดฝึก {vocab_train} คำ",
        "- Naive Bayes: P(w|c) = (n_k + m·p)/(n + m), p = 1/|Vocabulary|, log probability (สไลด์ ML 08)",
        "- k-NN: ระยะ L2 บนเวกเตอร์ความถี่ที่ปรับให้ยาว 1, โหวตเสียงข้างมาก (บันทึก ML 04)",
        "- กฎ keyword: เขียนใน Phase 2.1 ก่อนมีป้าย ไม่ได้ฝึกและไม่ได้ปรับ",
        "",
        "## ปรับค่าบนชุด dev",
        "| m (× |Vocabulary|) | " + " | ".join(str(f) for f, _ in nb_tuning) + " |",
        "|---|" + "---|" * len(nb_tuning),
        "| dev accuracy NB | " + " | ".join(pct(a) for _, a in nb_tuning) + " |",
        "",
        "| k | " + " | ".join(str(k) for k, _ in knn_tuning) + " |",
        "|---|" + "---|" * len(knn_tuning),
        "| dev accuracy k-NN | " + " | ".join(pct(a) for _, a in knn_tuning) + " |",
        "",
        f"เลือก m = {best_f} × |Vocabulary| และ k = {best_k} (ค่าดีเท่ากันเลือกค่าแรก) · dev มีแค่ {len(dev)} หน่วย ค่าที่เลือกจึงไม่แน่นอนนัก",
        "",
        "## ผลวัด",
        "| ตัวจัดประเภท | dev | ทดสอบ (ก) ทุกหน่วย | ทดสอบ (ก) ถ่วงตามครั้งที่ปรากฏ | ทดสอบ (ข) ถ้อยคำใหม่ |",
        "|---|---|---|---|---|",
    ]
    for name, res in results.items():
        lines.append(
            f"| {name} | {pct(res['dev'])} | {pct(res['test_all'])} | "
            f"{pct(res['test_all_weighted'])} | {pct(res['test_new'])} |"
        )
    lines += [
        "",
        f"**ตัวที่เลือก: {chosen}** (เลือกจาก accuracy บน dev ไม่ได้ดูชุดทดสอบ; dev เท่ากันเลือก Naive Bayes) "
        "โมเดลที่ท่อประมวลผลใช้ฝึกใหม่ด้วยป้ายทั้งหมด 292 หน่วยด้วยค่าเดียวกัน (`models/*.json`) แยกจากโมเดลที่ใช้วัด (`models/eval/`)",
        "",
        f"## ตารางสับสนของ {chosen} บนทดสอบ (ข) (แถว = ป้ายจริง, คอลัมน์ = ที่ทาย)",
        "| | " + " | ".join(LABELS) + " |",
        "|---|" + "---|" * len(LABELS),
    ]
    for t in LABELS:
        lines.append(f"| {t} | " + " | ".join(str(confusion[(t, p)]) for p in LABELS) + " |")
    lines += ["", f"## หน่วยที่ {chosen} จัดผิดบนทดสอบ (ข): {len(wrong)} หน่วย", ""]
    lines += ["| unit_id | ป้าย | ทาย | ข้อความ (ตัด 90 อักษร) | เหตุผลที่คาด |", "|---|---|---|---|---|"]
    for r in wrong:
        short = r["text"][:90].replace("|", "/")
        note = ERROR_NOTES.get(r["unit_id"], "")
        lines.append(
            f"| {r['unit_id']} | {r['final_label']} | {chosen_predict(r['unit_id'])} | {short} | {note} |"
        )
    lines += [
        "",
        "## ข้อจำกัด",
        "- ป้ายไม่ได้ผ่านคนตรวจ (ADR 0012) ความผิดของผู้ช่วยตอนติดป้ายจะไม่ปรากฏเป็นความผิดของโมเดล",
        "- `other` มีหน่วยเดียวในข้อมูลทั้งหมด (อยู่ชุดฝึก) โมเดลจึงแทบทายป้ายนี้ไม่ได้ และชุดทดสอบไม่มีป้ายนี้",
        f"- ชุดฝึก {len(train)} หน่วยและ dev {len(dev)} หน่วยเล็ก ตัวเลขแกว่งได้มากถ้าเปลี่ยนวันแบ่งชุด · TMD ใช้ถ้อยคำซ้ำเป็นแบบแผน accuracy จึงสูงได้ง่าย",
        f"- กฎ keyword ได้ accuracy สูงกว่าโมเดลที่เรียน ส่วนหนึ่งเพราะป้ายของผู้ช่วยตรงกับกฎ {kw_agree}/{len(rows)} หน่วยตั้งแต่ก่อนวัดผล "
        "(ผู้ติดป้ายกับกฎใช้เกณฑ์คล้ายกัน และ TMD ใช้ถ้อยคำเป็นแบบแผน) จึงไม่ได้แปลว่ากฎจะดีกว่ากับถ้อยคำแบบอื่น · "
        "โมเดลที่เรียนยังจำเป็นตามข้อกำหนดรายวิชา และใช้ตรวจหน่วยที่กฎกับโมเดลเห็นต่างกันได้",
        "- ไม่ได้วัด precision/recall/F1 แยกป้าย (ADR 0007 ตกลงวัดขั้นต่ำเป็น accuracy + ตัวอย่างผิด)",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    for name, res in results.items():
        print(name, {k: round(v, 4) for k, v in res.items()})
    print(f"best m factor={best_f} k={best_k} chosen={chosen} wrong(test new)={len(wrong)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
