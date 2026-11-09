# ผล spike Python บน Vercel (Phase 0.3, 2026-11-16)

**สรุป: ผ่าน ใช้แผน A ได้** (ฟังก์ชัน Python ใน `api/` อยู่คู่กับ Next.js ใน repo เดียว) ไม่ต้องใช้ทางถอยของ ADR 0006

deploy: commit `38816d5` จาก `Kanawatkha/tmd-plain-forecast` → โปรเจกต์ Vercel `tmd-plain-forecast` (Hobby) → https://tmd-plain-forecast.vercel.app · build 32 วินาที สถานะ Ready

## ตอบ 6 ข้อของ spike (`docs/architecture.md` หัวข้อ 4)
| # | คำถาม | ผล | หลักฐาน |
|---|---|---|---|
| 1 | `api/*.py` นำเข้าแพ็กเกจของเราและ PyThaiNLP ได้ไหม | **ได้** แพ็กเกจถูกติดตั้ง (`package_source: installed`) ไม่ต้องแก้ `sys.path` | JSON จาก `GET /api/hello` |
| 2 | ขนาด bundle และ cold start | **48.2 MB** (เพดาน 500 MB) · ครั้งแรกหลัง deploy 1.41 วินาที, ครั้งถัดไป 0.42 / 0.41 / 0.25 วินาที (เวลารวมที่ curl วัดจากเครื่องในไทย) | หน้า Resources ของ deployment, `curl -w` |
| 3 | Vercel ใช้ไฟล์ dependency ตัวไหน | `pyproject.toml` ผ่าน **uv 0.13.5** ("Installing required dependencies from pyproject.toml"), Python 3.12 จาก `requires-python` (เขียน `.python-version` ให้เอง) | build log |
| 4 | หน้า Next.js ยังทำงานไหม และ newmm ใช้ได้โดยไม่ดาวน์โหลด | `/` = 200, `/styleguide` = 200, `/api/nope` = 404 · newmm ตัด `ร้อยละ` และ `ฟ้าคะนอง` เป็นคำเดียว โดยตั้ง `PYTHAINLP_READ_ONLY=1`, `PYTHAINLP_OFFLINE=1`, `PYTHAINLP_DATA=/tmp/pythainlp-data` ในโค้ด (ไม่ต้องตั้งบนหน้า Vercel) | curl, JSON |
| 5 | pypdfium2 อ่าน PDF ไทยได้ดีแค่ไหน | คุณภาพข้อความตรวจแล้วใน 0.2 (ผ่าน) · บน Vercel ไลบรารีโหลดได้และสร้าง PDF ได้ (`pdfium_new_pages: 1`, 5.15.2) ยังไม่ได้ส่ง PDF จริงขึ้นไปทดสอบ (ทำใน 5.1) | JSON |
| 6 | เลือก `sin1` บน Hobby ได้ไหม | **ได้** `regions: ["sin1"]` ใน `vercel.json` → ทุกฟังก์ชันอยู่ SIN1 (`X-Vercel-Id: sin1::sin1::...`, `region: "sin1"`) ใกล้ Neon (Singapore) | header, หน้า Resources |

อื่นๆ: `excludeFiles` ทำงาน (`data_dir_bundled: false`) · ฟังก์ชัน Next.js รันบน Node.js 26.x · max duration ≤ 300 วินาที

## ข้อสังเกตและสิ่งที่ยังไม่ได้วัด
- เวลา cold start ที่วัดได้คือครั้งแรกหลัง deploy ใหม่ ไม่ได้รอให้ instance หลับแล้ววัดซ้ำ เวลานำเข้าใน JSON ของครั้งที่ warm เป็น 0 เพราะโมดูลถูกโหลดไว้แล้ว (ค่า cold บนเครื่อง: PyThaiNLP 93 ms + ตัดคำครั้งแรก 215 ms)
- ตัวเลขเวลาเป็นเวลารวมผ่านอินเทอร์เน็ตจากเครื่องผู้ใช้ ไม่ใช่เวลาในฟังก์ชันล้วน
- `api/hello.py` เป็นไฟล์ spike ลบแล้วใน Phase 5.1 แทนด้วย `api/summarize.py` (ผลบนเว็บจริงใน ai/PROGRESS.md หัวข้อ Phase 5.1)
