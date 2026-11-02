# แผน 00: ฐานโครง repo และการทดสอบความเสี่ยง (Phase 0)

**เป้าหมาย:** ตัดความไม่แน่นอนใหญ่ที่สุดก่อนเขียนโค้ดจริง: path ที่มีภาษาไทย/ช่องว่าง/`&`, คุณภาพข้อความจาก PDF (ฉบับ 7 วันเกือบทั้งหมดมีแต่ PDF), Python บน Vercel, Neon, และฟอนต์ Anuphan กับโทเคนดีไซน์

**สเปก:** [../../docs/architecture.md](../../docs/architecture.md) หัวข้อ 4 และ 7 · [../../docs/decisions/0006-python-on-vercel.md](../../docs/decisions/0006-python-on-vercel.md) · [../../docs/spec/design-system.md](../../docs/spec/design-system.md) · `.claude/skills/thai-text-handling/`

**ข้อจำกัดที่ใช้ (จาก .claude/CLAUDE.md):** ของฟรีเท่านั้น · ห้ามสร้างบัญชี/ล็อกอิน/deploy/รัน git (ผู้ใช้ทำ) · TypeScript ตรึง 6.0.x · ห้ามมี `app/api/` · ห้าม PyMuPDF · ห้ามดึง tmd.go.th ด้วยสคริปต์ (ใช้แค่ `data/raw/`) · ห้ามแก้ `docs/design/DESIGN-expo.md` · ห้ามเดาคำสั่ง

---

## Phase 0.1: โครง repo และคำสั่งจริง   [M]   [เจ้าของ: ผู้ช่วย]

Goal: ที่ Root มีแอป Next.js เปล่าที่ build ได้ และแพ็กเกจ Python เปล่าที่ทดสอบได้ หัวข้อ `Commands` ใน `.claude/CLAUDE.md` มีแต่คำสั่งที่รันแล้วจริง

Inputs
- `.claude/CLAUDE.md`, `docs/architecture.md` (หัวข้อ 2, 7), `docs/decisions/0004-tech-stack.md`, ชื่อแพ็กเกจ `tmd_plain` (Q1 ตกลงแล้ว)

Tasks
1. สร้าง Next.js 16 (App Router, TypeScript, Tailwind 4, ESLint) ที่ Root ถ้า `create-next-app` ไม่ยอมสร้างในโฟลเดอร์ที่ไม่ว่าง ให้สร้างในโฟลเดอร์ชั่วคราวในพื้นที่ scratch แล้วย้ายไฟล์เข้ามา **ห้ามเขียนทับ** `.claude/CLAUDE.md`, `README.md`, `.gitignore` (ผสานบรรทัด ignore ของ Next.js เข้า `.gitignore` เดิมด้วยมือ)
2. `package.json`: ตรึง `typescript` 6.0.x; ใส่ `@AGENTS.md` บรรทัดแรกของ `.claude/CLAUDE.md`
3. `app/globals.css`: จำกัดการสแกนคลาสของ Tailwind ไว้ที่ `app/`, `components/`, `lib/` (ไวยากรณ์ `@source` ตามเอกสารของเวอร์ชันที่ติดตั้ง)
4. Python: `pyproject.toml` (แพ็กเกจ `src/tmd_plain/`, `requires-python >= 3.12`, runtime: pythainlp, pypdfium2, pdfminer.six, pydantic; dev: pytest, ruff), `src/tmd_plain/__init__.py`, `tests/test_smoke.py`, virtualenv `.venv`
5. `.editorconfig` (UTF-8, LF), `.gitattributes` (`* text=auto eol=lf` แก้คำเตือน CRLF), `.env.example` (ชื่อตัวแปรเท่านั้น: `DATABASE_URL`, `DATABASE_URL_DIRECT`, `REVALIDATE_SECRET`, `PYTHAINLP_READ_ONLY`, `PYTHAINLP_DATA`)
6. เติม `Commands` ใน `.claude/CLAUDE.md` (ติดตั้งเว็บ, ติดตั้ง Python, dev, lint, typecheck, test Python, build) และแถว `.gitattributes`, `pyproject.toml` ในตารางของ `docs/architecture.md`

Outputs
- `package.json`, `package-lock.json`, `next.config.ts`, `tsconfig.json`, `eslint.config.mjs`, `app/` (หน้าเริ่มต้น), `AGENTS.md`, `pyproject.toml`, `src/tmd_plain/`, `tests/test_smoke.py`, `.editorconfig`, `.gitattributes`, `.env.example`, `.claude/CLAUDE.md` (Commands)

Checks
- `npm run build` ที่ path จริงของ Root → exit 0 (ถ้าพังเพราะ path ให้หยุด: ทางถอยคือผู้ใช้ clone ไป path สั้น เช่น `C:\dev\tmd-plain-forecast`)
- `npx tsc --noEmit` → exit 0 · `npx eslint .` → exit 0 · `npm ls typescript` → 6.0.x
- `.venv\Scripts\python -m pytest -q` → 1 passed · `.venv\Scripts\ruff check .` → ไม่มีข้อผิดพลาด
- `.venv\Scripts\python -c "from pythainlp.tokenize import word_tokenize; print(word_tokenize('ฝนฟ้าคะนองร้อยละ 30 ของพื้นที่', engine='newmm'))"` → มี `ร้อยละ` และ `ฟ้าคะนอง` เป็นคำเดียว
- ไม่มีโฟลเดอร์ `app/api/` · `.claude/CLAUDE.md` ยังไม่เกิน 200 บรรทัด
- session ใหม่ที่เปิดจาก Root เห็น skill ของโปรเจกต์ครบ 7 ตัวและกฎ `frontend.md`/`python.md` ถูกโหลดเมื่อแตะไฟล์ที่ตรง (ยังไม่เคยทดสอบ ดู ADR 0009)

Human steps: เปิด session ใหม่จาก Root เพื่อเช็กการโหลด skill · ถ้าต้องการ ให้สั่ง commit/push หลังเซ็นปิด

Out of scope: เนื้อหาหน้าเว็บ, ฟอนต์และโทเคน (0.5), `api/` (0.3), ฐานข้อมูล (0.4)

---

## Phase 0.2: ทดสอบข้อความจาก PDF ของ TMD   [M]   [เจ้าของ: ผู้ช่วย; ผู้ใช้ตัดสินถ้าไม่ผ่านเกณฑ์]

Goal: รู้เป็นตัวเลขว่า pypdfium2 (หรือ pdfminer.six) ให้ข้อความดีพอสำหรับรายวันและ 7 วันหรือไม่

Inputs
- `data/raw/daily/` (46 คู่ PDF + ข้อความจาก HTML), `data/raw/sevenday/` (19 PDF + ข้อความ 1 ฉบับ 16 พ.ย.), `.claude/skills/thai-text-handling/references/known-defects.md`

Tasks
1. `src/tmd_plain/prep/pdf_text.py`: ดึงข้อความด้วยตัวอ่านทั้งสอง + ทำความสะอาดลำดับ 1-5 ของ skill `thai-text-handling` (ไฟล์นี้ใช้ต่อใน 1.2 ไม่ใช่โค้ดทิ้ง)
2. `scripts/spike_pdf_extract.py`: ต่อไฟล์ต่อตัวอ่าน วัด (ก) พบหัวข้อ 7 ภาคไหม (ข) ตัวเลขทุกตัวในแต่ละบล็อกภาคตรงกับข้อความ HTML ของรอบเดียวกันไหม (รายวัน 46 คู่ + 7 วัน 1 คู่) (ค) อัตราความเหมือนของข้อความต่อบล็อก (ง) พบวลีช่วงวัน "ในช่วงวันที่" ในฉบับ 7 วันไหม (จ) อักษร PUA ที่เหลือ (ฉ) เวลาต่อไฟล์
3. `tests/fixtures/pdf/`: ข้อความคาดหวังที่ตรวจด้วยตา 5 ไฟล์ (รายวัน 3, 7 วัน 2 ตัดเป็นช่วงสั้น) + `tests/prep/test_pdf_text.py`
4. `docs/results/spike-pdf-extraction.md`: ตารางผล + ตัวอ่านที่เลือก + ข้อบกพร่องใหม่ (เพิ่มลง `known-defects.md`); สร้างโฟลเดอร์ `docs/results/` และเพิ่มแถวใน `docs/README.md`

เกณฑ์ผ่าน (ข้อเสนอ ผู้ใช้ปรับได้): รายวัน พบครบ 7 ภาค ≥ 44/46 ไฟล์ และตัวเลขต่อบล็อกตรงกับ HTML ≥ 95% ของบล็อก · 7 วัน พบครบ 7 ภาคและวลีช่วงวัน 19/19 ไฟล์ และตัวเลขตรงกับ HTML ในคู่ 16 พ.ย.

Checks
- `python scripts/spike_pdf_extract.py` รันครบ 65 PDF ไม่ crash และพิมพ์ตารางสรุป
- `python -m pytest tests/prep -q` → ผ่านทั้ง 5 fixture
- ตัวเลขในรายงานตรงกับผลรันซ้ำ (ผู้ตรวจรันเอง)

Human steps: ถ้าไม่ผ่านเกณฑ์ ผู้ใช้เลือก: (ก) ยอมรับคุณภาพที่ได้และเขียนเป็นข้อจำกัด (ข) แสดงฉบับ 7 วันเฉพาะฉบับที่มีข้อความ HTML (ค) ตัดฉบับ 7 วันออกจากหน้าหลัก (ต้อง ADR)

Out of scope: แยกบล็อกภาคจริงจัง (1.3), ข้อความจาก HTML (1.2)

---

## Phase 0.3: Spike Python บน Vercel   [M]   [เจ้าของ: ทั้งสอง]

Goal: ตอบด้วย deploy จริงบน Vercel Hobby ว่า `api/*.py` นำเข้าแพ็กเกจของเรา + PyThaiNLP + pypdfium2 ได้ภายในข้อจำกัด และหน้า Next.js ยังทำงาน

Inputs
- ผลของ 0.1, รายการ spike 6 ข้อใน `docs/architecture.md` หัวข้อ 4

Tasks (ผู้ช่วย)
1. `api/hello.py`: ตอบ JSON = รุ่น Python, ผลตัดคำ newmm ของประโยคตัวอย่าง, รุ่น pypdfium2, เวลานำเข้า (ms), ค่า `PYTHAINLP_DATA`; นำเข้า `tmd_plain` จาก `src/`
2. `vercel.json`: `excludeFiles` (อย่างน้อย `docs/**`, `course/**`, `data/**`, `ai/plans/**`, `.claude/**`, `tests/**`, `node_modules/**`), region ใกล้ Neon (ลอง `sin1` บันทึกว่า Hobby ยอมไหม)
3. ไฟล์ dependency ของ Python ตามเอกสาร Vercel ปัจจุบัน (อ่านก่อน แล้วบันทึกว่า Vercel ใช้ไฟล์ไหน)
4. `docs/results/spike-vercel-python.md` + อัปเดต `docs/architecture.md` หัวข้อ 4 ด้วยผลจริง

Human steps (ผู้ใช้)
1. สมัคร Vercel Hobby ด้วย GitHub, ติดตั้ง Vercel GitHub App
2. import repo หนึ่งตัว (`KhwamkhitMee/tmd-plain-forecast` หรือ `IdeaMee/tmd-plain-forecast`: ถ้าเป็น repo ของ organization ให้เช็กว่า Hobby import ได้ไหม)
3. ตั้ง env: `PYTHAINLP_READ_ONLY=1`, `PYTHAINLP_DATA=/tmp/pythainlp-data` (และ `VERCEL_ANALYZE_BUILD_OUTPUT=1` ชั่วคราว)
4. สั่ง commit + push แล้วส่ง URL ให้ผู้ช่วย

Checks (ผู้ช่วย หลังได้ URL)
- `GET <url>/` → 200 (หน้า Next.js) · `GET <url>/api/hello` → 200 JSON ที่ตัด `ร้อยละ` เป็นคำเดียว
- เวลา: ครั้งแรกหลังว่าง (cold) และครั้งที่ 2-3 (warm) บันทึกเป็นตัวเลข
- ขนาด bundle ของฟังก์ชันจาก log build < 500 MB · region ที่ใช้จริง
- ครบ 6 ข้อของ spike ในรายงาน (ข้อไหนตอบไม่ได้ให้เขียนว่าไม่ได้ตรวจ)

Stop conditions: นำเข้าไม่ได้, เกินขีดจำกัด, timeout → หยุด ใช้ทางถอยตาม Q2 ที่ตกลงแล้ว (ลอง Vercel Services หนึ่งรอบ ถ้าไม่ผ่านรัน `/demo` บนเครื่องตอนพรีเซนต์) โดยแจ้งผู้ใช้ก่อนเริ่ม ห้ามเปลี่ยนสถาปัตยกรรมเอง

Out of scope: `/api/summarize` จริง (5.1), ฐานข้อมูล

---

## Phase 0.4: ตั้ง Neon   [S]   [เจ้าของ: ทั้งสอง]

Goal: มีโปรเจกต์ Neon ที่มีตาราง `forecast_issue` เครื่องทีมเขียน/อ่านได้ และ role ของเว็บอ่านได้อย่างเดียว

Inputs
- `docs/spec/data-contract.md` หัวข้อ 3, ไลบรารี `psycopg[binary]` 3.x (Q5 ตกลงแล้ว)

Tasks (ผู้ช่วย)
1. `db/schema.sql` (ตาราง + index ตามสัญญา v0), `db/roles.sql` (GRANT SELECT ให้ role อ่านอย่างเดียว)
2. `scripts/db_check.py`: ใช้ `DATABASE_URL_DIRECT` สร้างตารางแบบรันซ้ำได้, เขียนแถวทดสอบ อ่านกลับ แล้วลบ; ใช้ `DATABASE_URL` ลองเขียน (ต้องถูกปฏิเสธ)
3. อ่านขีดจำกัดแผนฟรีปัจจุบันของ Neon จากเอกสาร บันทึกใน `docs/results/neon-setup.md`

Human steps: สมัคร Neon, สร้างโปรเจกต์ (Singapore ถ้ามี), รัน `db/roles.sql` หรือสร้าง role ใน dashboard, ใส่ `DATABASE_URL` (pooled, role อ่าน) และ `DATABASE_URL_DIRECT` ลงไฟล์ `.env` บนเครื่องเอง **ห้ามวางในแชท**

Checks
- `python scripts/db_check.py` → พิมพ์ว่า schema ok, เขียน/อ่าน ok, role อ่านอย่างเดียวถูกปฏิเสธการเขียน (ตามที่ควร)
- `.env` ไม่อยู่ในรายการไฟล์ที่ git จะเก็บ (ผู้ใช้ตรวจด้วย `git status` ตอนสั่ง commit)

Out of scope: เว็บอ่าน DB (4.1), สคริปต์โหลดจริง (4.1)

---

## Phase 0.5: โทเคนดีไซน์และฟอนต์ Anuphan   [S]   [เจ้าของ: ผู้ช่วย; ผู้ใช้ดูภาพ]

Goal: โทเคนของ `docs/design/DESIGN-expo.md` อยู่ใน `@theme`, Anuphan โหลดได้ และพิสูจน์ด้วยภาพหน้าจอว่าข้อความไทยไม่ถูกตัด

Inputs
- `docs/design/DESIGN-expo.md` (อ่านอย่างเดียว), `docs/spec/design-system.md` หัวข้อ 2-4, 7, ข้อความพยากรณ์จริง 1 ย่อหน้าจาก `data/raw/daily/`

Tasks
1. `app/layout.tsx`: Anuphan ผ่าน `next/font/google` (`thai`, `latin`), `<html lang="th">`
2. `app/globals.css`: `@theme` สี/รัศมี/เงา/ขนาดตัวอักษร (line-height ไทยตาม design-system หัวข้อ 3.1)
3. `app/styleguide/page.tsx` (หน้าชั่วคราว ลบใน 6.1): สเกลตัวอักษรด้วยข้อความพยากรณ์จริง, ปุ่ม, การ์ด, ป้าย, วงโฟกัส

Checks
- `npm run build` → exit 0 · `npx tsc --noEmit`, `npx eslint .` → exit 0
- ภาพหน้าจอ 320, 375, 768, 1280 px ของ `/styleguide` บรรยายสิ่งที่เห็น: วรรณยุกต์ไม่ถูกตัด, ไม่มี scroll แนวนอน
- `getComputedStyle(document.body).fontFamily` มี Anuphan
- ไม่มีรหัสสี hex นอก `app/globals.css` (ค้นด้วย regex `#[0-9a-fA-F]{3,8}\b` ใน `app/`, `components/`)

Human steps: ผู้ใช้ดูภาพหน้าจอ อนุมัติ หรือสั่งปรับข้อ D2/D3 (แก้ใน `docs/spec/design-system.md`)

Out of scope: คอมโพเนนต์จริงของแอป (4.2)
