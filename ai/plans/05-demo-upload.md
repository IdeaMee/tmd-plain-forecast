# แผน 05: ฟังก์ชัน `/api/summarize` และหน้า `/demo`

**สถานะ (2026-11-17):** 5.1 และ 5.2 เสร็จ ทดสอบบนเว็บจริงแล้ว ผู้ใช้ลองบนมือถือและเซ็นปิด · ตัดสินระหว่างทำ: body เป็น PDF ดิบ (ไม่ใช่ multipart) และอ่านรหัสฉบับจากหัว PDF (`meta_from_text`) ดู `docs/spec/data-contract.md` หัวข้อ 4 · ข้อความข้างล่างคือแผนเดิม

**เป้าหมาย:** ผู้ใช้อัปโหลด PDF พยากรณ์รายวันหรือ 7 วันของ TMD (ไม่เกิน 4 MB) แล้วเห็นสรุป 7 ภาคที่คำนวณสดด้วยท่อประมวลผลชุดเดียวกัน ไฟล์ผิดชนิดได้ข้อความภาษาไทยที่บอกว่าต้องทำอะไร ไม่มีการเก็บไฟล์

**สเปก:** [../../docs/spec/data-contract.md](../../docs/spec/data-contract.md) หัวข้อ 4 · [../../docs/spec/ui-spec.md](../../docs/spec/ui-spec.md) หัวข้อ 2 · [../../docs/decisions/0006-python-on-vercel.md](../../docs/decisions/0006-python-on-vercel.md) · ผล spike `docs/results/spike-vercel-python.md` (0.3) · skill `python-pipeline` (Function entry), `frontend-responsive-ui`

**เงื่อนไขเริ่ม:** 0.3 ผ่าน (ถ้าไม่ผ่าน ใช้ทางถอยตาม Q2 และแก้แผนนี้ก่อน) · 3.4 และ 4.2 เสร็จ

**ข้อจำกัดที่ใช้:** `api/` มีแค่ไฟล์ทางเข้าบางๆ logic อยู่ในแพ็กเกจ · นำเข้าแบบเบาตอนโหลดโมดูล (cold start) · `PYTHAINLP_READ_ONLY=1` · ไม่เก็บไฟล์และผลลัพธ์ · ตรวจขนาดในเบราว์เซอร์ก่อนส่ง (body ของ Vercel ไม่เกิน 4.5 MB)

---

## Phase 5.1: ฟังก์ชัน `/api/summarize`   [M]   [เจ้าของ: ผู้ช่วย; ผู้ใช้ push และเตรียมไฟล์ทดสอบ]

Goal: `POST /api/summarize` รับ PDF แล้วตอบ `{ok: true, issue}` หรือ `{ok: false, error: {code, message_th}}` ตามสัญญา

Inputs
- แพ็กเกจที่ผ่าน 3.4, `vercel.json` (0.3), PDF ทดสอบใน `data/raw/`

Tasks
1. `src/tmd_plain/service.py`: `summarize_pdf(bytes) -> Issue | ErrorResponse` (ตรวจขนาด → ตรวจว่าเป็น PDF → ดึงข้อความ → ตรวจชนิด → ท่อประมวลผล) เป็นฟังก์ชันบริสุทธิ์ที่ทดสอบได้โดยไม่ต้องมี Vercel
2. `api/summarize.py`: อ่านคำขอ (รูปแบบ body ตามเอกสาร Vercel Python ปัจจุบัน บันทึกว่าใช้แบบไหน) → `summarize_pdf` → JSON
3. `tests/service/test_summarize.py`: PDF รายวัน 1, PDF 7 วัน 1, ไม่ใช่ PDF, ไฟล์ว่าง, ไฟล์เกิน 4 MB (สร้างในเทสต์), PDF ที่ไม่ใช่พยากรณ์ (พยากรณ์เดินเรือ ถ้าผู้ใช้เตรียมให้ ไม่งั้นใช้ PDF อื่นที่ไม่ใช่ของ TMD)
4. `excludeFiles` ใน `vercel.json` ยังกันโฟลเดอร์ที่ไม่ใช้ และใส่ `models/` ที่ต้องใช้

Checks
- `.venv/Scripts/python.exe -m pytest tests/service -q` ผ่าน: 2 ไฟล์จริงได้ `Issue` ครบ 7 ภาค และผ่าน F1-F5 (ใช้ตัวตรวจจาก 3.4), อีก 4 กรณีได้รหัสข้อผิดพลาดตรงตามสัญญา
- หลังผู้ใช้ push: `POST <preview-url>/api/summarize` ด้วย PDF รายวันจริง → 200 + JSON ผ่าน Zod; บันทึกเวลา cold/warm

Human steps: โหลด PDF พยากรณ์เดินเรือ 1 ไฟล์ด้วยมือจากเว็บ TMD ไว้ที่ `data/raw/negative/` (ไม่ขึ้น repo) · สั่ง commit/push แล้วส่ง URL ของ preview

Out of scope: หน้าเว็บ (5.2)

---

## Phase 5.2: หน้า `/demo`   [M]   [เจ้าของ: ผู้ช่วย; ผู้ใช้รีวิว]

Goal: หน้า `/demo` อัปโหลด PDF ได้ด้วยเมาส์ นิ้ว และคีย์บอร์ด เห็นสถานะกำลังประมวลผล ผลลัพธ์ใช้การ์ดชุดเดียวกับหน้าหลัก และข้อผิดพลาด 4 แบบมีข้อความต่างกัน

Tasks
1. `app/demo/page.tsx` + `components/features/UploadDropzone` (`<input type="file" accept="application/pdf">` จริงพร้อม label, พื้นที่ลากวาง, ตรวจ 4 MB ก่อนส่ง, กันส่งซ้ำ) และ ResultPanel (ใช้ ForecastCard เดิม)
2. ข้อความ: "ไม่เก็บไฟล์ที่อัปโหลด", "ผลจาก PDF อาจแม่นน้อยกว่าผลบนหน้าหลัก", ข้อผิดพลาดตาม `message_th` ใน `aria-live`
3. ลิงก์ไป `/demo` จาก Header และ Hero
4. `tests/e2e/demo.spec.ts`: บนเครื่องจำลองคำตอบของ `/api/summarize` (ไม่มี Vercel CLI); บน preview URL รันกับไฟล์จริง

Checks
- `npm run e2e` ผ่าน (build + Playwright บน Edge โหมดจำลอง; ห้ามเรียก `npx` ใน path นี้ ดู `.claude/CLAUDE.md`) และกรณีไฟล์จริงบน preview URL ผ่าน
- ภาพหน้าจอ 375 / 1280 px ของ: ก่อนเลือกไฟล์, กำลังประมวลผล, ผลลัพธ์, ข้อผิดพลาดแต่ละแบบ ไล่ตาม `ui-checklist.md` หัวข้อ 4-5
- คำสั่งตรวจของ 4.2 ผ่านทั้งหมด

Human steps: ผู้ใช้ลองอัปโหลดเองบนมือถือจริง 1 ครั้ง แล้วเซ็นปิด

Out of scope: เก็บประวัติการอัปโหลด, รับเอกสารชนิดอื่น
