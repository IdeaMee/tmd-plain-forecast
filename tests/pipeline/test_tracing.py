import math
from collections import Counter
from pathlib import Path

import pytest

from tmd_plain.classify.features import bag_of_words
from tmd_plain.classify.knn import train_knn
from tmd_plain.classify.model_io import explain_knn, explain_naive_bayes, load_classifier
from tmd_plain.classify.naive_bayes import NaiveBayesModel, train_naive_bayes
from tmd_plain.contract import TRACE_MAX_BYTES, TRACE_MAX_ITEMS
from tmd_plain.doctypes.registry import generic_spec, registry, spec_for
from tmd_plain.tracing import SIZE_BUDGET, STEP_TITLES_TH, StepDraft, build_trace

ROOT = Path(__file__).resolve().parents[2]


def test_every_step_has_a_thai_title() -> None:
    from typing import get_args

    from tmd_plain.contract import TraceStepId

    assert set(STEP_TITLES_TH) == set(get_args(TraceStepId))


def test_long_lists_are_capped_and_flagged() -> None:
    trace = build_trace(
        [StepDraft("units", data={"units": [str(i) for i in range(80)], "count": 80})]
    )
    assert trace.truncated
    assert trace.steps[0].data["units"] == [str(i) for i in range(TRACE_MAX_ITEMS)]
    assert trace.steps[0].data["count"] == 80
    small = build_trace([StepDraft("units", data={"units": ["a"]})])
    assert not small.truncated and small.steps[0].title_th == "แบ่งหน่วยประโยค"


def test_oversized_trace_drops_biggest_step_data() -> None:
    big = ["ก" * 2000] * TRACE_MAX_ITEMS
    drafts = [
        StepDraft("units", data={"units": big}),
        StepDraft("tokenize", data={"tokens": big}),
        StepDraft("result", data={"lines": 3}),
    ]
    trace = build_trace(drafts)
    assert trace.truncated
    assert SIZE_BUDGET < TRACE_MAX_BYTES
    kept = [s for s in trace.steps if s.data]
    assert any(s.id == "result" for s in kept)
    assert any("ตัดข้อมูล" in s.note_th for s in trace.steps)


def _toy_nb() -> NaiveBayesModel:
    texts = ["ขอให้ประชาชนระวังอันตราย", "มีฝนตกหนักบางแห่ง", "ขอให้ชาวเรือระวัง", "อุณหภูมิต่ำสุด 20 องศา"]
    labels = ["advice", "weather", "advice", "weather"]
    return train_naive_bayes([bag_of_words(t) for t in texts], labels)


def test_naive_bayes_explanation_matches_prediction() -> None:
    nb = _toy_nb()
    bag = bag_of_words("ขอให้ประชาชนระวังฝน คำแปลกๆ")
    ex = explain_naive_bayes(nb, bag)
    assert ex.label == nb.predict(bag)
    assert math.isclose(sum(ex.scores.values()), 1.0)
    assert max(ex.scores, key=ex.scores.get) == ex.label
    assert "ขอให้" in ex.top_words
    assert all(w not in nb.log_likelihood[ex.label] for w in ex.unknown_words)


def test_knn_explanation_is_vote_share() -> None:
    bags = [Counter({"ฝน": 1}), Counter({"ฝน": 2}), Counter({"ระวัง": 1})]
    knn = train_knn(bags, ["weather", "weather", "advice"], ["a", "b", "c"], k=3)
    ex = explain_knn(knn, Counter({"ฝน": 1}))
    assert ex.label == "weather"
    assert math.isclose(ex.scores["weather"], 2 / 3)
    assert set(ex.top_words) == {"a", "b", "c"}


def test_registry_routes_known_types_and_falls_back_to_generic() -> None:
    assert set(registry()) == {"daily", "sevenday", "shipping", "warning"}
    assert registry()["shipping"].kind == "shipping"
    assert registry()["warning"].kind == "warning"
    # 11.4: ประกาศเตือนภัยได้หน้าแสดงผลแล้ว /demo ใช้ท่อของประกาศ (ไม่ส่งไปโหมดทั่วไปอีก)
    head = "ประกาศกรมอุตุนิยมวิทยา\nเรื่อง ฝนตกหนักบริเวณภาคใต้\nฉบับที่ 1 (300/2569)\n-----\nเนื้อหา"
    assert spec_for(head) is registry()["warning"]
    assert spec_for("คาดหมายอากาศทั่วไป\nคาดหมายอากาศรายภาค").key == "sevenday"
    assert spec_for("ลักษณะอากาศทั่วไป\nพยากรณ์อากาศสำหรับประเทศไทย").kind == "issue"
    # 10.3: ชนิดที่ไม่รู้จักไปโหมดทั่วไป ไม่ปฏิเสธ
    assert spec_for("Introduction to Machine Learning") is generic_spec()
    assert generic_spec().kind == "generic"


def test_real_classifier_label_and_explain_agree() -> None:
    if not (ROOT / "models" / "selected.json").exists():
        pytest.skip("ไม่มีโมเดล")
    clf = load_classifier(ROOT / "models")
    text = "ขอให้ประชาชนระวังอันตรายจากฝนตกหนัก"
    assert clf.explain(text).label == clf.label(text)
