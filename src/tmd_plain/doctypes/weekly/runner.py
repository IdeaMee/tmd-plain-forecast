"""สรุปรายสัปดาห์บนเครื่อง (run_pipeline, check_weekly): ข้อความดิบ -> WeeklySummary ที่ผ่านตัวตรวจ.

ไม่ลงทะเบียนใน doctypes/registry (ท่อน /demo): ข้อมูลหมวดนี้เป็นข้อความหน้าเว็บที่ต้องใช้ตำแหน่งแท็บของตาราง
ส่วน PDF เป็นแผนที่คนละเลย์เอาต์ จึงไปโหมดทั่วไป (ดู parse.py)
"""

from __future__ import annotations

import logging

from pydantic import ValidationError

from tmd_plain.contract import SummarizeError, WeeklySummary, error_response
from tmd_plain.doctypes.weekly.build import assemble_weekly, check_weekly
from tmd_plain.doctypes.weekly.parse import WeeklyParseError, parse_weekly

logger = logging.getLogger(__name__)


def summarize_weekly(raw: str, issue_id: str | None = None) -> WeeklySummary | SummarizeError:
    """ข้อความดิบของไฟล์ที่เก็บ -> WeeklySummary; โครงไม่ตรง/ไม่ผ่านตรวจ = extract_failed (ไม่เดา)."""
    try:
        parsed = parse_weekly(raw)
        summary = assemble_weekly(parsed, issue_id)
    except WeeklyParseError as exc:
        logger.warning("weekly parse failed: %s", exc)
        return error_response("extract_failed")
    except ValidationError as exc:
        logger.warning("weekly assemble failed: %s", exc)
        return error_response("extract_failed")
    problems = check_weekly(summary, parsed)
    if problems:
        logger.warning(
            "weekly fidelity failed issue=%s count=%d first=%s",
            summary.issue_id,
            len(problems),
            problems[0],
        )
        return error_response("extract_failed")
    return summary
