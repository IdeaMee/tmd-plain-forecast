"""ส่งออก JSON Schema จากสัญญาข้อมูล (Pydantic) ให้ฝั่งเว็บใช้ตรวจด้วย Zod.

รัน: .venv/Scripts/python.exe -X utf8 scripts/export_schema.py
ผล: lib/contract/issue.schema.json, summarize-response.schema.json (คำตอบ v2 ตาม ADR 0017:
    $defs มีทุกโมเดลของเอกสาร) (รันซ้ำต้องได้ไฟล์เดิมทุกไบต์)
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import TypeAdapter

from tmd_plain.contract import (
    CONTRACT_VERSION,
    Issue,
    SummarizeError,
    SummarizeOk,
)

OUT = Path(__file__).resolve().parents[1] / "lib" / "contract"
DRAFT = "https://json-schema.org/draft/2020-12/schema"


def build_schemas() -> dict[str, dict]:
    issue = Issue.model_json_schema(mode="serialization")
    response = TypeAdapter(SummarizeOk | SummarizeError).json_schema(mode="serialization")
    out = {}
    for name, schema in (
        ("issue", issue),
        ("summarize-response", response),
    ):
        out[f"{name}.schema.json"] = {
            "$schema": DRAFT,
            "$comment": f"generated from src/tmd_plain/contract.py (contract v{CONTRACT_VERSION}); do not edit",
            **schema,
        }
    return out


def render(schema: dict) -> str:
    return json.dumps(schema, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, schema in build_schemas().items():
        (OUT / filename).write_text(render(schema), encoding="utf-8", newline="\n")
        print(f"wrote lib/contract/{filename}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
