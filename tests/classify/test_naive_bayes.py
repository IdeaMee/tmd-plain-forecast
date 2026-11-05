import math
from collections import Counter

import pytest

from tmd_plain.classify.features import NUM_TOKEN, normalize_tokens
from tmd_plain.classify.naive_bayes import NaiveBayesModel, train_naive_bayes

# ตัวอย่างคำนวณมือ (สูตรสไลด์ ML 08):
# ชุดฝึก: x = {a:2}, x = {a:1,b:1}, y = {c:1} → Vocabulary {a,b,c} |V|=3, add-one: m=3, p=1/3, mp=1
# x: n=4 → P(a|x)=4/7, P(b|x)=2/7, P(c|x)=1/7 · y: n=1 → P(a|y)=1/4, P(b|y)=1/4, P(c|y)=2/4
# P(x)=2/3, P(y)=1/3
BAGS = [Counter(a=2), Counter(a=1, b=1), Counter(c=1)]
LABELS = ["x", "x", "y"]


def test_add_one_probabilities_match_hand_calculation() -> None:
    model = train_naive_bayes(BAGS, LABELS)
    assert model.m == 3 and model.vocabulary_size == 3
    expected = {
        "x": {"a": 4 / 7, "b": 2 / 7, "c": 1 / 7},
        "y": {"a": 1 / 4, "b": 1 / 4, "c": 2 / 4},
    }
    for c, table in expected.items():
        for w, prob in table.items():
            assert math.exp(model.log_likelihood[c][w]) == pytest.approx(prob)
    assert math.exp(model.log_prior["x"]) == pytest.approx(2 / 3)


def test_classify_matches_hand_calculation() -> None:
    model = train_naive_bayes(BAGS, LABELS)
    # {a,c}: x = 2/3·4/7·1/7 = 8/147 ≈ 0.0544 > y = 1/3·1/4·2/4 = 1/24 ≈ 0.0417
    s = model.scores(Counter(a=1, c=1))
    assert math.exp(s["x"]) == pytest.approx(8 / 147)
    assert math.exp(s["y"]) == pytest.approx(1 / 24)
    assert model.predict(Counter(a=1, c=1)) == "x"
    # {c:2}: x = 2/3·(1/7)² = 2/147 < y = 1/3·(1/2)² = 1/12
    assert model.predict(Counter(c=2)) == "y"
    # คำนอก Vocabulary ถูกข้าม คะแนนเท่ากับไม่มีคำนั้น
    assert model.scores(Counter(a=1, z=5)) == model.scores(Counter(a=1))


def test_m_estimate_with_other_m() -> None:
    # m=1.5, p=1/3 → mp=0.5: P(a|x) = (3+0.5)/(4+1.5)
    model = train_naive_bayes(BAGS, LABELS, m=1.5)
    assert math.exp(model.log_likelihood["x"]["a"]) == pytest.approx(3.5 / 5.5)
    assert math.exp(model.log_likelihood["y"]["c"]) == pytest.approx(1.5 / 2.5)


def test_json_round_trip_and_bad_input() -> None:
    model = train_naive_bayes(BAGS, LABELS)
    assert NaiveBayesModel.from_json(model.to_json()) == model
    with pytest.raises(ValueError):
        train_naive_bayes([], [])
    with pytest.raises(ValueError):
        train_naive_bayes(BAGS, LABELS, m=0)


def test_normalize_tokens_merges_numbers_and_drops_punctuation() -> None:
    assert normalize_tokens(["คลื่น", "สูง", "2", "-", "3.5", "เมตร", "(", "๒๕"]) == [
        "คลื่น",
        "สูง",
        NUM_TOKEN,
        NUM_TOKEN,
        "เมตร",
        NUM_TOKEN,
    ]
