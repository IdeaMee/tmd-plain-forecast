"""ไฟล์ชุดจากเบราว์เซอร์และการตรวจคลังข้อมูลดิบ (Phase 9.1, ADR 0015)."""

from __future__ import annotations

import base64

import pytest

from tmd_plain.raw_batch import (
    BatchError,
    DiskFile,
    check_inventory,
    manifest_row,
    parse_batch,
    parse_entry,
    text_layer_level,
)

SRC = "https://www.tmd.go.th/forecast/shipping/181120260700"
TEXT = "# source: " + SRC + "\n# round_id: 181120260700\n# label: ป้าย ก\n\nเนื้อหา"


def test_parse_text_entry():
    f = parse_entry("shipping/shipping_181120260700.txt", {"text": TEXT, "source": SRC})
    assert f.rel_path == "shipping/shipping_181120260700.txt"
    assert (f.kind, f.issue_id, f.fmt, f.label) == ("shipping", "181120260700", "txt", "ป้าย ก")
    assert f.data == TEXT.encode("utf-8")


def test_parse_pdf_entry():
    pdf = b"%PDF-1.7\n..."
    value = {"b64": base64.b64encode(pdf).decode(), "source": "https://www.tmd.go.th/media/x.pdf"}
    f = parse_entry("warning/warning_2569_315.pdf", value)
    assert f.data == pdf and f.fmt == "pdf" and f.label == ""


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("../evil/evil_1.txt", {"text": TEXT, "source": SRC}),
        ("shipping/daily_1.txt", {"text": TEXT, "source": SRC}),
        ("unknown/unknown_1.txt", {"text": TEXT, "source": SRC}),
        ("shipping/shipping_1.txt", {"text": TEXT, "source": "https://example.com/"}),
        ("shipping/shipping_1.txt", {"text": "ไม่มีหัวไฟล์", "source": SRC}),
        ("shipping/shipping_1.pdf", {"b64": base64.b64encode(b"<html>").decode(), "source": SRC}),
    ],
)
def test_bad_entries_rejected(key, value):
    with pytest.raises(BatchError):
        parse_entry(key, value)


def test_parse_batch_skips_bad_and_counts():
    files, errors = parse_batch(
        {
            "shipping/shipping_2.txt": {"text": TEXT, "source": SRC},
            "bad": {"text": TEXT, "source": SRC},
        }
    )
    assert [f.rel_path for f in files] == ["shipping/shipping_2.txt"]
    assert len(errors) == 1


def test_manifest_row_matches_columns():
    f = parse_entry("shipping/shipping_181120260700.txt", {"text": TEXT, "source": SRC})
    row = manifest_row(f, "sample_v2")
    assert row["bytes"] == str(len(f.data)) and row["sha256"] == f.sha256
    assert row["role"] == "sample_v2" and row["type"] == "shipping"


def _row(path: str, size: int, sha: str) -> dict[str, str]:
    return {"file": path, "bytes": str(size), "sha256": sha}


def test_check_inventory_clean():
    rows = [_row("a/a_1.txt", 3, "x"), _row("a/a_2.txt", 4, "y")]
    disk = [DiskFile("a/a_1.txt", 3, "x"), DiskFile("a/a_2.txt", 4, "y")]
    assert check_inventory(rows, disk) == []


def test_check_inventory_finds_problems():
    rows = [_row("a/a_1.txt", 3, "x"), _row("a/a_1.txt", 3, "x"), _row("a/a_3.txt", 1, "z")]
    disk = [DiskFile("a/a_1.txt", 3, "WRONG"), DiskFile("a/a_9.txt", 1, "q")]
    errs = check_inventory(rows, disk)
    assert any("duplicate row" in e for e in errs)
    assert any("without manifest row: a/a_9.txt" in e for e in errs)
    assert any("row without file: a/a_3.txt" in e for e in errs)
    assert any("mismatch: a/a_1.txt" in e for e in errs)


def test_check_inventory_same_content():
    rows = [_row("a/a_1.pdf", 3, "x"), _row("a/a_2.pdf", 3, "x")]
    disk = [DiskFile("a/a_1.pdf", 3, "x"), DiskFile("a/a_2.pdf", 3, "x")]
    assert check_inventory(rows, disk) == ["same content as a/a_1.pdf: a/a_2.pdf"]


def test_text_layer_level():
    assert [text_layer_level(n) for n in (0, 5, 200)] == ["none", "low", "yes"]
