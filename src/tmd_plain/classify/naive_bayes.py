"""Naive Bayes สำหรับข้อความ (เขียนเอง ตามสไลด์ ML 08 Learn/Classify_naive_Bayes_text).

P(w|c) = (n_k + m*p) / (n + m) โดย p = 1/|Vocabulary| (m-estimate; m = |Vocabulary| คือ add-one)
P(c) = จำนวนหน่วยของป้าย / จำนวนหน่วยทั้งหมด · คำนวณเป็นผลรวม log กัน underflow
คำที่ไม่อยู่ใน Vocabulary ถูกข้าม (ตาม "Positions" ในสไลด์)
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NaiveBayesModel:
    labels: tuple[str, ...]
    log_prior: dict[str, float]
    # log P(w|c) ของคำใน Vocabulary
    log_likelihood: dict[str, dict[str, float]]
    m: float
    vocabulary_size: int

    def scores(self, bag: Counter[str]) -> dict[str, float]:
        out: dict[str, float] = {}
        for c in self.labels:
            table = self.log_likelihood[c]
            out[c] = self.log_prior[c] + sum(n * table[w] for w, n in bag.items() if w in table)
        return out

    def predict(self, bag: Counter[str]) -> str:
        s = self.scores(bag)
        # คะแนนเท่ากันให้ป้ายที่มาก่อนตามลำดับตัวอักษร (ผลซ้ำได้)
        return max(sorted(s), key=lambda c: s[c])

    def to_json(self) -> dict[str, Any]:
        return {
            "kind": "naive_bayes",
            "labels": list(self.labels),
            "m": self.m,
            "vocabulary_size": self.vocabulary_size,
            "log_prior": self.log_prior,
            "log_likelihood": self.log_likelihood,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> NaiveBayesModel:
        return cls(
            labels=tuple(data["labels"]),
            log_prior=dict(data["log_prior"]),
            log_likelihood={c: dict(t) for c, t in data["log_likelihood"].items()},
            m=float(data["m"]),
            vocabulary_size=int(data["vocabulary_size"]),
        )


def train_naive_bayes(
    bags: Sequence[Counter[str]], labels: Sequence[str], m: float | None = None
) -> NaiveBayesModel:
    """ฝึกจากหน่วย (bag of words) กับป้าย; m=None ใช้ |Vocabulary| (add-one)."""
    if len(bags) != len(labels) or not bags:
        raise ValueError("จำนวนหน่วยกับป้ายต้องเท่ากันและไม่ว่าง")
    vocabulary = sorted({w for bag in bags for w in bag})
    v = len(vocabulary)
    m_value = float(v) if m is None else float(m)
    if m_value <= 0:
        raise ValueError("m ต้องมากกว่า 0")
    p = 1.0 / v
    classes = sorted(set(labels))
    text_counts: dict[str, Counter[str]] = {c: Counter() for c in classes}
    for bag, c in zip(bags, labels, strict=True):
        text_counts[c].update(bag)
    doc_counts = Counter(labels)
    log_prior = {c: math.log(doc_counts[c] / len(labels)) for c in classes}
    log_likelihood: dict[str, dict[str, float]] = {}
    for c in classes:
        n = sum(text_counts[c].values())
        log_likelihood[c] = {
            w: math.log((text_counts[c][w] + m_value * p) / (n + m_value)) for w in vocabulary
        }
    return NaiveBayesModel(tuple(classes), log_prior, log_likelihood, m_value, v)
