"""k-NN (เขียนเอง ตามบันทึก ML 04): ระยะ L2 (Euclidean) ระหว่างเวกเตอร์ความถี่คำ.

ปรับเวกเตอร์ให้ยาว 1 ก่อน (L2 normalize) เพื่อไม่ให้ประโยคยาวอยู่ไกลจากทุกตัวเพียงเพราะยาว
(ระยะ L2 ของเวกเตอร์ยาว 1 เรียงลำดับเหมือน cosine similarity ที่บันทึกแนะนำสำหรับข้อความ)
โหวตเสียงข้างมากใน k ตัวใกล้สุด เสมอกันให้ป้ายที่มีระยะรวมน้อยกว่า แล้วตามลำดับตัวอักษร
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any


def unit_vector(bag: Counter[str]) -> dict[str, float]:
    norm = math.sqrt(sum(n * n for n in bag.values()))
    if norm == 0:
        return {}
    return {w: n / norm for w, n in bag.items()}


def l2_distance(a: dict[str, float], b: dict[str, float]) -> float:
    keys = a.keys() | b.keys()
    return math.sqrt(sum((a.get(k, 0.0) - b.get(k, 0.0)) ** 2 for k in keys))


@dataclass(frozen=True)
class KnnModel:
    k: int
    vectors: tuple[dict[str, float], ...]
    labels: tuple[str, ...]
    ids: tuple[str, ...]

    def neighbors(self, bag: Counter[str]) -> list[tuple[float, str, str]]:
        """(ระยะ, ป้าย, unit_id) ของ k ตัวใกล้สุด เสมอกันเรียงตาม unit_id."""
        q = unit_vector(bag)
        dists = sorted(
            (l2_distance(q, v), self.ids[i], self.labels[i]) for i, v in enumerate(self.vectors)
        )
        return [(d, label, uid) for d, uid, label in dists[: self.k]]

    def predict(self, bag: Counter[str]) -> str:
        near = self.neighbors(bag)
        votes = Counter(label for _, label, _ in near)
        total = {c: sum(d for d, label, _ in near if label == c) for c in votes}
        return min(votes, key=lambda c: (-votes[c], total[c], c))

    def to_json(self) -> dict[str, Any]:
        return {
            "kind": "knn",
            "k": self.k,
            "distance": "l2 on l2-normalized term counts",
            "examples": [
                {"unit_id": uid, "label": label, "vector": vec}
                for uid, label, vec in zip(self.ids, self.labels, self.vectors, strict=True)
            ],
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> KnnModel:
        ex = data["examples"]
        return cls(
            k=int(data["k"]),
            vectors=tuple(dict(e["vector"]) for e in ex),
            labels=tuple(e["label"] for e in ex),
            ids=tuple(e["unit_id"] for e in ex),
        )


def train_knn(
    bags: Sequence[Counter[str]], labels: Sequence[str], ids: Sequence[str], k: int
) -> KnnModel:
    """k-NN ไม่มีการฝึกจริง แค่เก็บเวกเตอร์ของชุดฝึก."""
    if not (len(bags) == len(labels) == len(ids)) or not bags:
        raise ValueError("จำนวนหน่วย ป้าย และ id ต้องเท่ากันและไม่ว่าง")
    if k < 1:
        raise ValueError("k ต้องอย่างน้อย 1")
    return KnnModel(k, tuple(unit_vector(b) for b in bags), tuple(labels), tuple(ids))
