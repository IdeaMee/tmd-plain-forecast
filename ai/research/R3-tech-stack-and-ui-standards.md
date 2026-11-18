# R3 — Tech stack และมาตรฐาน UI (research only)

> วันที่ค้นคว้า: 2026-11-16 · ทุกเวอร์ชันมาจาก npm registry / PyPI ณ วันนี้ หรือจากเอกสารทางการ (ระบุ URL + วันที่ของหน้า) · ข้อที่ยืนยันไม่ได้จะใส่ **[unverified]**
> ไม่ได้ติดตั้งอะไร ไม่ได้สร้างบัญชี ไม่ได้แตะ git ไม่ได้เข้า tmd.go.th

---

## 0. สรุปสั้น (อ่านอันนี้ก่อน)

1. **Next.js 16.4.6 + React 19.3.1** คือ stable ล่าสุด ตั้งแต่ 16.4 `create-next-app` เปิด **Cache Components** เป็นค่าเริ่มต้น โจทย์ "DB เปลี่ยนแล้วเว็บโชว์ข้อมูลใหม่โดยไม่ต้อง redeploy" ทำได้ด้วย `'use cache'` + `cacheTag` + `cacheLife` แล้วให้ pipeline เรียก Route Handler ที่สั่ง `revalidateTag(tag, 'max')` (หรือใช้ `cacheLife('hours')` อย่างเดียวก็พอ)
2. **ห้ามใช้ TypeScript 7 (ตัวที่ npm ให้เป็น `latest`)** เพราะ `typescript-eslint` 8.72.2 (ซึ่ง `eslint-config-next` ใช้) ยังรับ TypeScript แค่ `>=4.8.4 <6.1.0` → ให้ pin **TypeScript 6.0.3**
3. **PyMuPDF 2.x (2.0 วันที่ 2026-10-19, 2.1 วันที่ 2026-11-02) ตาม metadata บน PyPI มีการบังคับติดตั้ง `onnxruntime`, `numpy`, `networkx`, `pymupdf-layout`, `pymupdf4llm` ด้วย** และเป็น **AGPL-3.0** → ไม่เหมาะกับ Vercel function สาธารณะ แนะนำ **pypdfium2 (BSD-3/Apache-2.0, wheel ~4 MB)** เป็นตัวหลัก และ pdfplumber/pdfminer.six (MIT) เป็นตัวสำรอง/ตัวเทียบ
4. **Vercel Python + Next.js ในโปรเจกต์เดียว:** เอกสารปัจจุบันแนะนำ **Vercel Services (Beta, ใช้ได้ทุก plan)** ส่วนแบบไฟล์ `/api/*.py` เดิมยังมีเอกสารอยู่ แต่ระบุว่าเป็นของ "existing projects" ขีดจำกัดของ Hobby คือ body ≤ **4.5 MB**, max duration **300 s**, memory **2 GB**, bundle Python ≤ **500 MB**
5. **Neon Free:** **1 GB storage/project**, **100 CU-hours/project/เดือน**, scale-to-zero หลังว่าง **5 นาที (ปิดไม่ได้)**, egress **5 GB/project/เดือน** มี region **Singapore** (`aws-ap-southeast-1`)
6. **Thai UI:** ใช้ `next/font/google` ได้ทั้ง Noto Sans Thai (variable), IBM Plex Sans Thai (static), Sarabun (static) ซึ่งทุกตัวมี subset `thai` ควรตั้ง `line-height` ราว 1.6–1.8 สำหรับเนื้อความ (WCAG 1.4.12 ต้องรับได้ถึง 1.5) ห้ามใส่ `letter-spacing` กับข้อความไทย และอย่าใช้ `word-break: break-all` กับไทย

---

## 1. Web stack

### 1.1 Next.js / React / TypeScript

| รายการ | ข้อเท็จจริง | แหล่งอ้างอิง |
|---|---|---|
| Next.js stable | `16.4.6` (dist-tag latest, ออก 2026-11-09), `engines.node >=20.9.0` เครื่องเรามี Node 24.19 จึงใช้ได้ | https://registry.npmjs.org/next/latest |
| Next.js 16.4 | ออก 2026-10-06 มากับ React 19.3 Cache Components เป็นค่าเริ่มต้นใน `create-next-app` จะเป็น default ทุกแอปใน Next 17 | https://nextjs.org/blog/next-16-4 |
| Security cadence | มี security release รายเดือน (ล่าสุดคือ November 2026 Security Release เมื่อ 2026-11-03) → **ต้องคอยอัปเดต patch** | https://nextjs.org/blog |
| React | `19.3.1` (2026-10-14) | https://registry.npmjs.org/react/latest |
| `next lint` | **ถูกลบตั้งแต่ Next 16** ให้ใช้ ESLint CLI + flat config แทน | https://nextjs.org/docs/app/api-reference/config/eslint (lastUpdated 2026-10-15) |
| TypeScript latest | `7.0.2` (2026-07-08, native Go compiler) ส่วน 6.0 คือรุ่นสุดท้ายที่เป็น JS (6.0.3 คือ 6.x ล่าสุด) | https://registry.npmjs.org/-/package/typescript/dist-tags , https://devblogs.microsoft.com/typescript/ |
| Next + TS 7 | `next build` ใช้ `tsc` CLI ตามค่าเริ่มต้น จึงรองรับ TS 6 และเปิดใช้ TS 7 ได้ | https://nextjs.org/docs/app/api-reference/config/next-config-js/useTypeScriptCli (lastUpdated 2026-08-03) |
| **ปัญหา TS 7 กับ lint** | `typescript-eslint@8.72.2` มี peer เป็น `typescript: ">=4.8.4 <6.1.0"` และ `eslint-config-next@16.4.6` ก็พึ่ง `typescript-eslint ^8.56.0` → **ให้ pin `typescript@~6.0.3`** | https://registry.npmjs.org/typescript-eslint/latest , https://registry.npmjs.org/eslint-config-next/latest |

**ฟีเจอร์ที่เราจะพึ่ง**
- **App Router + Server Components:** อ่าน DB ตรงใน async Server Component ได้เลย (ตัวอย่างใน blog ของ 16.4 query DB ภายใน component ที่มี `'use cache'`) — https://nextjs.org/blog/next-16-4
- **Cache Components** (`cacheComponents: true`, `partialPrefetching: true` ใน `next.config.ts`) — https://nextjs.org/docs/app/getting-started/caching (lastUpdated 2026-10-06)
  - `'use cache'` ใช้ได้ทั้งระดับ data function และระดับ component แนะนำให้คู่กับ `cacheLife` ทุกครั้ง
  - ถ้าไม่ cache ต้องห่อด้วย `<Suspense>` แล้วข้อมูลจะ stream ตอน request
  - **cache ผูกกับ deployment:** deploy ใหม่ = cache ว่าง (เพราะ build id อยู่ใน cache key)
  - cache แบบ in-memory ใน serverless อาจไม่คงอยู่ข้าม instance ต้องใช้ `'use cache: remote'` ถ้าอยากได้ cache ที่แชร์กัน
- **Revalidation** — https://nextjs.org/docs/app/getting-started/revalidating (lastUpdated 2026-06-25)
  - profile ของ `cacheLife`: `minutes` (revalidate 1m), `hours` (revalidate 1h, expire 1d), `days`, `max` (revalidate 30d)
  - `revalidateTag(tag, 'max')` = stale-while-revalidate **เรียกจาก Route Handler ได้** (เหมาะกับ webhook)
  - `updateTag` = หมดอายุทันที **แต่ใช้ได้เฉพาะใน Server Actions**
  - หน้า docs แนะนำรูปแบบนี้ตรงๆ: ใช้ `cacheTag` + `cacheLife('max')` แล้วให้แหล่งข้อมูลยิง webhook มาเรียก `revalidateTag`
- **แนวทางของเรา (ข้อเสนอ):** ทุก query ของข้อมูลพยากรณ์ใส่ `'use cache'` + `cacheTag('forecast')` + `cacheLife('hours')` แล้ว loader ฝั่ง Python ยิง `POST /api/revalidate` (มี secret ใน header) ซึ่งเรียก `revalidateTag('forecast','max')` ถ้า webhook พลาด ข้อมูลก็จะสดภายใน 1 ชม. อยู่ดี และ **ไม่ต้อง redeploy**
- ถ้าไม่เปิด Cache Components ก็ต้องดูคู่มือ "Previous Model" แยกต่างหาก — https://nextjs.org/docs/app/guides/caching-without-cache-components **[unverified: ไม่ได้อ่านหน้านี้]**

### 1.2 Tailwind CSS v4

| รายการ | ข้อเท็จจริง | แหล่ง |
|---|---|---|
| เวอร์ชัน | `tailwindcss 4.3.5`, `@tailwindcss/postcss 4.3.5` (2026-11-06) | npm registry |
| ติดตั้งกับ Next | `npm i tailwindcss @tailwindcss/postcss postcss` → `postcss.config.mjs` ใช้ plugin `"@tailwindcss/postcss"` → ใส่ `@import "tailwindcss";` ใน `app/globals.css` (**ไม่มี `tailwind.config.js` แล้ว**) | https://tailwindcss.com/docs/installation/framework-guides/nextjs |
| Breakpoints ค่าเริ่มต้น | `sm` 40rem/640px · `md` 48rem/768px · `lg` 64rem/1024px · `xl` 80rem/1280px · `2xl` 96rem/1536px (min-width, mobile-first) | https://tailwindcss.com/docs/responsive-design (v4.3) |
| ปรับ breakpoint | ใช้ CSS `@theme { --breakpoint-xs: 30rem; }`, ตั้ง `initial` เพื่อลบ, `--breakpoint-*: initial` เพื่อล้างทั้งหมด และควรใช้หน่วย rem ให้เหมือนกันทั้งหมด | เดียวกัน |
| Container queries | มีในตัว: `@container`, `@md:` ฯลฯ | เดียวกัน |
| เบราว์เซอร์ขั้นต่ำ | **Chrome 111, Safari 16.4, Firefox 128** (v4 "designed for modern browsers") | https://tailwindcss.com/docs/compatibility |

> ความเสี่ยง: มือถือ Android/iOS รุ่นเก่ามากที่ยังใช้ Safari < 16.4 จะแสดงผลเพี้ยน เราจะยอมรับความเสี่ยงนี้สำหรับงานรายวิชา

### 1.3 Lint / Format

| ตัวเลือก | เวอร์ชัน | หมายเหตุ | แหล่ง |
|---|---|---|---|
| ESLint (flat config) | `eslint 10.15.0`, `eslint-config-next 16.4.6` | ใช้ `eslint.config.mjs` + `defineConfig([...nextVitals, ...nextTs])` ตัว `eslint-config-next` รองรับ ESLint 9 และ 10 (ESLint 10 ต้องใช้ Node `^20.19 / ^22.13 / >=24`) **บาง plugin ยังไม่ประกาศ peer ESLint 10 อาจมี warning** | https://nextjs.org/docs/app/api-reference/config/eslint |
| Biome | `@biomejs/biome 2.6.8` (2026-11-15) | เร็ว ตัวเดียวทำได้ทั้ง lint+format แต่ไม่มีกฎเฉพาะ Next (`@next/next/*`) และกฎเรียง Tailwind class `useSortedClasses` **ยังอยู่ใน nursery** | https://biomejs.dev/linter/rules/use-sorted-classes (ข้อมูล nursery มาจากผลค้นหา) |
| Prettier | `prettier 3.10.1`, `prettier-plugin-tailwindcss 0.8.1` | สำหรับ v4 ให้ตั้ง `"tailwindStylesheet": "./app/globals.css"` และ `"tailwindFunctions": ["clsx","cn","cva"]` ต้องวาง plugin นี้ **ไว้ท้ายสุด** ใน `plugins` | https://github.com/tailwindlabs/prettier-plugin-tailwindcss |
| ESLint + Prettier | ใช้ `eslint-config-prettier/flat` | https://nextjs.org/docs/app/api-reference/config/eslint |

**ข้อเสนอ:** ใช้ **ESLint (eslint-config-next) + Prettier + prettier-plugin-tailwindcss** เพราะได้กฎของ Next/React Hooks/Core Web Vitals และเรียง class Tailwind v4 ได้ตามเอกสารทางการ ส่วน Biome ทำงานได้ดี แต่จะเสียกฎเฉพาะ Next

### 1.4 สร้าง component เอง (ไม่ใช้ shadcn)

| แพ็กเกจ | เวอร์ชัน (วันออก) | บทบาท |
|---|---|---|
| `clsx` | 2.1.1 (2024-04-23) | ต่อ className แบบมีเงื่อนไข |
| `tailwind-merge` | 3.7.0 (2026-09-12) — มี dist-tag `tailwind-merge-2` = 2.6.1 แยกไว้ให้ v3 | ใช้ merge class ที่ชนกัน (รวมกับ clsx เป็นฟังก์ชัน `cn()`) |
| `class-variance-authority` | 0.7.1 (2024-11-26) | ใช้นิยาม variant (size/intent) ของ Button/Badge **ไม่ได้ออกรุ่นใหม่มาเกือบ 2 ปี** แต่ API เล็กและนิ่ง |
| `lucide-react` | 1.73.0 (2026-11-14) | ไอคอน (tree-shakable) |

แหล่ง: npm registry (`https://registry.npmjs.org/<pkg>`) ข้อที่ว่า tailwind-merge 3.x ตรงกับ Tailwind v4 อนุมานจาก dist-tag `tailwind-merge-2` ที่ทำไว้สำหรับ v3 **[unverified: ไม่ได้อ่าน README]**

### 1.5 Validation / Testing

| รายการ | เวอร์ชัน | หมายเหตุ | แหล่ง |
|---|---|---|---|
| Zod | 4.6.7 (2026-10-12) | ใช้ validate แถวข้อมูลจาก DB และ input ของ API | npm |
| Vitest | 5.1.0 (2026-11-02) | ชุดที่ Next แนะนำ: `vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/dom vite-tsconfig-paths` **Vitest ยังไม่รองรับ async Server Components** → ให้ทดสอบส่วนนั้นด้วย E2E | https://nextjs.org/docs/app/guides/testing/vitest (lastUpdated 2026-08-25) |
| Testing Library | `@testing-library/react 16.3.3`, `@testing-library/jest-dom 7.0.1`, `jsdom 31.0.1`, `@vitejs/plugin-react 6.3.0` | | npm |
| Playwright | `@playwright/test 1.65.1` (2026-11-13) | `toHaveScreenshot()` ต้องสร้าง baseline ใน environment เดียวกับที่ใช้รันทดสอบ เพราะการ render ต่างกันตาม OS (ชื่อไฟล์มี `-chromium-win32` ฯลฯ) ตั้ง viewport ได้ทั้งระดับ project (`devices['iPhone 13']`, `viewport: {width,height}`) และใน test (`test.use({ viewport })`) | https://playwright.dev/docs/test-snapshots , https://playwright.dev/docs/emulation |

> ข้อเสนอ: ทำ screenshot test ที่ 3 ความกว้าง: **375** (มือถือ), **768** (แท็บเล็ต), **1280** (เดสก์ท็อป) และ **320** เพื่อเช็ก WCAG Reflow ส่วน baseline ให้สร้างบน CI (Linux) อย่างเดียว อย่าปนกับที่สร้างบน Windows

### 1.6 ฟอนต์ไทยผ่าน `next/font`

`next/font/google` จะดาวน์โหลดฟอนต์มา self-host ตอน build ทำให้ **เบราว์เซอร์ไม่ต้องยิง request ไป Google** ถ้าเป็นฟอนต์ที่ไม่ใช่ variable ต้องระบุ `weight` เอง — https://nextjs.org/docs/app/getting-started/fonts (lastUpdated 2026-05-27)

ข้อมูลด้านล่างมาจาก `font-data.json` ใน `next@16.4.6` (https://unpkg.com/next@16.4.6/dist/compiled/@next/font/dist/google/font-data.json):

| ฟอนต์ | subsets | weights | Variable? |
|---|---|---|---|
| **Noto Sans Thai** | latin, latin-ext, **thai** | 100–900 | ✅ (wght 100–900, wdth 62.5–100) |
| **IBM Plex Sans Thai** | cyrillic-ext, latin, latin-ext, **thai** | 100–700 | ❌ ต้องระบุ weight เช่น `['400','600']` |
| **Sarabun** | latin, latin-ext, **thai**, vietnamese | 100–800 | ❌ |
| Noto Sans Thai Looped | latin, latin-ext, thai | 100–900 | ✅ |
| Anuphan | latin, latin-ext, thai, vietnamese | 100–700 | ✅ (wght) |
| Noto Serif Thai / Prompt / Kanit / IBM Plex Sans Thai Looped | มี thai ทุกตัว | — | Noto Serif Thai = ✅ ส่วนตัวอื่น ❌ |

ข้อเสนอ: ใช้ **Noto Sans Thai (variable)** หรือ **Anuphan (variable)** เป็นตัวหลัก เพราะได้ทุก weight จากไฟล์เดียว ใส่ `subsets: ['thai','latin']` และ `variable: '--font-sans'` แล้ว map ใน Tailwind ด้วย `@theme { --font-sans: var(--font-sans), ... }` **[unverified: ไม่ได้ลองรูปแบบ map ตัวแปรนี้จริง]**

---

## 2. การเข้าถึง DB จาก Next.js บน Vercel

### 2.1 ตัวเลือก driver/ORM

| ตัวเลือก | เวอร์ชัน | ข้อดี / ข้อเสีย สำหรับแอปเล็กที่เน้นอ่าน | แหล่ง |
|---|---|---|---|
| **`@neondatabase/serverless`** (`neon()` แบบ HTTP) | 1.2.1 (2026-11-13) | ไม่มี dependency หนัก ตั้ง connection ราว 3 roundtrip เหมาะกับ query เดี่ยวที่ไม่ใช่ interactive transaction ตั้งแต่ 1.0.0 เป็น tagged-template อย่างเดียว (กัน SQL injection) ต้องใช้ Node 19+ | https://neon.com/docs/serverless/serverless-driver (2026-10-05) |
| `pg` / postgres.js ผ่าน TCP + pool | `postgres 4.1.1` | Neon บอกว่าบน **Vercel Fluid compute** แบบ TCP + pool คือ "the new fastest and most robust" (handshake ราว 8 roundtrip แต่จ่ายครั้งเดียว) ใช้คู่ `attachDatabasePool` จาก `@vercel/functions` และแนะนำให้ benchmark เอง | https://neon.com/docs/guides/vercel-connection-methods (2026-06-05) |
| Drizzle ORM | `drizzle-orm 0.45.4` (latest) แต่ docs ตอนนี้สั่ง `drizzle-orm@rc` (`1.0.0-rc.5`) | type-safe และเบา แต่ **กำลังเปลี่ยนจาก 0.x ไป 1.0** (docs กับ latest ไม่ตรงกัน) → เสี่ยง API เปลี่ยน | https://orm.drizzle.team/docs/connect-neon , npm dist-tags |
| Prisma | `@prisma/client 7.10.1` (stable) ส่วน dist-tag `latest` ของแพ็กเกจ `prisma` ชี้ไปที่ **`8.0.0-rc.33`** (แปลก ต้องระวังตอนติดตั้ง) | Prisma 7 เลิกใช้ Rust ทำให้ bundle เล็กลงมาก แต่ต้องมี adapter, `prisma.config.ts`, generate step และไม่โหลด `.env` ให้อัตโนมัติ → **เกินความจำเป็น** สำหรับไม่กี่ตาราง | npm dist-tags; สรุป Prisma 7 จากผลค้นหา https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7 **[unverified detail]** |

**ข้อเสนอ:** ใช้ **`@neondatabase/serverless` (HTTP `neon()`) + SQL ที่เขียนเอง + Zod parse ผลลัพธ์** เพราะง่ายที่สุดและไม่มีขั้น build/generate เนื่องจากหน้าเว็บส่วนใหญ่ถูก cache ด้วย `'use cache'` อยู่แล้ว จำนวนครั้งที่ query จริงจึงน้อย ทำให้เรื่อง cold-start ของ connection แทบไม่มีผล

### 2.2 Migrations และ pooling
- **Pooling ของ Neon:** เป็น PgBouncer แบบ transaction mode ใช้ hostname ที่มี `-pooler` รับได้ถึง 10,000 client connections ใน transaction mode จะใช้ `SET`, `LISTEN/NOTIFY`, SQL-level `PREPARE`, temp table ไม่ได้ (protocol-level prepared statement ใช้ได้) — https://neon.com/docs/connect/connection-pooling (2026-11-14)
- **Migration / bulk load ให้ใช้ direct connection (ไม่มี `-pooler`)** ตามคำแนะนำของ Neon (schema migrations, pg_dump/restore) — แหล่งเดียวกัน
- ข้อเสนอ: เก็บ migration เป็นไฟล์ `.sql` ที่มีเลขลำดับ (`db/migrations/001_init.sql`) แล้วรันด้วยสคริปต์ Python (`psycopg 3.3.9`, LGPL-3.0-only ซึ่งใช้เป็น library ได้) ผ่าน direct URL ฝั่งเว็บใช้ pooled URL แบบอ่านอย่างเดียว ถ้าอยากได้ ORM ค่อยใช้ drizzle-kit ทีหลัง

### 2.3 Neon Free plan (https://neon.com/pricing, หน้าอัปเดต 2026-11-04)

| ข้อจำกัด | Free |
|---|---|
| ราคา | $0 ตลอด ไม่ต้องใช้บัตร |
| Projects | 100 |
| Branches | 10 / project |
| Compute | **100 CU-hours / project / เดือน**, autoscale ได้ถึง 2 CU (8 GB RAM) |
| Scale-to-zero | **หลังว่าง 5 นาที ปิดไม่ได้** (request แรกหลัง suspend จะช้ากว่าปกติ) |
| Storage | **1 GB / project** (รวมทุก project ได้ 20 GB) ถ้าเกิน **write จะถูกบล็อก** |
| Egress | **5 GB / project / เดือน** ถ้าเกิน compute จะถูก suspend จนถึงรอบบิลถัดไป (ข้อมูลไม่หาย) |
| History / restore | 6 ชม. (จำกัด 1 GB), manual snapshot 1 ชุด |
| Region | มี **Asia Pacific (Singapore) `aws-ap-southeast-1`** — https://neon.com/docs/introduction/regions (2026-10-14) |

> ข้อสังเกต: ข้อมูลพยากรณ์แบบ text + JSON ของเรามีแค่หลัก MB/เดือน จึงห่าง 1 GB มาก และ `'use cache'` ช่วยลดทั้ง CU-hours และ egress

---

## 3. ฝั่ง Python

### 3.1 เครื่องมือ (PyPI ณ 2026-11-16 — https://pypi.org/pypi/<pkg>/json)

| เครื่องมือ | เวอร์ชัน (วันออก) | License | หมายเหตุ |
|---|---|---|---|
| uv | 0.13.8 (2026-11-12) | MIT/Apache-2.0 | Vercel รองรับ `pyproject.toml` + `uv.lock` แล้ว (ดู 3.4) ข้อดีเทียบกับ pip คือมี lockfile และเร็ว |
| Ruff | 0.17.5 (2026-11-12) | MIT | lint+format ตัวเดียว (แทน flake8/black/isort) |
| pytest | 9.2.0 (2026-10-27) | MIT | ต้องใช้ Python ≥3.10 |
| Pydantic | 2.14.3 (2026-11-05) | MIT | ใช้เป็น schema ของ JSON output ให้ตรงกับ Zod ฝั่งเว็บ |
| mypy | **2.4.1** (2026-10-28) | MIT | ตอนนี้เป็น major 2 แล้ว |
| pyright | 1.1.414 (2026-09-10) | MIT | ตัวบน PyPI ต้องมี Node (nodeenv) |
| pre-commit | 4.7.0 (2026-10-12) | MIT | ไม่บังคับ ต้องใช้ Python ≥3.11 |
| FastAPI | 0.163.1 (2026-11-15) | MIT | ถ้าจะทำ /demo เป็น ASGI app |
| psycopg | 3.3.9 (2026-11-12) | LGPL-3.0-only | ใช้สำหรับ loader |

### 3.2 PyThaiNLP
- เวอร์ชัน **5.4.0** (2026-10-09), Apache-2.0, ต้องใช้ Python ≥3.9 — https://pypi.org/project/pythainlp/ , https://github.com/PyThaiNLP/pythainlp/releases
- **ตอนติดตั้งพื้นฐานไม่มี dependency บังคับเลย** (มีแค่ `tzdata` บน Windows) ของหนักอย่าง torch/transformers อยู่ใน extras ทั้งหมด → **ติดตั้งเบา**
- ขนาด: wheel ราว **21.9 MB** (PyPI) ส่วนที่ติดตั้งในเครื่องเรา (5.4.0) วัดได้ **68.3 MB** ไฟล์ใหญ่ใน `corpus/` เช่น `wikipedia_titles_th.txt` 12.5 MB, `wordnet_th.db` 11.2 MB → ใส่ `excludeFiles` ตัด corpus ที่ไม่ใช้ได้ แต่ **ต้องทดสอบว่า newmm ยังทำงาน** **[unverified ว่าตัดไฟล์ไหนได้บ้าง]**
- Data dir ค่าเริ่มต้นคือ `~/pythainlp-data` ตั้งค่าใหม่ได้ด้วย `PYTHAINLP_DATA` มี `PYTHAINLP_OFFLINE=1` และ **`PYTHAINLP_READ_ONLY=1`** (ปิดการเขียน/ดาวน์โหลด/สร้างโฟลเดอร์อัตโนมัติ) — คำอธิบายบน PyPI ของ 5.4.0
- บน Vercel ระบบไฟล์เป็น read-only เขียนได้แค่ `/tmp` (ราว 500 MB ตามผลค้นหาที่อ้างถึง Vercel runtimes docs) → ตั้ง `PYTHAINLP_READ_ONLY=1` และ `PYTHAINLP_DATA=/tmp/pythainlp-data` **[unverified: ยังไม่ได้ทดสอบบน Vercel และยังไม่ได้เปิดหน้า Vercel ที่ระบุตัวเลข /tmp โดยตรง]**
- ช่วยแก้ปัญหา text จาก PDF: `pythainlp.util.normalize()` = `remove_zw` + `remove_dup_spaces` + `remove_spaces_before_marks` + `remove_repeat_vowels` + `remove_dangling` ส่วน `reorder_vowels()` แก้ลำดับวรรณยุกต์/สระ และ "Nikhahit + Sara Aa → Sara Am" — https://pythainlp.org/dev-docs/api/util.html (dev docs, commit 269d0f9)

### 3.3 การดึงข้อความไทยจาก PDF

| Library | เวอร์ชัน | License | ขนาด (wheel linux x86_64) | Dependencies | หมายเหตุ |
|---|---|---|---|---|---|
| **PyMuPDF** | **2.1** (2026-11-02) | **AGPL-3.0 หรือ Artifex commercial** | ~69 MB | **2.x บังคับ: `onnxruntime` (~28 MB wheel), `numpy` (~16 MB), `networkx`, `pyyaml`, `psutil`, `tabulate`, `pymupdf-layout`, `pymupdf4llm`** | 1.28.2 (2026-08-06) ไม่มี dep และ wheel ~26 MB ในเครื่องเราติดตั้ง 1.28.2 ไว้ (55.4 MB) |
| **pypdfium2** | 5.15.2 (2026-11-09) | BSD-3-Clause, Apache-2.0 | ~4 MB | ไม่มี | ใช้ engine PDFium (ของ Chrome) แต่ไม่วิเคราะห์ layout และขึ้นบรรทัดด้วย CRLF |
| pypdf | 7.1.0 (2026-11-13) | BSD-3-Clause | ~0.4 MB | ไม่มี (pure Python) | |
| pdfminer.six | 20260107 | MIT | ~6.6 MB | `charset-normalizer`, `cryptography` | |
| pdfplumber | 0.11.10 (2026-06-15) | MIT | 0.06 MB + deps | `pdfminer.six`, `Pillow`, `pypdfium2` | ดึงตารางได้ดี |

แหล่ง: PyPI JSON; changelog PyMuPDF https://pymupdf.readthedocs.io/en/latest/changes.html (2.0 ใช้ MuPDF 1.28.5, 2.1 ใช้ 1.28.6 และใน 2.1 แก้ "layout was eagerly initialized on import"); pypdfium2 API https://pypdfium2.readthedocs.io/en/stable/python_api.html

**License ของ PyMuPDF:** เป็น dual license "AGPL หรือ commercial" ถ้าทำตาม AGPL ไม่ได้ต้องซื้อ commercial license จาก Artifex — https://pymupdf.readthedocs.io/en/latest/about.html ส่วน AGPL §13 (Remote Network Interaction) กำหนดว่า **ถ้าเราแก้ไขโปรแกรมแล้วเปิดให้คนใช้ผ่านเครือข่าย ต้องให้ผู้ใช้ดาวน์โหลด source ได้ฟรี** — https://www.gnu.org/licenses/agpl-3.0.en.html ผลต่อเรา: ถ้า repo เป็น public และเปิด source ทั้งหมดภายใต้ license ที่เข้ากับ AGPL ได้ ก็น่าจะทำตามได้ แต่โค้ดทั้ง service ที่ link กับ PyMuPDF จะต้องเป็น AGPL ด้วย **[unverified: ไม่ใช่คำปรึกษาทางกฎหมาย]** → **เลี่ยงไปเลยจะง่ายกว่า**

**ปัญหาที่รู้กันของ PDF ภาษาไทย** (ทุก library เจอได้ ขึ้นกับว่าใน PDF ฝังฟอนต์อะไรไว้):
1. **อักขระ PUA (U+F700–U+F71A)** ฟอนต์ไทยรุ่นเก่าบน Windows ที่ไม่มีตาราง GSUB/GPOS จะ map วรรณยุกต์/สระที่ถูกเลื่อนตำแหน่งไปไว้ใน Private Use Area ทำให้ text ที่ดึงออกมามีอักขระแปลกปน หรืออักขระหายไป — https://www.unicode.org/mail-arch/unicode-ml/y2003-m04/0411.html (2003), โปรเจกต์ https://github.com/bact/constitution (ต้องสร้างตาราง map PUA กลับเป็นอักขระปกติ)
2. **ลำดับวรรณยุกต์กับสระสลับกัน** (วรรณยุกต์มาก่อนสระบน) — ตัวอย่างใน bact/constitution แก้ได้ด้วย `pythainlp.util.reorder_vowels`
3. **สระอำแตก** เป็น `ํ` (U+0E4D) + `า` (U+0E32) ซึ่ง CSS Text 3 เองก็ระบุว่าต้องแยก U+0E33 แบบนี้ตอนทำ letter-spacing — https://www.w3.org/TR/css-text-3/ แก้ได้ด้วย `normalize`/`reorder_vowels`
4. **PDF ที่เป็นภาพสแกน** ไม่มี text layer ต้องทำ OCR (อยู่นอกขอบเขต)
- ไม่พบ issue เฉพาะเรื่อง Thai ของ pypdf/pdfminer **[unverified: ต้องทดสอบกับ PDF จริงของกรมอุตุฯ ที่มีอยู่ใน dataset-raw]**

**ข้อเสนอ:** เขียน `extract_text(pdf) -> str` ที่ **ลอง pypdfium2 ก่อน แล้ว fallback ไป pdfminer.six** จากนั้นผ่าน `thai_fix()` = map PUA → `unicodedata.normalize('NFC')` → `pythainlp.util.normalize()` แล้วทำ golden test โดยเทียบกับข้อความที่คนพิมพ์ไว้จาก PDF ตัวอย่าง 5–10 ไฟล์ ให้รันกับ PyMuPDF 1.28.2 ในเครื่องเพื่อเทียบเท่านั้น ห้ามเอาขึ้น deploy

### 3.4 Vercel Python runtime

| รายการ | ค่า | แหล่ง |
|---|---|---|
| Python versions | **3.12 (default)**, 3.13, 3.14 กำหนดได้ผ่าน `pyproject.toml` / `.python-version` / `Pipfile.lock` | https://vercel.com/docs/functions/runtimes/python (2026-08-12) |
| Dependencies | `pyproject.toml` (มีหรือไม่มี `uv.lock` ก็ได้), `requirements.txt`, `Pipfile`+lock | เดียวกัน |
| Entrypoint | `app.py/index.py/server.py/main.py/...` หรือ `[tool.vercel] entrypoint = "pkg.mod:app"` ต้องมีตัวแปร `app` (ASGI/WSGI) | เดียวกัน |
| ไม่มี tree-shaking | ไฟล์ที่เข้าถึงได้จะถูกรวมเข้า bundle ทั้งหมด ใช้ `excludeFiles` ใน `vercel.json` ช่วยตัด | เดียวกัน |
| Bundle size | **500 MB uncompressed** (Python) ส่วน Node คือ 250 MB มี Large Functions (beta) ได้ถึง 5 GB | https://vercel.com/docs/functions/limitations (2026-08-24) |
| Max duration (Hobby) | **300 s ทั้งค่าเริ่มต้นและสูงสุด** | เดียวกัน |
| Memory (Hobby) | **2 GB / 1 vCPU** (ปรับไม่ได้) | เดียวกัน |
| **Request body** | **4.5 MB** ถ้าเกินได้ `413 FUNCTION_PAYLOAD_TOO_LARGE` | เดียวกัน |
| Region | ค่าเริ่มต้น `iad1` (US East) เปลี่ยนได้ | เดียวกัน |
| `/api/*.py` แบบเดิม | ยังรองรับใน "existing projects" (handler แบบ `app` / `application` / `BaseHTTPRequestHandler`) แต่ถ้าโปรเจกต์ใหม่ต้องการรันคู่กับ framework อื่น เอกสารแนะนำให้ใช้ **Services** | https://vercel.com/docs/functions/runtimes/python/api-directory (2026-08-12) |
| **Services** | **Beta ใช้ได้ทุก plan** นิยามใน `vercel.json` ด้วย `"services": {...}` + `rewrites` (เช่น `/api/py/(.*)` → backend, `/(.*)` → Next) แต่ละ service build แยกกัน คิดเงินเหมือน Functions (Hobby ได้ service requests ฟรี 1M) และเมื่อมี `services` แล้ว **ห้ามใส่ `functions`/`buildCommand`/`framework` ไว้ระดับบนสุด** | https://vercel.com/docs/services (2026-08-10), https://vercel.com/docs/services/pricing (2026-08-31) |

**Vercel Hobby โดยรวม** (https://vercel.com/docs/plans/hobby, 2026-11-12): invocations 1M, Active CPU 4 CPU-hrs, Provisioned Memory 360 GB-hrs, Fast Data Transfer 100 GB, deployments 100/วัน, runtime logs เก็บ 1 ชม. ถ้าใช้เกินต้องรอ 30 วัน

---

## 4. CI / Repo tooling

| รายการ | ข้อเท็จจริง | แหล่ง |
|---|---|---|
| GitHub Actions | **repo public: standard runner ฟรี ไม่นับโควตา** ส่วน private บน GitHub Free ได้เครดิต $12/เดือน (≈2,000 นาที Linux), artifact 500 MB, cache 10 GB/repo Windows แพงกว่า Linux ราว 1.7 เท่า | https://docs.github.com/en/billing/concepts/product-billing/github-actions |
| Workflow ที่เสนอ | job `web`: `npm ci` → `eslint .` → `tsc --noEmit` → `vitest run` → `next build` · job `py`: `uv sync` → `ruff check` → `ruff format --check` → `pytest` · job `e2e` (เลือกได้): Playwright เฉพาะ chromium | (ข้อเสนอ) |
| pre-commit | ไม่บังคับ: ใช้ `pre-commit` (Python) สำหรับ ruff หรือ lint-staged สำหรับ eslint | https://nextjs.org/docs/app/api-reference/config/eslint (ตัวอย่าง lint-staged) |
| Preview deployments | push ไป branch ที่ไม่ใช่ production หรือเปิด PR จะได้ preview URL (มีทั้งแบบ branch และแบบ commit) โดยค่าเริ่มต้น preview จะถูก **Vercel Authentication ป้องกัน** และไม่ถูก index ส่วน deployment แรกของโปรเจกต์จะเป็น production เสมอ Custom environments มีเฉพาะ Pro/Enterprise แต่ Hobby ใช้ "preview branch เป็น staging" ได้ | https://vercel.com/docs/deployments/environments (2026-09-17) |
| Env vars | แยก Production/Preview/Development ได้ **แก้ค่าแล้วมีผลเฉพาะ deployment ใหม่** (ต้อง redeploy ถ้าเปลี่ยนค่าลับ) จำกัด 64 KB ต่อ deployment, `vercel env pull` → `.env.local`, ตัวแปร `NEXT_PUBLIC_*` ถูกฝังลง client bundle ตอน build มีชนิด Config/Secret (Secret อ่านกลับไม่ได้) | https://vercel.com/docs/environment-variables (2026-09-17) |

ตัวแปรที่ต้องมี (ข้อเสนอ): `DATABASE_URL` (pooled, role ที่อ่านอย่างเดียว) ฝั่งเว็บ · `DATABASE_URL_DIRECT` เฉพาะในเครื่องที่รัน loader · `REVALIDATE_SECRET` ใช้ทั้งสองฝั่ง · `PYTHAINLP_READ_ONLY=1` ฝั่ง Python function **อย่าเอา secret ใส่ `NEXT_PUBLIC_`**

---

## 5. มาตรฐาน UI / Responsive / Accessibility

### 5.1 Breakpoints

| ระบบ | ค่า | แหล่ง |
|---|---|---|
| Tailwind v4 | sm 640 · md 768 · lg 1024 · xl 1280 · 2xl 1536 (px, min-width) | https://tailwindcss.com/docs/responsive-design |
| Material 3 / Android window size classes (width) | Compact < 600dp (มือถือแนวตั้ง 99.96%) · Medium 600–839 (แท็บเล็ตแนวตั้ง) · Expanded 840–1199 (แท็บเล็ตแนวนอน) · Large 1200–1599 · Extra-large ≥ 1600 (เดสก์ท็อป) | https://developer.android.com/develop/ui/compose/layouts/adaptive/window-size-classes |
| ข้อเสนอการ map | มือถือ = ไม่มี prefix (<640) · แท็บเล็ต = `md:` (≥768) · เดสก์ท็อป = `lg:` (≥1024) ถ้าอยากให้ตรงกับ M3 ก็เพิ่ม `--breakpoint-tablet: 37.5rem` (600px) / `--breakpoint-desktop: 52.5rem` (840px) ได้ | (ข้อเสนอ) |

### 5.2 Touch target

| มาตรฐาน | ขนาด | แหล่ง |
|---|---|---|
| WCAG 2.2 **2.5.8 Target Size (Minimum), AA** | **≥ 24×24 CSS px** มีข้อยกเว้น: spacing (วงกลม 24px ไม่ทับกัน), equivalent, inline (อยู่ในประโยค), user-agent control, essential | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html |
| WCAG 2.5.5 Target Size (Enhanced), AAA | 44×44 CSS px | เดียวกัน |
| Apple HIG | **44×44 pt** (มาจากแหล่งรอง ไม่ได้อ่านหน้า HIG ตรงเพราะ fetch ไม่สำเร็จ) | https://developer.apple.com/design/human-interface-guidelines/accessibility **[unverified: เปิดหน้าไม่ได้ ECONNRESET]** |
| Material / Android | **48×48 dp** เว้นระยะห่าง ≥ 8dp | https://support.google.com/accessibility/android/answer/7101858 (จากผลค้นหา) |
| ข้อเสนอ | ปุ่ม/ลิงก์หลักให้ **≥ 44×44 px** (`min-h-11 min-w-11`) และห่างกัน ≥ 8px | |

### 5.3 WCAG 2.2 (W3C Recommendation 12 Dec 2024 — https://www.w3.org/TR/WCAG22/)

| SC | ระดับ | ข้อกำหนด | ผลต่อเรา |
|---|---|---|---|
| 1.4.3 Contrast (Minimum) | AA | ข้อความ ≥ **4.5:1**, ข้อความใหญ่ ≥ 3:1 | ระวังสีของ badge ระดับเตือนภัย (เหลือง/ส้ม) บนพื้นขาว |
| 1.4.6 Contrast (Enhanced) | AAA | 7:1 | ไม่บังคับ |
| 1.4.11 Non-text Contrast | AA | UI component/กราฟิก ≥ 3:1 | ขอบ input, ไอคอนสภาพอากาศ |
| 1.4.4 Resize Text | AA | ซูมข้อความได้ถึง **200%** โดยไม่เสียเนื้อหา | ใช้หน่วย rem และห้าม `maximum-scale=1` |
| 1.4.10 Reflow | AA | ที่ความกว้าง **320 CSS px** ต้องไม่ต้องเลื่อน 2 แนว | ต้องทดสอบที่ 320px ตารางพยากรณ์ 7 วันต้องเปลี่ยนเป็นการ์ด หรือ scroll เฉพาะในตาราง (ตารางข้อมูลได้รับยกเว้นตาม Understanding) |
| 1.4.12 Text Spacing | AA | ต้องไม่พังเมื่อผู้ใช้ตั้ง line-height 1.5×, ระยะย่อหน้า 2×, letter 0.12×, word 0.16× **ภาษา/อักษรที่ไม่ใช้ property ไหนก็ conform ได้ด้วย property ที่มีอยู่** (ไทยไม่เว้นวรรคระหว่างคำ) | ห้ามกำหนดความสูงตายตัวให้กล่องข้อความ — https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html |
| 2.4.11 Focus Not Obscured (Min) | AA | element ที่ได้ focus ต้องไม่ถูกบังทั้งหมด | ระวัง sticky header |
| 1.4.8 Visual Presentation | AAA | บรรทัดยาว ≤ 80 ตัวอักษร (CJK 40), line spacing ≥ 1.5 | ใช้เป็นแนวทาง — https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html |

### 5.4 ขนาดตัวอักษรและความยาวบรรทัด
- **ตัวอักษรเนื้อความ 16px** (Tailwind `text-base` = 1rem) และ **input/select/textarea ต้อง ≥ 16px** ไม่งั้น iOS Safari จะซูมเข้าเมื่อ focus วิธีห้ามซูมด้วย `maximum-scale=1` ทำให้ผิด accessibility — แหล่งรอง: https://css-tricks.com/?p=339455 , https://weblog.west-wind.com/posts/2023/Apr/17/Preventing-iOS-Textbox-Auto-Zooming-and-ViewPort-Sizing **[ไม่มีเอกสาร Apple ทางการยืนยัน]**
- สำหรับข้อความไทย แนะนำ body **16–18px** เพราะตัวอักษรไทยดูเล็กกว่าละตินที่ขนาดเดียวกัน **[unverified: ไม่พบแหล่งทางการระบุตัวเลข]**
- ความยาวบรรทัด: **45–90 ตัวอักษร** — https://practicaltypography.com/line-length.html และ WCAG 1.4.8 (AAA) ไม่เกิน 80 → ใช้ `max-w-prose` (65ch) หรือ `max-w-[70ch]` กับเนื้อความ
- ความกว้าง layout เดสก์ท็อป: ตัวเลือกที่นิยมคือ container `max-w-5xl` (64rem = 1024px) ถึง `max-w-7xl` (80rem = 1280px) ของ Tailwind ส่วนเนื้อความยาวๆ ให้จำกัดที่ ~65–70ch **[เป็นแนวปฏิบัติทั่วไป ไม่มีมาตรฐานทางการ]**

### 5.5 Typography ภาษาไทยบนเว็บ
- **Line-height:** วรรณยุกต์และสระบน/ล่างซ้อนกันได้หลายชั้น จึงต้องมีพื้นที่แนวตั้งมากกว่าละติน (ข้อความไทยปกติจะมีระยะระหว่างบรรทัดมากกว่า) — https://r12a.github.io/scripts/tutorial/summaries/thai , https://docs.thottingal.in/web-typography เอกสาร W3C Thai Script Resources (Group Note Draft 20 Mar 2026) มีหัวข้อ "Baselines, line height" แต่ยังเป็น "tbc" — https://www.w3.org/TR/thai-lreq/ **ไม่มีตัวเลขทางการ** → ข้อเสนอ: เนื้อความ `leading-relaxed` (1.625) ถึง `leading-loose`/1.75 หัวข้อ ≥ 1.3 และ **ห้ามใช้ `leading-none`/`leading-tight` กับไทย** เพราะวรรณยุกต์จะถูกตัด (ต้องทดสอบกับฟอนต์ที่เลือก เพราะขึ้นกับ vertical metrics ของฟอนต์) **[unverified ตัวเลข]**
- **Letter-spacing:** ห้ามใส่ `tracking-*` กับข้อความไทย CSS Text 3 ระบุว่า letter-spacing กับไทยต้องจัดการระดับต่ำกว่า grapheme cluster (เช่น แยกสระอำ) และ W3C Thai Gap Analysis (#47) บันทึกว่าเบราว์เซอร์จะเติมช่องว่างท้าย range — https://www.w3.org/TR/css-text-3/ (CRD 14 Aug 2026), https://www.w3.org/TR/thai-gap/ (Draft Note 01 Jun 2025)
- **การตัดบรรทัด:**
  - ไทยไม่มีช่องว่างระหว่างคำ ช่องว่างใช้คั่นวลี เบราว์เซอร์ต้องใช้ "lexical resource" (พจนานุกรม) หาจุดตัด ถ้าทำไม่ได้จะตัดระหว่างตัวอักษร — CSS Text 3 §5
  - `word-break: normal` (ค่าเริ่มต้น) = ตัดตามพจนานุกรม ✅ **ใช้อันนี้**
  - `word-break: break-all` = ไทยตัดได้ทุกตัวอักษร (class SA ถูกปฏิบัติเหมือน ideographic) ❌ ห้ามใช้กับเนื้อความไทย
  - `word-break: keep-all` = ไทยยังตัดตามพจนานุกรม (อ่านจาก spec ไม่ได้เขียนตรงๆ) ; `auto-phrase` เป็น experimental ; `manual` ยังไม่มีเบราว์เซอร์รองรับ — https://developer.mozilla.org/en-US/docs/Web/CSS/word-break (2026-04-20)
  - `line-break` (loose/strict) เน้น CJK ไม่มีผลชัดเจนกับไทย — https://developer.mozilla.org/en-US/docs/Web/CSS/line-break
  - ช่องโหว่ที่รู้กัน: **ไม้ยมก (ๆ) อาจหลุดไปขึ้นต้นบรรทัดใหม่** (Gecko/Blink/WebKit fail ทุกตัว), `text-justify: inter-character` ใช้กับไทยได้เฉพาะ Firefox → **ไม่ควรจัด justify ข้อความไทย** ให้ใช้ `text-left` — https://www.w3.org/TR/thai-gap/
  - คำยาวที่ล้น (URL, ชื่อสถานี): ใช้ `overflow-wrap: anywhere` (Tailwind `wrap-anywhere`/`break-words`) แทน `break-all` **[unverified ชื่อ utility ใน v4.3]**
  - ถ้าต้องควบคุมจุดตัดเอง: แทรก `<wbr>` หรือ U+200B ตามขอบเขตคำจาก PyThaiNLP ฝั่ง server หรือใช้ `Intl.Segmenter('th', {granularity:'word'})` ฝั่ง client (Baseline Widely available ตั้งแต่ Apr 2024) — https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Segmenter (2025-07-20) **ผลการตัดของ Intl.Segmenter (ICU) อาจไม่ตรงกับ newmm** **[unverified]**
- **ภาษา:** ใส่ `<html lang="th">` เพื่อให้เบราว์เซอร์เลือกกฎตัดบรรทัด/ฟอนต์ไทย และให้ screen reader อ่านถูก (แนวปฏิบัติมาตรฐาน **[ไม่ได้ดึงแหล่งเฉพาะ]**)

---

## 6. ตาราง Stack ทั้งหมด

| Layer | Tool | Version (2026-11-16) | ทำไม | Free-tier / limit | Risk |
|---|---|---|---|---|---|
| Runtime (dev) | Node.js | 24.19 (มีในเครื่อง) | Next ต้องการ ≥20.9 | — | ต่ำ |
| Framework | Next.js (App Router) | 16.4.6 | RSC + Cache Components + Route Handlers | — | กลาง: security patch ออกทุกเดือน, Cache Components เพิ่งเป็น default |
| UI lib | React / React DOM | 19.3.1 | มากับ Next 16.4 | — | ต่ำ |
| Language | TypeScript | **pin 6.0.3** (latest = 7.0.2) | typescript-eslint รับ `<6.1.0` | — | กลาง ถ้ามีคนติดตั้ง TS 7 โดยไม่ตั้งใจ |
| CSS | Tailwind CSS + @tailwindcss/postcss | 4.3.5 | CSS-first `@theme` | — | ต่ำ–กลาง: ต้องใช้ Safari ≥16.4 |
| Class utils | clsx / tailwind-merge / cva | 2.1.1 / 3.7.0 / 0.7.1 | สร้าง `cn()` + variants เอง | — | ต่ำ (cva ไม่อัปเดต) |
| Icons | lucide-react | 1.73.0 | tree-shakable | — | ต่ำ |
| Fonts | next/font/google (Noto Sans Thai หรือ Anuphan) | มาพร้อม Next | self-host + subset thai | — | ต่ำ |
| Validation (TS) | Zod | 4.6.7 | parse แถว DB/อินพุต | — | ต่ำ |
| DB driver | @neondatabase/serverless | 1.2.1 | HTTP, เบา, ไม่ต้อง generate | ดู Neon | ต่ำ |
| ORM (เลือกได้) | Drizzle | 0.45.4 (docs ใช้ 1.0 rc) | ถ้าอยากได้ type-safe | — | กลาง (กำลังจะเปลี่ยนเป็น 1.0) |
| Database | Neon Postgres (Singapore) | Free | serverless Postgres | 1 GB, 100 CU-h, 5 GB egress, suspend 5 นาที | กลาง: cold start หลัง suspend, write ถูกบล็อกถ้าเกิน 1 GB |
| Hosting | Vercel Hobby | — | Next native, preview URL | 1M invocations, 4 CPU-h, 100 GB transfer, 100 deploy/วัน | กลาง: ถ้าเกินโควตาต้องรอ 30 วัน |
| Python on Vercel | Vercel Python runtime + **Services (Beta)** | Python 3.12 default / 3.13 | /demo pipeline สด | 500 MB bundle, 4.5 MB body, 300 s, 2 GB | **สูง**: Services ยังเป็น beta และมีเพดาน body 4.5 MB |
| Python API | FastAPI | 0.163.1 | ASGI `app` ที่ Vercel ตรวจเจอเอง | — | ต่ำ |
| Thai NLP | PyThaiNLP (newmm) | 5.4.0 | tokenizer ไทย | wheel 22 MB / ติดตั้งแล้ว 68 MB | กลาง: data dir บนระบบไฟล์ read-only |
| PDF | **pypdfium2** (+ pdfminer.six สำรอง) | 5.15.2 / 20260107 | permissive, เล็ก | ~4 MB / ~7 MB | กลาง: ปัญหา PUA/ลำดับอักขระไทย |
| PDF (ห้าม deploy) | PyMuPDF | 2.1 (เครื่องเรา 1.28.2) | ใช้เทียบในเครื่องเท่านั้น | ~69 MB + onnxruntime/numpy | **สูง**: AGPL + deps หนัก |
| Schema (Py) | Pydantic | 2.14.3 | JSON contract | — | ต่ำ |
| DB loader | psycopg | 3.3.9 | ใช้ direct URL สำหรับ migrate/load | — | ต่ำ |
| Py env | uv | 0.13.8 | lockfile + Vercel อ่านได้ | — | ต่ำ |
| Py lint/format | Ruff | 0.17.5 | ตัวเดียวครบ | — | ต่ำ |
| Py type check | mypy / pyright | 2.4.1 / 1.1.414 | เลือกตัวใดตัวหนึ่ง | — | ต่ำ |
| Py test | pytest | 9.2.0 | | — | ต่ำ |
| JS lint | ESLint + eslint-config-next | 10.15.0 / 16.4.6 | กฎ Next/React/CWV | — | ต่ำ–กลาง: peer warning กับ ESLint 10 |
| Format | Prettier + prettier-plugin-tailwindcss | 3.10.1 / 0.8.1 | เรียง class v4 | — | ต่ำ |
| Unit test | Vitest + Testing Library + jsdom | 5.1.0 / 16.3.3 / 31.0.1 | ตามคู่มือ Next | — | ต่ำ: async RSC เทสไม่ได้ |
| E2E/visual | Playwright | 1.65.1 | viewport + screenshot | — | กลาง: baseline ต่างกันตาม OS |
| CI | GitHub Actions | — | lint/test/build | public repo ฟรี; private $12 เครดิต | ต่ำ |
| Hooks (เลือกได้) | pre-commit / lint-staged | 4.7.0 / — | | — | ต่ำ |

---

## 7. ความเสี่ยงที่ยังเปิดอยู่ (เรียงตามผลต่อแผน)

1. **PyMuPDF 2.x = AGPL + dependency หนัก (onnxruntime, numpy, …)** → ตัดออกจาก deploy ใช้ pypdfium2/pdfminer.six แทน ถ้าจะใช้ PyMuPDF ในเครื่อง ต้องไม่ commit โค้ดที่ import มันเข้าไปใน service (หรือยอมรับ AGPL ทั้ง repo)
2. **คุณภาพข้อความไทยจาก PDF ของกรมอุตุฯ ยังไม่รู้** (PUA, สระอำ, ลำดับวรรณยุกต์, PDF สแกน) → ต้องทำ spike ทดสอบ 3 library กับ PDF จริงก่อนจะตัดสินใจเลือก
3. **เพดาน body 4.5 MB ของ Vercel** → PDF ที่อัปโหลดเข้า /demo ต้อง ≤ ~4 MB (ตรวจขนาดฝั่ง client ก่อนส่ง) ถ้าใหญ่กว่านั้นต้องใช้ Vercel Blob client upload (ยังไม่ได้ศึกษา) **ขนาด PDF จริงของกรมอุตุฯ ยังไม่ได้วัด**
4. **Vercel Services ยังเป็น Beta** และ `/api/*.py` แบบเดิมถูกวางไว้สำหรับ "existing projects" → แผนสำรอง: แยก Python ไปเป็น Vercel project ที่สอง (FastAPI preset) แล้วเรียกข้าม origin (ต้องตั้ง CORS)
5. **PyThaiNLP บนระบบไฟล์ read-only** → ต้องตั้ง `PYTHAINLP_READ_ONLY=1` / `PYTHAINLP_DATA=/tmp/...` และทดสอบว่า newmm ใช้แค่พจนานุกรมที่มากับแพ็กเกจ (ไม่ดาวน์โหลดเพิ่ม) ส่วน cold start จะช้าเพราะ word list โหลดแบบ lazy
6. **TypeScript 7 ชนกับ typescript-eslint** → pin `typescript@~6.0.3` ใน package.json
7. **Neon scale-to-zero (5 นาที) + Vercel region เริ่มต้น `iad1`** → ตั้ง Vercel function region ให้ใกล้ Singapore และสร้าง Neon ที่ `aws-ap-southeast-1` ถ้าไม่ทำ ทุก query จะข้ามโลก ส่วน `'use cache'` ช่วยซ่อน cold start ได้ **ยังไม่ได้ยืนยันว่า Hobby เลือก region `sin1` ได้**
8. **Cache ผูกกับ deployment + in-memory บน serverless** → revalidate ด้วย webhook อาจไม่ hit ทุก instance ต้องตั้ง `cacheLife('hours')` เป็นตาข่ายรองรับ และทดสอบจริงบน Vercel
9. **Security release ของ Next ออกทุกเดือน** และ Vercel บล็อกการ deploy เวอร์ชันที่มีช่องโหว่ (มี changelog "New deployments of vulnerable Next.js applications are now blocked by default") → ต้องอัปเดต patch ก่อน demo
10. **dist-tag `latest` ของแพ็กเกจ `prisma` ชี้ไปที่ 8.0.0-rc** (ถ้าเลือก Prisma ต้อง pin ให้ชัด) และ docs ของ Drizzle ใช้ `@rc` → ถ้าใช้ ORM ต้อง pin เวอร์ชัน
11. **Tailwind v4 ต้องใช้เบราว์เซอร์ใหม่** (Safari 16.4+) เครื่องเก่ามากจะแสดงผลเพี้ยน

---

## สิ่งที่ยังไม่ได้ตรวจ

- หน้า Apple HIG (Accessibility/Buttons) โดยตรง เพราะ fetch ล้ม (ECONNRESET) ตัวเลข 44×44 pt มาจากแหล่งรอง และหน้า Material 3 (m3.material.io) โดยตรง เพราะได้ 404/ไม่มีเนื้อหา ตัวเลข 48dp มาจาก Google Accessibility Help และแหล่งรอง
- ตัวเลข `/tmp` ~500 MB ของ Vercel มาจากผลค้นหา ไม่ได้เปิดหน้า Vercel ที่ระบุตรงๆ
- Vercel Hobby เลือก function region (เช่น `sin1`) ได้หรือไม่ และเงื่อนไข "non-commercial" ของ Hobby (หน้า fair-use ที่ดึงมาไม่มีข้อความนี้)
- `/api/*.py` แบบเดิมยังทำงานคู่กับ Next.js 16 ในโปรเจกต์ใหม่ได้จริงหรือไม่ (ถ้าไม่ใช้ Services)
- Vercel Blob client upload (ทางเลี่ยงเพดาน 4.5 MB) และขนาดจริงของ PDF พยากรณ์จากกรมอุตุฯ
- ผลการดึงข้อความไทยของ pypdfium2 / pypdf / pdfminer.six / PyMuPDF กับ PDF จริงใน `dataset-raw` (ยังไม่ได้ลอง เพราะงานนี้ research only)
- ขนาด bundle จริงของ Python function (FastAPI + PyThaiNLP + pypdfium2) และ cold start บน Vercel รวมถึงว่าตัดไฟล์ corpus ไหนของ PyThaiNLP ได้บ้าง
- README ของ tailwind-merge (ยืนยันว่า 3.x = Tailwind v4) และรายละเอียด Prisma 7 + Neon adapter
- ชื่อ utility ของ Tailwind v4.3 สำหรับ `overflow-wrap: anywhere` และรูปแบบ map `next/font` variable เข้า `@theme`
- ตัวเลข line-height สำหรับไทยที่มีแหล่งทางการรองรับ (W3C ยังเป็น "tbc") และขนาดตัวอักษรไทยที่แนะนำ
- คู่มือ caching แบบ "Previous Model" (ไม่เปิด Cache Components) และ API reference ของ `revalidateTag` (signature ละเอียด)
- Biome `useSortedClasses` รองรับ Tailwind v4 แค่ไหน (หน้า rule ได้ 404 ข้อมูลมาจากผลค้นหา)
- ข้อกำหนดของ AGPL ต่อกรณีของเราในทางกฎหมาย (ไม่ใช่คำปรึกษาทางกฎหมาย)
