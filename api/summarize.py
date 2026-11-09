"""POST /api/summarize (Phase 5.1): body = ไฟล์ PDF ดิบ (Content-Type: application/pdf) -> JSON ตามสัญญา.

ไฟล์ทางเข้าบางๆ: อ่านคำขอ -> tmd_plain.service -> ตอบ JSON · ไม่เก็บไฟล์และผลลัพธ์
ส่ง PDF ดิบแทน multipart เพราะไม่ต้องแยกส่วน (โมดูล cgi ถูกลบใน Python 3.13) และไม่มีส่วนหัวกินเพดาน 4.5 MB ของ Vercel
"""

from __future__ import annotations

import json
import logging
import os
from functools import cache
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# PyThaiNLP ห้ามดาวน์โหลด/เขียนข้อมูลนอก /tmp บน Vercel (ระบบไฟล์อ่านอย่างเดียว) ต้องตั้งก่อนนำเข้าแพ็กเกจ
os.environ.setdefault("PYTHAINLP_READ_ONLY", "1")
os.environ.setdefault("PYTHAINLP_OFFLINE", "1")
os.environ.setdefault("PYTHAINLP_DATA", "/tmp/pythainlp-data")

from tmd_plain.classify.model_io import load_labeler  # noqa: E402
from tmd_plain.contract import error_response  # noqa: E402
from tmd_plain.extract.advice import Labeler  # noqa: E402
from tmd_plain.service import http_status, summarize_pdf  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api.summarize")

MODELS = Path(__file__).resolve().parents[1] / "models"


@cache
def _labeler() -> Labeler:
    # โหลดโมเดลครั้งเดียวต่อ instance
    return load_labeler(MODELS)


def _read_chunked(handler: BaseHTTPRequestHandler) -> bytes:
    # Transfer-Encoding: chunked (ไม่มี Content-Length): บรรทัดขนาดฐาน 16 + ข้อมูล + CRLF จนเจอขนาด 0
    parts: list[bytes] = []
    while True:
        size = int(handler.rfile.readline().split(b";", 1)[0].strip() or b"0", 16)
        if size == 0:
            break
        parts.append(handler.rfile.read(size))
        handler.rfile.readline()
    while handler.rfile.readline().strip():
        pass  # ข้าม trailer
    return b"".join(parts)


def _read_body(handler: BaseHTTPRequestHandler) -> bytes:
    # อ่านครบตาม Content-Length: Vercel ตัด body เกิน 4.5 MB ก่อนถึงฟังก์ชันอยู่แล้ว
    # (อ่านไม่ครบแล้วตอบทันที ทำให้การเชื่อมต่อถูกตัดก่อนผู้ใช้ได้ข้อความ too_large)
    if "chunked" in handler.headers.get("Transfer-Encoding", "").lower():
        return _read_chunked(handler)
    try:
        length = int(handler.headers.get("Content-Length") or 0)
    except ValueError:
        length = 0
    return handler.rfile.read(length) if length > 0 else b""


class handler(BaseHTTPRequestHandler):  # noqa: N801 (ชื่อที่ Vercel กำหนด)
    def do_POST(self) -> None:  # noqa: N802
        try:
            result = summarize_pdf(_read_body(self), _labeler())
        except Exception:
            # ด่านสุดท้าย (F7): ข้อผิดพลาดที่ไม่คาดต้องได้ JSON ตามสัญญา ไม่ใช่ 500 เปล่า
            logger.exception("summarize crashed")
            self._send(500, error_response("extract_failed").model_dump(mode="json"))
            return
        self._send(http_status(result), result.model_dump(mode="json"))

    def do_GET(self) -> None:  # noqa: N802
        self._send(405, {"ok": False}, allow="POST")

    def _send(self, status: int, body: dict, allow: str | None = None) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        if allow:
            self.send_header("Allow", allow)
        self.end_headers()
        self.wfile.write(data)
