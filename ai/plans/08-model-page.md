# แผน 08: หน้า `/model` ภาพผลการเทรนแบบเข้าใจง่าย (รอบปรับปรุง v2)

**เป้าหมาย:** คนทั่วไปและอาจารย์เปิดหน้าเดียวแล้วเข้าใจว่าโมเดลจัดประเภทประโยคเรียนจากอะไร ตัดสินใจอย่างไร เก่งแค่ไหน และพลาดตรงไหน ด้วยวิธีพื้นฐานที่เรียนในวิชาเท่านั้น

**สเปก:** [../../docs/spec/scope-and-pipeline.md](../../docs/spec/scope-and-pipeline.md) · [../../docs/results/classifier-evaluation.md](../../docs/results/classifier-evaluation.md) · [../../docs/spec/labeling-guideline.md](../../docs/spec/labeling-guideline.md) · ADR 0012 (ป้ายจากผู้ช่วย ไม่ได้ตรวจโดยคน) · skill `dataviz`

**ที่ผู้ใช้ตกลง (2026-11-18):** 8 ส่วน + กราฟเส้นการเรียนรู้ (learning curve 25/50/75/100% ของ train) · กราฟเขียนด้วย HTML/SVG ไม่เพิ่ม dependency · ตัวอย่างคำนวณไว้ล่วงหน้า (ไม่รันโมเดลบนหน้าเว็บ) · อยู่ใต้เมนู "ความรู้ / โมเดล" · ช่อง "พิมพ์ประโยคเอง" เลื่อนไปรอบหลัง

**ข้อจำกัดที่ใช้:** ทุกตัวเลขบนหน้ามาจากไฟล์ที่สคริปต์สร้าง ห้ามพิมพ์ตัวเลขเอง · บอกตรง ๆ ว่าป้ายมาจากผู้ช่วย (ADR 0012) และ keyword baseline ได้คะแนนสูงกว่า NB · ไม่มีอนิเมชันกับค่าตัวเลข (แผน 07) · ห้ามแตะ `models/*.json` ที่ไปป์ไลน์ใช้ และห้ามจูน m, k ใหม่บน test

**เงื่อนไขเริ่ม:** 8.1 เริ่มได้ทันที (ไม่ขึ้นกับดีไซน์) · 8.2 หลัง 7.2 (ใช้คอมโพเนนต์ v2) และ 7.3 (ใส่ลิงก์เมนู)

---

## Phase 8.1: สคริปต์ส่งออกรายงานโมเดล   [M]   [เจ้าของ: ผู้ช่วย]

Goal: ไฟล์ JSON เดียวที่มีทุกตัวเลขและตัวอย่างที่หน้า `/model` ต้องใช้ สร้างซ้ำได้ผลเดิมทุกไบต์

Inputs
- `data/labeled/units_labeled.csv`, `data/labeled/split.csv`, `src/tmd_plain/classify/` (NB, k-NN, keyword, tokenize/vectorize), `src/tmd_plain/config.toml` `[classify]`, `models/eval/*.json`

Tasks
1. `scripts/export_model_report.py` → `lib/generated/model-report.json` (+ `lib/generated/model-report.schema.json` ถ้าต้องใช้ Zod ฝั่งเว็บสร้างจาก pydantic แบบ `export_schema.py`) เนื้อหา:
   - ภาพรวมไปป์ไลน์ (ชื่อขั้น ว่าเป็นกฎหรือ ML)
   - จำนวนหน่วยต่อ label ต่อ split (train/dev/test) และต่อชนิดเอกสาร
   - ตัวอย่าง 3 ประโยคจาก train: ประโยค → โทเคน (newmm) → ที่ถูกทิ้ง (เครื่องหมาย, คำนอกคลัง) → `<num>` → นับคำ
   - คำเด่นต่อ label ของ NB (เรียงตาม log P(w|c) − ค่าเฉลี่ยของ class อื่น, 15 คำ)
   - ตัวอย่างการตัดสินของ NB 3-4 ประโยคจาก test (ถูก + ผิด): log prior, ผลรวมต่อ class, คำที่ดันคะแนนมากสุด 5 คำ, ความมั่นใจ (softmax ของ log score)
   - k-NN: ประโยคเดียวกัน → เพื่อนบ้านใกล้สุด 3 ตัวจาก train พร้อมระยะ L2 และ label
   - ตาราง dev ของ m และ k ที่ลองแล้ว (อ่านจาก `models/eval` หรือคำนวณซ้ำด้วยค่าเดียวกับ `train_eval.py`), ผลบน test ของ NB / k-NN / keyword, confusion matrix ของแต่ละตัว
   - learning curve: เทรน NB และ k-NN บน train 25/50/75/100% (เลือกแบบแบ่งตามวัน ด้วย seed ใน config) วัด accuracy + macro-F1 บน dev
   - รายการที่ทายผิดบน test ทั้งหมด (ประโยค, label จริง, ที่ทาย, ความมั่นใจ)
   - โครงรองรับหลายโมเดล (`models: [{id: "sentence-role", ...}]`) เพื่อให้แผน 11.3 เพิ่มตัวจัดประเภทประกาศเตือนภัยได้
2. ใช้ฟังก์ชันเดิมใน `src/tmd_plain/classify/` เท่านั้น (ห้ามเขียน NB ซ้ำ) ถ้าต้องเปิดค่าภายใน (log score ต่อ class, คำที่ดันคะแนน) ให้เพิ่มฟังก์ชันอ่านอย่างเดียว ไม่เปลี่ยนผลของ `predict`
3. `tests/classify/test_model_report.py`: รายงานตรงกับ `models/eval` (accuracy เท่ากัน), ไฟล์ใน repo ไม่เก่า (รันสคริปต์ในหน่วยความจำแล้วเทียบ), ผลรวมจำนวนหน่วย = 292
4. บรรทัดใหม่ใน `.claude/CLAUDE.md` Commands หลังรันจริง

Checks
- `.venv/Scripts/python.exe -X utf8 scripts/export_model_report.py` สองครั้ง → sha256 ของไฟล์เท่าเดิม
- `.venv/Scripts/python.exe -m pytest -q` ผ่านทั้งหมด (212 + ใหม่) · ruff check / format --check ผ่าน
- `scripts/train_eval.py` รันแล้ว `models/*.json` ไม่เปลี่ยน (sha256 เท่าเดิม)

Human steps
- none

Stop conditions
- ตัวเลขที่คำนวณซ้ำไม่ตรงกับ `docs/results/classifier-evaluation.md` → หยุดรายงาน ห้ามแก้ให้ตรงเอง

Out of scope
- หน้าเว็บ (8.2), ตัวจัดประเภทใหม่ (11.3)

---

## Phase 8.2: หน้า `/model` + กราฟ HTML/SVG   [M]   [เจ้าของ: ผู้ช่วย; ผู้ใช้รีวิว]

Goal: หน้า `/model` แสดง 8 ส่วน + learning curve อ่านง่ายบนมือถือ ทุกตัวเลขมาจาก `model-report.json`

Inputs
- 8.1, คอมโพเนนต์ v2 (7.2), เมนู (7.3)

Tasks
1. `lib/data/model-report.ts` (อ่าน JSON + Zod parse, `server-only`) + Vitest
2. `app/model/page.tsx` (Server Component) + `app/model/_components/`: ส่วนที่ 1-8 ตามที่ตกลง
   1. ภาพรวมไปป์ไลน์ (ขั้นไหนเป็นกฎ ขั้นไหนเป็น ML)
   2. ข้อมูลเทรน: แท่งจำนวนต่อ label ต่อ split
   3. ประโยค → โทเคน → นับคำ (ชิปคำ, ชิปที่ถูกทิ้งขีดฆ่า)
   4. คำเด่นต่อ label (แท่งแนวนอน)
   5. NB ตัดสินอย่างไร: แท่งคะแนนต่อ class + คำที่ดันคะแนน (ลูกศร/แถบ)
   6. k-NN เพื่อนบ้านใกล้สุด
   7. จูนบน dev (m, k) + เทียบ NB / k-NN / keyword + confusion matrix (ตาราง heatmap ที่มีตัวเลขในช่อง)
   8. จุดที่พลาดและข้อจำกัด (ป้ายจากผู้ช่วย, ข้อมูลน้อย, keyword ชนะ, label `other` มี 1 แถว)
   + learning curve (เส้น SVG ไม่ต้องมีไลบรารี)
3. กราฟทุกตัว: มีข้อความทางเลือก/ตารางข้อมูลสำหรับ screen reader, สีตามโทเคน (ไม่ใช้สีอย่างเดียวสื่อความหมาย), ไม่มีอนิเมชันกับค่า (เข้าแบบเฟดได้)
4. ลิงก์ในเมนู "ความรู้ / โมเดล" (`lib/nav.ts`) · `tests/e2e/model.spec.ts` (หน้าโหลด, 8 หัวข้อมีครบ, ตัวเลข accuracy บนหน้าเท่ากับใน JSON, ไม่มี scroll แนวนอนที่ 320-1280) · เพิ่ม 1 เทสต์ใน `tests/smoke/live.spec.ts`
5. `docs/spec/ui-spec.md`: หัวข้อหน้า `/model`

Checks
- `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`, `npm run e2e` ผ่าน · grep กฎดีไซน์ของ 7.2 ผ่าน
- ภาพหน้าจอ 375 และ 1280 ของทุกส่วน ไล่ `ui-checklist.md`
- ตรวจด้วยตา: ตัวเลข 5 ตัวสุ่มบนหน้าตรงกับ `docs/results/classifier-evaluation.md`

Human steps
- ผู้ใช้อ่านหน้าแล้วบอกว่าเข้าใจหรือไม่ (ถ้าส่วนไหนงง ปรับคำอธิบาย) แล้วเซ็นปิด

Out of scope
- ช่องพิมพ์ประโยคเอง (รอบหลัง), โมเดลประกาศเตือนภัย (เพิ่มใน 11.3)
