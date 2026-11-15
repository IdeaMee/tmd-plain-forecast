"""โหลดตัวจัดประเภทที่อนุมัติ (models/selected.json): ป้ายของข้อความ และคำอธิบายสำหรับภาพขั้นตอน.

ชนิดเอกสารที่มีตัวเฉพาะ (models/<ชนิด>_selected.json เช่น warning ใน 11.3) โหลดติดมาด้วย เรียกผ่าน for_doc()
"""

from __future__ import annotations

import json
import math
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path

from tmd_plain.classify.features import bag_of_words
from tmd_plain.classify.knn import KnnModel
from tmd_plain.classify.naive_bayes import NaiveBayesModel

TOP_WORDS = 5
LABEL_CACHE_SIZE = 4096
# ชนิดเอกสารที่อาจมีตัวจัดประเภทของตัวเอง (ไม่มีไฟล์ = ใช้ตัวของรายวัน)
SPECIFIC_DOC_TYPES = ("warning",)


@dataclass(frozen=True)
class Explanation:
    label: str
    # คะแนนต่อป้ายรวมเป็น 1: NB = posterior จาก log score, k-NN = สัดส่วนเสียงโหวต
    scores: dict[str, float]
    # คำที่ดันป้ายที่เลือกมากที่สุด (NB) หรือ unit_id ของเพื่อนบ้าน (k-NN)
    top_words: tuple[str, ...]
    # คำของหน่วยที่ไม่อยู่ในคลังคำของโมเดล (ถูกข้ามตอนคำนวณ)
    unknown_words: tuple[str, ...]


@dataclass(frozen=True)
class Classifier:
    name: str
    label: Callable[[str], str]
    explain: Callable[[str], Explanation]
    # ชนิดเอกสาร -> ตัวจัดประเภทเฉพาะชนิด (เรียงตามชื่อชนิด เพื่อให้ dataclass frozen เทียบค่าได้)
    specific: tuple[tuple[str, Classifier], ...] = ()
    # ตัวเฉพาะชนิดบอกชนิดของตัวเอง (ตัวหลัก = "")
    doc_type: str = ""

    def for_doc(self, doc_type: str) -> Classifier:
        """ตัวเฉพาะของชนิดนี้ถ้ามี ไม่มีใช้ตัวหลัก (รายวัน/7 วัน)."""
        return dict(self.specific).get(doc_type, self)


def _softmax(log_scores: dict[str, float]) -> dict[str, float]:
    top = max(log_scores.values())
    exp = {c: math.exp(s - top) for c, s in log_scores.items()}
    total = sum(exp.values())
    return {c: v / total for c, v in exp.items()}


def word_push(nb: NaiveBayesModel, bag: Counter[str], label: str) -> list[tuple[str, float]]:
    """แรงดันของแต่ละคำที่มีในคลังคำต่อป้าย label เรียงมากไปน้อย (เท่ากันเรียงตามคำ).

    แรงดัน = จำนวนครั้ง x (log P(w|label) - log P(w|ป้ายอื่นที่ใกล้สุด)) ค่าบวก = ดันไปทาง label
    """
    table = nb.log_likelihood[label]
    others = [c for c in nb.labels if c != label]
    out = []
    for w in bag:
        if w in table:
            best_other = max((nb.log_likelihood[c][w] for c in others), default=0.0)
            out.append((w, bag[w] * (table[w] - best_other)))
    return sorted(out, key=lambda p: (-p[1], p[0]))


def posterior(nb: NaiveBayesModel, bag: Counter[str]) -> dict[str, float]:
    """คะแนน log ของแต่ละป้าย -> ความน่าจะเป็นรวมเป็น 1."""
    return _softmax(nb.scores(bag))


def explain_naive_bayes(nb: NaiveBayesModel, bag: Counter[str]) -> Explanation:
    label = nb.predict(bag)
    pushes = word_push(nb, bag, label)
    return Explanation(
        label=label,
        scores=posterior(nb, bag),
        top_words=tuple(w for w, p in pushes[:TOP_WORDS] if p > 0),
        unknown_words=tuple(sorted(w for w in bag if w not in nb.log_likelihood[label])),
    )


def explain_knn(knn: KnnModel, bag: Counter[str]) -> Explanation:
    near = knn.neighbors(bag)
    votes = Counter(label for _, label, _ in near)
    known = {w for v in knn.vectors for w in v}
    return Explanation(
        label=knn.predict(bag),
        scores={c: n / len(near) for c, n in sorted(votes.items())},
        top_words=tuple(uid for _, _, uid in near[:TOP_WORDS]),
        unknown_words=tuple(sorted(w for w in bag if w not in known)),
    )


def _load_one(models_dir: Path, prefix: str) -> Classifier:
    selected = json.loads((models_dir / f"{prefix}selected.json").read_text(encoding="utf-8"))[
        "model"
    ]
    data = json.loads((models_dir / f"{prefix}{selected}.json").read_text(encoding="utf-8"))
    model: NaiveBayesModel | KnnModel
    if selected == "naive_bayes":
        model = NaiveBayesModel.from_json(data)
    elif selected == "knn":
        model = KnnModel.from_json(data)
    else:
        raise ValueError(f"ไม่รู้จักโมเดล {selected!r}")

    def predict(text: str) -> str:
        return model.predict(bag_of_words(text))

    def explain(text: str) -> Explanation:
        bag = bag_of_words(text)
        if isinstance(model, NaiveBayesModel):
            return explain_naive_bayes(model, bag)
        return explain_knn(model, bag)

    return Classifier(name=selected, label=predict, explain=explain, doc_type=prefix.rstrip("_"))


def load_classifier(models_dir: Path) -> Classifier:
    """ตัวหลัก (selected.json) + ตัวเฉพาะชนิดที่มีไฟล์ <ชนิด>_selected.json."""
    specific = tuple(
        (key, _load_one(models_dir, f"{key}_"))
        for key in sorted(SPECIFIC_DOC_TYPES)
        if (models_dir / f"{key}_selected.json").exists()
    )
    return replace(_load_one(models_dir, ""), specific=specific)


def with_label_cache(classifier: Classifier) -> Classifier:
    """สำเนาที่จำป้ายตามข้อความ ใช้ต่อหนึ่งคำขอ (ภาพขั้นตอนนับป้ายซ้ำโดยไม่ตัดคำใหม่).

    สร้างใหม่ทุกคำขอ ไม่ให้ข้อความจากไฟล์ของผู้ใช้คนก่อนค้างในหน่วยความจำของฟังก์ชัน
    """
    return replace(
        classifier,
        label=lru_cache(maxsize=LABEL_CACHE_SIZE)(classifier.label),
        specific=tuple((key, with_label_cache(c)) for key, c in classifier.specific),
    )


def load_labeler(models_dir: Path) -> Callable[[str], str]:
    """ฟังก์ชัน ข้อความ -> ป้าย (ใช้ในสคริปต์และท่อประมวลผลเดิม)."""
    return load_classifier(models_dir).label
