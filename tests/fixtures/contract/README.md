# ไฟล์ตัวอย่างตามสัญญาข้อมูล v1 และ v2 (เขียนด้วยมือ)

ให้ฝั่งเว็บ (Phase 4.2-4.3) เริ่มงานได้ก่อนท่อประมวลผลเสร็จ และใช้ทดสอบสัญญาทั้งฝั่ง Python และ Zod

| ไฟล์ | ต้นฉบับ |
|---|---|
| `issue-daily-example.json` | `data/raw/daily/daily_311020261200.txt` (ฉบับ 31 ต.ค. 2569 11.00 น.) |
| `issue-sevenday-example.json` | `data/raw/sevenday/sevenday_261116.txt` (ฉบับ 16 พ.ย. 2569) |
| `shipping-example.json` (v2) | `data/raw/shipping/shipping_311020261900.txt` (เดินเรือ 31 ต.ค. 2569 19.00 น.) |
| `warning-example.json` (v2) | `data/raw/warning/warning_2569_315.txt` (ประกาศฉบับที่ 7 (315/2569)) |
| `weekly-example.json` (v2) | `data/raw/weekly/weekly_310820261200.txt` (สัปดาห์ 24-30 ส.ค. 2569) |
| `summarize-v2-generic-example.json` (v2) | `data/raw/generic/generic_outlook_monthly_2569_12.pdf` (คาดหมายเดือน ธ.ค. 2569) คำตอบ `/api/summarize` v2 แบบโหมดทั่วไปพร้อม trace ตัวอย่าง |

- ตัวเลข ช่วงตัวเลข ชื่อจังหวัด และคำแนะนำทุกค่ามาจากต้นฉบับของภาคนั้น คำแนะนำคัดมาตรงๆ
- **ถ้อยคำของประโยคสรุปเป็นตัวอย่างชั่วคราว ไม่ใช่ผลลัพธ์จริงหรือ golden file** แม่แบบจริงทำใน Phase 3.3
- การแบ่งคำแนะนำเป็นหน่วยและ scope ทำด้วยมือตามตารางแมปภาค (ของจริงมาจาก Phase 1.4 และ 3.2) `source_unit_id` เป็นค่าสมมุติ `fixture-uN`
- v2: ตัวเลข/ความมั่นใจ/คะแนนใน trace และป้ายของหน่วย generic เป็นค่าตัวอย่าง ไม่ใช่ผลของโมเดลจริง · เทสต์ `tests/contract/test_contract_v2.py` ตรวจว่าตัวเลขในประโยคแม่แบบมีในต้นฉบับ และข้อความที่คัดมา (คำแนะนำ หัวเรื่อง ชื่อพื้นที่ ช่องตาราง หน่วย generic) ตรงต้นฉบับคำต่อคำ
