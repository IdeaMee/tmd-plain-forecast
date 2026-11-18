# เอกสารเก่า (archive)

เก็บไว้เป็นประวัติ **ไม่ใช้สั่งงาน** ถ้าข้อความในไฟล์ขัดกับ `PLAN.md`, `docs/spec/` หรือ `docs/decisions/` ให้ยึดฉบับปัจจุบัน

| ไฟล์ | คืออะไร | แทนที่ด้วย |
|---|---|---|
| `PLAN-history.md` | PLAN.md ฉบับยาวเดิม (ประวัติคุย + decision log เต็ม 2026-11-06 ถึง 11-16) | [../../PLAN.md](../../PLAN.md) (ฉบับสั้น) + [../../docs/decisions/](../../docs/decisions/README.md) |
| `BUILD-PLAN.md` | ร่างแผน 9 phase ที่เสนอเกินหน้า (ผู้ใช้สั่งพัก) | ขั้น 2 ในอนาคต: [../plans/](../plans/README.md) |
| `STATE.md` | ตารางสถานะของ BUILD-PLAN | [../PROGRESS.md](../PROGRESS.md) |
| `SETUP-PROPOSAL.md` | ข้อเสนอ tech stack + ชุด md/skill (ตกลงครบ 6 ข้อ) | [../../docs/decisions/0004-tech-stack.md](../../docs/decisions/0004-tech-stack.md), [../../docs/decisions/0008-md-and-skills.md](../../docs/decisions/0008-md-and-skills.md) |
| `LABEL-GUIDELINE-DRAFT.md` | ต้นฉบับคู่มือป้าย | [../../docs/spec/labeling-guideline.md](../../docs/spec/labeling-guideline.md) |
| `REGION-SCOPE-MAP-DRAFT.md` | ต้นฉบับตารางแมปภาค | [../../docs/spec/region-scope-map.md](../../docs/spec/region-scope-map.md) |

## ตารางย้ายไฟล์ (โครงเก่า → โครงใหม่ 2026-11-16)
พาธที่เขียนเป็นข้อความธรรมดาหรือในเครื่องหมาย ` ` ในไฟล์เก่ายังเป็นพาธเดิม (ไม่แก้เพื่อรักษาประวัติ) ส่วนลิงก์ที่คลิกได้ถูกแก้ให้ชี้ที่ใหม่แล้ว

| เดิม | ใหม่ |
|---|---|
| `tmd-plain-forecast/*` (CLAUDE.md, README.md, .claude/, docs/, THIRD_PARTY_NOTICES.md) | ราก (Root) |
| `docs/progress.md` | `PROGRESS.md` |
| `docs/plans/` | `plans/` |
| `PLAN.md` (ฉบับยาว) | `docs/archive/PLAN-history.md` (ฉบับสั้นใหม่อยู่ที่ `PLAN.md`) |
| `dataset-raw/` | `data/raw/` |
| `_excluded-scripted-downloads/` | `data/excluded-scripted/` |
| `research/`, `tmd-digest/`, `TMD-DATA-INVENTORY.md`, `TMD-SITE-MAP.md` | `docs/research/` |
| `docs/` เดิม (สไลด์วิชา) | `course/slides/` |
| `notes/` | `course/notes/` |
