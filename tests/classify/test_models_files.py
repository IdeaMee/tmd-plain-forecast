import json
from pathlib import Path

import pytest

from tmd_plain.classify.features import bag_of_words
from tmd_plain.classify.knn import KnnModel
from tmd_plain.classify.naive_bayes import NaiveBayesModel

MODELS = Path(__file__).resolve().parents[2] / "models"


def load(name: str) -> dict:
    path = MODELS / name
    if not path.exists():
        pytest.skip("ยังไม่ได้รัน scripts/train_eval.py")
    return json.loads(path.read_text(encoding="utf-8"))


def test_saved_models_load_and_predict() -> None:
    # โมเดลที่ท่อประมวลผลใช้ต้องโหลดจาก JSON ได้และทายประโยคชัด ๆ ถูก
    nb = NaiveBayesModel.from_json(load("naive_bayes.json"))
    knn = KnnModel.from_json(load("knn.json"))
    assert load("selected.json")["model"] in {"naive_bayes", "knn"}
    for text, label in [
        ("ขอให้ประชาชนระวังอันตรายจากฝนตกหนัก", "advice"),
        ("เนื่องจากมรสุมตะวันออกเฉียงเหนือพัดปกคลุมอ่าวไทย", "cause"),
        ("ภาคใต้มีฝนตกหนักบางแห่ง", "weather"),
    ]:
        assert nb.predict(bag_of_words(text)) == label
        assert knn.predict(bag_of_words(text)) == label
