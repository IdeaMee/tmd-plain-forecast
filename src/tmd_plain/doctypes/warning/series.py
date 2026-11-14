"""เชื่อมประกาศฉบับต่อเนื่องของเหตุการณ์เดียวกัน (ฉบับที่ 1..n) ด้วยกฎ (แผน 11.2 task 2).

TMD นับ "ฉบับที่" ต่อเหตุการณ์ และหัวเรื่องเปลี่ยนได้ระหว่างเหตุการณ์ (เช่น ขยายพื้นที่) จึงไม่ใช้หัวเรื่องเป็นหลัก:
ฉบับที่ n ต่อจากชุดที่ฉบับล่าสุดเป็น n-1 และออกห่างกันไม่เกิน MAX_GAP
ถ้ามีหลายชุดเข้าเงื่อนไข (สองเหตุการณ์พร้อมกัน) เลือกชุดที่บอกเวลาฉบับต่อไปตรงกับเวลาฉบับนี้ แล้วชุดที่หัวเรื่องเหมือนกัน
ฉบับสุดท้ายปิดชุด · ฉบับที่ 1 เริ่มชุดใหม่เสมอ · ชุดที่เริ่มด้วยฉบับที่ > 1 = ฉบับแรกๆ ไม่อยู่ในข้อมูลที่เก็บ
ไม่เก็บลงสัญญาข้อมูล: หน้าเว็บ (11.4) คำนวณจากรายการประกาศได้เอง
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

MAX_GAP = timedelta(hours=48)


@dataclass(frozen=True)
class NoticeKey:
    issue_id: str
    series_no: int
    title: str
    issued_at: datetime
    next_issue_at: datetime | None
    final: bool


@dataclass
class Series:
    notices: list[NoticeKey] = field(default_factory=list)
    closed: bool = False

    @property
    def series_id(self) -> str:
        # รหัสชุด = รหัสของฉบับแรกที่มีในข้อมูล
        return self.notices[0].issue_id

    @property
    def complete_start(self) -> bool:
        return self.notices[0].series_no == 1

    @property
    def last(self) -> NoticeKey:
        return self.notices[-1]


def _order(n: NoticeKey) -> tuple[datetime, int, str]:
    return (n.issued_at, int(n.issue_id.split("_")[1]), n.issue_id)


def link_series(notices: list[NoticeKey]) -> list[Series]:
    """จัดประกาศเป็นชุดตามเวลาออก ผลคงที่สำหรับชุดข้อมูลเดิม (เรียงตามเวลาแล้วเลขประกาศ)."""
    series: list[Series] = []
    for notice in sorted(notices, key=_order):
        open_ = [
            s
            for s in series
            if not s.closed
            and s.last.series_no == notice.series_no - 1
            and timedelta(0) <= notice.issued_at - s.last.issued_at <= MAX_GAP
        ]
        if notice.series_no == 1 or not open_:
            chosen = Series()
            series.append(chosen)
        else:
            chosen = min(
                open_,
                key=lambda s: (
                    s.last.next_issue_at != notice.issued_at,
                    s.last.title != notice.title,
                    notice.issued_at - s.last.issued_at,
                ),
            )
        chosen.notices.append(notice)
        chosen.closed = notice.final
    return series
