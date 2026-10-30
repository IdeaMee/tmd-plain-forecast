# แผนหลัก: สรุปพยากรณ์อากาศ TMD เป็นภาษาไทยง่ายๆ

> ไฟล์นี้คือ **แผนหลักฉบับสั้นที่อ่านได้ในไม่กี่นาที** อยู่ที่ราก (Root) ตามที่ผู้ใช้สั่ง · ความคืบหน้าจริง: [PROGRESS.md](PROGRESS.md) · แผนรายละเอียดแต่ละ phase: [plans/](plans/) · ประวัติการคุยและ decision log ฉบับเต็ม (84 KB): [docs/archive/PLAN-history.md](docs/archive/PLAN-history.md)
> สถานะ: **ขั้น 1 (เตรียมแผน/ข้อมูล/เอกสาร) ครบ · ขั้น 2 (แบ่ง phase) รอผู้ใช้สั่ง · ขั้น 3 (เจนโค้ด) ยังไม่เริ่ม** · อัปเดตล่าสุด 2026-11-16

## 1. ลำดับงาน 3 ขั้น (ผู้ใช้กำหนด)
| ขั้น | ทำอะไร | สถานะ |
|---|---|---|
| 1 | เตรียมแผน ข้อมูล คู่มือป้าย เอกสาร (md) และ skill | **ครบ** |
| 2 | วิเคราะห์และแบ่ง phase ด้วย skill `planning-phases` ผลอยู่ที่ `plans/` | **รอผู้ใช้สั่ง ห้ามเริ่มเอง** |
| 3 | เจนโค้ดทีละ phase (ผู้ใช้เปลี่ยนไปใช้ Fable/Opus) รวมการติดป้ายข้อมูล (ต้องมีโค้ดตัดหน่วยก่อน) | ยังไม่เริ่ม |

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
- **ทำ:** พยากรณ์รายวัน (4 รอบ/วัน) และพยากรณ์ 7 วัน · หน้า `/` ไม่มีช่องกรอก แสดงครบ 7 ภาค ย้อนหลัง 1 สัปดาห์ + แท็บเลือกภาค · หน้า `/demo` อัปโหลด PDF ของ TMD แล้วคำนวณสด (ไม่เก็บไฟล์)
- **ไม่ทำ:** ช่องใส่ข้อความเองในหน้าหลัก, ดึงข้อมูลอัตโนมัติ, ตารางตรวจวัด/พยากรณ์เดินเรือ/รายงานอื่น, เอกสารของหน่วยงานอื่น, ผู้ตรวจก่อนขึ้นเว็บ
- รายละเอียดและกฎของผลลัพธ์ (ห้ามเขียนเอง ห้ามแปลง "ร้อยละ N ของพื้นที่" เป็นโอกาสฝน): [docs/spec/scope-and-pipeline.md](docs/spec/scope-and-pipeline.md)

## 4. สถาปัตยกรรม (ภาพเดียว)
```
เครื่องทีม:  ไฟล์ TMD (data/raw) → ท่อ Python (ตรวจชนิด → เตรียมข้อความ → จัดประเภท NB/k-NN → ดึงค่า → แม่แบบ) → JSON → Neon Postgres
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

ป้าย/ตารางแมป: [docs/spec/labeling-guideline.md](docs/spec/labeling-guideline.md), [docs/spec/region-scope-map.md](docs/spec/region-scope-map.md) (v1 ตกลงแล้ว) · รูปแบบข้อมูล: [docs/spec/data-contract.md](docs/spec/data-contract.md) (ร่าง v0)

## 6. ข้อมูล
เก็บมือด้วย Claude in Chrome เมื่อ 2026-11-16 ตามที่ผู้ใช้อนุญาต: รายวัน 46 รอบ (ข้อความ+PDF), 7 วัน 19 ฉบับ → **112 ไฟล์ที่ `data/raw/`** (ไม่ขึ้น repo) · แบ่งตามวัน: ฝึก 14 วัน เว้น 1 dev 2 เว้น 1 ทดสอบ 7 วันล่าสุด · แหล่งและเครดิต: [docs/data-sources.md](docs/data-sources.md) · ข้อมูลที่เคยดึงด้วยสคริปต์ (ตัดออกจากแผน) อยู่ที่ `data/excluded-scripted/`

## 7. การออกแบบหน้าเว็บ
**มาตรฐานหลักคือ [DESIGN-expo.md](DESIGN-expo.md)** (ผู้ใช้เป็นคนใส่ **อ่านอย่างเดียว ห้ามแก้**) ใช้ฟอนต์ไทย **Anuphan** แทน Inter · ส่วนที่ต้องปรับให้เข้ากับภาษาไทยและงานนี้ บันทึกแยกใน [docs/spec/design-system.md](docs/spec/design-system.md) · หน้าและคอมโพเนนต์: [docs/spec/ui-spec.md](docs/spec/ui-spec.md)

## 8. การตัดสินใจหลัก (ADR ใน `docs/decisions/`)
0001 ไม่ใช้สคริปต์ดึงเว็บ TMD · 0002 ขอบเขต · 0003 สถาปัตยกรรม · 0004 tech stack · 0005 ตัวอ่าน PDF · 0006 Python บน Vercel (มีเงื่อนไข) · 0007 ป้ายและการวัดผล · 0008 ชุด md/skill · 0009 โครงรากและที่เก็บ skill · 0010 มาตรฐานดีไซน์และฟอนต์ · ดู [docs/decisions/README.md](docs/decisions/README.md)

## 9. ความเสี่ยงและเรื่องที่ยังเปิด
- **ยังไม่ได้ทดสอบ:** Python + PyThaiNLP + pypdfium2 บน Vercel (spike ใน Phase 0; ทางถอยยังไม่ยืนยัน), คุณภาพข้อความไทยจาก PDF, Claude Code โหลด skill/rules ที่ราก, path ที่มีภาษาไทย/ช่องว่าง/`&` กับ Next.js build และ Vercel CLI, แผนฟรีปัจจุบันของ Neon, ภูมิภาค `sin1` บน Hobby, ฟอนต์ Anuphan ดูดีกับค่า line-height ที่เลือก
- **ผู้ใช้ต้องกรอก/ตัดสินใจ:** วันส่งจริง, ขนาดทีมและบทบาท, บัญชี Vercel/Neon/GitHub, ชื่อแอปและแพ็กเกจ, ทางถอยของ `/demo`, จะเก็บ `course/slides/` กับ `docs/research/tmd-digest/` ใน repo หรือไม่ (ตอนนี้ `.gitignore` กันไว้)
- รายการเต็มของสเปก: [docs/spec/scope-and-pipeline.md](docs/spec/scope-and-pipeline.md) หัวข้อ 7-8

## 10. ข้อกำหนดตายตัวจากผู้ใช้
ของฟรีเท่านั้น · **ห้ามใช้ git ถ้าผู้ใช้ไม่สั่งในข้อความนั้น** · ห้ามดึง tmd.go.th ด้วยสคริปต์ · คอมเมนต์โค้ดเป็นภาษาไทย สั้น · ห้ามแก้ `DESIGN-expo.md` · ห้ามเริ่มขั้น 2/3 ถ้าผู้ใช้ไม่สั่ง · ห้ามสร้างบัญชีหรือ deploy เอง (บอกผู้ใช้ว่าต้องทำอะไร)

## 11. แผนที่เอกสาร
อยู่ที่ [docs/README.md](docs/README.md) (ตารางย้ายไฟล์จากโครงเก่าอยู่ใน [docs/archive/README.md](docs/archive/README.md))
