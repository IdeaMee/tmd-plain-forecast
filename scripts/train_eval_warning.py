"""Phase 11.3: ฝึกและวัดตัวจัดประเภทประโยคของประกาศเตือนภัย (NB, k-NN เขียนเอง) เทียบกฎคำสำคัญและ NB ของรายวัน.

รัน: .venv/Scripts/python.exe -X utf8 scripts/train_eval_warning.py (รันซ้ำได้ผลเดิม)
เขียน models/eval/warning_*.json (ฝึกด้วยชุดฝึก ใช้วัด), models/warning_*.json (ฝึกด้วยป้ายทั้งหมด ใช้ในหลังบ้าน),
docs/results/warning-classifier-evaluation.md · โมเดลเดิม models/{naive_bayes,knn,selected}.json ไม่แตะ
ปรับ m และ k บน dev เท่านั้น เลือก NB/k-NN จาก dev (ห้ามเลือกจากชุดทดสอบ)
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

from tmd_plain.classify.evaluate import (
    Predict,
    accuracy,
    fit_knn,
    fit_nb,
    macro_f1,
    tune,
    vocabulary_size,
)
from tmd_plain.classify.features import bag_of_words
from tmd_plain.classify.keyword import keyword_label
from tmd_plain.classify.model_io import load_classifier
from tmd_plain.config import load_config
from tmd_plain.doctypes.warning.dataset import WARNING_LABELS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "labeled" / "warning" / "units_labeled.csv"
MODELS = ROOT / "models"
REPORT = ROOT / "docs" / "results" / "warning-classifier-evaluation.md"
LABELS = WARNING_LABELS


def dump_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2)
    path.write_text(text + "\n", encoding="utf-8", newline="\n")


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def recall(rows: list[dict], predict: Predict, label: str) -> str:
    gold = [r for r in rows if r["final_label"] == label]
    if not gold:
        return "-"
    hit = sum(predict(r["unit_id"]) == label for r in gold)
    return f"{hit}/{len(gold)}"


def main() -> int:
    with DATA.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    bags = {r["unit_id"]: bag_of_words(r["text"]) for r in rows}
    text_of = {r["unit_id"]: r["text"] for r in rows}
    train = [r for r in rows if r["split"] == "train"]
    dev = [r for r in rows if r["split"] == "dev"]
    test = [r for r in rows if r["split"] == "test"]

    tuning = tune(train, dev, bags, load_config()["classify"])
    nb_eval = fit_nb(train, bags, tuning.best_m_factor * tuning.vocab_train)
    knn_eval = fit_knn(train, bags, tuning.best_k)
    daily = load_classifier(MODELS)
    predictors: dict[str, Predict] = {
        "Naive Bayes (ประกาศ)": lambda u: nb_eval.predict(bags[u]),
        "k-NN (ประกาศ)": lambda u: knn_eval.predict(bags[u]),
        "กฎ keyword (baseline)": lambda u: keyword_label(text_of[u]),
        f"{'Naive Bayes' if daily.name == 'naive_bayes' else 'k-NN'} ของรายวัน (โมเดลเดิม)": lambda u: (
            daily.label(text_of[u])
        ),
    }
    results = {
        name: {
            "dev": accuracy(dev, p),
            "test": accuracy(test, p),
            "test_f1": macro_f1(test, p),
        }
        for name, p in predictors.items()
    }
    chosen = (
        "Naive Bayes (ประกาศ)"
        if results["Naive Bayes (ประกาศ)"]["dev"] >= results["k-NN (ประกาศ)"]["dev"]
        else "k-NN (ประกาศ)"
    )

    dump_json(MODELS / "eval" / "warning_naive_bayes.json", nb_eval.to_json())
    dump_json(MODELS / "eval" / "warning_knn.json", knn_eval.to_json())
    vocab_all = vocabulary_size(rows, bags)
    dump_json(
        MODELS / "warning_naive_bayes.json",
        fit_nb(rows, bags, tuning.best_m_factor * vocab_all).to_json(),
    )
    dump_json(MODELS / "warning_knn.json", fit_knn(rows, bags, tuning.best_k).to_json())
    dump_json(
        MODELS / "warning_selected.json",
        {
            "model": "naive_bayes" if chosen.startswith("Naive") else "knn",
            "chosen_on": "dev accuracy",
        },
    )

    choose = predictors[chosen]
    confusion: Counter[tuple[str, str]] = Counter(
        (r["final_label"], choose(r["unit_id"])) for r in test
    )
    predicted_labels = sorted(
        {p for _, p in confusion} | set(LABELS), key=lambda x: (x not in LABELS, x)
    )
    wrong = [r for r in test if choose(r["unit_id"]) != r["final_label"]]
    count = {
        s: Counter(r["final_label"] for r in rows if r["split"] == s)
        for s in ("train", "dev", "test")
    }
    lines = [
        "# ผลวัดตัวจัดประเภทประโยคของประกาศเตือนภัย (Phase 11.3)",
        "",
        "คำสั่ง: `.venv/Scripts/python.exe -X utf8 scripts/train_eval_warning.py` (รันซ้ำได้ผลเดิม) · ไฟล์นี้สร้างโดยสคริปต์ ห้ามแก้มือ",
        "",
        "**ที่มาของป้าย:** ผู้ช่วย (Claude) ร่างด้วยกฎคำสำคัญแล้วอ่านทุกหน่วย แก้ 5 หน่วย ไม่ได้ผ่านคนตรวจ "
        "([ADR 0012](../decisions/0012-agent-labels-without-human-review.md), `data/labeled/warning/FROZEN.md`) "
        "ความแม่นข้างล่างจึงวัดว่าโมเดลทำซ้ำป้ายชุดนี้ได้แค่ไหน และ**กฎ keyword ได้เปรียบ** เพราะร่างป้ายใช้คำสำคัญแนวเดียวกัน",
        "",
        "## ข้อมูล",
        "- หน่วยไม่ซ้ำ 370 จาก 155 ฉบับ (1,671 หน่วย) · แบ่งตามเหตุการณ์ (13 ชุดประกาศ) เรียงตามเวลา: ฝึก 8 / dev 2 / ทดสอบ 3 เหตุการณ์ "
        "· หน่วยอยู่ชุดที่เก่าที่สุดที่ปรากฏ ชุด dev/ทดสอบจึงเป็นถ้อยคำที่ไม่อยู่ในชุดฝึก",
        *[
            f"- {name} {sum(c.values())} หน่วย ({', '.join(f'{lab} {c[lab]}' for lab in LABELS)})"
            for name, c in (("ฝึก", count["train"]), ("dev", count["dev"]), ("ทดสอบ", count["test"]))
        ],
        "- dev มี advice แค่ 7 หน่วย การเลือกค่า m/k จึงแกว่งได้มาก",
        "",
        "## ปรับค่าบน dev",
        f"- คลังคำของชุดฝึก {tuning.vocab_train} คำ",
        "- Naive Bayes m = ตัวคูณ x |คลังคำ|: "
        + ", ".join(f"{f} → {pct(a)}" for f, a in tuning.nb)
        + f" · เลือก {tuning.best_m_factor}",
        "- k-NN: "
        + ", ".join(f"k={k} → {pct(a)}" for k, a in tuning.knn)
        + f" · เลือก k={tuning.best_k}",
        f"- เลือกโมเดลที่ใช้ในหลังบ้านจาก dev: **{chosen}**",
        "",
        "## ผลวัด",
        "| วิธี | dev | ทดสอบ (ถ้อยคำใหม่) | macro-F1 ทดสอบ | advice ที่จับได้ (ทดสอบ) | cause | weather |",
        "|---|---|---|---|---|---|---|",
        *[
            f"| {name} | {pct(r['dev'])} | {pct(r['test'])} | {pct(r['test_f1'])} | "
            f"{recall(test, predictors[name], 'advice')} | {recall(test, predictors[name], 'cause')} | "
            f"{recall(test, predictors[name], 'weather')} |"
            for name, r in results.items()
        ],
        "",
        "NB ของรายวันฝึกจากพยากรณ์รายวัน/7 วัน (4 ป้ายรวม other) ใช้กับประกาศได้โดยไม่ฝึกใหม่ แถวนี้ตอบว่าการฝึกเฉพาะประกาศช่วยแค่ไหน",
        "",
        f"## ตารางสับสนของ {chosen} บนชุดทดสอบ (แถว = ป้ายจริง, คอลัมน์ = ที่ทาย)",
        "| | " + " | ".join(predicted_labels) + " |",
        "|---|" + "---|" * len(predicted_labels),
        *[
            f"| {g} | " + " | ".join(str(confusion[(g, p)]) for p in predicted_labels) + " |"
            for g in LABELS
        ],
        "",
        f"## หน่วยที่ {chosen} จัดผิดบนชุดทดสอบ ({len(wrong)})",
        *(
            [
                f"- `{r['unit_id']}` จริง {r['final_label']} ทาย {choose(r['unit_id'])}: {r['text'][:120]}"
                for r in wrong
            ]
            or ["- ไม่มี"]
        ),
        "",
        "## ไฟล์",
        "- `models/eval/warning_{naive_bayes,knn}.json` ฝึกด้วยชุดฝึกเท่านั้น (ใช้วัด) · `models/warning_{naive_bayes,knn,selected}.json` "
        "ฝึกด้วยป้ายทั้งหมด 370 หน่วยด้วยค่าเดียวกัน ใช้ในหลังบ้าน (คัดข้อควรระวังของประกาศ)",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    for name, r in results.items():
        print(f"{name}: dev {pct(r['dev'])} test {pct(r['test'])} f1 {pct(r['test_f1'])}")
    print(f"chosen {chosen} · m {tuning.best_m_factor} · k {tuning.best_k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
