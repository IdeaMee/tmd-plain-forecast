# ข้อมูลทดสอบ e2e

- `empty/`: ไม่มีฉบับเลย → หน้า /, /warnings และ /summaries ต้องแสดงสถานะ "ยังไม่มีข้อมูล"
- `broken/`: ไฟล์ไม่ผ่านสัญญา (`Issue`, `WarningNotice` ใน `warning/`, `WeeklySummary` ใน `weekly/`) → หน้า /, /warnings และ /summaries ต้องแสดงสถานะผิดพลาดพร้อมปุ่ม "ลองใหม่"

`playwright.config.ts` เปิด `next start` แยกพอร์ตโดยตั้ง `FORECAST_DATA_DIR` ชี้มาที่โฟลเดอร์เหล่านี้
