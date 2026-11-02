"""ตัดคำไทยด้วย PyThaiNLP newmm + พจนานุกรมคำอากาศ (resources/weather_words.txt)."""

from __future__ import annotations

from functools import cache
from importlib.resources import files

from pythainlp.corpus import thai_words
from pythainlp.tokenize import word_tokenize
from pythainlp.util import Trie


def weather_words() -> frozenset[str]:
    raw = files("tmd_plain").joinpath("resources/weather_words.txt").read_text(encoding="utf-8")
    return frozenset(w.strip() for w in raw.splitlines() if w.strip() and not w.startswith("#"))


@cache
def _trie() -> Trie:
    return Trie(set(thai_words()) | weather_words())


def tokenize(text: str) -> list[str]:
    """รายการคำ ไม่รวมช่องว่าง; ผลซ้ำได้ (พจนานุกรมคงที่)."""
    return [t for t in word_tokenize(text, custom_dict=_trie(), engine="newmm") if t.strip()]
