"""อ่านค่าตั้งจาก config.toml ที่มากับแพ็กเกจ (ใช้ได้ทั้งบนเครื่องและบน Vercel)."""

from __future__ import annotations

import tomllib
from functools import cache
from importlib.resources import files
from typing import Any


@cache
def load_config() -> dict[str, Any]:
    raw = files("tmd_plain").joinpath("config.toml").read_text(encoding="utf-8")
    return tomllib.loads(raw)
