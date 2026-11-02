# แผน 06: deploy จริง และของที่ต้องส่ง

**สถานะ (2026-11-17):** 6.1 เสร็จ ผู้ใช้เซ็นปิด (smoke 16/16 ด้วย `npm run smoke`, รายงาน `docs/results/smoke-test.md`; `PYTHAINLP_*` ไม่ต้องตั้งใน Vercel เพราะฟังก์ชันตั้งเอง) · 6.2 ผู้ใช้สั่งพักไว้ก่อน ทำทีหลัง · ข้อความข้างล่างคือแผนเดิม

**เป้าหมาย:** มีลิงก์ใช้งานจริงบน Vercel ที่ผ่าน smoke test และ repo มี README ครบตามเกณฑ์รายวิชา พร้อมผลวัดสำหรับสไลด์และรายงาน

**สเปก:** skill `vercel-deploy-checklist` (ผู้ใช้เรียก `/vercel-deploy-checklist`) · [../../PLAN.md](../../PLAN.md) หัวข้อ 2 (เกณฑ์รายวิชา) · [../../docs/spec/scope-and-pipeline.md](../../docs/spec/scope-and-pipeline.md) หัวข้อ 6-7 (การวัดผล, ข้อจำกัด) · [../../docs/data-sources.md](../../docs/data-sources.md) (เครดิต)

**ข้อจำกัดที่ใช้:** ผู้ช่วยเตรียมและตรวจ ผู้ใช้ทำขั้นบัญชี git และ deploy · ห้ามมี secret ใน repo · `data/raw/` ไม่ขึ้น repo

---

## Phase 6.1: deploy production และ smoke test   [M]   [เจ้าของ: ทั้งสอง]

Goal: เว็บ production ทำงานครบตาม smoke test 15 ข้อ และอัปเดตข้อมูลได้โดยไม่ deploy ใหม่

Tasks (ผู้ช่วย)
1. ไล่ส่วนที่ 1 ของ `vercel-deploy-checklist` บนเครื่อง (lint, typecheck, เทสต์เว็บและ Python, build, ไม่มี secret, ไม่มี `app/api/`, `excludeFiles`, TypeScript 6.0.x)
2. ลบหน้า `app/styleguide/` (จาก 0.5) และตรวจว่า `.env.example` ครบทุกตัวแปร
3. หลังผู้ใช้ deploy: รัน smoke test 15 ข้อ (ส่วนที่ 4 ของ checklist) → `docs/results/smoke-test.md` พร้อมเวลาตอบสนองครั้งแรก/ครั้งที่สอง และภาพหน้าจอ 320 / 375 px

Human steps: ตั้ง env ของ production (`DATABASE_URL`, `REVALIDATE_SECRET`, `PYTHAINLP_READ_ONLY`, `PYTHAINLP_DATA`), สั่ง commit/push และ deploy, ส่ง URL, ลองโหลดข้อมูลใหม่หนึ่งรอบ

Checks
- ทุกข้อของส่วนที่ 1 ผ่านพร้อมผลคำสั่ง · smoke test 15/15 ผ่าน (ข้อที่ไม่ผ่านบันทึกและหยุด ตามส่วนที่ 5 ของ checklist)

Out of scope: ฟีเจอร์ใหม่

---

## Phase 6.2: README ผลวัด และวัสดุนำเสนอ   [S]   [เจ้าของ: ทั้งสอง]

**แผนเร่ง (ปรับ 2026-11-18):** ส่วนของผู้ช่วย (README, `summary-for-slides.md`, ตรวจลิงก์) ย้ายไปเป็น **Phase 13.2** ในชุด C ([13-v2-release.md](13-v2-release.md)) โดยปรับให้ครอบหมวดรอบ v2 · ที่เหลือใน 6.2 คืองานของผู้ใช้เท่านั้น (สไลด์ วิดีโอ GitHub team MS Form) · ข้อความข้างล่างคือแผนเดิม

Goal: README มี 4 ส่วนตามเกณฑ์ (Idea / How to use-run-customize / Data + Results / สมาชิก + บทบาท) และตัวเลขทุกตัวในเอกสารมาจากไฟล์ใน `docs/results/`

Tasks (ผู้ช่วย)
1. `README.md`: ไอเดียและ pain point, ทำไมต้อง NLP/ML, วิธีใช้ (ลิงก์ product), วิธีรันบนเครื่องและปรับแต่ง (คำสั่งจริงจาก `.claude/CLAUDE.md`), ข้อมูลและเครดิต, ผลวัด (accuracy NB / k-NN / keyword ทั้งสองแบบ + ตัวอย่างผิด + F1-F7 + อัตราตรงกันของป้าย), ข้อจำกัด (หัวข้อ 7 ของสเปก รวม "ติดโดยโมเดลภาษา ตรวจโดยคน 20%"), อ้างอิง
2. `docs/results/summary-for-slides.md`: ตัวเลขและตัวอย่างก่อน/หลังสำหรับสไลด์ (ต้นฉบับ → สรุป ของภาคเดียวกัน)
3. ตรวจลิงก์ทั้งหมดใน README และ `docs/`

Checks
- ตัวเลขทุกตัวใน README ตรงกับไฟล์ใน `docs/results/` (ผู้ตรวจเทียบทีละตัว) · ลิงก์ใน md เสีย 0
- คำสั่งใน "วิธีรัน" รันได้จริงบนเครื่องสะอาด (ผู้ตรวจลองตามจากต้น)

Human steps: กรอกสมาชิกและบทบาท, ทำสไลด์ (pain point + idea, solution + product, เดโมสด) และวิดีโอ, ทุกคนอยู่ใน GitHub team ของทั้ง 2 org, สมาชิก commit งานของตัวเอง, ส่ง MS Form

Out of scope: งานต่อยอดหลังส่ง
