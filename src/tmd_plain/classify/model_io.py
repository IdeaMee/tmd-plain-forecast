"""โหลดตัวจัดประเภทที่อนุมัติ (models/selected.json) เป็นฟังก์ชัน ข้อความ -> ป้าย."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from tmd_plain.classify.features import bag_of_words
from tmd_plain.classify.knn import KnnModel
from tmd_plain.classify.naive_bayes import NaiveBayesModel


def load_labeler(models_dir: Path) -> Callable[[str], str]:
    selected = json.loads((models_dir / "selected.json").read_text(encoding="utf-8"))["model"]
    data = json.loads((models_dir / f"{selected}.json").read_text(encoding="utf-8"))
    if selected == "naive_bayes":
        nb = NaiveBayesModel.from_json(data)
        return lambda text: nb.predict(bag_of_words(text))
    if selected == "knn":
        knn = KnnModel.from_json(data)
        return lambda text: knn.predict(bag_of_words(text))
    raise ValueError(f"ไม่รู้จักโมเดล {selected!r}")
