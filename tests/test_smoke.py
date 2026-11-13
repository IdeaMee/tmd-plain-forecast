from pythainlp.tokenize import word_tokenize

import tmd_plain


def test_package_imports() -> None:
    assert tmd_plain.__version__ == "0.1.0"


def test_newmm_keeps_weather_terms_whole() -> None:
    # คำโดเมนอากาศต้องไม่ถูกตัดแยก (เหตุผลที่ตัดคำฝั่ง Python ไม่ใช่ Intl.Segmenter)
    tokens = word_tokenize("ฝนฟ้าคะนองร้อยละ 30 ของพื้นที่", engine="newmm")
    assert "ร้อยละ" in tokens
    assert "ฟ้าคะนอง" in tokens
