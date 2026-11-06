"""ตัวโหลดตัวจัดประเภท (11.3): ตัวเฉพาะชนิดเอกสาร และการถอยไปใช้ตัวหลักเมื่อไม่มีไฟล์."""

import shutil
from pathlib import Path

from tmd_plain.classify.model_io import load_classifier, with_label_cache

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / "models"


def test_missing_warning_model_falls_back_to_base(tmp_path: Path) -> None:
    # ไม่มี warning_selected.json (เช่น bundle ขาดไฟล์) = ประกาศใช้ตัวของรายวัน ไม่ล้ม
    for name in ("selected.json", "naive_bayes.json", "knn.json"):
        shutil.copy(MODELS / name, tmp_path / name)
    clf = load_classifier(tmp_path)
    assert clf.specific == ()
    assert clf.for_doc("warning") is clf


def test_warning_model_is_loaded_and_cached_copy_keeps_it() -> None:
    clf = load_classifier(MODELS)
    warning = clf.for_doc("warning")
    assert warning is not clf and warning.doc_type == "warning"
    cached = with_label_cache(clf)
    text = "ขอให้ประชาชนระวังอันตรายจากฝนตกหนัก"
    assert cached.for_doc("warning").label(text) == warning.label(text)
