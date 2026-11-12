"""รายงานโมเดลของหน้า /model (Phase 8.1): ตรงกับผลวัดเดิม ไม่เก่า และนับครบ."""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

from tmd_plain.classify.evaluate import accuracy, macro_f1
from tmd_plain.classify.features import bag_of_words
from tmd_plain.classify.knn import KnnModel
from tmd_plain.classify.naive_bayes import NaiveBayesModel
from tmd_plain.labeled_io import load_labeled_rows
from tmd_plain.model_report import ModelReport

ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "lib" / "generated"
sys.path.insert(0, str(ROOT / "scripts"))
import export_model_report  # noqa: E402

REPORT = ModelReport.model_validate_json(
    (GENERATED / "model-report.json").read_text(encoding="utf-8")
)
SR = REPORT.models[0]
ROWS = load_labeled_rows(ROOT / "data" / "labeled")
BAGS = {r["unit_id"]: bag_of_words(r["text"]) for r in ROWS}


def _load(name: str) -> dict:
    return json.loads((ROOT / "models" / "eval" / name).read_text(encoding="utf-8"))


def test_generated_files_are_not_stale() -> None:
    for name, body in export_model_report.build().items():
        assert (GENERATED / name).read_text(encoding="utf-8") == body, (
            f"{name}: รัน scripts/export_model_report.py"
        )


def test_results_match_saved_eval_models() -> None:
    # โมเดลที่ใช้วัดผล (models/eval, ฝึกจากชุดฝึก) ต้องให้ accuracy เท่ากับในรายงาน
    nb = NaiveBayesModel.from_json(_load("naive_bayes.json"))
    knn = KnnModel.from_json(_load("knn.json"))
    test_new = [r for r in ROWS if r["split"] == "test"]
    dev = [r for r in ROWS if r["split"] == "dev"]
    by_name = {r.name: r for r in SR.results}
    for name, model in (("Naive Bayes", nb), ("k-NN", knn)):
        predict = lambda u, m=model: m.predict(BAGS[u])  # noqa: E731
        assert by_name[name].test_new == round(accuracy(test_new, predict), 4)
        assert by_name[name].dev == round(accuracy(dev, predict), 4)
    assert SR.chosen == "Naive Bayes"
    assert len(SR.mistakes) == sum(
        nb.predict(BAGS[r["unit_id"]]) != r["final_label"] for r in test_new
    )


def test_counts_cover_all_units() -> None:
    assert SR.facts.total_units == len(ROWS) == 292
    assert sum(s.total for s in SR.splits) == 292
    assert sum(sum(c.values()) for c in SR.by_doc_type.values()) == 292
    assert Counter(r["final_label"] for r in ROWS) == Counter(
        {k: sum(s.by_label[k] for s in SR.splits) for k in SR.labels}
    )


def test_learning_curve_ends_at_full_train() -> None:
    last = SR.learning_curve[-1]
    assert last.fraction == 1.0
    assert last.train_units == next(s.total for s in SR.splits if s.split == "train")
    assert last.nb_dev_accuracy == next(r.dev for r in SR.results if r.name == "Naive Bayes")
    units = [p.train_units for p in SR.learning_curve]
    assert units == sorted(units)


def test_examples_come_from_the_right_split() -> None:
    split_of = {r["unit_id"]: r["split"] for r in ROWS}
    assert all(split_of[e.unit_id] == "train" for e in SR.token_examples)
    assert all(split_of[e.unit_id] == "test" for e in SR.nb_examples)
    assert all(split_of[n.unit_id] == "train" for e in SR.knn_examples for n in e.neighbors)
    assert any(not e.correct for e in SR.nb_examples)
    for e in SR.nb_examples:
        assert abs(sum(e.posterior.values()) - 1) < 1e-3
        assert e.predicted == max(e.log_score, key=lambda c: e.log_score[c])


def test_macro_f1_small_example() -> None:
    rows = [
        {"unit_id": "a", "final_label": "x"},
        {"unit_id": "b", "final_label": "x"},
        {"unit_id": "c", "final_label": "y"},
    ]
    guess = {"a": "x", "b": "y", "c": "y"}
    # x: P=1 R=0.5 F1=2/3 · y: P=0.5 R=1 F1=2/3
    assert abs(macro_f1(rows, guess.__getitem__) - 2 / 3) < 1e-9


WARNING = next(m for m in REPORT.models if m.id == "warning-role")


def test_warning_report_matches_saved_warning_models() -> None:
    # 11.3: ตัวเลขของแท็บประกาศตรงกับ models/eval/warning_*.json (scripts/train_eval_warning.py)
    with (ROOT / "data" / "labeled" / "warning" / "units_labeled.csv").open(
        encoding="utf-8", newline=""
    ) as f:
        rows = list(csv.DictReader(f))
    bags = {r["unit_id"]: bag_of_words(r["text"]) for r in rows}
    test_new = [r for r in rows if r["split"] == "test"]
    by_name = {r.name: r for r in WARNING.results}
    for name, model in (
        ("Naive Bayes", NaiveBayesModel.from_json(_load("warning_naive_bayes.json"))),
        ("k-NN", KnnModel.from_json(_load("warning_knn.json"))),
    ):
        predict = lambda u, m=model: m.predict(bags[u])  # noqa: E731
        assert by_name[name].test_new == round(accuracy(test_new, predict), 4)
    assert WARNING.labels == ["weather", "advice", "cause"]
    assert WARNING.facts.total_units == len(rows) == sum(s.total for s in WARNING.splits)
    assert all(r.test_all_weighted is None for r in WARNING.results)
    assert WARNING.learning_curve[-1].train_units == next(
        s.total for s in WARNING.splits if s.split == "train"
    )
    # ตัวของรายวันอยู่ในตารางผลวัดเท่านั้น (ทายป้าย other ได้ จึงไม่มีตารางสับสน)
    assert len(WARNING.results) == len(WARNING.confusion) + 1
