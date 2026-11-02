# แผน 02: ติดป้าย และขั้น 1 จัดประเภทหน่วย (Naive Bayes เทียบ k-NN เทียบกฎ keyword)

**เป้าหมาย:** ได้ชุดป้ายที่ผ่านคนตรวจ และโมเดลที่เขียนเองพร้อมผลวัดขั้นต่ำตามที่ตกลง (ส่วน Results ของรายวิชา)

**สเปก:** [../../docs/spec/labeling-guideline.md](../../docs/spec/labeling-guideline.md) หัวข้อ 2, 6 · [../../docs/decisions/0007-labeling-and-evaluation.md](../../docs/decisions/0007-labeling-and-evaluation.md) · [../../docs/spec/scope-and-pipeline.md](../../docs/spec/scope-and-pipeline.md) หัวข้อ 5-6 · skill `python-pipeline` (Hand-written models) · บันทึกวิชา `course/notes/ML/08-bayesian-learning.md`, `04-knn.md`, `course/notes/NLP/4-1-word-embeddings.md`

**ข้อจำกัดที่ใช้:** Naive Bayes และ k-NN เขียนเอง ห้าม sklearn/numpy/pandas ในโค้ดที่ ship · baseline เขียนก่อนมีป้ายและไม่ขึ้นกับการติดป้าย · แบ่งชุดตามวัน หน่วยถ้อยคำเดียวกันอยู่ชุดเดียว · หลังปิดชุดป้าย ห้ามแก้ป้ายชุดทดสอบ · รายงานต้องเขียนว่า "ติดโดยโมเดลภาษา ไม่ได้ผ่านคนตรวจ" (แก้ 2026-11-17 ตาม ADR 0012 ข้าม 2.3)

---

## Phase 2.1: แบ่งชุดข้อมูล และกฎ keyword baseline   [S]   [เจ้าของ: ผู้ช่วย]

Goal: ทุกหน่วยมีชุด (train / dev / test) ตามวัน และมี baseline ที่เขียนเสร็จก่อนมีป้าย

Inputs
- `data/labeled/units.csv` (1.4), `data/raw/MANIFEST.csv` (วันที่ของแต่ละฉบับ)

Tasks
1. `src/tmd_plain/classify/split.py`: ฝึก 14 วันเก่าสุด, เว้น 1 วัน, dev 2 วัน, เว้น 1 วัน, ทดสอบ 7 วันล่าสุด (10-16 พ.ย.); หน่วยที่ถ้อยคำเคยอยู่ในชุดที่เก่ากว่าให้อยู่ชุดนั้น → `data/labeled/split.csv`
2. `src/tmd_plain/classify/keyword.py`: กฎคำสำคัญ 4 ป้าย เขียนจากคู่มือหัวข้อ 2 เท่านั้น (ห้ามดูผลชุดทดสอบ)
3. `tests/classify/test_split.py`, `test_keyword.py`

Checks
- `python -m pytest tests/classify -q` ผ่าน
- ไม่มีข้อความหน่วยใดอยู่สองชุด (ทดสอบ) · ช่วงวันที่ของแต่ละชุดตรงสเปก · รายงานจำนวนหน่วยต่อชุด

Out of scope: ติดป้าย, โมเดล

---

## Phase 2.2: ผู้ช่วยติดป้ายทุกหน่วย   [M]   [เจ้าของ: ผู้ช่วย]

Goal: ทุกหน่วยมีป้ายที่เสนอ และทุกหน่วย `advice` มี `scope` พร้อมไฟล์สุ่ม 20% ที่ซ่อนป้ายไว้ให้ผู้ใช้

Inputs
- `data/labeled/units.csv`, คู่มือป้ายหัวข้อ 2-5, `docs/spec/region-scope-map.md` (สำหรับ scope) · Q4 ตกลงแล้ว: `data/labeled/` เก็บใน repo

Tasks
1. ผู้ช่วยอ่านทีละหน่วยแล้วติด `suggested_label` (ตามความหมายตามคู่มือ ไม่ใช้กฎ keyword ของ 2.1) และ `scope` ของ advice + `note` สำหรับกรณีก้ำกึ่ง → `data/labeled/units_labeled.csv`
2. `scripts/make_blind_sample.py`: สุ่ม 20% แบบแบ่งชั้นตามป้าย (seed คงที่) → `data/labeled/blind_sample.csv` ที่ไม่มีคอลัมน์ป้ายและ scope

Checks
- สคริปต์ตรวจ: ทุกแถวมีป้ายใน 4 แบบ; ทุก `advice` มี scope เป็นคีย์ภาคหรือ "ทั้ง 7 ภาค"; จำนวนแถวสุ่ม = ปัดขึ้น 20% ของทั้งหมด; ไฟล์สุ่มไม่มีคอลัมน์ป้าย
- ผู้ตรวจสุ่ม 10 แถวอ่านเทียบคู่มือ

Human steps: none

Out of scope: ป้ายสุดท้าย (2.3)

---

## Phase 2.3: ผู้ใช้ติดป้ายซ้ำแบบไม่เห็นป้าย และตัดสิน   [S]   [เจ้าของ: ผู้ใช้; ผู้ช่วยคำนวณ]

> **ข้าม (2026-11-17, ADR 0012):** ผู้ใช้ให้ใช้ป้ายของผู้ช่วยเป็นป้ายสุดท้าย ปิดชุดป้ายด้วย `scripts/freeze_labels.py` → `data/labeled/FROZEN.md` (`reviewer` = `agent-only`)

Goal: ได้อัตราตรงกันจริง และป้ายสุดท้ายที่ผ่านคนตรวจ แล้วปิดชุดป้าย

Human steps (ผู้ใช้)
1. เปิด `data/labeled/blind_sample.csv` ในโปรแกรมตาราง ติดป้าย (และ scope ถ้าเป็น advice) ราว 60 แถว **โดยไม่เปิดดู `units_labeled.csv`**
2. ดูทุกแถวที่ไม่ตรงกัน แล้วตัดสิน (ไล่ดูทั้งชุดได้ถ้าต้องการ)

Tasks (ผู้ช่วย)
1. `scripts/label_agreement.py` → อัตราตรงกันของป้ายและของ scope, ตารางสับสน, รายการแถวที่ไม่ตรง
2. ถ้าตรงกัน < 0.8: แก้คู่มือ (บันทึกการแก้ในคู่มือ) ติดป้ายของป้ายที่ขัดกันใหม่ แล้วให้ผู้ใช้ตรวจซ้ำ
3. รวมเป็น `final_label` + `reviewer`, บันทึกจำนวนแถวที่คนแก้, ทำ `data/labeled/FROZEN.md` (วันที่ปิด + sha256 ของไฟล์ป้าย)

Checks
- ตัวเลขอัตราตรงกันจากสคริปต์ (ผู้ตรวจรันซ้ำได้ค่าเดียวกัน) · ทุกแถวที่ไม่ตรงมีคำตัดสิน · sha256 ใน `FROZEN.md` ตรงกับไฟล์

Stop conditions: ตรงกัน < 0.8 สองรอบ → หยุด คุยกับผู้ใช้เรื่องคู่มือ

Out of scope: โมเดล

---

## Phase 2.4: Naive Bayes, k-NN และรายงานผลวัด   [M]   [เจ้าของ: ผู้ช่วย; ผู้ใช้อนุมัติโมเดล]

Goal: โมเดลทั้งสองเขียนเองและตรวจกับตัวอย่างที่คำนวณมือได้ มีรายงานเทียบกับ baseline และเลือกตัวที่ท่อประมวลผลจะใช้

Inputs
- ป้ายที่ปิดแล้ว (2.3), `split.csv`, baseline (2.1)

Tasks
1. `src/tmd_plain/classify/features.py`: bag of words บนผลตัด newmm (ถ้าใช้ TF-IDF ให้เลือกสูตรเดียวและบันทึก เพราะสไลด์ NLP 4-1 ขัดกันเอง)
2. `src/tmd_plain/classify/naive_bayes.py`: m-estimate, log probability; `tests/classify/test_naive_bayes.py` เทียบตัวอย่างที่คำนวณมือ
3. `src/tmd_plain/classify/knn.py`: ระยะตามบันทึกวิชา, `k` จาก config; ปรับ `k` และ `m` บนชุด dev เท่านั้น
4. `scripts/train_eval.py` → `models/naive_bayes.json`, `models/knn.json`, `docs/results/classifier-evaluation.md`: accuracy ของ NB / k-NN / keyword บนชุดทดสอบ (ก) ทุกหน่วย (ข) เฉพาะถ้อยคำใหม่ พร้อมจำนวนหน่วย, ตัวอย่างที่จัดผิด 3-5 หน่วยพร้อมเหตุผลที่คาด, ตัวที่เลือกและเหตุผล, ข้อจำกัด
5. หลังวัดผล ฝึกโมเดลสุดท้ายด้วยป้ายทั้งหมด (ตามสเปก) บันทึกแยกจากโมเดลที่ใช้วัด

Checks
- `python -m pytest tests/classify -q` ผ่าน (รวมตัวอย่างคำนวณมือ)
- ค้นใน `src/` ไม่พบ `sklearn`, `numpy`, `pandas`
- `python scripts/train_eval.py` สองครั้ง → JSON ของโมเดลและตัวเลขในรายงานเหมือนเดิม

Human steps: ผู้ใช้อนุมัติโมเดลที่เลือก

Out of scope: ใช้ผลจัดประเภทในการสรุป (3.2-3.3)
