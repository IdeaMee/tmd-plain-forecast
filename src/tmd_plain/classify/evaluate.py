"""วัดผลและปรับค่าตัวจัดประเภท (ใช้ร่วมกันโดย scripts/train_eval.py และ scripts/export_model_report.py).

ฟังก์ชันล้วน: รับแถวหน่วย (dict จาก units_labeled.csv + split.csv) และ bag of words ที่ตัดคำไว้แล้ว
ปรับ m และ k บน dev เท่านั้น ค่าดีเท่ากันเลือกค่าแรกในรายการ (Phase 2.4)
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from tmd_plain.classify.knn import KnnModel, train_knn
from tmd_plain.classify.naive_bayes import NaiveBayesModel, train_naive_bayes

Row = dict[str, str]
Bags = dict[str, Counter[str]]
Predict = Callable[[str], str]

# เหตุผลที่คาดของหน่วยที่จัดผิด (ผู้ช่วยเขียนหลังอ่านผลรอบแรก ไม่ได้ใช้ปรับโมเดล)
ERROR_NOTES: dict[str, str] = {
    "d-1fc91bdf": 'คำแนะนำมีวลีเหตุ "เนื่องจากสภาพอากาศที่หนาวเย็นลง" และชุดฝึกมี advice แค่ 21 หน่วย คำกลไก/อากาศจึงดึงไป cause',
    "d-ffd00808": 'ประโยคคลื่นลมใช้คำเดียวกับประโยคมรสุม ("มีกำลังแรงขึ้น", อ่าวไทย, ทะเลอันดามัน) bag of words ไม่รู้ลำดับคำ',
    "s-bc71e9e0": "หน่วยปนกลไก + คลื่น + อากาศช่วงถัดไป ป้ายเองก็ก้ำกึ่ง (มี note) คำสภาพอากาศมีมากกว่าคำกลไก",
    "d-3e085216": '"เริ่มมีกำลังอ่อนลงเป็นกำลังปานกลาง" เป็นคำที่พบบ่อยในประโยคมรสุม (cause) ในชุดฝึก',
}


def accuracy(rows: Sequence[Row], predict: Predict, weight: str | None = None) -> float:
    if not rows:
        return 0.0
    w = [int(r[weight]) if weight else 1 for r in rows]
    hit = sum(
        wi for r, wi in zip(rows, w, strict=True) if predict(r["unit_id"]) == r["final_label"]
    )
    return hit / sum(w)


def macro_f1(rows: Sequence[Row], predict: Predict) -> float:
    """F1 เฉลี่ยของป้ายที่มีในป้ายจริงหรือที่ทาย (ป้ายที่ไม่มีทั้งสองฝั่งไม่นับ)."""
    pairs = [(r["final_label"], predict(r["unit_id"])) for r in rows]
    labels = sorted({t for t, _ in pairs} | {p for _, p in pairs})
    if not labels:
        return 0.0
    scores = []
    for c in labels:
        tp = sum(t == c and p == c for t, p in pairs)
        fp = sum(t != c and p == c for t, p in pairs)
        fn = sum(t == c and p != c for t, p in pairs)
        scores.append(2 * tp / (2 * tp + fp + fn) if tp else 0.0)
    return sum(scores) / len(scores)


def fit_nb(rows: Sequence[Row], bags: Bags, m: float | None) -> NaiveBayesModel:
    return train_naive_bayes(
        [bags[r["unit_id"]] for r in rows], [r["final_label"] for r in rows], m
    )


def fit_knn(rows: Sequence[Row], bags: Bags, k: int) -> KnnModel:
    return train_knn(
        [bags[r["unit_id"]] for r in rows],
        [r["final_label"] for r in rows],
        [r["unit_id"] for r in rows],
        k,
    )


def vocabulary_size(rows: Sequence[Row], bags: Bags) -> int:
    return len({w for r in rows for w in bags[r["unit_id"]]})


@dataclass(frozen=True)
class Tuning:
    vocab_train: int
    # (ตัวคูณ m, accuracy บน dev) / (k, accuracy บน dev) ตามลำดับใน config
    nb: tuple[tuple[float, float], ...]
    knn: tuple[tuple[int, float], ...]
    best_m_factor: float
    best_k: int


def tune(train: Sequence[Row], dev: Sequence[Row], bags: Bags, cfg: dict) -> Tuning:
    """ลองค่าใน [classify] ของ config บน dev แล้วเลือกค่าดีสุด (เท่ากันเลือกค่าแรก)."""
    vocab_train = vocabulary_size(train, bags)
    nb_tuning = []
    for f in cfg["nb_m_factors"]:
        model = fit_nb(train, bags, f * vocab_train)
        nb_tuning.append((f, accuracy(dev, lambda u, m=model: m.predict(bags[u]))))
    knn_tuning = []
    for k in cfg["knn_k_values"]:
        model = fit_knn(train, bags, k)
        knn_tuning.append((k, accuracy(dev, lambda u, m=model: m.predict(bags[u]))))
    return Tuning(
        vocab_train=vocab_train,
        nb=tuple(nb_tuning),
        knn=tuple(knn_tuning),
        best_m_factor=max(nb_tuning, key=lambda t: t[1])[0],
        best_k=max(knn_tuning, key=lambda t: t[1])[0],
    )
