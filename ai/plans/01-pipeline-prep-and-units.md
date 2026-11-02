# แผน 01: สัญญาข้อมูล และขั้น 0 ของท่อประมวลผล (เตรียมข้อความ → ตารางหน่วย)

**เป้าหมาย:** ตรึงสัญญาข้อมูลเป็นโค้ด แล้วเปลี่ยนไฟล์พยากรณ์ทุกฉบับ (ข้อความหรือ PDF) เป็นบล็อก 7 ภาค ช่วงวัน และตารางหน่วยที่พร้อมติดป้าย

**สเปก:** [../../docs/spec/data-contract.md](../../docs/spec/data-contract.md) · [../../docs/spec/scope-and-pipeline.md](../../docs/spec/scope-and-pipeline.md) หัวข้อ 3 · [../../docs/spec/labeling-guideline.md](../../docs/spec/labeling-guideline.md) หัวข้อ 3-4 · skill `python-pipeline`, `thai-text-handling` · ผล [0.2](00-foundation-and-spikes.md)

**ข้อจำกัดที่ใช้:** ทุกขั้นเป็นฟังก์ชันบริสุทธิ์ใน `src/tmd_plain/<stage>/` I/O อยู่ใน `scripts/` · `encoding="utf-8"`, `ensure_ascii=False` · ผลซ้ำได้ (เรียงข้อมูล ไม่มีเวลาในไฟล์ผล) · ข้อมูลผิดหนึ่งฉบับเตือนแล้วข้าม ไม่หยุดทั้งชุด · ห้าม sklearn/pandas/numpy ในโค้ดที่ ship · เปลี่ยนสัญญาต้องเขียน ADR

---

## Phase 1.1: สัญญาข้อมูล v1   [S]   [เจ้าของ: ผู้ช่วย; ผู้ใช้รีวิว]

Goal: รูปข้อมูล Issue และค่าคงที่ (7 ภาค, 4 ป้าย, 2 ชนิดเอกสาร, รหัสข้อผิดพลาด) เป็นโค้ดที่ทุกขั้นใช้ร่วม และมีไฟล์ตัวอย่างให้ฝั่งเว็บเริ่มงานได้ทันที

Inputs
- `docs/spec/data-contract.md` (ร่าง v0)

Tasks
1. `src/tmd_plain/contract.py`: Pydantic models `Issue`, `RegionSummary`, `Period`, `SummaryLine`, `AdviceItem`, `ErrorResponse` + `REGION_KEYS`, `LABELS`, `DOC_TYPES`, `ERROR_CODES`
2. `src/tmd_plain/config.toml` + ตัวอ่าน config (path, เกณฑ์ต่างๆ, k, m จะเติมทีหลัง)
3. `scripts/export_schema.py` → `lib/contract/issue.schema.json` (JSON Schema 2020-12) ฝั่งเว็บสร้างชนิด TypeScript/Zod จากไฟล์นี้ใน 4.1
4. `tests/fixtures/contract/issue-daily-example.json` และ `issue-sevenday-example.json`: เขียนด้วยมือจากฉบับจริง 1 ฉบับต่อชนิด (ตัวเลขทุกตัวมาจากต้นฉบับ) ใช้เป็น fixture ของเว็บ
5. แก้ `docs/spec/data-contract.md` เป็น v1 (ถ้าต่างจาก v0 ให้เขียน ADR)

Checks
- `python -m pytest tests/contract -q`: model รับไฟล์ตัวอย่างทั้งสองได้, ขาดภาคใดภาคหนึ่งต้องไม่ผ่าน, ป้ายนอก 4 แบบต้องไม่ผ่าน
- `python scripts/export_schema.py` สองครั้ง → ไฟล์เหมือนกันทุกไบต์
- `ruff check .` ผ่าน

Human steps: ผู้ใช้รีวิวสัญญา v1 (ไฟล์ตัวอย่างอ่านง่ายที่สุด) แล้วเซ็นปิด หลังจากนี้เปลี่ยนสัญญาได้ผ่าน ADR เท่านั้น

Out of scope: การดึงข้อความ, ฝั่งเว็บ

---

## Phase 1.2: ดึงและทำความสะอาดข้อความ   [M]   [เจ้าของ: ผู้ช่วย]

Goal: ไฟล์พยากรณ์ใดๆ (`.txt` จาก HTML หรือ PDF) กลายเป็นข้อความสะอาดที่ตัวเลขและวรรณยุกต์ครบ

Inputs
- `src/tmd_plain/prep/pdf_text.py` และผลจาก 0.2, `known-defects.md`, `data/raw/`

Tasks
1. `src/tmd_plain/prep/extract.py`: อ่าน `.txt` (ตัดหัวไฟล์ `# source / round_id / ...` ที่เราใส่ตอนเก็บ) และ PDF (ตัวอ่านที่เลือกใน 0.2 พร้อมตัวสำรอง)
2. `src/tmd_plain/prep/clean.py`: ลำดับ PUA → NFC → normalize/reorder → ต่อบรรทัดที่ขาด (skill `thai-text-handling`)
3. `tests/prep/test_clean.py` จาก fixture ของ 0.2 + กรณีข้อบกพร่องที่รู้แล้วทุกข้อ

Checks
- `python -m pytest tests/prep -q` ผ่าน
- สคริปต์เทียบ 46 คู่รายวัน: ตัวเลขในข้อความ PDF ที่ทำความสะอาดแล้วตรงกับข้อความ HTML กี่ % (ต้องไม่ต่ำกว่าผลของ 0.2)
- ไม่มีอักษร PUA เหลือในผลของทั้ง 112 ไฟล์

Out of scope: แยกภาค (1.3)

---

## Phase 1.3: ตรวจชนิดเอกสาร แยกบล็อกภาคและช่วงวัน   [M]   [เจ้าของ: ผู้ช่วย]

Goal: ทุกฉบับถูกระบุชนิด และแยกได้เป็นส่วนภาพรวม ส่วนข้อควรระวัง บล็อก 7 ภาค และ (7 วัน) ช่วงวัน หรือได้ข้อผิดพลาดแบบมีชนิด

Inputs
- ผลของ 1.2, `docs/spec/region-scope-map.md` (ชื่อภาคหลายรูปแบบ), `data/raw/`

Tasks
1. `src/tmd_plain/prep/doctype.py`: `daily` / `sevenday` / ไม่รองรับ (รวมพยากรณ์เดินเรือ) จากหัวเอกสาร
2. `src/tmd_plain/prep/regions.py`: หัวข้อภาคทุกรูปแบบ → 7 คีย์; ภาคใต้ฝั่งตะวันออกที่มีบล็อกย่อยตามจังหวัด; แยกย่อหน้าภาพรวมและข้อควรระวัง
3. `src/tmd_plain/prep/periods.py`: "ในช่วงวันที่ 17 - 19 พ.ย. 69" → วันที่ ISO (พ.ศ. - 543)
4. `tests/golden/regions/` ผลที่ตรวจด้วยตา 3 ฉบับ (รายวัน 2 รวมฉบับจาก PDF 1, 7 วัน 1)

Checks
- `python -m pytest tests/prep -q` ผ่าน (รวม golden)
- สคริปต์รันทั้ง 65 ฉบับ: ชนิดถูก 65/65; ได้ครบ 7 ภาค หรือข้อผิดพลาดแบบมีชนิด (รายงานจำนวน แยก txt / PDF; txt ต้องผิดพลาด 0); 7 วันได้ช่วงวันครบ 19/19
- ข้อความที่ไม่ใช่พยากรณ์ / ไฟล์ว่าง → ข้อผิดพลาดแบบมีชนิด ไม่ crash

Out of scope: ตัดหน่วย (1.4), ดึงค่า (3.1)

---

## Phase 1.4: ตัดหน่วย ตัดคำ และสร้างตารางหน่วย   [M]   [เจ้าของ: ผู้ช่วย; ผู้ใช้ดูตัวอย่าง]

Goal: ย่อหน้าภาพรวมและข้อควรระวังของทุกฉบับถูกตัดเป็นหน่วยตามคู่มือ และได้ตารางหน่วยไม่ซ้ำที่พร้อมติดป้าย

Inputs
- ผลของ 1.3, `docs/spec/labeling-guideline.md` หัวข้อ 3-4 และ 7

Tasks
1. `src/tmd_plain/prep/units.py`: กติกาตัด/ไม่ตัดตามหัวข้อ 3 ของคู่มือ (รวม "เนื่องจาก" ตามด้วยคำกลไก และ "ส่งผล(ทำ)ให้")
2. `src/tmd_plain/prep/tokenize.py` + `src/tmd_plain/resources/weather_words.txt` (พจนานุกรมคำอากาศ)
3. `scripts/build_units.py` → `data/labeled/units.csv` คอลัมน์ตามคู่มือหัวข้อ 7 (`unit_id`, `doc_type`, `appears_in`, `text`, `context_prev`, `context_next`, ป้ายว่างไว้) บรรทัดในบล็อกภาคไม่อยู่ในตาราง (เป็น `weather` ตามตำแหน่ง) แต่นับจำนวนไว้
4. `tests/prep/test_units.py`: ทุกตัวอย่างในหัวข้อ 3-4 ของคู่มือเป็นกรณีทดสอบ

Checks
- `python -m pytest tests/prep -q` ผ่าน · `ruff check .` ผ่าน
- `python scripts/build_units.py` สองครั้ง → `units.csv` เหมือนกันทุกไบต์
- รายงานจำนวนจริง: หน่วยไม่ซ้ำ (การนับหยาบเดิม ~310), หน่วยที่มีคำแนะนำ (หยาบ ~71), บรรทัดบล็อกภาค; ถ้าต่างจากเดิมมากกว่า 30% ให้อธิบาย
- `ร้อยละ`, `ฟ้าคะนอง`, `น้ำป่าไหลหลาก` เป็นคำเดียวในผลตัดคำ

Human steps: ผู้ใช้ดูหน่วยสุ่ม 20 หน่วย ว่าตัดตรงตามคู่มือไหม แล้วเซ็นปิด (ถ้าต้องแก้กติกา ให้แก้คู่มือก่อน)

Out of scope: ป้าย (2.x)
