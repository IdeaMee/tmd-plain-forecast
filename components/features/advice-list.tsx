import { Badge } from "@/components/ui/badge";

// ใช้ได้ทั้งคำแนะนำรายภาค (AdviceItem) และคำแนะนำที่คัดมา (QuotedAdvice ของเดินเรือ)
type AdviceListProps = {
  items: { text: string; source_unit_id: string }[];
  // แสดงป้าย "ข้อแนะนำทั่วไป" ที่แต่ละข้อ (ใช้กับทุกภาค)
  general?: boolean;
};

// คำแนะนำคัดจากต้นฉบับตรงๆ ห้ามแก้ข้อความ · ไม่พึ่งสีอย่างเดียว: แถบซ้ายสี + หัวข้อ "คำแนะนำ" ของส่วน (D10)
export function AdviceList({ items, general = false }: AdviceListProps) {
  return (
    <ul className="space-y-3">
      {items.map((item) => (
        <li key={item.source_unit_id} className="flex gap-3 border-l-4 border-l-accent-warning pl-3">
          <div className="min-w-0">
            {general ? <Badge className="mb-1">ข้อแนะนำทั่วไป</Badge> : null}
            <p className="text-body-md text-ink">{item.text}</p>
          </div>
        </li>
      ))}
    </ul>
  );
}
