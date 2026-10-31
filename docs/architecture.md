# สถาปัตยกรรมและโครงโฟลเดอร์

เอกสารนี้เป็นโครงใหญ่ที่ **ยืดหยุ่น ปรับได้ระหว่างขั้น 3** ถ้าเปลี่ยนโครงให้แก้ไฟล์นี้และบันทึก ADR (`docs/decisions/`) ผู้สร้างต้องไม่เปลี่ยนโครงเงียบๆ

**ราก (Root) ของ repo = โฟลเดอร์ `NLP & ML Mini-Project`** (ย้ายจากโฟลเดอร์ย่อย `tmd-plain-forecast/` เมื่อ 2026-11-16 ตาม [ADR 0009](decisions/0009-root-layout-and-skills-location.md)) เปิด Claude Code จากที่นี่ ราก Vercel project ก็คือที่นี่ด้วย

## 1. ภาพรวมการทำงาน

```
[เครื่องทีม]  ไฟล์พยากรณ์ (data/raw)  ->  ท่อประมวลผล Python (src/)  ->  ผลสรุปเป็น JSON  ->  npm run load:neon (Node, ADR 0014) เข้า Neon Postgres
[Vercel]      หน้าเว็บ Next.js (/, /demo)  อ่าน Neon ผ่าน lib/data (แคช + revalidateTag)
              /demo  -> ฟังก์ชัน Python (api/) รันท่อประมวลผลชุดเดียวกัน (ไม่เก็บไฟล์)
```
- อัปเดตข้อมูลวันถัดไป: ทีมวางไฟล์ใหม่ใน `data/raw/` -> `scripts/run_pipeline.py` -> `npm run load:neon` (โหลดเข้า DB แล้วเรียก route ล้างแคชให้) -> เว็บเปลี่ยนโดยไม่ deploy ใหม่ (ทดสอบบนเว็บจริงแล้ว 2026-11-17)
- ไม่มีการดึงเว็บ TMD อัตโนมัติ (นโยบายเว็บ TMD ข้อ 3.3)

## 2. โครงโฟลเดอร์

```
/                      ราก repo = ราก Vercel project  (โฟลเดอร์ "NLP & ML Mini-Project")
│  ไฟล์ md ที่ราก (มีแค่นี้): PLAN.md แผนหลัก, ai/PROGRESS.md ความคืบหน้า, .claude/CLAUDE.md, README.md,
│                            docs/design/DESIGN-expo.md (มาตรฐานดีไซน์ อ่านอย่างเดียว), THIRD_PARTY_NOTICES.md, AGENTS.md (Next.js สร้างให้)
├─ .claude/            rules/ (โหลดอัตโนมัติ), skills/ (ขั้นตอนงาน)
├─ docs/               architecture.md, data-sources.md, README.md (แผนที่เอกสาร)
│  ├─ spec/            scope-and-pipeline, data-contract, labeling-guideline, region-scope-map, design-system, ui-spec
│  ├─ decisions/       ADR
│  ├─ results/         ผลทดสอบ/ผลวัดของแต่ละ phase (เริ่ม 0.2)
│  ├─ research/        งานค้นคว้า R1-R4, TMD-DATA-INVENTORY, TMD-SITE-MAP, tmd-digest/ (อ้างอิง ไม่แก้)
│  └─ archive/         เอกสารเก่าที่ถูกแทนที่ (ไม่ใช้สั่งงาน)
├─ ai/plans/              แผนแต่ละ phase (ผลของขั้น 2) ชื่อ NN-<slug>.md
├─ course/             slides/ (สไลด์ ไม่ขึ้น repo), notes/ (บันทึกเนื้อหาวิชา) ไม่ใช่ส่วนของแอป
├─ data/               raw/ (ข้อมูล TMD โหลดมือ ไม่ขึ้น repo), excluded-scripted/ (ตัดออกแล้ว ไม่ใช้), labeled/, processed/
│  ── โค้ด (มีครบทุกโฟลเดอร์ข้างล่างแล้ว ณ Phase 5.2) ──
├─ app/                หน้าเว็บ: / (หลัก), /demo   ห้ามมี app/api/
│  └─ <route>/_components/   คอมโพเนนต์เฉพาะหน้านั้น
│  └─ internal/revalidate/   route สำหรับล้างแคช (ต้องมี secret)
│  └─ globals.css            บล็อก @theme = โทเคนของ docs/design/DESIGN-expo.md (docs/spec/design-system.md)
├─ components/         ui/ layout/ features/
├─ lib/                ฟังก์ชันใช้ร่วม ค่าคงที่ ชนิดข้อมูล Zod; lib/data/ = ชั้นเข้าถึงข้อมูล (server only)
├─ public/
├─ api/                ไฟล์ทางเข้าฟังก์ชัน Python บางๆ (เช่น summarize.py -> /api/summarize)
├─ src/tmd_plain/      แพ็กเกจ Python ท่อประมวลผล (ใช้ร่วมทั้งเครื่องและ Vercel)
├─ scripts/            คำสั่งหลังบ้าน: ประมวลผลชุดข้อมูลและฝึก (Python *.py), โหลดเข้า Neon (load-to-neon.mts, Node)
├─ models/             พารามิเตอร์โมเดลที่ฝึกแล้ว (JSON เล็ก)
├─ db/                 schema.sql, roles.sql
├─ tests/              pytest + fixtures เล็ก + e2e ของเว็บ (e2e/) + smoke test เว็บจริง (smoke/)
└─ ไฟล์ตั้งค่า (มีแล้วตั้งแต่ 0.1): package.json (+ package-lock.json), next.config.ts, next-env.d.ts, tsconfig.json,
   eslint.config.mjs, pyproject.toml, .env.example, .editorconfig, .gitattributes, .gitignore · เพิ่มภายหลัง: vercel.json (0.3),
   vitest.config.mts (4.1), playwright.config.ts (4.3), playwright.smoke.config.ts (6.1), .claude/launch.json (0.5)
   โฟลเดอร์ที่สร้างอัตโนมัติและไม่ขึ้น repo: node_modules/, .next/, .venv/
```

| ส่วน | ความมั่นคง | อาจเปลี่ยนเพราะ |
|---|---|---|
| ไฟล์ md ที่ราก, `docs/`, `ai/plans/`, `course/`, `data/`, `.claude/` | คงที่ (ผู้ใช้สั่งจัดเมื่อ 2026-11-16) | เพิ่มไฟล์ที่ราก = ต้องมี ADR (กฎข้อ 11) |
| `app/`, `components/`, `lib/`, `public/` | คงที่ (convention ของ Next.js) | `components/` เกิน ~15 ไฟล์ -> ย้ายทีละ feature ไป `features/<name>/` |
| `api/` + `vercel.json` | คงที่ (spike 0.3 ผ่าน ใช้แผน A) | มีไฟล์เดียว `api/summarize.py` (5.1; ไฟล์ spike `api/hello.py` ลบแล้ว) logic อยู่ใน `src/tmd_plain/service.py` |
| `src/tmd_plain/` | คงที่ในหลักการ | อาจเป็นโฟลเดอร์ที่รากแทนถ้า import บน Vercel ง่ายกว่า |
| `models/` | อาจเปลี่ยน | ไฟล์ใหญ่หรือเปลี่ยนบ่อยอาจเก็บใน DB |
| `data/` โครงย่อย | ปรับได้ | เพิ่ม `processed/`, `labeled/` ตามจำเป็น |
| ชื่อแพ็กเกจ `tmd_plain` | ตั้งแล้ว (ผู้ใช้ตกลง 2026-11-16, Q1 ใน `ai/plans/README.md`) | - |
| npm scripts เรียก `node node_modules/...` ตรงๆ | คงที่ (0.1) | shim ใน `node_modules/.bin` พังกับ `&` ใน path บน Windows (ทดสอบแล้ว) |
| Next.js เปิด `cacheComponents` (และ `partialPrefetching` ตามแม่แบบ) | คงที่ (0.1) | จำเป็นต่อ `'use cache'` ใน `lib/data/` (หัวข้อ 5) |

## 3. กฎการเพิ่มโฟลเดอร์

1. ก่อนสร้างโฟลเดอร์ระดับบนใหม่ ถามว่ามีโฟลเดอร์เดิมที่ใส่ได้ไหม ถ้าสร้างจริง เขียน ADR สั้นๆ และเพิ่มบรรทัดในตารางหัวข้อ 2
2. ชื่อโฟลเดอร์: ภาษาอังกฤษ ตัวพิมพ์เล็ก คั่นด้วย `-` (ชื่อแพ็กเกจ Python ใช้ `_`) ไม่มีช่องว่างหรือภาษาไทย
3. โค้ดที่ใช้หน้าเดียวอยู่ใน `app/<route>/_components`; มีหน้าที่สองใช้ค่อยย้ายขึ้น `components/` หรือ `lib/`
4. ทิศ import: `app -> components -> lib -> lib/data` ห้ามย้อนขึ้น; feature ห้าม import กันเอง
5. `api/` มีแค่ไฟล์ทางเข้า (อ่านคำขอ -> เรียก `src/tmd_plain` -> ตอบ JSON) helper ขึ้นต้นด้วย `_`
6. Python: logic ทั้งหมดอยู่ใน `src/tmd_plain/<stage>/`; `scripts/` แค่เรียกแพ็กเกจ; test วางใน `tests/<stage>/`
7. ไฟล์ข้อมูลใหม่อยู่ใต้ `data/` เสมอ (ยกเว้น fixture เล็ก < 100 KB ใน `tests/fixtures/` และพารามิเตอร์โมเดลใน `models/`)
8. เพิ่มโฟลเดอร์ที่ฟังก์ชัน Python ไม่ต้องใช้ -> เพิ่มใน `excludeFiles` ของ `vercel.json`
9. การตัดสินใจเชิงสถาปัตยกรรมทุกเรื่อง -> ADR (`docs/decisions/NNNN-ชื่อ.md`) ห้ามลบ ให้ mark ว่า superseded
10. จบทุก phase: ลบโฟลเดอร์ว่าง อัปเดตตารางนี้และ `.claude/CLAUDE.md`
11. ที่ราก (Root) มีเฉพาะไฟล์/โฟลเดอร์ที่ระบุในหัวข้อ 2 เอกสารใหม่ใส่ใน `docs/` (สเปกใน `docs/spec/`, ค้นคว้าใน `docs/research/`, ของเก่าใน `ai/archive/`) แผน phase ใส่ใน `ai/plans/` อย่าวางไฟล์ md ใหม่ที่ราก
12. เนื้อหารายวัน/สไลด์ใส่ใน `course/` ไม่ปนกับ `docs/` ของโปรเจกต์ และไม่ให้โค้ดของแอปอ่านไฟล์ใน `course/`, `docs/`, `ai/plans/`

## 4. Python บน Vercel: ข้อเท็จจริงและแผน

**ผล spike จริง (Phase 0.3, 2026-11-16): ผ่าน ใช้แผน A** ฟังก์ชัน `api/hello.py` นำเข้า `tmd_plain` (ติดตั้งจาก `pyproject.toml` ด้วย uv), PyThaiNLP และ pypdfium2 ได้; Python 3.12; ขนาด 48.2 MB; region `sin1` ใช้ได้บน Hobby; หน้า Next.js ทำงานปกติ รายละเอียด: `docs/results/spike-vercel-python.md`

ข้อเท็จจริงจากเอกสาร Vercel (อ่าน 2026-11-16 ก่อนทดสอบ):
- รองรับฟังก์ชันแบบไฟล์ใน `api/` สำหรับโปรเจกต์ที่มีอยู่; "Vercel Services" (Beta ทุก plan) เป็นอีกทางสำหรับรัน Python คู่เฟรมเวิร์กอื่น (ต้องเป็นแอป ASGI/WSGI และแยก `web/` กับ `pipeline/`)
- Hobby: body 4.5 MB, bundle Python 500 MB, รัน 300 วินาที, หน่วยความจำ 2 GB, Python 3.12 เป็นค่าเริ่มต้น (3.13 และ 3.14 ใช้ได้), ภูมิภาคเริ่มต้น `iad1`
- ฟังก์ชัน Python แพ็กทุกไฟล์ในโปรเจกต์ที่เข้าถึงได้ (ไม่มี tree-shaking) ต้องใช้ `excludeFiles`
- `/api/*` ชนกับ `app/api/*` ของ Next.js ได้ (รายงานชุมชน: 404) -> ห้ามมี `app/api/`

**แผน A (ใช้ก่อน):** ราก repo รวม Next.js + `api/*.py` + แพ็กเกจ `src/tmd_plain`
**แผน B (ถ้า spike ไม่ผ่าน):** Vercel Services แยก `web/` (Next.js) กับ `pipeline/` (Python) หรือรัน `/demo` ที่เครื่องตอนพรีเซนต์ (ต้องให้ผู้ใช้ตัดสินใจ)

### Spike ที่ต้องทำใน Phase 0 (ก่อนสร้างหน้า /demo)
1. `api/hello.py` นำเข้าแพ็กเกจของเราและ PyThaiNLP ได้ไหม (ยังไม่มีเอกสารยืนยันว่ารากโปรเจกต์อยู่ใน `sys.path`)
2. ขนาด bundle (ตั้ง `VERCEL_ANALYZE_BUILD_OUTPUT=1`) และเวลา cold start เมื่อรวม PyThaiNLP และ pypdfium2
3. Vercel ใช้ไฟล์ dependency ตัวไหนเมื่อมี `pyproject.toml` ที่ราก (และไม่มีข้อกำหนดซ้ำกับ `requirements.txt`)
4. หน้า Next.js ยังทำงานปกติ และ `PYTHAINLP_READ_ONLY=1` ทำให้ newmm ใช้ได้โดยไม่ดาวน์โหลดเพิ่ม
5. pypdfium2 และ pdfminer.six อ่านข้อความไทยจาก PDF จริงใน `data/raw/` ได้ดีแค่ไหน (เทียบกับข้อความที่ตรวจด้วยตา)
6. ภูมิภาค `sin1` เลือกได้บน Hobby ไหม

## 5. แคชและการอัปเดตข้อมูลโดยไม่ deploy ใหม่
- `lib/data/*` อ่าน Neon ด้วย `'use cache'` + `cacheTag('forecasts')` + `cacheLife('hours')` เป็นตาข่ายสำรอง
- สคริปต์โหลดข้อมูลเรียก `app/internal/revalidate/route.ts` (ตรวจ `REVALIDATE_SECRET`) ซึ่งเรียก `revalidateTag` (`updateTag` ใช้ได้เฉพาะ Server Action)
- ยืนยันแล้ว (4.1, 2026-11-17): ใช้ `revalidateTag('forecasts', { expire: 0 })` ตามเอกสารของ Next.js 16 ที่ติดตั้ง · บนเว็บจริง แก้แถวใน Neon แล้วเรียก route ล้างแคช หน้าเว็บเปลี่ยนทันทีโดยไม่ deploy ใหม่ (`docs/results/smoke-test.md`)

## 6. ตัวแปรสภาพแวดล้อม
`DATABASE_URL` (pooled, role `web_reader` อ่านอย่างเดียว, ฝั่งเว็บ; ตั้งใน Vercel แล้ว) · `DATABASE_URL_DIRECT` (role เจ้าของ เฉพาะเครื่องที่รันสคริปต์โหลด ห้ามใส่ใน Vercel) · `REVALIDATE_SECRET` (ทั้ง Vercel และเครื่องทีม) · `SITE_URL` (สคริปต์โหลดใช้เรียกล้างแคช) · `PYTHAINLP_READ_ONLY=1` และ `PYTHAINLP_DATA` ตั้งในโค้ดของ `api/summarize.py` เองแล้ว ไม่ต้องตั้งใน Vercel · ห้ามใส่ secret ใน `NEXT_PUBLIC_*`

## 7. รายการตั้งต้น (Phase 0)
**ทำครบแล้วใน Phase 0.1-0.5 (2026-11-16)** ยกเว้น `.claude/settings.json` (ทางเลือก ยังไม่ได้สร้าง) ผลตรวจอยู่ใน `ai/PROGRESS.md` รายการเดิมข้างล่างเก็บไว้เป็นประวัติ
- สร้างโปรเจกต์ Next.js (ได้ `AGENTS.md`) แล้วเพิ่ม `@AGENTS.md` บนสุดของ `.claude/CLAUDE.md`
- ตรึง TypeScript ที่ 6.0.x (typescript-eslint ยังไม่รับ 7)
- `.gitignore` สร้างแล้วที่ Root (2026-11-16) กัน `data/raw/` (เว้น README+MANIFEST), `data/excluded-scripted/`, `course/slides/`, `docs/research/tmd-digest/`, `.env*`, `.venv/`, `CLAUDE.local.md` ให้ตรวจเพิ่มเมื่อมีโค้ดจริง
- `.editorconfig` (UTF-8, LF), `vercel.json` (`excludeFiles` ต้องกันอย่างน้อย `docs/**`, `course/**`, `data/**`, `ai/plans/**`, `.claude/**`, `node_modules/**` ออกจากฟังก์ชัน Python, region)
- รากมีไฟล์อยู่แล้ว (.claude/CLAUDE.md, README.md, .gitignore, .claude/): ถ้า `create-next-app` ไม่ยอมสร้างในโฟลเดอร์ที่ไม่ว่าง ให้สร้างในโฟลเดอร์ชั่วคราวแล้วย้ายเฉพาะไฟล์ที่ได้มา **ห้ามเขียนทับ** .claude/CLAUDE.md, README.md, .gitignore (ผสานด้วยมือ)
- Tailwind 4: ราก repo มี md จำนวนมากใน `docs/`, `course/` ตั้ง `@source` ให้สแกนแค่ `app/`, `components/`, `lib/` (ไวยากรณ์ต้องยืนยันกับเอกสารของเวอร์ชันที่ติดตั้ง)
- ตั้งฟอนต์ Anuphan ใน `app/layout.tsx` และโทเคนใน `app/globals.css` ตาม `docs/spec/design-system.md` แล้วตรวจเรนเดอร์ตามหัวข้อ 7 ของไฟล์นั้น
- `.claude/settings.json` ตั้งให้ถามก่อน `git commit` และ `git push` (ทางเลือก ต้องทดสอบ hook บน Windows ก่อนใช้)
- กรอกคำสั่งจริงในหัวข้อ Commands ของ `.claude/CLAUDE.md`
- ทดสอบว่า path ที่มีภาษาไทย ช่องว่าง และเครื่องหมาย `&` ("NLP & ML Mini-Project") ใช้กับ Next.js build, npm scripts (บน Windows รันผ่าน cmd ซึ่ง `&` มีความหมายพิเศษ) และ Vercel CLI ได้ ถ้าไม่ได้ให้ผู้ใช้ย้ายหรือ clone repo ไป path สั้น (เช่น `C:\dev\tmd-plain-forecast`) ห้ามย้ายเอง
