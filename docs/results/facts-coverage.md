# ความครอบคลุมของการดึงค่า (Phase 3.1)

คำสั่ง: `.venv/Scripts/python.exe -X utf8 scripts/check_facts.py` · ไฟล์นี้สร้างโดยสคริปต์

ขอบเขต: บล็อกภาคของฉบับที่แสดงบนเว็บ (`display_test` ใน MANIFEST) ทั้งข้อความหน้าเว็บและ PDF · daily/pdf 28 ไฟล์, daily/txt 28 ไฟล์, sevenday/pdf 7 ไฟล์, sevenday/txt 1 ไฟล์

| ตรวจ | ผล |
|---|---|
| บรรทัดในบล็อกภาค | 2496 |
| บรรทัดที่ได้ค่าอย่างน้อยหนึ่งค่า | 2496 (100.0%) |
| ข้อผิดพลาด (ตัวเลขไม่ถูกดึง, source ไม่อยู่ในบรรทัด, จังหวัดผิดภาค) | 0 |

## จำนวนค่าที่ดึงได้ แยกตามชื่อ
| ชื่อ | จำนวน |
|---|---|
| `area_part` | 40 |
| `cloud` | 65 |
| `cold` | 228 |
| `fog` | 112 |
| `gusts` | 31 |
| `heavy_rain` | 119 |
| `light_rain` | 79 |
| `peak_feel` | 148 |
| `peak_place` | 148 |
| `peak_temp_min_high` | 148 |
| `peak_temp_min_low` | 148 |
| `period_end` | 119 |
| `period_start` | 119 |
| `period_text` | 119 |
| `province` | 984 |
| `rain_area_pct_high` | 289 |
| `rain_area_pct_low` | 289 |
| `rain_kind` | 289 |
| `some_rain` | 85 |
| `strong_wind` | 94 |
| `temp_change_high` | 182 |
| `temp_change_low` | 182 |
| `temp_max_high` | 488 |
| `temp_max_low` | 488 |
| `temp_min_high` | 488 |
| `temp_min_low` | 488 |
| `temp_trend` | 213 |
| `very_heavy_rain` | 26 |
| `wave_m_high` | 262 |
| `wave_m_low` | 262 |
| `wave_offshore_m_high` | 134 |
| `wave_offshore_m_low` | 134 |
| `wave_offshore_qualifier` | 134 |
| `wave_qualifier` | 262 |
| `wave_storm_m_high` | 210 |
| `wave_storm_m_low` | 210 |
| `wave_storm_qualifier` | 210 |
| `wind_area` | 96 |
| `wind_dir` | 553 |
| `wind_speed_kmh_high` | 553 |
| `wind_speed_kmh_low` | 553 |

## บรรทัดที่ไม่ได้ค่า (0)
ไม่มี

## ข้อผิดพลาด (0)
ไม่มี

## ข้อสังเกต
- วลีช่วงวันที่ไม่ต่อเนื่อง ("16 และ 18 - 19 พ.ย.") เก็บเป็นวันแรกถึงวันสุดท้าย และเก็บวลีเต็มไว้ใน `period_text`
- วลีช่วงวันกลางบรรทัด ("ฝนตกหนักมากในช่วงวันที่ 20 - 22 พ.ย.") หมายถึงเฉพาะส่วนนั้น ไม่ใช่ทั้งบรรทัด ขั้นแม่แบบ (3.3) ต้องดู `period_text` คู่กับตำแหน่ง
- รายชื่อจังหวัดบางบรรทัดต่อจากบรรทัดก่อน (บรรทัดที่มีแต่จังหวัด) ขั้นแม่แบบต้องรวมกับบรรทัดก่อนหน้า
