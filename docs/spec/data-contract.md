# สัญญาข้อมูล v1

สถานะ: **v1 เป็นโค้ดแล้ว (Phase 1.1, 2026-11-16) รอผู้ใช้รีวิว** รูปร่างเหมือนร่าง v0 ทุกอย่าง (จึงไม่ต้องมี ADR) เพิ่มกฎตรวจและข้อความข้อผิดพลาดภาษาไทย หลังผู้ใช้เซ็นปิด การเปลี่ยนใดๆ ต้องบันทึก ADR

**ต้นฉบับอยู่ในโค้ด:** `src/tmd_plain/contract.py` (Pydantic) → `scripts/export_schema.py` → `lib/contract/issue.schema.json`, `lib/contract/summarize-response.schema.json` (ห้ามแก้ไฟล์ JSON เอง เทสต์จะตรวจว่าตรงกับโค้ด) · ไฟล์ตัวอย่าง: `tests/fixtures/contract/` (เขียนมือจากฉบับจริง ใช้กับฝั่งเว็บก่อนท่อประมวลผลเสร็จ)

**กฎตรวจที่เพิ่มใน v1:** `regions` ต้องมีครบ 7 คีย์พอดี · `issued_at` ต้องมีเขตเวลา · `issue_id` รายวัน 12 หลัก (DDMMYYYYHHMM) / 7 วัน 6 หลัก (YYMMDD) · รายวันต้องมี `lines` และห้ามมี `periods`; 7 วันต้องมี `periods` · คำแนะนำในภาคใดต้องมีภาคนั้นใน `scope` · `general=true` ต้องมี scope ครบ 7 ภาค และอยู่ใน `general_advice` เท่านั้น · `Period.start` ไม่หลัง `end` และมีอย่างน้อย 1 บรรทัด · `facts` เก็บได้แค่ string / ตัวเลข / bool / list ของ string · ห้ามมีฟิลด์นอกสัญญา (`extra="forbid"`)

**หลักการ:** Pydantic (Python) เป็นต้นฉบับของรูปข้อมูล -> ส่งออก JSON Schema (Draft 2020-12) -> สร้างชนิด TypeScript (`json-schema-to-typescript`) และตรวจด้วย Zod ฝั่งเว็บ มีขั้นตรวจว่าชนิดที่สร้างใหม่แล้วไม่มีความต่าง

## 1. ค่าคงที่ที่ตกลงแล้ว

**ภาค 7 แบบ** (คีย์ตรงกับฟิลด์ของ API พยากรณ์รายวันของ TMD)

| คีย์ | ชื่อไทย | รหัสในตารางแมปภาค |
|---|---|---|
| `north` | ภาคเหนือ | N |
| `northeast` | ภาคตะวันออกเฉียงเหนือ | NE |
| `central` | ภาคกลาง | C |
| `east` | ภาคตะวันออก | E |
| `south_east_coast` | ภาคใต้ฝั่งตะวันออก (อ่าวไทย) | SE |
| `south_west_coast` | ภาคใต้ฝั่งตะวันตก (อันดามัน) | SW |
| `bangkok_vicinity` | กรุงเทพมหานครและปริมณฑล | BKK |

**ป้ายหน่วย:** `weather`, `advice`, `cause`, `other`
**ชนิดเอกสาร:** `daily`, `sevenday`

## 2. ผลสรุปต่อฉบับ (ข้อเสนอ)

```
Issue {
  issue_id: string            // รายวัน: รหัสรอบ DDMMYYYYHHMM; 7 วัน: YYMMDD
  doc_type: "daily" | "sevenday"
  issued_at: string           // ISO 8601 พร้อมเขตเวลา +07:00
  source_label: string        // ข้อความป้ายต้นฉบับ เช่น "ประจำวันที่ 16 พฤศจิกายน 2569 17.00 น."
  regions: { <region_key>: RegionSummary }   // ครบ 7 คีย์
  general_advice: AdviceItem[]               // คำแนะนำที่ใช้กับทุกภาค
  pipeline_version: string
}
RegionSummary {
  lines: SummaryLine[]        // รายวัน: ข้อความสรุปสภาพอากาศ
  periods: Period[]           // 7 วัน: แยกตามช่วงวัน (รายวันเป็น [])
  advice: AdviceItem[]        // เฉพาะภาคนี้
}
Period { start: string, end: string, lines: SummaryLine[] }   // วันที่ ISO
SummaryLine { kind: "rain"|"temperature"|"wind"|"wave"|"fog"|"other", text: string, facts: object }
AdviceItem { text: string, scope: <region_key>[], general: boolean, source_unit_id: string }
```
- `text` ของ `SummaryLine` เป็นประโยคภาษาไทยที่เขียนตามแม่แบบ ส่วน `AdviceItem.text` คัดมาจากต้นฉบับตรงๆ
- `facts` เก็บค่าที่ดึงได้ (เช่น `rain_area_pct`, `temp_min`, `temp_max`) เพื่อใช้ตรวจ F1-F5
- ไม่ใส่เวลาประมวลผลไว้ในไฟล์ผลลัพธ์ (เพื่อให้ผลซ้ำได้) ใส่ใน metadata ตอนโหลด

## 3. ฐานข้อมูล (ข้อเสนอ ตารางเดียว)

```
forecast_issue (
  issue_id     text,
  doc_type     text,          -- 'daily' | 'sevenday'
  issued_at    timestamptz,
  source_label text,
  payload      jsonb,         -- Issue ทั้งก้อน
  loaded_at    timestamptz default now(),
  primary key (doc_type, issue_id)
)
index on (doc_type, issued_at desc)
```
ข้อมูลน้อย (หลักสิบฉบับ) การเก็บ JSON ทั้งก้อนง่ายที่สุด; บทบาท DB: ผู้โหลดเขียน (`DATABASE_URL_DIRECT`), เว็บอ่านอย่างเดียว (`DATABASE_URL`)

## 4. API ของ /demo (ข้อเสนอ)

`POST /api/summarize` (PDF ไม่เกิน 4 MB)
- สำเร็จ: `{ "ok": true, "issue": Issue }`
- ผิดพลาด: `{ "ok": false, "error": { "code": "unsupported_document" | "too_large" | "extract_failed" | "empty_file", "message_th": string } }` ข้อความภาษาไทยมาตรฐานอยู่ที่ `ERROR_MESSAGES_TH` ใน `contract.py`
- ไม่เก็บไฟล์ ไม่เก็บผลลัพธ์

## 5. ชุดป้าย (ไฟล์ตารางติดป้าย)
`unit_id | doc_type | appears_in (list) | text | context_prev | context_next | suggested_label | final_label | scope (เฉพาะ advice) | reviewer | note` ดูรายละเอียดใน `labeling-guideline.md`

## 6. พารามิเตอร์โมเดล
`models/*.json`: Naive Bayes (log prior, log likelihood ต่อคำ, ค่า m, คำศัพท์) และ k-NN (เวกเตอร์ตัวอย่าง, k) ขนาดเล็ก commit ได้
