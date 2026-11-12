"""รายงานโมเดลสำหรับหน้า /model (Phase 8.1): ทุกตัวเลขและตัวอย่างที่หน้าเว็บแสดง คำนวณจากข้อมูลจริง.

ใช้ฟังก์ชันเดิมของ classify/ ทั้งหมด (ไม่เขียน Naive Bayes / k-NN ซ้ำ) และไม่แตะ models/*.json ที่ท่อประมวลผลใช้
หลายโมเดล (models: list): ประโยคของรายวัน/7 วัน (8.1) + ท่อนของประกาศเตือนภัย (11.3) สร้างด้วยฟังก์ชันเดียวกัน
ต่างกันแค่ ReportSpec (ป้าย ชุด หน่วยของการแบ่งชุด ขั้นของท่อ ข้อความอธิบาย)
ไฟล์ผล: lib/generated/model-report.json (scripts/export_model_report.py) · schema: lib/generated/model-report.schema.json
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from tmd_plain.classify.evaluate import (
    ERROR_NOTES,
    Bags,
    Predict,
    Row,
    accuracy,
    fit_knn,
    fit_nb,
    macro_f1,
    tune,
    vocabulary_size,
)
from tmd_plain.classify.features import NUM_TOKEN, bag_of_words, normalize_tokens
from tmd_plain.classify.keyword import keyword_label
from tmd_plain.classify.knn import KnnModel
from tmd_plain.classify.model_io import posterior, word_push
from tmd_plain.classify.naive_bayes import NaiveBayesModel
from tmd_plain.contract import LABELS
from tmd_plain.doctypes.warning.dataset import WARNING_LABELS
from tmd_plain.prep.tokenize import tokenize

REPORT_VERSION = "2"
DIGITS = 4
TOP_WORDS_PER_LABEL = 15
PUSH_WORDS = 5
NEIGHBORS = 3
LEARNING_FRACTIONS = (0.25, 0.5, 0.75, 1.0)
SPLITS = ("train", "dev", "test", "gap")
WARNING_SPLITS = ("train", "dev", "test")

LABELS_TH = {"weather": "สภาพอากาศ", "cause": "สาเหตุ", "advice": "คำแนะนำ", "other": "อื่นๆ"}
NB, KNN, KEYWORD = "Naive Bayes", "k-NN", "กฎ keyword (baseline)"


class _Model(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class PipelineStep(_Model):
    id: str
    title_th: str
    # rule = กฎที่เขียนเอง, ml = โมเดลที่เรียนจากข้อมูล
    kind: Literal["rule", "ml"]
    detail_th: str


class SplitCount(_Model):
    split: str
    total: int
    by_label: dict[str, int]


class TokenExample(_Model):
    unit_id: str
    label: str
    text: str
    tokens: list[str]
    dropped: list[str]
    kept: list[str]
    counts: dict[str, int]


class WordScore(_Model):
    word: str
    score: float


class NbExample(_Model):
    unit_id: str
    text: str
    true_label: str
    predicted: str
    correct: bool
    log_prior: dict[str, float]
    log_score: dict[str, float]
    posterior: dict[str, float]
    # คำที่ดันไปทางป้ายที่ทาย (แรงดัน = จำนวนครั้ง x ส่วนต่าง log P(w|c) กับป้ายอื่นที่ใกล้สุด)
    push_words: list[WordScore]
    unknown_words: list[str]


class Neighbor(_Model):
    unit_id: str
    text: str
    label: str
    distance: float


class KnnExample(_Model):
    unit_id: str
    text: str
    true_label: str
    predicted: str
    neighbors: list[Neighbor]


class TuningPoint(_Model):
    value: float
    dev_accuracy: float


class Tuning(_Model):
    nb_m_factor: list[TuningPoint]
    knn_k: list[TuningPoint]
    best_m_factor: float
    best_k: int
    vocab_train: int


class ModelResult(_Model):
    name: str
    dev: float
    test_all: float
    # ถ่วงตามจำนวนครั้งที่พบในชุดทดสอบ (มีเฉพาะรายวัน ชุดของประกาศไม่ได้นับครั้งต่อฉบับ = None)
    test_all_weighted: float | None
    test_new: float


class Confusion(_Model):
    name: str
    # matrix[i][j] = ป้ายจริง labels[i] ทายเป็น labels[j] บนทดสอบ (ข) ถ้อยคำใหม่
    matrix: list[list[int]]


class LearningPoint(_Model):
    fraction: float
    # จำนวนกลุ่มที่ใช้ฝึก (วันของรายวัน, เหตุการณ์ของประกาศ) ชื่อกลุ่มอยู่ที่ group_th
    train_groups: int
    train_units: int
    nb_dev_accuracy: float
    nb_dev_macro_f1: float
    knn_dev_accuracy: float
    knn_dev_macro_f1: float


class Mistake(_Model):
    unit_id: str
    text: str
    true_label: str
    predicted: str
    confidence: float
    note_th: str


class Facts(_Model):
    total_units: int
    keyword_agrees_with_labels: int
    other_units: int
    vocab_all: int
    num_token: str


class SentenceRoleReport(_Model):
    id: Literal["sentence-role", "warning-role"]
    title_th: str
    # หน่วยที่ใช้แบ่งชุดและกราฟข้อมูลมากขึ้น ("วัน" / "เหตุการณ์") + คำอธิบายการแบ่งชุด
    group_th: str
    split_note_th: str
    labels: list[str]
    labels_th: dict[str, str]
    chosen: str
    label_source_th: str
    pipeline: list[PipelineStep]
    splits: list[SplitCount]
    by_doc_type: dict[str, dict[str, int]]
    token_examples: list[TokenExample]
    top_words: dict[str, list[WordScore]]
    nb_examples: list[NbExample]
    knn_examples: list[KnnExample]
    tuning: Tuning
    results: list[ModelResult]
    confusion: list[Confusion]
    learning_curve: list[LearningPoint]
    mistakes: list[Mistake]
    facts: Facts


class ModelReport(_Model):
    version: str
    models: list[SentenceRoleReport] = Field(min_length=1)


PIPELINE: list[PipelineStep] = [
    PipelineStep(id="clean", title_th="อ่านและทำความสะอาดข้อความ", kind="rule",
                 detail_th="แก้อักขระพิเศษของฟอนต์ไทยใน PDF จัดสระและช่องว่าง"),
    PipelineStep(id="segment", title_th="แบ่งส่วนและแบ่งหน่วยประโยค", kind="rule",
                 detail_th="แยกภาพรวม ข้อควรระวัง และบล็อก 7 ภาค แล้วตัดย่อหน้าเป็นหน่วยตามคำเชื่อม"),
    PipelineStep(id="tokenize", title_th="ตัดคำ", kind="rule",
                 detail_th="PyThaiNLP newmm + พจนานุกรมคำอากาศ ตัวเลขรวมเป็น <num> ทิ้งเครื่องหมาย"),
    PipelineStep(id="classify", title_th="จัดประเภทหน่วยประโยค", kind="ml",
                 detail_th="Naive Bayes ที่เขียนเอง (เทียบ k-NN และกฎ keyword) ป้าย สภาพอากาศ/สาเหตุ/คำแนะนำ/อื่นๆ"),
    PipelineStep(id="scope", title_th="แยกคำแนะนำตามภาค", kind="rule",
                 detail_th="หน่วยที่เป็นคำแนะนำไปภาคที่เอ่ยชื่อ ไม่มีชื่อภาค = ข้อแนะนำทั่วไป"),
    PipelineStep(id="extract", title_th="ดึงข้อเท็จจริง", kind="rule",
                 detail_th="regex ดึงร้อยละพื้นที่ฝน อุณหภูมิ ลม คลื่น จังหวัด จากบล็อกภาค"),
    PipelineStep(id="template", title_th="เขียนตามแม่แบบ + ตรวจ", kind="rule",
                 detail_th="ประกอบประโยคภาษาง่ายจากค่าที่ดึงได้ แล้วตรวจ F1-F5 ว่าทุกตัวเลขมาจากต้นฉบับ"),
]  # fmt: skip

WARNING_PIPELINE: list[PipelineStep] = [
    PipelineStep(id="clean", title_th="อ่านและทำความสะอาดข้อความ", kind="rule",
                 detail_th="ข้อความจาก PDF หรือหน้าเว็บของประกาศ แก้อักขระพิเศษ ต่อบรรทัดที่ถูกตัดกลางประโยค"),
    PipelineStep(id="segment", title_th="แยกหัวประกาศและตัดเป็นท่อน", kind="rule",
                 detail_th="แยกเรื่อง ฉบับที่ ช่วงที่มีผล แล้วตัดเนื้อหาเป็นท่อนตามคำเชื่อม (คำเชื่อมสั้นอย่าง ส่วน/สำหรับ รวมเข้าท่อนถัดไป)"),
    PipelineStep(id="tokenize", title_th="ตัดคำ", kind="rule",
                 detail_th="PyThaiNLP newmm + พจนานุกรมคำอากาศ ตัวเลขรวมเป็น <num> ทิ้งเครื่องหมาย"),
    PipelineStep(id="classify", title_th="จัดประเภทท่อน", kind="ml",
                 detail_th="Naive Bayes ที่เขียนเอง ฝึกจากประกาศ (เทียบ k-NN กฎ keyword และตัวของรายวัน) ป้าย สภาพอากาศ/สาเหตุ/คำแนะนำ"),
    PipelineStep(id="scope", title_th="ภาค จังหวัด และข้อควรระวัง", kind="rule",
                 detail_th="ภาคจากชื่อภาค/จังหวัดในหัวเรื่องและเนื้อหา ท่อนที่เป็นคำแนะนำไปเป็นข้อควรระวังของประกาศ"),
    PipelineStep(id="extract", title_th="ดึงวันที่", kind="rule",
                 detail_th="ช่วงที่มีผล วันประกาศ และฉบับต่อไปจากหัวประกาศ"),
    PipelineStep(id="verify", title_th="ตรวจคำต่อคำ", kind="rule",
                 detail_th="ทุกท่อน ตัวเลข และชื่อจังหวัดต้องอยู่ในต้นฉบับ ไม่ผ่าน = ไม่แสดงผล"),
]  # fmt: skip

LABEL_SOURCE_TH = (
    "ป้ายติดโดยโมเดลภาษา (Claude) ไม่ได้ผ่านคนตรวจ (ADR 0012) ตัวเลขความแม่นจึงวัดว่า"
    "โมเดลทำซ้ำป้ายชุดนี้ได้แค่ไหน ไม่ใช่เทียบกับป้ายที่คนยืนยัน"
)


@dataclass(frozen=True)
class ReportSpec:
    """สิ่งที่ต่างกันระหว่างรายงานของรายวันกับของประกาศ (ส่วนอื่นคำนวณเหมือนกัน)."""

    id: Literal["sentence-role", "warning-role"]
    title_th: str
    group_th: str
    split_note_th: str
    label_source_th: str
    labels: tuple[str, ...]
    splits: tuple[str, ...]
    pipeline: list[PipelineStep]
    # กลุ่มของแถวสำหรับกราฟข้อมูลมากขึ้น (เรียงตามเวลาได้)
    group_of: Callable[[Row], tuple[int, ...]]
    # แถวนี้อยู่ในฉบับของชุดทดสอบไหม (นับรวมหน่วยที่ซ้ำกับชุดฝึก) และถ่วงตามจำนวนครั้งได้ไหม
    in_test: Callable[[Row], bool]
    weighted: bool
    doc_type_of: Callable[[Row], str]
    error_notes: dict[str, str] = field(default_factory=dict)


def _day_key(row: Row) -> tuple[int, ...]:
    return (date.fromisoformat(row["first_seen"]).toordinal(),)


DAILY_SPEC = ReportSpec(
    id="sentence-role",
    title_th="ตัวจัดประเภทหน่วยประโยคของพยากรณ์รายวัน/7 วัน",
    group_th="วัน",
    split_note_th="แบ่งชุดตามวันที่ประกาศ (ชุดทดสอบเป็นวันล่าสุด ไม่ให้โมเดลเห็นก่อน)",
    label_source_th=LABEL_SOURCE_TH,
    labels=tuple(LABELS),
    splits=SPLITS,
    pipeline=PIPELINE,
    group_of=_day_key,
    in_test=lambda r: int(r["test_occurrences"]) > 0,
    weighted=True,
    doc_type_of=lambda r: r["doc_type"],
    error_notes=ERROR_NOTES,
)


def _events(row: Row) -> list[str]:
    return row["events"].split(";")


def _event_key(event: str) -> tuple[int, ...]:
    # รหัสเหตุการณ์ = เลขประกาศฉบับแรก "ปี_เลข" เรียงตามเวลาได้
    year, no = event.split("_")
    return int(year), int(no)


def warning_spec(rows: Sequence[Row]) -> ReportSpec:
    """สเปกของประกาศ: เหตุการณ์ทดสอบ = เหตุการณ์ของหน่วยในชุดทดสอบ (หน่วยอยู่ชุดเก่าสุดที่พบ)."""
    test_events = {e for r in rows if r["split"] == "test" for e in _events(r)}
    return ReportSpec(
        id="warning-role",
        title_th="ตัวจัดประเภทท่อนของประกาศเตือนภัย",
        group_th="เหตุการณ์",
        split_note_th=(
            "แบ่งชุดตามเหตุการณ์ (ประกาศหลายฉบับของเรื่องเดียว) เรียงตามเวลา ชุดทดสอบเป็นเหตุการณ์ล่าสุด "
            "ท่อนที่ซ้ำข้ามฉบับนับครั้งเดียวและอยู่ชุดที่เก่าที่สุดที่พบ"
        ),
        label_source_th=(
            LABEL_SOURCE_TH + " ผู้ช่วยร่างป้ายด้วยกฎคำสำคัญแล้วอ่านทุกหน่วย กฎ keyword จึงได้เปรียบในการวัดนี้"
        ),
        labels=WARNING_LABELS,
        splits=WARNING_SPLITS,
        pipeline=WARNING_PIPELINE,
        group_of=lambda r: _event_key(_events(r)[0]),
        in_test=lambda r: bool(test_events & set(_events(r))),
        weighted=False,
        doc_type_of=lambda _r: "warning",
    )


def _r(x: float) -> float:
    return round(x, DIGITS)


def _split_counts(rows: Sequence[Row], spec: ReportSpec) -> list[SplitCount]:
    out = []
    for split in spec.splits:
        part = [r for r in rows if r["split"] == split]
        c = Counter(r["final_label"] for r in part)
        out.append(
            SplitCount(split=split, total=len(part), by_label={k: c[k] for k in spec.labels})
        )
    return out


def _by_doc_type(rows: Sequence[Row], spec: ReportSpec) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for doc_type in sorted({spec.doc_type_of(r) for r in rows}):
        c = Counter(r["final_label"] for r in rows if spec.doc_type_of(r) == doc_type)
        out[doc_type] = {k: c[k] for k in spec.labels}
    return out


def _token_example(row: Row) -> TokenExample:
    tokens = tokenize(row["text"])
    kept = normalize_tokens(tokens)
    return TokenExample(
        unit_id=row["unit_id"],
        label=row["final_label"],
        text=row["text"],
        tokens=tokens,
        dropped=[t for t in tokens if not normalize_tokens([t])],
        kept=kept,
        counts=dict(sorted(Counter(kept).items(), key=lambda p: (-p[1], p[0]))),
    )


def _token_examples(train: Sequence[Row]) -> list[TokenExample]:
    # หนึ่งหน่วยต่อป้ายหลัก (หน่วยแรกตาม unit_id) หน่วยสภาพอากาศเลือกที่มีทั้งตัวเลขและเครื่องหมายที่ถูกทิ้ง
    # ให้เห็นทั้ง <num> และการคัดทิ้ง ถ้าไม่มีหน่วยแบบนั้นใช้หน่วยแรก
    ordered = sorted(train, key=lambda r: r["unit_id"])
    picks = []
    for label in ("weather", "cause", "advice"):
        cands = [_token_example(r) for r in ordered if r["final_label"] == label]
        if label == "weather":
            cands = [e for e in cands if e.dropped and NUM_TOKEN in e.kept] or cands
        if cands:
            picks.append(cands[0])
    return picks


def _top_words(nb: NaiveBayesModel) -> dict[str, list[WordScore]]:
    """คำเด่นต่อป้าย = log P(w|c) ลบค่าเฉลี่ย log P(w|ป้ายอื่น) (คำที่บอกป้ายนี้มากกว่าป้ายอื่น)."""
    out = {}
    for c in nb.labels:
        others = [o for o in nb.labels if o != c]
        scores = [
            (w, lp - sum(nb.log_likelihood[o][w] for o in others) / len(others))
            for w, lp in nb.log_likelihood[c].items()
            if w != NUM_TOKEN
        ]
        scores.sort(key=lambda p: (-p[1], p[0]))
        out[c] = [WordScore(word=w, score=_r(s)) for w, s in scores[:TOP_WORDS_PER_LABEL]]
    return out


def _nb_example(row: Row, nb: NaiveBayesModel, bags: Bags) -> NbExample:
    bag = bags[row["unit_id"]]
    predicted = nb.predict(bag)
    return NbExample(
        unit_id=row["unit_id"],
        text=row["text"],
        true_label=row["final_label"],
        predicted=predicted,
        correct=predicted == row["final_label"],
        log_prior={c: _r(v) for c, v in nb.log_prior.items()},
        log_score={c: _r(v) for c, v in nb.scores(bag).items()},
        posterior={c: _r(v) for c, v in posterior(nb, bag).items()},
        push_words=[
            WordScore(word=w, score=_r(p))
            for w, p in word_push(nb, bag, predicted)[:PUSH_WORDS]
            if p > 0
        ],
        unknown_words=sorted(w for w in bag if w not in nb.log_likelihood[predicted]),
    )


def _example_rows(test_new: Sequence[Row], predict: Predict) -> list[Row]:
    # ทายถูก 1 หน่วยต่อป้ายหลัก + ทายผิดหน่วยแรก (ตามลำดับ unit_id ผลซ้ำได้)
    ordered = sorted(test_new, key=lambda r: r["unit_id"])
    picks = []
    for label in ("weather", "cause", "advice"):
        hit = [r for r in ordered if r["final_label"] == label and predict(r["unit_id"]) == label]
        picks += hit[:1]
    picks += [r for r in ordered if predict(r["unit_id"]) != r["final_label"]][:1]
    return picks


def _learning_curve(
    train: Sequence[Row],
    dev: Sequence[Row],
    bags: Bags,
    m_factor: float,
    k: int,
    group_of: Callable[[Row], tuple[int, ...]],
) -> list[LearningPoint]:
    """ฝึกด้วยกลุ่มแรกๆ ของชุดฝึก 25/50/75/100% ของจำนวนกลุ่ม (แบ่งแบบเดียวกับการแบ่งชุด) วัดบน dev."""
    groups = sorted({group_of(r) for r in train})
    out = []
    for f in LEARNING_FRACTIONS:
        n_groups = max(1, round(len(groups) * f))
        cutoff = groups[n_groups - 1]
        part = [r for r in train if group_of(r) <= cutoff]
        nb = fit_nb(part, bags, m_factor * vocabulary_size(part, bags))
        knn = fit_knn(part, bags, k)

        def p_nb(u: str, m: NaiveBayesModel = nb) -> str:
            return m.predict(bags[u])

        def p_knn(u: str, m: KnnModel = knn) -> str:
            return m.predict(bags[u])

        out.append(
            LearningPoint(
                fraction=f,
                train_groups=n_groups,
                train_units=len(part),
                nb_dev_accuracy=_r(accuracy(dev, p_nb)),
                nb_dev_macro_f1=_r(macro_f1(dev, p_nb)),
                knn_dev_accuracy=_r(accuracy(dev, p_knn)),
                knn_dev_macro_f1=_r(macro_f1(dev, p_knn)),
            )
        )
    return out


def sentence_report(
    rows: Sequence[Row],
    bags: Bags,
    classify_cfg: dict,
    spec: ReportSpec,
    extra: dict[str, Predict] | None = None,
) -> SentenceRoleReport:
    """แถวหน่วยที่ปิดป้ายแล้ว + bag of words -> รายงานหนึ่งโมเดล.

    ค่าเดียวกับ scripts/train_eval.py (รายวัน) และ scripts/train_eval_warning.py (ประกาศ)
    extra = วิธีเทียบเพิ่ม (อยู่ในตารางผลวัดเท่านั้น ไม่มีตารางสับสน)
    """
    train = [r for r in rows if r["split"] == "train"]
    dev = [r for r in rows if r["split"] == "dev"]
    test_new = [r for r in rows if r["split"] == "test"]
    test_all = [r for r in rows if spec.in_test(r)]
    text_of = {r["unit_id"]: r["text"] for r in rows}

    tuning = tune(train, dev, bags, classify_cfg)
    nb = fit_nb(train, bags, tuning.best_m_factor * tuning.vocab_train)
    knn = fit_knn(train, bags, tuning.best_k)
    # เพื่อนบ้านสำหรับแสดง 3 ตัว (โมเดลที่ใช้วัดผลยังโหวตด้วย k ที่เลือก)
    knn_show = fit_knn(train, bags, NEIGHBORS)
    predictors: dict[str, Predict] = {
        NB: lambda u: nb.predict(bags[u]),
        KNN: lambda u: knn.predict(bags[u]),
        KEYWORD: lambda u: keyword_label(text_of[u]),
    }
    results = [
        ModelResult(
            name=name,
            dev=_r(accuracy(dev, p)),
            test_all=_r(accuracy(test_all, p)),
            test_all_weighted=_r(accuracy(test_all, p, "test_occurrences"))
            if spec.weighted
            else None,
            test_new=_r(accuracy(test_new, p)),
        )
        for name, p in {**predictors, **(extra or {})}.items()
    ]
    dev_nb = next(r.dev for r in results if r.name == NB)
    dev_knn = next(r.dev for r in results if r.name == KNN)
    chosen = NB if dev_nb >= dev_knn else KNN
    confusion = []
    for name, p in predictors.items():
        pairs = Counter((r["final_label"], p(r["unit_id"])) for r in test_new)
        outside = {q for _, q in pairs} - set(spec.labels)
        if outside:
            # ตารางสับสนมีแต่ป้ายของชุดนี้ ถ้ามีป้ายอื่นจะหายจากตารางเงียบๆ
            raise ValueError(f"{name} ทายป้ายนอกชุด {sorted(outside)}")
        confusion.append(
            Confusion(name=name, matrix=[[pairs[(t, q)] for q in spec.labels] for t in spec.labels])
        )

    examples = _example_rows(test_new, predictors[NB])
    train_row = {r["unit_id"]: r for r in train}
    knn_examples = []
    for row in examples:
        near = knn_show.neighbors(bags[row["unit_id"]])
        knn_examples.append(
            KnnExample(
                unit_id=row["unit_id"],
                text=row["text"],
                true_label=row["final_label"],
                predicted=knn.predict(bags[row["unit_id"]]),
                neighbors=[
                    Neighbor(unit_id=uid, text=train_row[uid]["text"], label=label, distance=_r(d))
                    for d, label, uid in near
                ],
            )
        )
    chosen_predict = predictors[chosen]
    mistakes = []
    for row in sorted(test_new, key=lambda r: r["unit_id"]):
        predicted = chosen_predict(row["unit_id"])
        if predicted == row["final_label"]:
            continue
        conf = posterior(nb, bags[row["unit_id"]])[predicted] if chosen == NB else 0.0
        mistakes.append(
            Mistake(
                unit_id=row["unit_id"],
                text=row["text"],
                true_label=row["final_label"],
                predicted=predicted,
                confidence=_r(conf),
                note_th=spec.error_notes.get(row["unit_id"], ""),
            )
        )

    return SentenceRoleReport(
        id=spec.id,
        title_th=spec.title_th,
        group_th=spec.group_th,
        split_note_th=spec.split_note_th,
        labels=list(spec.labels),
        labels_th={k: LABELS_TH[k] for k in spec.labels},
        chosen=chosen,
        label_source_th=spec.label_source_th,
        pipeline=spec.pipeline,
        splits=_split_counts(rows, spec),
        by_doc_type=_by_doc_type(rows, spec),
        token_examples=_token_examples(train),
        top_words=_top_words(nb),
        nb_examples=[_nb_example(r, nb, bags) for r in examples],
        knn_examples=knn_examples,
        tuning=Tuning(
            nb_m_factor=[TuningPoint(value=f, dev_accuracy=_r(a)) for f, a in tuning.nb],
            knn_k=[TuningPoint(value=k, dev_accuracy=_r(a)) for k, a in tuning.knn],
            best_m_factor=tuning.best_m_factor,
            best_k=tuning.best_k,
            vocab_train=tuning.vocab_train,
        ),
        results=results,
        confusion=confusion,
        learning_curve=_learning_curve(
            train, dev, bags, tuning.best_m_factor, tuning.best_k, spec.group_of
        ),
        mistakes=mistakes,
        facts=Facts(
            total_units=len(rows),
            keyword_agrees_with_labels=sum(
                keyword_label(r["text"]) == r["final_label"] for r in rows
            ),
            other_units=sum(r["final_label"] == "other" for r in rows),
            vocab_all=vocabulary_size(rows, bags),
            num_token=NUM_TOKEN,
        ),
    )


def build_report(
    rows: Sequence[Row],
    bags: Bags,
    classify_cfg: dict,
    warning_rows: Sequence[Row] | None = None,
) -> ModelReport:
    """รายงานของรายวัน (+ ของประกาศถ้าส่งแถวประกาศมา) -> ไฟล์เดียวของหน้า /model."""
    daily = sentence_report(rows, bags, classify_cfg, DAILY_SPEC)
    models = [daily]
    if warning_rows:
        # ตัวของรายวันที่เว็บใช้จริง (ฝึกด้วยป้ายทั้งหมด ค่าที่เลือกบน dev) = models/{naive_bayes,knn}.json
        base: NaiveBayesModel | KnnModel = (
            fit_nb(rows, bags, daily.tuning.best_m_factor * daily.facts.vocab_all)
            if daily.chosen == NB
            else fit_knn(rows, bags, daily.tuning.best_k)
        )
        w_bags = {r["unit_id"]: bag_of_words(r["text"]) for r in warning_rows}
        extra: dict[str, Predict] = {
            f"{daily.chosen} ของรายวัน (โมเดลเดิม)": lambda u: base.predict(w_bags[u])
        }
        spec = warning_spec(warning_rows)
        models.append(sentence_report(warning_rows, w_bags, classify_cfg, spec, extra))
    return ModelReport(version=REPORT_VERSION, models=models)
