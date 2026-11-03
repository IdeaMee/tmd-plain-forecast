-- ตารางเดียวเก็บผลสรุปทั้งฉบับเป็น JSON ตามสัญญาข้อมูล (docs/spec/data-contract.md หัวข้อ 3 และ v2.8)
-- รันซ้ำได้ (if not exists) รันด้วย role เจ้าของฐานข้อมูล (neondb_owner)
-- ชนิดเอกสารตามสัญญา v2 (ADR 0017) ฐานข้อมูลที่สร้างก่อน 11.1 ให้รัน db/migrations/001-doc-type-v2.sql
create table if not exists forecast_issue (
  issue_id     text        not null,
  doc_type     text        not null constraint forecast_issue_doc_type_check
               check (doc_type in ('daily', 'sevenday', 'shipping', 'warning', 'weekly', 'agro7', 'outlook3m')),
  issued_at    timestamptz not null,
  source_label text        not null,
  payload      jsonb       not null,
  loaded_at    timestamptz not null default now(),
  primary key (doc_type, issue_id)
);

create index if not exists forecast_issue_doc_type_issued_at_idx
  on forecast_issue (doc_type, issued_at desc);
