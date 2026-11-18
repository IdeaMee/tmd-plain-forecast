# แผนและขอบเขตโครงงาน: สรุปพยากรณ์อากาศ TMD เป็นภาษาไทยง่ายๆ

> ไฟล์นี้คือ **ภาพรวมโครงงานฉบับสั้นที่อ่านได้ในไม่กี่นาที**: โจทย์ ไอเดีย ขอบเขต สถาปัตยกรรม ข้อมูล และความเสี่ยง · คู่มือติดตั้งและใช้งาน: [README.md](README.md) · แผนที่เอกสาร: [docs/README.md](docs/README.md) · ขั้นตอนทำงานร่วมกับผู้ช่วย AI แผนแต่ละ phase และความคืบหน้า: [ai/](ai/README.md)
> สถานะ: ระบบอยู่บนเว็บจริง https://tmd-plain-forecast.vercel.app (5 หมวดเอกสาร: รายวัน 7 วัน เดินเรือ เตือนภัย รายสัปดาห์ พร้อมย้อนหลังทั้งหมดที่เก็บไว้, `/demo`, `/model`) · ที่เหลือที่ทำเมื่อสั่ง: เกษตร/คาดหมาย 3 เดือน · ความคืบหน้าละเอียด: [ai/PROGRESS.md](ai/PROGRESS.md) · อัปเดตล่าสุด 2026-11-19

## 1. ลำดับงานและความคืบหน้า
งานแบ่งเป็น 3 ขั้น (เตรียมแผนและข้อมูล → แบ่ง phase → สร้างทีละ phase) แล้วรอบปรับปรุง v2 ตารางลำดับงานและสถานะแต่ละขั้นอยู่ที่ [ai/README.md](ai/README.md) ความคืบหน้าจริงของทุก phase อยู่ที่ [ai/PROGRESS.md](ai/PROGRESS.md)

## 2. โจทย์รายวิชา (NLP 1323326/1323404 ผู้สอน Satida Sookpong ควบ ML 1322308)
งานกลุ่ม 6-7 คน 40% ของวิชา NLP · ต้องส่ง: GitHub repo (README) · Product link · สไลด์ · วิดีโอ · MS Form Teamwork

| หัวข้อ | คะแนน | สิ่งที่ต้องมี |
|---|---|---|
| Idea + pain point + reference | 10 | what/why/how, ผู้ใช้, ทำไมต้อง NLP, Data+Model, ข้อจำกัด, อ้างอิง |
| Product | 10 | deploy ใช้ได้ 5 (ไม่มี deploy ได้ 2%) · Results 5 (train-test, metrics, baseline, error analysis) |
| Code | 5 | ทุกคนอยู่ใน GitHub team, commit มีข้อความ, README 4 ส่วน |
| Presentation / Q&A / Teamwork | 5 / 5 / 5 | สไลด์+เดโมสด+วิดีโอ / ถาม-ตอบ / จำนวน commit + MS Form |

รายละเอียด: [course/notes/NLP/00-course-info.md](course/notes/NLP/00-course-info.md) · โจทย์ต้นฉบับ: `course/slides/0_MiniProject.pdf` · **ยังไม่ทราบวันส่ง/นำเสนอจริง** (ตารางสไลด์ว่า 14 พ.ย. 2026 ซึ่งผ่านแล้ว ผู้ใช้บอกว่ายังไม่ต้องห่วง) · ผูกเกณฑ์ฝั่งวิชา ML ยังไม่ได้เช็ก (ไม่มีไฟล์โจทย์ ML)

## 3. ไอเดียและขอบเขต
ข้อความพยากรณ์ของ TMD ครอบคลุมทั้งประเทศในแม่แบบเดียว ผู้อ่านต้องหาภาคตัวเอง และสาเหตุเชิงเทคนิคปนกับคำเตือน → **เว็บสรุปเป็นภาษาไทยง่ายๆ แยก 7 ภาค** ผู้ใช้คือประชาชนทั่วไป (ยังไม่ได้สำรวจผู้อ่านจริง)
- **ทำ (ขอบเขต v2, ADR 0017):** พยากรณ์รายวัน (4 รอบ/วัน), 7 วัน, เดินเรือ, ประกาศเตือนภัย (`/warnings`) และสรุปรายสัปดาห์ (`/summaries`) ย้อนหลังทั้งหมดที่เก็บไว้ พร้อมตัวเลือกรอบรายเดือน · `/model` แสดงโมเดลและผลวัด · `/demo` รับ PDF ชนิดอื่นของ TMD ด้วยโหมดทั่วไป · (ขอบเขตแรก: หน้า `/` ไม่มีช่องกรอก แสดงครบ 7 ภาค ย้อนหลัง 1 สัปดาห์ + แท็บเลือกภาค · หน้า `/demo` อัปโหลด PDF ของ TMD แล้วคำนวณสด (ไม่เก็บไฟล์)
- **ไม่ทำ:** ช่องใส่ข้อความเองในหน้าหลัก, ดึงข้อมูลอัตโนมัติ, ตารางตรวจวัด, เกษตร/คาดหมาย 3 เดือน (รอแผน 12), เอกสารของหน่วยงานอื่น, ผู้ตรวจก่อนขึ้นเว็บ
- รายละเอียดและกฎของผลลัพธ์ (ห้ามเขียนเอง ห้ามแปลง "ร้อยละ N ของพื้นที่" เป็นโอกาสฝน): [docs/spec/scope-and-pipeline.md](docs/spec/scope-and-pipeline.md)

## 4. สถาปัตยกรรม (ภาพเดียว)
```
เครื่องทีม:  ไฟล์ TMD (data/raw) → ท่อ Python (ตรวจชนิด → เตรียมข้อความ → จัดประเภท NB/k-NN → ดึงค่า → แม่แบบ) → JSON → npm run load:neon (Node, ADR 0014) → Neon Postgres
Vercel:      Next.js (App Router) อ่าน Neon เอง (แคช + revalidateTag)   /demo → ฟังก์ชัน Python (api/) ใช้ท่อเดียวกัน
```
Next.js 16 + TypeScript 6.0.x + Tailwind 4, เขียนคอมโพเนนต์เอง · Python: Naive Bayes กับ k-NN เขียนเอง, pypdfium2 อ่าน PDF (ห้าม PyMuPDF) · ของฟรีเท่านั้น (Vercel Hobby, Neon Free, GitHub) · โครงโฟลเดอร์และ spike: [docs/architecture.md](docs/architecture.md)

## 5. ท่อประมวลผล 4 ขั้น
| ขั้น | ทำอะไร | วิธี |
|---|---|---|
| doctype | รับเฉพาะรายวัน/7 วัน | กฎจากหัวเอกสาร |
| 0 | แก้ข้อความ แยกบล็อกภาค ตัดหน่วย ตัดคำ | กฎ + newmm |
| 1 | จัดประเภทหน่วย weather/advice/cause/other | Naive Bayes เทียบ k-NN เทียบกฎ keyword |
| 2 | ดึงค่าตามภาค + เลือกคำแนะนำให้ภาค | regex + ตารางแมปภาค |
| 3 | เขียนประโยคภาษาง่าย | แม่แบบ + พจนานุกรม |

ป้าย/ตารางแมป: [docs/spec/labeling-guideline.md](docs/spec/labeling-guideline.md), [docs/spec/region-scope-map.md](docs/spec/region-scope-map.md) (v1 ตกลงแล้ว) · รูปแบบข้อมูล: [docs/spec/data-contract.md](docs/spec/data-contract.md) (v1 เป็นโค้ดแล้วใน `src/tmd_plain/contract.py` ผู้ใช้รีวิวผ่าน 2026-11-16)

## 6. ข้อมูล
เก็บมือด้วย Claude in Chrome เมื่อ 2026-11-16 ตามที่ผู้ใช้อนุญาต: รายวัน 46 รอบ (ข้อความ+PDF), 7 วัน 19 ฉบับ → 112 ไฟล์ แล้วเก็บเพิ่มรอบ v2 (ADR 0015) รวม **1,481 ไฟล์ที่ `data/raw/`** (ไม่ขึ้น repo, [รายการ](docs/results/raw-inventory.md)) · แบ่งตามวัน: ฝึก 14 วัน เว้น 1 dev 2 เว้น 1 ทดสอบ 7 วันล่าสุด · แหล่งและเครดิต: [docs/data-sources.md](docs/data-sources.md) · ข้อมูลที่เคยดึงด้วยสคริปต์ (ตัดออกจากแผน) อยู่ที่ `data/excluded-scripted/`

## 7. การออกแบบหน้าเว็บ
**มาตรฐานหลักคือ [DESIGN-expo.md](docs/design/DESIGN-expo.md)** (ผู้ใช้เป็นคนใส่ **อ่านอย่างเดียว ห้ามแก้**) ใช้ฟอนต์ไทย **Anuphan** แทน Inter · ส่วนที่ต้องปรับให้เข้ากับภาษาไทยและงานนี้ บันทึกแยกใน [docs/spec/design-system.md](docs/spec/design-system.md) · หน้าและคอมโพเนนต์: [docs/spec/ui-spec.md](docs/spec/ui-spec.md)

## 8. การตัดสินใจหลัก (ADR ใน `docs/decisions/`)
0001 ไม่ใช้สคริปต์ดึงเว็บ TMD · 0002 ขอบเขต · 0003 สถาปัตยกรรม · 0004 tech stack · 0005 ตัวอ่าน PDF · 0006 Python บน Vercel (มีเงื่อนไข) · 0007 ป้ายและการวัดผล · 0008 ชุด md/skill · 0009 โครงรากและที่เก็บ skill · 0010 มาตรฐานดีไซน์และฟอนต์ · 0011 Vercel จาก repo ส่วนตัว + push 3 repo · 0012 ป้ายของผู้ช่วยเป็นป้ายสุดท้าย (ข้าม 2.3) · 0013 ตัวเลขคำนวณและเกณฑ์ TMD ในกฎ F1 · 0014 สคริปต์โหลดเข้า Neon เป็น Node · 0015 เก็บข้อมูลด้วยเบราว์เซอร์ของผู้ใช้ · 0016 ดีไซน์ A · 0017 ขอบเขตเอกสาร 5 ชนิด · 0018 ลำดับประกาศเตือนภัยไม่เก็บใน contract · ดู [docs/decisions/README.md](docs/decisions/README.md)

## 9. ความเสี่ยงและเรื่องที่ยังเปิด
- **ทดสอบแล้วผ่าน (Phase 0, 2026-11-16):** Python + PyThaiNLP + pypdfium2 บน Vercel และ region `sin1` ([ผล](docs/results/spike-vercel-python.md)), ข้อความไทยจาก PDF ด้วย pypdfium2 ([ผล](docs/results/spike-pdf-extraction.md)), path ที่มี `&` (แก้ด้วย npm scripts ที่เรียก `node` ตรง), ฟอนต์ Anuphan, แผน Free ของ Neon (1 GB, 100 ชม. compute)
- **ข้อจำกัดของเครื่องทีม:** `psycopg` ถูก Windows Application Control บล็อก จึงโหลดข้อมูลด้วย Node (ADR 0014)
- **ผู้ใช้ต้องกรอก/ตัดสินใจ:** วันส่งจริง, ขนาดทีมและบทบาท, จะเก็บ `course/slides/` กับ `docs/research/tmd-digest/` ใน repo หรือไม่ (ตอนนี้ `.gitignore` กันไว้) · ตัดสินแล้ว: บัญชี Vercel/Neon/GitHub (ADR 0011), ชื่อแพ็กเกจ `tmd_plain` (Q1), ทางถอยของ `/demo` (Q2, spike 0.3 ผ่านจึงไม่ต้องใช้)
- รายการเต็มของสเปก: [docs/spec/scope-and-pipeline.md](docs/spec/scope-and-pipeline.md) หัวข้อ 7-8

## 10. ข้อกำหนดตายตัวของโครงงาน
ของฟรีเท่านั้น (Vercel Hobby, Neon Free, GitHub) · ห้ามดึง tmd.go.th ด้วยสคริปต์ (นโยบายเว็บ TMD ข้อ 3.3) · คอมเมนต์โค้ดเป็นภาษาไทย สั้น · ห้ามแก้ [DESIGN-expo.md](docs/design/DESIGN-expo.md) · กฎสำหรับผู้ช่วย AI (ห้ามใช้ git โดยไม่ได้สั่ง ห้ามสร้างบัญชีหรือ deploy เอง) อยู่ที่ [ai/README.md](ai/README.md)

## 11. แผนที่เอกสาร
อยู่ที่ [docs/README.md](docs/README.md) (ตารางย้ายไฟล์จากโครงเก่าอยู่ใน [ai/archive/README.md](ai/archive/README.md))
