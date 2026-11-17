import { AdviceList } from "@/components/features/advice-list";
import { SummaryLines } from "@/components/features/forecast-card";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Disclosure } from "@/components/ui/disclosure";
import type { WarningNotice as WarningNoticeDoc } from "@/lib/contract/documents";
import { REGION_LABELS, thaiDateTimeShort } from "@/lib/format/thai";

type WarningNoticeProps = {
  notice: WarningNoticeDoc;
  // ระดับหัวข้อของชื่อเรื่อง (หน้า /warnings ใช้ h2, /demo ใช้ h3 ใต้หัวข้อผลลัพธ์)
  headingLevel?: 2 | 3;
};

// ไอคอนเตือน (ตกแต่งเท่านั้น: ระดับความรุนแรงอยู่ในคำของ TMD ที่หัวเรื่องและป้ายข้อความ ไม่ใช้สีอย่างเดียว)
function AlertIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="mt-1 size-6 shrink-0 text-ink"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 3.5 2.5 20h19L12 3.5z" />
      <path d="M12 10v4.5M12 17.5v.5" />
    </svg>
  );
}

// ประกาศเตือนภัยหนึ่งฉบับ: หัวเรื่อง (คำของ TMD) + ฉบับ/เลขประกาศ + ช่วงที่มีผล + ภาคที่กล่าวถึง + สถานการณ์ + ข้อควรระวัง
// ทุกข้อความคัดจากต้นฉบับคำต่อคำ (เนื้อหาไม่ถูกเขียนใหม่)
export function WarningNoticeCard({ notice, headingLevel = 2 }: WarningNoticeProps) {
  const Heading = headingLevel === 2 ? "h2" : "h3";
  const isFinal = notice.next_issue_at === null;
  return (
    <Card className="animate-enter-up space-y-6">
      <header className="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <Badge>ฉบับที่ {notice.series_no}</Badge>
          <Badge variant="muted">ประกาศเลขที่ {notice.notice_no}</Badge>
          <Badge variant={isFinal ? "default" : "muted"}>
            {isFinal ? "ฉบับสุดท้ายของเหตุการณ์นี้" : `ฉบับต่อไป ${thaiDateTimeShort(notice.next_issue_at!)}`}
          </Badge>
        </div>
        <div className="flex gap-3">
          <AlertIcon />
          <Heading className="min-w-0 text-display-sm [overflow-wrap:anywhere]">{notice.title}</Heading>
        </div>
        <p className="text-body-sm text-body">ประกาศ ณ {thaiDateTimeShort(notice.issued_at)}</p>
        {notice.effect ? <p className="text-body-md text-ink">{notice.effect.text}</p> : null}
      </header>

      {notice.regions.length > 0 || notice.provinces.length > 0 ? (
        <section aria-label="พื้นที่ที่กล่าวถึง" className="space-y-3">
          {notice.regions.length > 0 ? (
            <>
              <h3 className="text-title-sm">พื้นที่ที่กล่าวถึง</h3>
              <ul className="flex flex-wrap gap-2" aria-label="ภาคที่กล่าวถึง">
                {notice.regions.map((key) => (
                  <li
                    key={key}
                    className="inline-flex min-h-9 items-center rounded-md border border-hairline-strong bg-canvas px-3 text-body-md text-ink"
                  >
                    {REGION_LABELS[key]}
                  </li>
                ))}
              </ul>
            </>
          ) : null}
          {notice.provinces.length > 0 ? (
            <Disclosure summary={`จังหวัดที่ประกาศระบุชื่อ (${notice.provinces.length})`}>
              <p className="text-body-md text-ink">{notice.provinces.join(" ")}</p>
            </Disclosure>
          ) : null}
        </section>
      ) : null}

      {notice.lines.length > 0 ? (
        <section className="space-y-3 border-t border-hairline pt-6">
          <h3 className="text-title-md">สถานการณ์</h3>
          <SummaryLines lines={notice.lines} />
        </section>
      ) : null}

      {notice.precautions.length > 0 ? (
        <section className="space-y-3 border-t border-hairline pt-6">
          <h3 className="text-title-md">ข้อควรระวัง</h3>
          <AdviceList items={notice.precautions} />
        </section>
      ) : null}
    </Card>
  );
}
