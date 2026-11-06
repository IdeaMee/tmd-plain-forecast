import math
from collections import Counter

import pytest

from tmd_plain.classify.knn import KnnModel, l2_distance, train_knn, unit_vector

# ตัวอย่างคำนวณมือ: u1 = {a} ป้าย x, u2 = {b} ป้าย y, u3 = {a,b} ป้าย y; คำถาม {a:2} → เวกเตอร์ยาว 1 = (1, 0)
# ระยะ: u1 = 0, u2 = √2 ≈ 1.414, u3 = √((1-1/√2)² + (1/√2)²) = √(2-√2) ≈ 0.765
BAGS = [Counter(a=1), Counter(b=1), Counter(a=1, b=1)]
LABELS = ["x", "y", "y"]
IDS = ["u1", "u2", "u3"]
QUERY = Counter(a=2)


def test_distances_match_hand_calculation() -> None:
    q = unit_vector(QUERY)
    assert q == {"a": 1.0}
    dists = [l2_distance(q, unit_vector(b)) for b in BAGS]
    assert dists == pytest.approx([0.0, math.sqrt(2), math.sqrt(2 - math.sqrt(2))])


@pytest.mark.parametrize(("k", "expected"), [(1, "x"), (2, "x"), (3, "y")])
def test_vote_matches_hand_calculation(k: int, expected: str) -> None:
    # k=2: x 1 เสียง (ระยะ 0) กับ y 1 เสียง (0.765) เสมอ → ระยะรวมน้อยกว่าชนะ = x
    # k=3: y 2 เสียงชนะ x 1 เสียง
    assert train_knn(BAGS, LABELS, IDS, k).predict(QUERY) == expected


def test_neighbors_order_and_json_round_trip() -> None:
    model = train_knn(BAGS, LABELS, IDS, k=2)
    assert [uid for _, _, uid in model.neighbors(QUERY)] == ["u1", "u3"]
    assert KnnModel.from_json(model.to_json()) == model
    with pytest.raises(ValueError):
        train_knn(BAGS, LABELS, IDS, k=0)
