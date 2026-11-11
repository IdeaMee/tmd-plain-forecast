"""golden file ของโหมดทั่วไป (Phase 10.3): ผลต้องเหมือนเดิมทุกไบต์ จนกว่าจะจงใจเปลี่ยนกฎ."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "tests" / "golden" / "generic"
sys.path.insert(0, str(ROOT / "scripts"))
import make_golden_generic  # noqa: E402


def test_golden_generic() -> None:
    if not make_golden_generic.sources_exist():
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    built = make_golden_generic.build()
    assert sorted(built) == sorted(p.name for p in GOLDEN.glob("*.json"))
    for name, body in built.items():
        assert body == (GOLDEN / name).read_text(encoding="utf-8"), (
            f"{name}: รัน scripts/make_golden_generic.py แล้วอ่าน diff"
        )
