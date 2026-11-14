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
