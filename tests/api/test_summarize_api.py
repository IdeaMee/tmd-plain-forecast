import http.client
import importlib.util
import json
import threading
import urllib.error
import urllib.request
from collections.abc import Iterator
from http.server import HTTPServer
from pathlib import Path
from types import ModuleType

import pytest
from pydantic import TypeAdapter

from tmd_plain.contract import SummarizeError, SummarizeIssueOk, SummarizeOk

ROOT = Path(__file__).resolve().parents[2]
DAILY_PDF = ROOT / "data" / "raw" / "daily" / "daily_161120261800.pdf"
OK = TypeAdapter(SummarizeOk)


def _load_api() -> ModuleType:
    spec = importlib.util.spec_from_file_location("api_summarize", ROOT / "api" / "summarize.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def api() -> ModuleType:
    return _load_api()


@pytest.fixture(scope="module")
def server(api: ModuleType) -> Iterator[HTTPServer]:
    # รันตัวจัดการจริงบนพอร์ตชั่วคราว เหมือนที่ Vercel เรียกคลาส handler
    srv = HTTPServer(("127.0.0.1", 0), api.handler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    try:
        yield srv
    finally:
        srv.shutdown()
        srv.server_close()


@pytest.fixture(scope="module")
def base_url(server: HTTPServer) -> str:
    return f"http://127.0.0.1:{server.server_port}/api/summarize"


def _call(url: str, method: str, body: bytes | None = None) -> tuple[int, str, dict]:
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/pdf")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.headers["Content-Type"], json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, err.headers["Content-Type"], json.loads(err.read())


def test_post_real_pdf_returns_issue(base_url: str) -> None:
    if not DAILY_PDF.exists():
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    status, ctype, body = _call(base_url, "POST", DAILY_PDF.read_bytes())
    assert status == 200 and ctype.startswith("application/json")
    result = OK.validate_python(body)
    assert isinstance(result, SummarizeIssueOk) and result.trace is None
    assert result.document.issue_id == "161120261800"


def test_chunked_upload_is_read(server: HTTPServer) -> None:
    # ไม่มี Content-Length (Transfer-Encoding: chunked) ต้องอ่าน body ได้ ไม่ใช่ตอบว่าไฟล์ว่าง
    if not DAILY_PDF.exists():
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    data = DAILY_PDF.read_bytes()
    conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=60)
    try:
        chunks = (data[i : i + 65536] for i in range(0, len(data), 65536))
        conn.request(
            "POST",
            "/api/summarize",
            body=chunks,
            headers={"Content-Type": "application/pdf"},
            encode_chunked=True,
        )
        resp = conn.getresponse()
        status, body = resp.status, json.loads(resp.read())
    finally:
        conn.close()
    assert status == 200 and OK.validate_python(body).document.issue_id == "161120261800"


@pytest.mark.parametrize(
    ("body", "status", "code"),
    [
        (b"", 422, "empty_file"),
        (b"not a pdf at all", 422, "unsupported_document"),
        (b"%PDF-1.4" + b"\0" * (4 * 1024 * 1024), 413, "too_large"),
    ],
)
def test_post_bad_body_returns_contract_error(
    base_url: str, body: bytes, status: int, code: str
) -> None:
    got_status, _, payload = _call(base_url, "POST", body)
    result = SummarizeError.model_validate(payload)
    assert (got_status, result.error.code) == (status, code)


def test_unexpected_crash_still_returns_contract_json(
    api: ModuleType, base_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(data: bytes, classifier: object, trace: bool) -> None:
        raise RuntimeError("ทดสอบ")

    monkeypatch.setattr(api, "summarize_pdf", boom)
    status, ctype, payload = _call(base_url, "POST", b"%PDF-1.4 x")
    assert status == 500 and ctype.startswith("application/json")
    assert SummarizeError.model_validate(payload).error.code == "extract_failed"


def test_get_is_not_allowed(base_url: str) -> None:
    status, _, payload = _call(base_url, "GET")
    assert status == 405 and payload["ok"] is False


@pytest.mark.parametrize(
    ("query", "has_trace"), [("?trace=1", True), ("?trace=0", False), ("", False)]
)
def test_trace_query_param(base_url: str, query: str, has_trace: bool) -> None:
    if not DAILY_PDF.exists():
        pytest.skip("ไม่มีข้อมูลดิบ (data/raw ไม่อยู่ใน repo)")
    status, _, body = _call(base_url + query, "POST", DAILY_PDF.read_bytes())
    result = OK.validate_python(body)
    assert status == 200 and result.kind == "issue"
    assert (result.trace is not None) is has_trace
    if has_trace:
        assert result.trace.steps[0].id == "read_pdf" and result.trace.steps[-1].id == "result"
