# วิธีเก็บข้อมูลดิบด้วย Claude in Chrome (รอบ v2)

ใช้กับ Phase 9.1-9.3 (`ai/plans/09-data-collection.md`) ภายใต้ ADR 0015 · เขียนจากการเก็บจริง 2026-11-18 · โค้ดที่รันในแท็บอยู่ใน [collection/collector.js](collection/collector.js)

## หลักการ
- ทุกหน้าเปิดในแท็บ Chrome ของผู้ใช้ทีละหน้า (Claude in Chrome) ไม่มีสคริปต์บนเครื่องยิง tmd.go.th
- ข้อความไม่ผ่านแชต: โค้ดในแท็บอ่าน `document.body.innerText` ตัดเฉพาะเนื้อหาหลัก เก็บใน IndexedDB ของแท็บ แล้วส่งออกเป็น JSON ไฟล์เดียวต่อชุด (ลง Downloads) จากนั้น `scripts/import_raw_batch.py` เขียนไฟล์ลง `data/raw/<ชนิด>/` และต่อแถว `MANIFEST.csv`
- PDF: โค้ดในแท็บอ่าน path ใต้ `/media/` จากปุ่ม "ดาวน์โหลดเอกสาร" (`window.open(...)`) หรือ iframe แล้วโหลดไฟล์นั้นจากหน้าเดียวกัน (เท่ากับกดปุ่ม) ต้องขึ้นต้นด้วย `%PDF`
- เว้นจังหวะ ~4 วินาทีต่อหน้า (รอโหลดเสร็จ + 2 วินาที + รอระหว่างขั้น) ส่งออกทุก ≤ 10-20 ฉบับ
- หยุดทันทีเมื่อเจอ CAPTCHA, หน้าบล็อก, 403/429 ซ้ำ หรือหน้าเข้าสู่ระบบ
- เสร็จแล้วลบ key `tmd*` ใน localStorage และฐาน IndexedDB `tmdc` ของแท็บ ย้ายไฟล์ชุดออกจาก Downloads

## ขั้นตอน
1. เปิดหน้าใดก็ได้ของ www.tmd.go.th แล้วเก็บฟังก์ชัน `tmdc`, `tmdpdf`, `tmdstep` จาก `collector.js` ลง localStorage (`localStorage.setItem("tmdc", tmdc.toString())` ...)
2. สร้างคิว `localStorage.tmdq = [{kind, id, path, pdf?, pdfonly?}]` จากหน้ารายการ (ตารางด้านล่าง)
3. เรียกซ้ำ `await (0,eval)('(' + localStorage.getItem('tmdstep') + ')')()` (หลายครั้งต่อ `browser_batch` คั่นด้วย wait 1 วินาที) จนได้ `done` · ผลแต่ละขั้นเป็นข้อความสั้น `ok <ชนิด> <รหัส> len <n> pdf <bytes>`
4. ส่งออก: `await (0,eval)('(' + localStorage.getItem('tmdc') + ')')('__export', 'tmdc_v2_<ชนิด>_<nn>.json')` แล้วรอ ~5 วินาทีโดยไม่เปลี่ยนหน้า · ตรวจว่าไฟล์อยู่ใน Downloads จริง แล้วค่อยล้างด้วย `('__clear')` (`__export` ไม่ล้างเองแล้ว เพราะ Chrome อาจบล็อกการดาวน์โหลดแบบเงียบ)
5. นำเข้า: `.venv/Scripts/python.exe -X utf8 scripts/import_raw_batch.py "<Downloads>/tmdc_v2_<...>.json" --role <บทบาท>` (ต้อง `errors: 0`; ไฟล์ที่มีแล้วและเหมือนเดิมจะข้าม ต่างกันจะไม่เขียนทับ)
6. ตรวจ: `.venv/Scripts/python.exe -X utf8 scripts/check_raw.py` (ต้อง `errors: 0`) → `docs/results/raw-inventory.md`

## ต่อหมวด
| ชนิด (`kind`) | หน้ารายการ | หน้ารายฉบับ / รหัส | เนื้อหาที่ตัด | PDF |
|---|---|---|---|---|
| `daily` | `/forecast/daily` (ตัวเลือก 100 รอบ) | `/forecast/daily/<DDMMYYYYHHMM>` | "ลักษณะอากาศทั่วไป" → ก่อน "เนื้อหาในหน้านี้" (**ตรงกับไฟล์เดิมทุกไบต์**, ตรวจ 2026-11-18 ด้วยรอบ 161120261800) | ไม่มีปุ่มในหน้า (ไฟล์เดิมมาจาก `/media/forecast/daily-forecast/...`) |
| `sevenday` | `/forecast/sevenday` (ฉบับวันนี้เท่านั้น) | รหัส `<YYMMDD>` ตามชื่อ PDF (ยังอยู่ที่ path `/forecast/sevenday`) | "คาดหมายอากาศทั่วไป" → ก่อน "เนื้อหาในหน้านี้" | ปุ่มดาวน์โหลด `/media/forecast/7-day/t_<YYMMDD>.pdf` |
| `shipping` | `/forecast/shipping` (ตัวเลือก 100 รอบ 24 ต.ค.-18 พ.ย.) | `/forecast/shipping/<DDMMYYYYHHMM>` | เหมือนรายวัน | ไม่มี |
| `weekly` | `/climate/summaryweekly` (ตัวเลือก 100 ฉบับ ธ.ค. 2568-พ.ย. 2569) | `/climate/summaryweekly/<DDMMYYYYHHMM>` | "ประเทศไทย" (หลังปุ่มแบ่งปัน) → ก่อน "เนื้อหาในหน้านี้" มีตารางรายภาคคั่นด้วยแท็บ | แผนที่ (มีชั้นข้อความ) 1 ฉบับไม่มีปุ่ม |
| `warning` | `/warning-and-events/warning-storm?page=N` (10 ต่อหน้า 16 หน้า) | slug ภาษาไทยที่ลงท้าย `-<เลข>-<ปี>` → รหัส `<ปี>_<เลข>` | "ประกาศกรมอุตุนิยมวิทยา" → ก่อน "วันที่โพส" หรือ "Tags:" (ฉบับเก่าก่อน ต.ค. ไม่มี "วันที่โพส") | ปุ่มดาวน์โหลด `/media/forecast/warning/<yyyy-mm_dd_hh>_warning_th.pdf` |
| `agro7` | `/forecast/agromet/7days` | `/forecast/agromet/7days/<DDMMYYYY>` | - | iframe `/media/agro/7day/<ปี>/agronews_<n>_<yy>.pdf` |
| `outlook3m` | `/forecast/threemonthcountry` | `/forecast/threemonthcontentcountry/<slug>` (slug ไม่สม่ำเสมอ ใช้ตามลิงก์) | - | iframe |
| `generic` | ENSO `/climate/El-Nino-La-Nina`, คาดหมายรายเดือน `/forecast/monthly`, สรุปรายเดือน `/climate/summarymonthly`, รายปี `/climate/summaryyearly`, เกษตรรายปักษ์ `/forecast/agromet/fortnight/<id>`, เกษตรราย 3 เดือน `/forecast/agromet/quater/<id>` | รหัสตั้งเอง เช่น `enso_2569_09` | - | ฉบับล่าสุดในหน้า |

## ข้อควรรู้
- เครื่องมือของ Claude in Chrome บล็อกผลลัพธ์ที่มี query string หรือข้อความยาวคล้าย base64 ให้คืนเฉพาะตัวเลข/สถานะสั้น ๆ และเปรียบเทียบ hash ในแท็บ
- เกษตร 7 วัน: หน้ารายการมี 72 หน้า = 711 รหัส (รวมรหัสพิมพ์ผิดของ TMD เช่น `08121478`) PDF ตอบ 404 รวม 43 ฉบับ (ส่วนใหญ่ปี 2564-2565 และ พ.ค. 2566 ทั้งเดือน) บางหน้าฝัง PDF ของฉบับก่อนหน้าซ้ำ (`check_raw` จะฟ้อง "same content") · คาดหมาย 3 เดือนบางหน้าไม่มีเอกสารแนบเลย · บันทึกเป็นช่องโหว่ (รายชื่อใน `ai/PROGRESS.md` หัวข้อ 9.2) ไม่ต้องลองซ้ำ
- ถ้าไฟล์ชุดไม่ลง Downloads (แม้ไฟล์ทดสอบเล็ก ๆ) แปลว่า Chrome บล็อกการดาวน์โหลดอัตโนมัติของไซต์ ให้ผู้ใช้เพิ่ม `[*.]tmd.go.th` ในรายการ "Allowed to automatically download multiple files" ที่ `chrome://settings/content/automaticDownloads` (กด Allow ที่แถบที่อยู่ได้ผลแค่หน้านั้น) ผู้ช่วยแก้การตั้งค่า Chrome ไม่ได้
- `agro7_11112026.pdf` เป็นภาพล้วน (ไม่มีชั้นข้อความ) ใช้ทดสอบการปฏิเสธใน `/demo` ได้
- ไฟล์ชุด JSON หลังนำเข้าแล้วไม่ต้องเก็บ (ข้อมูลอยู่ใน `data/raw` + sha256 ใน MANIFEST)
