# ข้อเสนอชุด md / skill / tech stack / โครงโฟลเดอร์ (ร่างรอรีวิว)

สถานะ: **ผู้ใช้ตกลงทั้ง 6 ข้อในหัวข้อ 10 แล้ว (2026-11-16)** (ข้อ 4 และ 5 มีสองตัวเลือก ผู้ใช้ตอบรวมว่า "ตกลงทั้ง 6 ข้อ" ผู้ช่วยตีความว่าเลือกตัวแรกที่เสนอ: ข้อ 4 = repo เป็นโฟลเดอร์ย่อยในโปรเจกต์ (ถ้า Next.js build/Vercel CLI มีปัญหากับ path ภาษาไทยและช่องว่าง ให้ย้ายไป path สั้น), ข้อ 5 = คำสั่งใน skill/rules เป็นภาษาอังกฤษกระชับ + ใส่คำค้นภาษาไทยใน description) ยังไม่ได้สร้างไฟล์ md หรือ skill จริง รอผู้ใช้สั่งเขียน · (ข้อความเดิม: ร่าง รอผู้ใช้รีวิว ยังไม่ได้สร้างไฟล์ md หรือ skill จริง) · 2026-11-16 · ขั้น 1 (เตรียมแผน)
ที่มา: ผลค้นคว้า 4 ไฟล์ใน [research/](../../docs/research/) (R1 skill และ CLAUDE.md, R2 โครงโฟลเดอร์, R3 tech stack และ UI, R4 แนวปฏิบัติการเขียนโค้ด) + การตรวจซ้ำของผมเอง (หัวข้อ 9)

## 0. สิ่งที่ค้นพบแล้วเปลี่ยนแผน (สรุปสั้น)

| # | เรื่อง | ผลต่อแผน | ตรวจซ้ำแล้ว? |
|---|---|---|---|
| 1 | **skill ที่เป็น "มาตรฐาน/ความรู้" มักไม่ถูกเรียกใช้** (Vercel ทดสอบ: ไม่ถูกเรียก 56% ของกรณี; ดัชนีเอกสารในไฟล์ที่โหลดตลอดได้ 100%) | มาตรฐานการเขียนโค้ดย้ายไปเป็น **ไฟล์กฎตามโฟลเดอร์** (`.claude/rules/*.md` + `paths:`) ซึ่งโหลดอัตโนมัติเมื่อแตะไฟล์ในโฟลเดอร์นั้น ส่วน skill ใช้กับ **ขั้นตอนงาน** | ✅ บล็อก Vercel 27 ม.ค. 2026 และเอกสาร Claude Code |
| 2 | **`CLAUDE.md` ควรไม่เกิน 200 บรรทัด** ใส่เฉพาะสิ่งที่อ่านจากโค้ดไม่ได้ | `CLAUDE.md` สั้น ชี้ไปเอกสารอื่นด้วยข้อความธรรมดา (ไม่ใช้ `@` import เพราะ import โหลดทุกครั้ง ไม่ประหยัด context) | ✅ เอกสาร Claude Code |
| 3 | **Next.js 16.3+ สร้าง `AGENTS.md` ให้** แต่ Claude Code อ่านแค่ `CLAUDE.md` ถ้ามีทั้งคู่ | บรรทัดแรกของ `CLAUDE.md` = `@AGENTS.md` (เอกสารแนะนำให้นำเข้าแบบนี้ มีอีกทางคือตั้งค่าให้โหลดทั้งคู่) | ✅ บางส่วน |
| 4 | **PyMuPDF 2.x เป็น AGPL-3.0 และหนักมาก** (wheel 63-69 MB + ต้องมี onnxruntime, numpy, networkx ฯลฯ) | ตัวอ่าน PDF ใช้ **pypdfium2** (BSD/Apache, wheel 2.7-5.4 MB, ไม่มี dependency) และ pdfminer.six (MIT) เป็นทางสำรอง | ✅ PyPI |
| 5 | **TypeScript ล่าสุด 7.0.2 แต่ typescript-eslint 8.72.2 รับได้แค่ < 6.1.0** | ตรึง TypeScript ไว้ที่ 6.0.x | ✅ npm |
| 6 | **ฟังก์ชัน Python ที่ `/api/*` อาจชนกับ `app/api/*` ของ Next.js** (รายงานจากชุมชนว่าเกิด 404) | `/api/*` เป็นของ Python อย่างเดียว ฝั่ง Next.js ห้ามมี `app/api/` (Route Handler ที่จำเป็น เช่น สั่งล้างแคช ให้ใช้ path อื่น เช่น `app/internal/...`) | รายงานชุมชน (ยังไม่ได้ทดสอบเอง) |
| 7 | **Vercel มีทางใหม่ชื่อ "Services" (Beta)** สำหรับรัน Python คู่เฟรมเวิร์กอื่น ส่วนแบบไฟล์ใน `/api` ยังรองรับ (เอกสารเรียกว่าสำหรับ "existing projects") | คงแบบ `/api` ไว้ (repo รากเดียว) **แต่ต้องทดสอบ deploy ก่อนงานจริง** ถ้าไม่ผ่าน ใช้ Services (แยก `web/` + `pipeline/`) | ✅ บางส่วน (เอกสารเขียนว่า "you can use Services" ไม่ได้บังคับ) |
| 8 | **ฟังก์ชัน Python แพ็กทุกไฟล์ในโปรเจกต์** (ไม่มีการตัดไฟล์ที่ไม่ใช้) | ต้องตั้ง `excludeFiles` ใน `vercel.json` กัน `node_modules`, `.next`, `data` | รายงานชุมชน |
| 9 | **ข้อความไทยจาก PDF มีปัญหาที่รู้กันอยู่** (อักขระ PUA แทนวรรณยุกต์, สระอำแยกเป็น ํ + า, วรรณยุกต์มาก่อนสระ) | ขั้น 0 ต้องมีขั้นซ่อม: แปลง PUA กลับ → NFC → `pythainlp.util.normalize` และทดสอบกับ PDF จริงใน `dataset-raw/` | เคยพบ PUA ในรอบสำรวจ (เอเจนต์ E) |
| 10 | **"ข้อมูลใหม่ขึ้นเว็บโดยไม่ deploy" ทำได้ด้วยแคชของ Next.js** | อ่าน DB ด้วย `'use cache'` + `cacheTag`; สคริปต์โหลดข้อมูลเรียก Route Handler ที่รัน `revalidateTag` (ห้ามใช้ `updateTag` เพราะใช้ได้เฉพาะ Server Action) | ✅ เอกสาร Next.js |

## 1. Tech stack (ฉบับเต็ม)

| ชั้น | เครื่องมือ | เวอร์ชัน | หมายเหตุ |
|---|---|---|---|
| เว็บ | Next.js (App Router, Server Components, Cache Components) | 16.4.6 ✅ | ไม่มี `next lint` แล้ว ใช้ ESLint ตรง |
| | React | 19.3.1 ✅ | |
| | TypeScript (strict) | **ตรึง 6.0.x** ✅ | เพราะข้อ 0.5 |
| | Tailwind CSS (ตั้งค่าใน CSS ด้วย `@theme`) | 4.3.5 ✅ | ต้องใช้ Safari 16.4 ขึ้นไป (ตาม R3) |
| | คอมโพเนนต์เขียนเอง + `clsx` + `tailwind-merge` + `class-variance-authority` | ตาม R3 | ไม่ใช้ shadcn/ui |
| | ไอคอน `lucide-react`, ฟอนต์ Noto Sans Thai ผ่าน `next/font` (มี subset `thai`, เป็น variable font) | ตาม R3 | |
| | Zod (ตรวจข้อมูลจาก DB) | 4.6.7 ✅ | |
| ฐานข้อมูล | Neon Postgres + `@neondatabase/serverless` (SQL ธรรมดา ไม่ใช้ ORM) | 1.2.1 ✅ | แผนฟรีตาม R3: 1 GB/โปรเจกต์, 100 CU-ชั่วโมง/เดือน, หยุดเองหลังว่าง 5 นาที, มีภูมิภาคสิงคโปร์ (ยังไม่ได้ตรวจซ้ำ) |
| | migration: ไฟล์ `db/schema.sql` + สคริปต์ | | เล็กพอไม่ต้องใช้เครื่องมือ migration |
| หลังบ้าน/อัลกอริทึม | Python | 3.12 บน Vercel (ค่าเริ่มต้น) / 3.13 บนเครื่อง ✅ | ต้องเลือกเวอร์ชันเดียวกันทั้งสองที่ |
| | PyThaiNLP (newmm) | 5.4.0 ✅ Apache-2.0, wheel 21.9 MB, ไม่มี dependency บังคับ | บน Vercel ต้องตั้ง `PYTHAINLP_READ_ONLY=1` และ `PYTHAINLP_DATA=/tmp/...` (ตาม R3 ยังไม่ได้ทดสอบ) |
| | ตัวอ่าน PDF: **pypdfium2** (หลัก), pdfminer.six (สำรอง) | 5.15.2 / 20260107 ✅ | ไม่ใช้ PyMuPDF (ข้อ 0.4) |
| | Pydantic (สัญญาข้อมูลต้นฉบับ) | 2.14.3 ✅ | ส่งออก JSON Schema → สร้างชนิด TypeScript ด้วย `json-schema-to-typescript` 16.0.0 ✅ |
| | Naive Bayes / k-NN เขียนเอง | - | ไม่ใช้ sklearn ในโค้ดที่ deploy |
| | uv (จัดการแพ็กเกจ), Ruff 0.17.5 ✅, pytest | | |
| ทดสอบเว็บ | Vitest + Testing Library (หน่วย), Playwright (end-to-end + ภาพหน้าจอ 375/768/1280) | ตาม R3 | Server Component แบบ async ทดสอบด้วย end-to-end |
| คุณภาพ | ESLint (flat config, `eslint-config-next` มี jsx-a11y อยู่แล้ว ✅), Prettier + `prettier-plugin-tailwindcss` | | |
| Deploy/CI | Vercel Hobby, GitHub, GitHub Actions (lint + typecheck + pytest) | | ภูมิภาคฟังก์ชันเริ่มต้น `iad1` (สหรัฐฯ) ควรย้ายใกล้ Neon (ยังไม่ได้ตรวจว่า Hobby เลือก `sin1` ได้) |

✅ = ผมตรวจกับ npm หรือ PyPI เองแล้ววันนี้ ที่เหลือมาจากรายงาน R3

## 2. อะไรควรอยู่ที่ไหน (หลักการ)

| ชนิด | ใส่อะไร | โหลดเมื่อไร |
|---|---|---|
| **`CLAUDE.md`** (ราก repo, ≤ 200 บรรทัด) | คำสั่งรัน/ทดสอบ, การตัดสินใจของทีม, กับดักที่รู้แล้ว, ขั้นตอนทำงาน, ลิงก์เอกสาร | ทุกครั้ง |
| **`.claude/rules/*.md`** + `paths:` | มาตรฐานที่ต้องใช้ทุกครั้งที่แก้ไฟล์ชนิดนั้น | อัตโนมัติเมื่อแตะไฟล์ตาม path |
| **`.claude/skills/<ชื่อ>/SKILL.md`** (≤ 500 บรรทัด) | ขั้นตอนหลายขั้น เช็กลิสต์ และเอกสารอ้างอิงยาว | เมื่อเกี่ยวข้อง หรือคุณสั่งด้วย `/ชื่อ` |
| **`.claude/settings.json`** | สิทธิ์ (เช่น ถามก่อน `git commit` / `git push`) และ hook | ทุกครั้ง แบบบังคับ |
| **`docs/`** | สเปก แผน phase การตัดสินใจ (ADR) สัญญาข้อมูล | เมื่อถูกอ้างถึง |

## 3. ไฟล์ md ใหม่ที่เสนอ (ใน repo)

| ไฟล์ | หน้าที่ | ขนาด | ฐานจาก |
|---|---|---|---|
| `CLAUDE.md` | บรรทัดแรก `@AGENTS.md` แล้ว Project / Commands / Conventions / Decisions / Gotchas / Workflow / Docs | 80-120 บรรทัด | เอกสาร Claude Code + R1 หัวข้อ 7.1 |
| `AGENTS.md` | Next.js สร้างให้เอง (ชี้ไปเอกสารของเวอร์ชันที่ติดตั้ง) | - | create-next-app |
| `README.md` | ภาพรวม วิธีรัน env โครงโฟลเดอร์ สมาชิกและบทบาท แหล่งข้อมูลและเครดิต TMD (ตามเกณฑ์วิชา) | - | |
| `THIRD_PARTY_NOTICES.md` | รวม license ของ skill ที่ดัดแปลง (Apache-2.0, MIT) | สั้น | R1 หัวข้อ 8 |
| `.claude/rules/frontend.md` | มาตรฐานหน้าเว็บ (paths: `app/**`, `components/**`, `lib/**`) | ~40 บรรทัด | Vercel web-interface-guidelines + R3 หัวข้อ 5 |
| `.claude/rules/python.md` | มาตรฐาน Python + กฎข้อความไทย 5-6 ข้อ (paths: `src/**/*.py`, `api/**/*.py`, `scripts/**`) | ~50 บรรทัด | R4 หัวข้อ 7.3 |
| `.claude/skills/*` | 7 skill (หัวข้อ 4) | 80-180 บรรทัด/ตัว | หัวข้อ 4 |
| `docs/architecture.md` | **โครงโฟลเดอร์แบบยืดหยุ่น** + กฎเพิ่มโฟลเดอร์ (หัวข้อ 6) | 40-80 บรรทัด | R2 หัวข้อ 6-7 |
| `docs/spec/scope-and-pipeline.md` | ขอบเขต ปัญหา ท่อ 4 ขั้น กฎความถูกต้อง (ย้ายจาก PLAN.md หัวข้อ 2-3) | | PLAN.md |
| `docs/spec/data-contract.md` | สัญญาข้อมูล: โครง JSON ผลลัพธ์, ตาราง DB, ป้าย, ภาค 7 ภาค | | ใหม่ |
| `docs/spec/labeling-guideline.md` | คู่มือป้าย v1 | | LABEL-GUIDELINE-DRAFT.md |
| `docs/spec/region-scope-map.md` | ตารางแมปภาค v1 | | REGION-SCOPE-MAP-DRAFT.md |
| `docs/spec/ui-spec.md` | หน้าเว็บ 2 ส่วน (หลัก + Demo), ส่วนประกอบแต่ละหน้า, มาตรฐาน responsive (หัวข้อ 7) | | ใหม่ |
| `docs/decisions/NNNN-*.md` | ADR แบบ Nygard (Title / Status / Context / Decision / Consequences) ห้ามลบ ให้ mark superseded | สั้นต่อไฟล์ | ย้ายจาก decision log ใน PLAN.md |
| `docs/plans/` | แผนแต่ละ phase (สร้างในขั้น 2) | | skill `planning-phases` |
| `docs/progress.md` + `docs/progress.json` | ความคืบหน้าจริง และรายการงานที่มีช่อง `passes` (ผ่าน/ไม่ผ่าน) | | บทความ Anthropic เรื่อง harness (ตาม R4) แทน STATE.md |

## 4. Skill 7 ตัวที่เสนอ

| Skill | ทำอะไร | ฐานจาก skill ที่มีแจก (license) | เพิ่มเฉพาะงานเรา | ตัดออก | เรียกใช้ |
|---|---|---|---|---|---|
| `planning-phases` | แตกงานเป็น phase เขียนแผนลง `docs/plans/` แต่ละ phase จบด้วยการตรวจ | obra/superpowers `writing-plans`, `brainstorming` (MIT) | ประตูตรวจต่อ phase, ไม่มีขั้น commit | commit ทุกงาน, subagent ต่องาน | **คุณสั่งเองเท่านั้น** |
| `testing-and-verification` | ตรวจก่อนบอกว่าเสร็จ: รันคำสั่งจริง แปะหลักฐาน | superpowers `verification-before-completion`, `test-driven-development`, `systematic-debugging` (MIT), Anthropic `webapp-testing` (Apache-2.0) | คำสั่งตรวจของเรา, golden file, ชุดกันหลอน F1-F7, ภาพหน้าจอ 3 ขนาด | ภาษาแรงๆ, worktree | อัตโนมัติ + สั่งเอง |
| `frontend-responsive-ui` | สร้าง/รีวิวหน้าใหม่ | Anthropic `frontend-design` (Apache-2.0), Vercel `web-interface-guidelines` (MIT, คัดลอกกฎมาเก็บเอง ไม่ดึงจาก URL ทุกครั้ง) | มาตรฐานหัวข้อ 7, ภาษาไทย, สถานะว่าง/ผิดพลาด | สไตล์ "หวือหวา", shadcn | อัตโนมัติ + สั่งเอง |
| `nextjs-component-architecture` | ข้อตกลงคอมโพเนนต์ของเรา (บาง) | Vercel `composition-patterns`, `react-best-practices` เฉพาะข้อสำคัญ (MIT) | Server Component เป็นค่าเริ่มต้น, ชั้นเข้าถึงข้อมูล (DAL) ที่เดียว, `'use client'` เฉพาะปลายทาง, ห้าม `app/api/` | กฎ performance 40+ ข้อ | อัตโนมัติ + สั่งเอง |
| `python-pipeline` | เพิ่ม/แก้ขั้นในท่อประมวลผล | wshobson python skills (MIT) ใช้เทียบ | ฟังก์ชันบริสุทธิ์ต่อขั้น, seed คงที่, โค้ดชุดเดียวใช้ทั้งเครื่องและ Vercel, Pydantic เป็นสัญญา | uv/mypy strict, coverage 80% | อัตโนมัติ + สั่งเอง |
| `thai-text-handling` | ทำความสะอาดข้อความไทยจาก PDF, newmm, คำเฉพาะอุตุฯ | boom-vitt `thai-text-processing`, `thai-date-format` (MIT) | ซ่อม PUA/สระอำ (ข้อ 0.9), พจนานุกรมคำอุตุฯ, สคริปต์ทดสอบกับ PDF จริง | romanization, Elasticsearch | อัตโนมัติ + สั่งเอง |
| `vercel-deploy-checklist` | เช็กลิสต์ deploy | Vercel `deploy-to-vercel` (MIT) เฉพาะลำดับตรวจ | env vars, `excludeFiles`, ภูมิภาค, ทดสอบหลัง deploy | **ขั้น commit/push/login ทั้งหมด** | **คุณสั่งเองเท่านั้น** |

**ไม่ทำเป็น skill แยก:**
- `code-quality-and-reuse` ยุบเป็นไม่กี่บรรทัดใน `CLAUDE.md` + ใช้คำสั่ง `/code-review` ที่มีอยู่แล้ว
- คู่มือโครงโฟลเดอร์อยู่ใน `docs/architecture.md` ตามที่คุณอยากให้ยืดหยุ่น

**กฎร่วมของทุก skill:** กฎสำคัญอยู่บนสุด, `description` บอกว่าทำอะไรและใช้เมื่อไร (เอกสารบอกว่าตัดที่ 1,536 อักษร), ไม่มี skill ใด commit/push เอง, เขียนใหม่โดยได้แรงบันดาลใจแทนการคัดลอกทั้งย่อหน้า และเก็บ license ไว้ใน `THIRD_PARTY_NOTICES.md`

## 5. จัดไฟล์ md เดิมใหม่

| ไฟล์เดิม | จะทำอะไร |
|---|---|
| `PLAN.md` (82 KB มีประวัติปนข้อความที่ถูกแทนที่) | แยก: สเปกที่ตกลงแล้ว → `docs/spec/scope-and-pipeline.md`; บันทึกการตัดสินใจ → ADR ใน `docs/decisions/`; ตัวไฟล์เดิมเก็บเป็นประวัติการวางแผนนอก repo |
| `LABEL-GUIDELINE-DRAFT.md`, `REGION-SCOPE-MAP-DRAFT.md` | ย้ายเข้า `docs/spec/` (ตัดคำว่า DRAFT, เก็บสถานะ v1) |
| `BUILD-PLAN.md`, `STATE.md` (ร่างเก่าที่พักไว้ ขัดกับสิ่งที่ตกลงแล้วหลายข้อ) | เลิกใช้ แทนด้วย `docs/plans/` + `docs/progress.*` |
| `TMD-SITE-MAP.md`, `TMD-DATA-INVENTORY.md`, `tmd-digest/` | อยู่นอก repo (เป็นผลสำรวจที่มีข้อความคัดจาก TMD); ใน repo ใส่แค่ `docs/data-sources.md` สั้นๆ บอกแหล่งข้อมูลและเครดิต |
| `research/` | อยู่นอก repo (หรือ `docs/research/` ถ้าอยากให้ทีมเห็น) |
| `notes/` (สรุปสไลด์วิชา) | อยู่นอก repo |
| `dataset-raw/` | ย้ายเข้า `data/raw/` ของ repo ในขั้น 3 โดยอยู่ใน `.gitignore` |
| `_excluded-scripted-downloads/` | อยู่นอก repo (รอคุณสั่งลบถาวรหรือไม่) |

**ตำแหน่ง repo:** โฟลเดอร์โปรเจกต์ปัจจุบันมี `docs/` (สไลด์วิชา) ชื่อชนกับ `docs/` ของ repo จึงเสนอให้ repo อยู่ในโฟลเดอร์ย่อยแยก (เช่น `tmd-plain-forecast/`) **ข้อควรระวัง:** path หลักมีภาษาไทยและช่องว่าง (`C:\PIM ET CAI 2567\ปี 3-2569\...`) Python และ Node ที่ผมรันวันนี้ใช้ได้ แต่ยังไม่ได้ทดสอบ Next.js build, Vercel CLI, hook (ทางเลือก: วาง repo ที่ path สั้นๆ เช่น `C:\dev\tmd-plain-forecast`)

## 6. โครงโฟลเดอร์ (โครงใหญ่ ยืดหยุ่น ปรับได้ในขั้น 3)

```
/                      ราก repo = ราก Vercel project
├─ app/                หน้าเว็บ: / (หลัก), /demo  (ห้ามมี app/api/)
│  └─ <route>/_components/   คอมโพเนนต์เฉพาะหน้านั้น
├─ components/         คอมโพเนนต์ที่ใช้ร่วมหลายหน้า
├─ lib/                โค้ด TS ใช้ร่วม: ชั้นเข้าถึงข้อมูล (DAL), ชนิดข้อมูล, จัดรูปวันที่ไทย
├─ public/
├─ api/                ไฟล์ทางเข้าฟังก์ชัน Python บางๆ (เช่น summarize.py → /api/summarize)
├─ src/<pkg>/          แพ็กเกจ Python ท่อประมวลผล (ใช้ร่วมทั้งเครื่องและ Vercel)
├─ scripts/            คำสั่งหลังบ้าน: ประมวลผลชุดข้อมูล ฝึก โหลดเข้า Neon
├─ models/             พารามิเตอร์โมเดลที่ฝึกแล้ว (JSON เล็ก)
├─ db/                 schema.sql
├─ data/               ข้อมูล (raw/ อยู่ใน .gitignore)
├─ tests/              pytest + fixtures เล็ก (+ e2e ของเว็บ)
├─ docs/               architecture.md, spec/, decisions/, plans/, progress.*
├─ .claude/, CLAUDE.md, AGENTS.md
└─ ไฟล์ตั้งค่า: package.json, next.config.ts, tsconfig.json, eslint.config.mjs, pyproject.toml (+ uv.lock), vercel.json, .env.example, .editorconfig, .gitignore, README.md
```

**ส่วนที่ยังไม่แน่นอน:** `api/` + `vercel.json` ขึ้นกับผลทดสอบ deploy (ถ้าไม่ผ่าน → แผน B: Services แยก `web/` + `pipeline/`); `src/<pkg>` อาจเป็นโฟลเดอร์ที่รากแทนถ้า import บน Vercel ง่ายกว่า; ชื่อแพ็กเกจยังไม่ตั้ง

**กฎเพิ่มโฟลเดอร์ (ย่อจาก R2 11 ข้อ):** ถามก่อนสร้างโฟลเดอร์ระดับบนใหม่และบันทึก ADR, ชื่ออังกฤษตัวเล็กไม่มีช่องว่างหรือไทย, โค้ดใช้หน้าเดียววางใน `_components` แล้วค่อยย้ายขึ้นเมื่อมีหน้าที่สองใช้, ทิศ import เดียว (`components`/`lib` ห้าม import จาก `app/`), `api/` มีแค่ไฟล์ทางเข้า, ข้อมูลใหม่อยู่ใต้ `data/` เสมอ, โฟลเดอร์ที่ฟังก์ชัน Python ไม่ต้องใช้ต้องอยู่ใน `excludeFiles`, ทบทวนโครงทุกจบ phase แล้วอัปเดต `docs/architecture.md`

## 7. มาตรฐานหน้าเว็บ (ไปอยู่ใน rule frontend + skill frontend-responsive-ui)

| เรื่อง | ค่า | แหล่ง |
|---|---|---|
| Breakpoint (mobile-first) | 640 / 768 / 1024 / 1280 / 1536 (ค่าเริ่มต้น Tailwind) | R3 |
| ทดสอบภาพหน้าจอ | 375 (มือถือ), 768 (แท็บเล็ต), 1280 (เดสก์ท็อป) | ข้อเสนอ |
| ความกว้างเนื้อหาเดสก์ท็อป | กรอบสูงสุดราว 1200-1280px จัดกลาง, ข้อความยาวจำกัดความกว้าง | ข้อเสนอ |
| ตัวอักษรไทย | เนื้อหาและช่องกรอก ≥ 16px, line-height ราว 1.6-1.75 (ไม่พบตัวเลขทางการสำหรับภาษาไทย), ห้ามเพิ่ม letter-spacing และห้ามจัดชิดสองข้าง, `word-break: normal` (ห้าม `break-all`), `lang="th"` | R3 |
| จุดแตะ | ขั้นต่ำ 24px (WCAG 2.2 ข้อ 2.5.8), แนะนำ 44px (Apple) / 48dp (Material) จากแหล่งรอง | R3 |
| สี | ความต่าง ≥ 4.5:1 (WCAG 1.4.3), ไม่ใช้สีอย่างเดียวบอกความหมาย | R3 |
| การแบ่งคอมโพเนนต์ | `components/` ชิ้นพื้นฐาน (Button, Card, Tabs, Badge, Alert, Skeleton) + คอมโพเนนต์ฟีเจอร์ (ForecastCard, RegionTabs, RoundPicker, AdviceList, UploadDropzone, ResultPanel, Disclaimer), ตรรกะอยู่ใน `lib/` | ข้อเสนอ |

## 8. นโยบายคอมเมนต์โค้ด (ไปอยู่ใน CLAUDE.md)

- คอมเมนต์ **ภาษาไทย สั้น** เขียนเฉพาะ "ทำไม" ไม่เขียน "ทำอะไร" (ถ้าต้องอธิบายว่าทำอะไร ให้แก้โค้ดให้อ่านง่ายแทน)
- ชื่อตัวแปร ฟังก์ชัน ไฟล์ โฟลเดอร์ เป็นภาษาอังกฤษ
- ฟังก์ชัน/คลาสที่ใช้ข้ามโมดูลมี docstring หรือ TSDoc บรรทัดเดียวได้ ไม่ใส่ชนิดข้อมูลซ้ำใน JSDoc (TypeScript บอกอยู่แล้ว)
- TODO รูปแบบ `TODO(ลิงก์งาน): ...` ไม่ใส่ชื่อคน
- Python เปิดไฟล์ด้วย `encoding="utf-8"` ทุกครั้ง, JSON ภาษาไทยเขียนด้วย `ensure_ascii=False`
(ที่มา: R4 — Google eng-practices, PEP 8, Google TS style guide)

## 9. ผลการตรวจซ้ำของผม (แก้ข้อที่เอเจนต์พูดเกิน)

| ข้อที่เอเจนต์เขียน | ผลตรวจ |
|---|---|
| `description` ของ skill จำกัด 1,024 อักษร | **ไม่ตรง** เอกสาร Claude Code: `description` + `when_to_use` ถูกตัดที่ 1,536 อักษร (1,024 อาจเป็นข้อกำหนดของแพลตฟอร์มอื่น) |
| "การเขียนสถาปัตยกรรมใน CLAUDE.md เป็นคำแนะนำเก่า" | **บางส่วน** ตารางในเอกสารยังระบุสถาปัตยกรรมเป็นสิ่งที่ใส่ได้ แต่คำสั่ง `/doctor` จะตัดผังโฟลเดอร์และภาพรวมสถาปัตยกรรมออกเพราะอ่านจากโค้ดได้ |
| Vercel "แนะนำ" Services สำหรับโปรเจกต์ใหม่ | **บางส่วน** หน้า Python เขียนว่า "you can use Services" และรองรับ `/api` สำหรับโปรเจกต์เดิม; Services เป็น Beta ทุก plan |
| หลังสรุปบทสนทนา skill เก็บไว้ 5,000 token แรก | **บางส่วน** เก็บเฉพาะการเรียกครั้งล่าสุดของแต่ละ skill และ skill ทั้งหมดใช้งบรวม 25,000 token |
| `eslint-config-next` มีกฎ accessibility หรือไม่ (R4 ไม่แน่ใจ) | **มี** `eslint-plugin-jsx-a11y` อยู่ใน dependencies (npm) |
| ข้อจำกัด Vercel: body 4.5 MB, Python 500 MB, 300 วินาที, Python 3.12 ค่าเริ่มต้น | **ตรง** (3.13 และ 3.14 ใช้ได้ด้วย) |
| บล็อก Vercel: skill ไม่ถูกเรียก 56%, AGENTS.md 100% | **ตรง** (ถ้าเขียนคำสั่งชัดให้เรียก skill อัตราเรียกขึ้นเป็น 95% และผ่าน 79%) |

## 10. สิ่งที่ต้องให้คุณตัดสิน

1. **มาตรฐานโค้ดเป็นไฟล์กฎตามโฟลเดอร์ + skill สำหรับขั้นตอน** (แทน "skill 7 ตัวที่เป็นมาตรฐาน") ตกลงไหม
2. **ชุด skill 7 ตัวในหัวข้อ 4** (มี `planning-phases` ใหม่, ยุบ `code-quality-and-reuse`) ตกลงไหม
3. **ตัวอ่าน PDF = pypdfium2** (ไม่ใช้ PyMuPDF เพราะ AGPL และหนัก) ตกลงไหม
4. **ตำแหน่ง repo:** โฟลเดอร์ย่อยในโปรเจกต์ หรือ path สั้นๆ นอกโปรเจกต์ (เช่น `C:\dev\...`)
5. **ภาษาในไฟล์ skill/rules:** คำสั่งเป็นอังกฤษกระชับ (ใช้ token น้อยกว่า) แต่ใส่คำค้นภาษาไทยใน `description` หรือเขียนไทยทั้งหมด
6. **การจัดไฟล์ md เดิมตามหัวข้อ 5** ตกลงไหม (รวมเลิกใช้ BUILD-PLAN.md/STATE.md)

## 11. สิ่งที่ยังไม่ได้ตรวจ
- ทดสอบ deploy จริงบน Vercel ทั้งหมด (import แพ็กเกจจาก `api/`, ขนาดและเวลาเริ่มของฟังก์ชันที่มี PyThaiNLP + pypdfium2, ไฟล์ dependency ที่ Vercel เลือก, `excludeFiles`)
- pypdfium2 ดึงข้อความไทยจาก PDF ของ TMD ได้ดีแค่ไหน (ยังไม่ได้ติดตั้งและทดสอบ)
- ข้อจำกัดแผนฟรีของ Neon, ภูมิภาค `sin1` บน Hobby, ตัวเลขจุดแตะของ Apple/Material (จากแหล่งรอง)
- ว่า hook ตัวอย่างในเอกสารรันบน Windows ได้ไหม และ path ภาษาไทย/ช่องว่างกับ Next.js build
- license ของ skill-creator และรายละเอียด license ของแต่ละ repo MIT (ชื่อผู้ถือลิขสิทธิ์)
