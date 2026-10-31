# 0008 ชุด md และ skill ของโปรเจกต์

Status: accepted (2026-11-16); **ที่ตั้งไฟล์ถูกแทนที่บางส่วนโดย [0009](0009-root-layout-and-skills-location.md)** (ชุดนี้ย้ายจาก `tmd-plain-forecast/` มาอยู่ที่ราก; `docs/progress.md` -> `PROGRESS.md`, `docs/plans/` -> `plans/`)

Context: ผลค้นคว้า (ไฟล์ R1-R4 ตอนนี้อยู่ใน `docs/research/`) พบว่า skill ที่เป็นความรู้/มาตรฐานมักไม่ถูกเรียกใช้ (Vercel ทดสอบ 27 ม.ค. 2026: ไม่ถูกเรียก 56% ของกรณี); เอกสาร Claude Code แนะนำ `CLAUDE.md` ไม่เกิน 200 บรรทัด และไฟล์กฎแบบ `paths:` โหลดอัตโนมัติเมื่อแตะไฟล์ที่ตรง

Decision
- `CLAUDE.md` สั้น เป็นอังกฤษกระชับ (มีสรุปภาษาไทยใน HTML comment ที่ถูกตัดก่อนส่งให้ Claude)
- มาตรฐานเป็นไฟล์กฎตามโฟลเดอร์: `.claude/rules/frontend.md`, `.claude/rules/python.md`
- Skill 7 ตัวสำหรับขั้นตอนและเช็กลิสต์: `planning-phases`, `testing-and-verification`, `frontend-responsive-ui`, `nextjs-component-architecture`, `python-pipeline`, `thai-text-handling`, `vercel-deploy-checklist` (ตั้ง `disable-model-invocation: true` กับ `planning-phases` และ `vercel-deploy-checklist` เพราะผู้ใช้เป็นคนสั่งเอง)
- ไม่ทำ skill `code-quality-and-reuse` แยก ยุบเข้า `CLAUDE.md` และใช้ `/code-review`
- ไม่มี skill ใด commit/push/ล็อกอิน; เขียนใหม่ได้แรงบันดาลใจจาก skill ที่มีแจก (รายชื่อและ license ใน `THIRD_PARTY_NOTICES.md`)
- สเปกอยู่ `docs/spec/` ความคืบหน้า `docs/progress.md` แผน phase `docs/plans/` (เดิม; ปัจจุบัน `PROGRESS.md` และ `plans/` ที่ราก ตาม 0009)

Consequences: ผู้ใช้เรียก `/planning-phases` และ `/vercel-deploy-checklist` เอง; ควรทดสอบว่า skill ถูกโหลดจริง (ยังไม่เคยรัน); hook และ permission ใน `.claude/settings.json` เป็นทางเลือก ต้องทดสอบบน Windows ก่อน
