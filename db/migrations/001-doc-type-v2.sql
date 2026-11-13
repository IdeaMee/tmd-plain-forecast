-- Phase 11.1 (สัญญาข้อมูล v2 หัวข้อ v2.8, ADR 0017): ขยายชนิดเอกสารที่ตาราง forecast_issue ยอมรับ
-- เพิ่มเดินเรือ ประกาศเตือนภัย สรุปรายสัปดาห์ (แผน 11) และเกษตร 7 วัน คาดหมาย 3 เดือน (แผน 12) ในครั้งเดียว
-- ไม่ลบหรือแก้แถวเดิม (รายวัน/7 วัน) ข้อมูลเดิมผ่านเงื่อนไขใหม่อยู่แล้ว
-- ผู้ใช้เป็นคนรันใน Neon SQL Editor ด้วย role เจ้าของ (neondb_owner) รันซ้ำได้ (drop ... if exists)
-- ตรวจหลังรัน: select pg_get_constraintdef(oid) from pg_constraint where conname = 'forecast_issue_doc_type_check';
begin;

alter table forecast_issue drop constraint if exists forecast_issue_doc_type_check;

alter table forecast_issue add constraint forecast_issue_doc_type_check
  check (doc_type in ('daily', 'sevenday', 'shipping', 'warning', 'weekly', 'agro7', 'outlook3m'));

commit;
