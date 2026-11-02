# แผน 04: โหลดเข้า Neon ชั้นข้อมูล และหน้าหลัก `/`

**สถานะ (2026-11-17):** เสร็จครบ ผู้ใช้เซ็นปิดแล้ว · สคริปต์โหลดใน 4.1 เปลี่ยนจาก `scripts/load_to_neon.py` (psycopg) เป็น `npm run load:neon` (Node) ตาม ADR 0014 เพราะ psycopg ถูกบล็อกบนเครื่องทีม · ข้อความข้างล่างคือแผนเดิม

**เป้าหมาย:** หน้า `/` แสดงสรุปพยากรณ์รายวันและ 7 วันครบ 7 ภาค ย้อนหลัง 1 สัปดาห์ จาก Neon โดยอัปเดตข้อมูลได้โดยไม่ deploy ใหม่ และหน้าตาตาม `docs/design/DESIGN-expo.md`

**สเปก:** [../../docs/spec/ui-spec.md](../../docs/spec/ui-spec.md) · [../../docs/spec/design-system.md](../../docs/spec/design-system.md) · [../../docs/design/DESIGN-expo.md](../../docs/design/DESIGN-expo.md) (อ่านอย่างเดียว) · [../../docs/architecture.md](../../docs/architecture.md) หัวข้อ 5-6 · skill `frontend-responsive-ui` (+ `references/ui-checklist.md`), `nextjs-component-architecture` · กฎ `.claude/rules/frontend.md`

**ข้อจำกัดที่ใช้:** Server Component เป็นค่าเริ่มต้น `'use client'` เฉพาะใบล่างสุด · อ่าน DB และ `process.env` เฉพาะใน `lib/data/` · ห้ามมี `app/api/` (route handler ไว้ใต้ `app/internal/`) · ใช้โทเคนตามชื่อ ห้าม hex/ขนาด/รัศมีเอง · Anuphan · ทุกหน้าที่แสดงสรุปมี "ตัวช่วยสรุป ไม่ใช่ประกาศทางการ" และ "ที่มา: กรมอุตุนิยมวิทยา" · secret ห้ามขึ้นต้น `NEXT_PUBLIC_` · dependency ที่อยู่ใน ADR 0004 ใช้ได้ (Zod, `@neondatabase/serverless`, `clsx`, `tailwind-merge`, `class-variance-authority`, `lucide-react`, Vitest, Testing Library, Playwright) ตัวอื่นต้องขออนุญาต

**ทำก่อนท่อประมวลผลเสร็จได้:** 4.2 และ 4.3 ใช้ fixture จาก 1.1 (`tests/fixtures/contract/`) ได้ตั้งแต่หลัง 0.5 + 1.1 แล้วค่อยต่อข้อมูลจริงหลัง 3.4 + 4.1

---

## Phase 4.1: สคริปต์โหลดข้อมูล ชั้นข้อมูล และการล้างแคช   [M]   [เจ้าของ: ผู้ช่วย; ผู้ใช้ตั้ง env]

Goal: JSON จาก `data/processed/` เข้า Neon ด้วยคำสั่งเดียว เว็บอ่านผ่าน `lib/data/` ที่มีแคช และการโหลดใหม่ล้างแคชได้

Inputs
- `data/processed/` (3.4) หรือ fixture, `db/schema.sql` (0.4), `lib/contract/issue.schema.json` (1.1)

Tasks
1. `scripts/load_to_neon.py`: ตรวจทุกไฟล์กับโมเดล `Issue` → upsert ด้วย `DATABASE_URL_DIRECT` → เรียก `/internal/revalidate` พร้อม `REVALIDATE_SECRET`
2. `lib/contract/`: ชนิด TypeScript + Zod schema ของ `Issue` (สร้างจาก JSON Schema ด้วย `json-schema-to-typescript` ถ้าผู้ใช้อนุญาต dependency นี้ ไม่งั้นเขียน Zod เองแล้วให้เทสต์สัญญาตรวจว่าตรงกัน)
3. `lib/data/forecasts.ts` (`import 'server-only'`, `'use cache'` + `cacheTag('forecasts')` + `cacheLife('hours')` ตรวจรูปแบบ API จากเอกสารของ Next.js ที่ติดตั้ง): ฉบับล่าสุด, รายการรอบ 7 วันล่าสุด, ฉบับตาม id
4. `app/internal/revalidate/route.ts`: ตรวจ secret แล้ว `revalidateTag`
5. ติดตั้ง Vitest; `lib/**/*.test.ts`; เติม Commands ใน `.claude/CLAUDE.md`

Checks
- `npx vitest run` ผ่าน รวมเทสต์สัญญา: JSON ทุกไฟล์ใน `data/processed/` (หรือ fixture) ผ่าน Zod
- `python scripts/load_to_neon.py` สองครั้ง → จำนวนแถวเท่าเดิม (รายวัน 28 + 7 วัน 7 = 35 เมื่อใช้ข้อมูลจริง)
- `/internal/revalidate` ตอบ 401 เมื่อ secret ผิด และสำเร็จเมื่อถูก (ทดสอบบน dev server)
- `npx tsc --noEmit`, `npx eslint .`, `npm run build` → exit 0

Human steps: ใส่ `REVALIDATE_SECRET` ใน `.env` และใน Vercel

Out of scope: หน้าตา (4.2)

---

## Phase 4.2: เลย์เอาต์และมุมมองพยากรณ์รายวัน   [M]   [เจ้าของ: ผู้ช่วย]

Goal: หน้า `/` แสดงฉบับรายวันล่าสุดครบ 7 ภาค พร้อมแท็บภาค บนมือถือ แท็บเล็ต เดสก์ท็อป ตามมาตรฐานดีไซน์

Inputs
- ผลของ 0.5 และ 4.1 (หรือ fixture), `ui-spec.md` หัวข้อ 1, 3-5, `design-system.md` หัวข้อ 4-6

Tasks
1. `components/ui/`: Button, Card, Tabs, Badge, Alert, Skeleton (`cva` + `cn()` ใน `lib/`)
2. `components/layout/`: Header (`top-nav`, hamburger ต่ำกว่า 768), Footer (ข้อความสงวนสิทธิ์ + เครดิต + ลิงก์ TMD), Container (1200px), Hero แบบกระชับ (D7)
3. `components/features/`: ForecastCard, RegionTabs (ชิปเลื่อนแนวนอนบนมือถือ, พื้นที่กด 44px), DocTypeTabs, AdviceList (ป้าย "ข้อแนะนำทั่วไป"), Disclaimer
4. `lib/format/`: วันที่ไทย พ.ศ., ชื่อภาค (ฟังก์ชันบริสุทธิ์ + Vitest)
5. `app/page.tsx`: ดึงข้อมูลบนเซิร์ฟเวอร์ ส่ง props เล็กๆ ลงไป

Checks
- `npx vitest run`, `npx tsc --noEmit`, `npx eslint .`, `npm run build` → ผ่าน
- ภาพหน้าจอ 320 / 375 / 768 / 1280 px บรรยายตาม `ui-checklist.md` หัวข้อ 1-3 และ 6 (ไม่มี scroll แนวนอน, วรรณยุกต์ไม่ถูกตัด, พื้นที่กด, โฟกัสมองเห็น, ข้อความสงวนสิทธิ์)
- ค้นหา hex นอก `app/globals.css` → ไม่พบ · ไม่ใช้ `muted`/`semantic-error`/`semantic-success` เป็นสีข้อความ

Out of scope: ฉบับ 7 วัน ประวัติย้อนหลัง สถานะว่าง/ผิดพลาด (4.3)

---

## Phase 4.3: มุมมอง 7 วัน ประวัติย้อนหลัง สถานะ และเทสต์ end-to-end   [M]   [เจ้าของ: ผู้ช่วย; ผู้ใช้รีวิวหน้าเว็บ]

Goal: ผู้ใช้สลับรายวัน/7 วัน เลือกรอบหรือฉบับย้อนหลัง 1 สัปดาห์ และเห็นสถานะโหลด/ว่าง/ผิดพลาดที่บอกว่าต้องทำอะไร

Tasks
1. `components/features/`: RoundPicker (รายวัน 7 วัน x 4 รอบ ล่าสุดก่อน), รายการฉบับ 7 วัน, การแสดง `periods` ในการ์ด
2. สถานะ: `loading.tsx` (Skeleton), ไม่มีข้อมูล (บอกสาเหตุ), ผิดพลาด (`error.tsx` ปุ่มลองใหม่)
3. ตัดสินเลย์เอาต์การ์ด 7 ใบที่ 3 คอลัมน์ (ข้อเปิดใน `ui-spec.md` หัวข้อ 4) แล้วแก้ `ui-spec.md`
4. ติดตั้ง Playwright; `tests/e2e/home.spec.ts`: เห็น 7 ภาคของฉบับล่าสุด, สลับชนิด, เลือกรอบเก่า, โฟกัสภาคบนมือถือ, ใช้คีย์บอร์ดได้; เติม Commands

Checks
- `npx playwright test` ผ่าน · ทุกคำสั่งของ 4.2 ผ่าน
- ภาพหน้าจอของทุกสถานะ (ปกติ, กำลังโหลด, ว่าง, ผิดพลาด) ที่ 375 และ 1280 px ไล่ตาม `ui-checklist.md` ครบทุกหัวข้อ
- ลองโหลดข้อมูลใหม่ด้วย `load_to_neon.py` แล้วหน้าเปลี่ยนโดยไม่ build ใหม่ (บน dev server/`next start`)

Human steps: ผู้ใช้รีวิวหน้าเว็บจากภาพหน้าจอ เลือกเลย์เอาต์การ์ด 7 ใบ แล้วเซ็นปิด

Out of scope: `/demo` (แผน 05)
