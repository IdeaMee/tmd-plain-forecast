# R2 — โครงสร้างโฟลเดอร์และสถาปัตยกรรม (Next.js + Python บน Vercel)

> ค้นคว้าเมื่อ 2026-11-16 · เป็นงาน research อย่างเดียว ยังไม่ได้ติดตั้งหรือทดลอง deploy อะไร
> วันที่ที่กำกับ = `lastUpdated` / `last_updated` ที่หน้าเอกสารแสดงไว้ตอนเปิดอ่าน
> ข้อไหนที่ยังไม่ได้ยืนยันจากแหล่งข้อมูล จะมีป้ายกำกับ **[unverified]**

---

## 0. สรุปสั้น: เรื่องที่อาจต้องเปลี่ยนแผน

| # | ข้อค้นพบ | ผลต่อแผน | แหล่ง |
|---|---|---|---|
| 1 | Vercel เขียนชัดว่าการวางไฟล์ Python ในโฟลเดอร์ `/api` รองรับสำหรับ "existing projects" ส่วนการรัน Python ร่วมกับ framework อื่นให้ใช้ **Services** แทน | แผนเดิม (Next.js ที่ root + `api/*.py`) **ยังใช้ได้** แต่ไม่ใช่ทางที่ Vercel แนะนำสำหรับโปรเจกต์ใหม่แล้ว ต้องทำ spike ทดสอบก่อนเริ่มสร้างจริง | [api-directory (2026-08-12)](https://vercel.com/docs/functions/runtimes/python/api-directory) |
| 2 | **Services** (Beta, ใช้ได้ทุก plan รวมถึง Hobby) คือวิธีทางการตอนนี้ในการรวม Next.js กับ Python ไว้ในโปรเจกต์เดียว แต่ template ทางการทุกตัวแยกโค้ดเป็น `frontend/` กับ `backend/` | ถ้าเลือกใช้ Services โครงสร้างจะกลายเป็นสอง root ซึ่งไม่ใช่ single-root ตามแผน จึงเก็บไว้เป็น Plan B | [Services (2026-08-10)](https://vercel.com/docs/services), [KB python-backend (2026-10-15)](https://vercel.com/kb/guide/python-backend-on-vercel) |
| 3 | Request body ของ Vercel Function รับได้สูงสุด **4.5 MB** | หน้า `/demo` ต้องจำกัดขนาด PDF ที่อัปโหลดไม่ให้เกิน ~4.5 MB และตรวจขนาดฝั่ง client ก่อนส่ง | [Functions Limits (2026-08-24)](https://vercel.com/docs/functions/limitations) |
| 4 | มีรายงานจากชุมชนว่า root `api/` ของ Python ชนกับ route handler ของ Next.js ใน `app/api/*` จนได้ 404 | กำหนดให้ **URL `/api/*` เป็นของ Python เท่านั้น** และห้ามสร้าง `app/api/` ใน Next.js (เราอ่าน DB ตรงจาก Server Components อยู่แล้ว) | [Vercel Community #9087 (2025)](https://community.vercel.com/t/issue-integrating-python-serverless-function-with-app-router/9087) |
| 5 | Python function จะรวม "ทุกไฟล์ในโปรเจกต์ที่เข้าถึงได้ตอน build" เข้าไปใน bundle ด้วย เพราะไม่มี tree-shaking | ต้องใส่ `excludeFiles` เพื่อกัน `node_modules`, `.next`, `data/`, `notebooks/` ออกจาก Python bundle ซึ่งจำกัดไว้ที่ 500 MB | [Python runtime (2026-08-12)](https://vercel.com/docs/functions/runtimes/python) |
| 6 | Function ทุกตัวรันที่ region `iad1` (สหรัฐฯ) เป็นค่าเริ่มต้น แต่เปลี่ยนได้ | ควรตั้ง region ของ function ให้ใกล้กับ region ของ Neon DB | [Runtimes (2026-08-12)](https://vercel.com/docs/functions/runtimes) |
| 7 | `create-next-app` ใส่ `.env*` ไว้ใน `.gitignore` | ต้องเพิ่มบรรทัด `!.env.example` ถ้าจะ commit ไฟล์ตัวอย่าง | [create-next-app gitignore template](https://raw.githubusercontent.com/vercel/next.js/canary/packages/create-next-app/templates/app-tw/ts/gitignore) |
| 8 | ค่า default ที่ Next.js แนะนำคือ **ไม่ใช้ `src/`** | ไม่ควรใช้ `src/` ฝั่ง Next.js เพราะชื่อจะชนกับ Python src layout และ Vercel ก็ค้นหา Python entrypoint ใน `src/` กับ `app/` ด้วย | [Installation (2026-10-02)](https://nextjs.org/docs/app/getting-started/installation), [Python runtime](https://vercel.com/docs/functions/runtimes/python) |

---

## 1. Next.js App Router — โครงสร้างตามเอกสารทางการ

**เวอร์ชัน:** เอกสาร installation พูดถึงพฤติกรรม "Starting with Next.js 16" ([Installation, 2026-10-02](https://nextjs.org/docs/app/getting-started/installation)) จึงอยู่ในสาย 16.x ส่วนเลข patch ล่าสุด (มีแหล่งระบุว่าเป็น 16.4.x) ยังเป็น **[unverified]** ให้เช็กด้วย `npm view next version`
หน้า Project Structure มี lastUpdated 2026-07-21 ([nextjs.org](https://nextjs.org/docs/app/getting-started/project-structure))

### 1.1 โฟลเดอร์และไฟล์ระดับบนสุด
| รายการ | หน้าที่ | หมายเหตุ |
|---|---|---|
| `app/` | App Router | ใช้อันนี้ |
| `pages/` | Pages Router | ไม่ใช้ |
| `public/` | static assets เสิร์ฟจาก `/` | เช่น `public/logo.png` เข้าถึงได้ที่ `/logo.png` |
| `src/` | โฟลเดอร์ซอร์สแบบ optional | ถ้าใช้ `src/` ไฟล์ `.env*` ยังต้องอยู่ที่ root ([env docs](https://nextjs.org/docs/app/guides/environment-variables)) |
| `next.config.js`, `tsconfig.json`, `eslint.config.mjs`, `package.json` | config | |
| `proxy.ts`, `instrumentation.ts` | request proxy (ชื่อเดิมคือ middleware) และ monitoring | |
| `.env`, `.env.local`, ... | env | เอกสารระบุว่า "should not be tracked by version control" |
| `next-env.d.ts` | type declaration | ไม่ต้อง track |

ที่มา: [Project structure](https://nextjs.org/docs/app/getting-started/project-structure)

### 1.2 Convention ภายใน `app/`
| Convention | ความหมาย | การนำมาใช้ในโปรเจกต์เรา |
|---|---|---|
| `page.tsx` / `layout.tsx` / `loading.tsx` / `error.tsx` / `not-found.tsx` | ไฟล์พิเศษที่ใช้กำหนด route | หน้าหลัก `/`, `/history`, `/demo` |
| `route.ts` | API endpoint (Route Handler) | **ไม่ใช้ใต้ `app/api/`** (ดูข้อ 4.5) |
| `[segment]` | dynamic route | เช่น `app/history/[date]/page.tsx` ถ้าต้องการ |
| `_folder` (private folder) | ไม่ถูกนับเป็น route รวมถึงโฟลเดอร์ย่อยข้างในทั้งหมด | ใช้วาง `_components/` ของแต่ละหน้า |
| `(group)` (route group) | จัดกลุ่ม route โดยไม่กระทบ URL และแชร์ layout ได้ | ใช้ภายหลังถ้าต้องการ layout แยก |
| Colocation | route จะ public ก็ต่อเมื่อมี `page`/`route` จึงวางไฟล์อื่นปนไว้ได้อย่างปลอดภัย | |

เอกสารบอกว่า Next.js "**unopinionated**" เรื่องการจัดไฟล์ และเสนอไว้ 3 กลยุทธ์ ([Project structure](https://nextjs.org/docs/app/getting-started/project-structure)):
1. เก็บโค้ดไว้นอก `app/` เช่น root `components/` และ `lib/` ให้ `app/` ทำหน้าที่ routing อย่างเดียว
2. เก็บโค้ดในโฟลเดอร์ระดับบนสุดภายใน `app/`
3. แยกตาม feature/route: โค้ดที่ใช้ร่วมกันวางไว้ระดับบน โค้ดเฉพาะหน้าวางใน segment นั้น

ชื่อโฟลเดอร์อย่าง `components` และ `lib` เป็นแค่ placeholder ไม่มีความหมายพิเศษต่อ framework ข้อสรุปของเอกสารคือ "choose a strategy that works for you and your team and be consistent"

### 1.3 ค่า default ของ `create-next-app`
TypeScript, ESLint, Tailwind CSS, App Router, Turbopack, alias `@/*`, **"No src/ directory"**, Cache Components และ `AGENTS.md` ใช้ Node ขั้นต่ำ 20.9 และตั้งแต่ Next.js 16 คำสั่ง `next build` ไม่รัน linter ให้อัตโนมัติแล้ว ([Installation](https://nextjs.org/docs/app/getting-started/installation))

---

## 2. โครงสร้างจากชุมชน React/Next.js

| แนวทาง | แนวคิดหลัก | กฎสำคัญ | ข้อดี | ข้อเสีย | แหล่ง |
|---|---|---|---|---|---|
| **bulletproof-react** (feature-based) | `src/` แบ่งเป็น `app`, `components`, `config`, `features`, `hooks`, `lib`, `stores`, `types`, `utils`; ใน `features/x/` มี `api`, `components`, `hooks`, `types`, `utils` ตามที่จำเป็น | โค้ดไหลทางเดียว shared → features → app, ห้าม import ข้าม feature, บังคับด้วย ESLint `import/no-restricted-paths`, ไม่แนะนำ barrel file | ขยายได้ดี ขอบเขตชัด | ยาวเกินจำเป็นสำหรับโปรเจกต์ 3 หน้า | [project-structure.md](https://github.com/alan2207/bulletproof-react/blob/master/docs/project-structure.md) |
| **Feature-Sliced Design v2.1** | มี layer `app` / `pages` / `widgets` / `features` / `entities` / `shared` (ส่วน `processes` deprecated แล้ว), แต่ละ layer มี slice และ segment (`ui`, `api`, `model`, `lib`, `config`) | import ได้เฉพาะจาก layer ที่อยู่ต่ำกว่า slice ใน layer เดียวกันห้ามใช้กันเอง ถ้าใช้กับ Next.js ต้องเปลี่ยนชื่อ layer เป็น `_app`/`_pages` เพื่อไม่ให้ชนกับ `app/` | มีกฎเข้มและมี linter ชื่อ Steiger | ต้องเรียนรู้เยอะ เกินขนาดงานของเรา | [Overview](https://feature-sliced.design/docs/get-started/overview), [with-nextjs](https://feature-sliced.design/docs/guides/tech/with-nextjs) |
| **Blazity next-enterprise** | Next.js 15 วาง `app/`, `components/`, `assets/`, `styles/`, `e2e/` ที่ root (ไม่มี `src/`), มี `.github/` และ `vercel.json` | เครื่องมือครบชุด: Vitest, Playwright, Storybook, T3 Env, GitHub Actions | เป็นตัวอย่างการวางไฟล์ที่ root ที่ใช้จริง (~7.5k stars) | tooling เยอะเกินสำหรับงานวิชา | [GitHub](https://github.com/Blazity/next-enterprise) |

**จุดร่วม:** (ก) แยก routing ออกจากโค้ดที่ใช้ซ้ำ (ข) โค้ดที่ใช้ร่วมกันไหลทางเดียว (ค) เริ่มจาก type-based (`components/`, `lib/`) แล้วค่อยยกเป็น `features/` เมื่อโปรเจกต์โต ข้อนี้เป็นความเห็นจากบทความชุมชนหลายแห่ง ไม่ใช่มาตรฐานทางการ ([search summary/บทความชุมชน](https://github.com/drbarzaga/nextjs-project-structures)) **[unverified รายละเอียดเกณฑ์จำนวน feature]**

| | Type-based (`components/`, `lib/`, `hooks/`) | Feature-based (`features/forecast/...`) |
|---|---|---|
| เหมาะกับ | โปรเจกต์เล็ก หน้าไม่กี่หน้า | หลาย domain หรือหลายทีม |
| ข้อดี | ไม่ต้องคิดเยอะ คนใหม่เข้าใจทันที | โค้ดของเรื่องเดียวกันอยู่ใกล้กัน ลบทั้ง feature ได้ง่าย |
| ข้อเสีย | โฟลเดอร์จะบวมเมื่อโปรเจกต์โต | มีโครงเยอะตั้งแต่ต้น |
| **ข้อเสนอสำหรับเรา** | เริ่มแบบนี้ ใช้ root `components/` + `lib/` และวาง `_components/` ไว้ในแต่ละหน้า | ย้ายมาแบบนี้เมื่อมีเงื่อนไขตามกฎในข้อ 7 |

---

## 3. โครงสร้างโปรเจกต์ Python

| หัวข้อ | สาระ | แหล่ง |
|---|---|---|
| src layout กับ flat layout | src layout คือวาง package ไว้ใน `src/` ช่วยป้องกันการ import สำเนาที่กำลังพัฒนาโดยไม่ตั้งใจ แต่ต้อง install ก่อนถึงจะรันได้ ส่วน flat layout คือวาง package ไว้ที่ root | [PyPA discussion](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) |
| `pyproject.toml` | ควรมี `[build-system]` เสมอ, `[project]` มี `name`/`version`/`dependencies`/`requires-python` (ไม่ควรใส่ upper bound), `[project.optional-dependencies]`, `[dependency-groups]` สำหรับ dev/test และ `[project.scripts]` สำหรับ CLI เช่น `spam-cli = "spam:main_cli"` | [Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) |
| tests | แนะนำให้วาง `tests/` แยกนอกตัวโค้ด, "strongly suggested" ให้ใช้ src layout, โปรเจกต์ใหม่ใช้ `--import-mode=importlib`, ตั้ง `pythonpath = ["src"]` ได้ถ้าไม่ได้ install, และ `uv run pytest` | [pytest good practices (pytest ≥9)](https://docs.pytest.org/en/stable/explanation/goodpractices.html) |

### 3.1 การแชร์ package เดียวระหว่างสคริปต์บนเครื่องกับ serverless
| วิธี | วิธีทำ | สถานะ |
|---|---|---|
| A. ให้ api function import package ที่ root | Vercel แนะนำ "Keep shared code outside `api/` and import it from your function entry point" | ✅ [Advanced Configuration (2026-09-16)](https://vercel.com/docs/functions/configuring-functions/advanced-configuration) |
| ทำให้ path ใช้ได้ | ตอนรันบน Vercel, cwd = root ของโปรเจกต์ ("The working directory is the base of your project") | ✅ [Python runtime](https://vercel.com/docs/functions/runtimes/python) |
| `sys.path` ตอนรันบน Vercel | ไม่มีเอกสารทางการบอกว่า root อยู่ใน `sys.path` หรือไม่ ในชุมชนนิยมใส่ `sys.path.insert(0, <root>)` ไว้บนสุดของ `api/*.py` | **[unverified]** ต้อง spike |
| ให้ Vercel install package ของเราเอง (src layout) | ไม่พบเอกสารว่า Vercel ติดตั้งตัวโปรเจกต์เองจาก `pyproject.toml` ด้วยหรือเปล่า (เอกสารพูดถึงแค่ dependencies) | **[unverified]** |
| สคริปต์บนเครื่อง | ใช้ `uv run python -m <pkg>.cli ...` หรือประกาศ `[project.scripts]` แล้ว install แบบ editable | ✅ (PyPA/pytest ข้างบน) |

**ข้อเสนอ:** ใช้ **src layout** (`src/<pkg>/`) ตามที่ PyPA และ pytest แนะนำ ส่วน `api/*.py` ให้เพิ่ม `src/` เข้า `sys.path` เองหนึ่งบรรทัด ถ้า spike พบว่า Vercel ติดตั้งตัวโปรเจกต์ให้อยู่แล้วก็ลบบรรทัดนั้นทิ้งได้ อีกทางที่ยอมรับได้คือ flat layout `<pkg>/` ที่ root ซึ่งไม่ต้องแตะ `sys.path` ถ้า root อยู่ใน path อยู่แล้ว **[unverified]**

---

## 4. Next.js + Python บน Vercel ในโปรเจกต์เดียว (ส่วนที่สำคัญที่สุด)

### 4.1 Python runtime: ข้อเท็จจริงหลัก
| หัวข้อ | ค่า / พฤติกรรม | แหล่ง (วันที่) |
|---|---|---|
| เวอร์ชัน Python | **3.12 (default)**, 3.13, 3.14 กำหนดได้ผ่าน `pyproject.toml` `requires-python`, `.python-version` หรือ `Pipfile.lock` | [python-version (2026-04-10)](https://vercel.com/docs/functions/runtimes/python/python-version) |
| ไฟล์ dependency | `pyproject.toml` (มีหรือไม่มี `uv.lock` ก็ได้), `requirements.txt`, `Pipfile`+`Pipfile.lock` | [Python runtime (2026-08-12)](https://vercel.com/docs/functions/runtimes/python) |
| Entrypoint แบบ `/api` | ไฟล์ `.py` แต่ละไฟล์ใน `/api` กลายเป็น function แยกกัน (`api/users.py` → `/api/users`) ต้องประกาศ top-level เป็น `app` (ASGI/WSGI), `application` (WSGI) หรือ `handler` (class ที่สืบจาก `BaseHTTPRequestHandler`) | [api-directory (2026-08-12)](https://vercel.com/docs/functions/runtimes/python/api-directory) |
| ไฟล์ช่วยใน `/api` | ไฟล์ที่ขึ้นต้นด้วย `_` หรือ `.` จะไม่ถูกทำเป็น function | [Advanced Configuration](https://vercel.com/docs/functions/configuring-functions/advanced-configuration) |
| Entrypoint แบบ framework preset | `app.py` / `index.py` / `main.py` ฯลฯ ที่ root, ใน `src/` หรือใน `app/` หรือกำหนดผ่าน `[tool.vercel] entrypoint = "pkg.mod:app"` ถ้า Vercel ตรวจเจอ preset (FastAPI/Flask) ตัว preset จะมาก่อน และไฟล์ใน `/api` จะ**ไม่**ถูกทำเป็น function | [Python runtime](https://vercel.com/docs/functions/runtimes/python), [api-directory](https://vercel.com/docs/functions/runtimes/python/api-directory) |
| Bundle | รวม "all files ... reachable at build time" ไม่มี tree-shaking, compile เป็น `.pyc` ให้อัตโนมัติ, จำกัด **500 MB** (uncompressed), ถ้าเปิด Large Functions (Beta) ได้ถึง 5 GB | [Python runtime](https://vercel.com/docs/functions/runtimes/python), [Limits](https://vercel.com/docs/functions/limitations) |
| ตัดไฟล์ออก | `vercel.json` → `functions` → `"api/**/*.py": { "excludeFiles": "<glob>" }` (`includeFiles`/`excludeFiles` ใช้กับ function ของ Next.js ไม่ได้) | [api-directory](https://vercel.com/docs/functions/runtimes/python/api-directory), [vercel.json (2026-08-14)](https://vercel.com/docs/project-configuration/vercel-json) |
| คีย์ใน `functions` | `runtime`, `maxDuration`, `includeFiles`, `excludeFiles`, `regions`, `supportsCancellation` (Node เท่านั้น), `memory` (ตั้งใน vercel.json ไม่ได้เมื่อเปิด Fluid) | [vercel.json](https://vercel.com/docs/project-configuration/vercel-json) |
| Filesystem | read-only แต่เขียนได้ที่ `/tmp` (≤500 MB) | [Runtimes (2026-08-12)](https://vercel.com/docs/functions/runtimes) |

### 4.2 ขีดจำกัดของ Hobby (Fluid compute)
| รายการ | Hobby | แหล่ง |
|---|---|---|
| Max duration | 300 วินาที (ทั้งค่า default และค่าสูงสุด) | [Limits (2026-08-24)](https://vercel.com/docs/functions/limitations) |
| Memory | 2 GB / 1 vCPU | เดียวกัน |
| Request/response body | **4.5 MB** (ถ้าเกินได้ 413 `FUNCTION_PAYLOAD_TOO_LARGE`) | เดียวกัน |
| Region | ค่าเริ่มต้น `iad1` เปลี่ยนได้ แต่หลาย region ต้องใช้ Pro | [Runtimes](https://vercel.com/docs/functions/runtimes) |
| จำนวน function | กรณีไม่มี framework: 1 ไฟล์ใน `api/` = 1 function และ Hobby ได้ไม่เกิน 12 ต่อ deployment ส่วน Next.js รวม route เป็น function ให้เอง | เดียวกัน |
| Cold start | function ที่ไม่ถูกเรียกจะถูก archive (production ภายใน 2 สัปดาห์) และเมื่อเรียกใหม่จะ cold start ช้าขึ้นอย่างน้อย ~1 วินาที | เดียวกัน |

### 4.3 Template ทางการกับของชุมชน
| ชื่อ | โครง | วิธีหลบการชนของ route | สถานะ |
|---|---|---|---|
| **Next.js FastAPI Starter** (Vercel template) | `frontend/` + `backend/` + `vercel.json` ใช้ **Services** | rewrite `/svc/api/:path*` → service backend, ที่เหลือ → frontend | ทางการ ([template page](https://vercel.com/templates/fast-api/next-js-fastapi-starter.md)) ส่วนลิงก์ repo `vercel/examples/python/nextjs-fastapi` เปิดแล้วได้ 404 **[unverified ตำแหน่ง repo]** |
| **python-nextjs-starter** (KB guide) | `frontend/` (Next.js) + `backend/` (FastAPI, `pyproject.toml`+`uv.lock`) | Python เป็น private, Next.js มี Route Handler `/api/backend/[...path]` เป็นสะพานส่งต่อ และใช้ service binding ซึ่งฉีด `BACKEND_URL` ให้ | ทางการ, อัปเดต 2026-10-15 ([KB](https://vercel.com/kb/guide/python-backend-on-vercel)) |
| **digitros/nextjs-fastapi** (แบบเก่า) | `app/` (Next.js) + `api/` (FastAPI) + `requirements.txt` ที่ root | ใช้ `next.config.js` rewrite `/api/py/:path*` → FastAPI, ตอน dev ชี้ไป `127.0.0.1:8000` | ชุมชน มี issue ว่า prefix `/api/py` ไม่ทำงานบน Vercel และ path กลายเป็น `/api/index` ([GitHub](https://github.com/digitros/nextjs-fastapi)) |

### 4.4 ทางเลือกสำหรับโปรเจกต์เรา
| | **Plan A: single-root + `api/*.py` (legacy file-based)** | **Plan B: Services** |
|---|---|---|
| โครง | Next.js ที่ root, `api/summarize.py`, Python package ที่ root | `web/` (Next.js) + `pipeline/` (Python service: package, scripts, ASGI entry) |
| ตรงกับแผนเดิม | ✅ single-root | ❌ เป็นสอง root (แต่ยังเป็น repo เดียวและ Vercel project เดียว) |
| สถานะทางการ | Vercel เรียกว่า "existing projects" ไม่ได้ประกาศ deprecate ([GA changelog 2026-10-15](https://vercel.com/changelog/python-on-vercel-is-now-generally-available) ไม่มีคำว่า deprecation) | Beta ใช้ได้ทุก plan ([Services](https://vercel.com/docs/services)) และเป็นทางที่ Vercel แนะนำ |
| Import package ร่วม | import จาก root ได้ เพราะไฟล์ทั้งโปรเจกต์ถูก bundle แต่เรื่อง `sys.path` ยัง **[unverified]** | ไม่มีปัญหาถ้า package อยู่ใน root ของ service เอง แต่การ import ข้าม service root ยัง **[unverified]** |
| Python handler | `BaseHTTPRequestHandler` (stdlib) ไม่ต้องลง framework | ต้องเป็น ASGI/WSGI app (เช่น FastAPI) ทำให้มี dependency เพิ่ม |
| Local dev | `next dev` ไม่เสิร์ฟ Python ต้องใช้ `vercel dev` (ชุมชนรายงานว่ามักเจอ 404 ตอน local) หรือรัน Python server แยกแล้ว rewrite เฉพาะตอน dev | `vercel dev` / `vercel dev -L` รันทุก service พร้อมกัน ([Services](https://vercel.com/docs/services)) |
| ความเสี่ยง | path ชนกับ `app/api`, เครื่องมือ local, รูปแบบนี้อาจถูกลดการสนับสนุนในอนาคต | Beta, ถ้าตั้ง `services` แล้วคีย์ top-level อย่าง `functions`/`buildCommand` ใช้ไม่ได้ |

**ข้อเสนอ:** เริ่มด้วย **Plan A** ตามแผนเดิม แต่**ทำ spike ก่อน Phase 1** คือ deploy `api/hello.py` ที่ import package ของเราและ PyThaiNLP แล้ววัด (1) import ผ่านไหม (2) ขนาด bundle ซึ่งดูได้จาก env `VERCEL_ANALYZE_BUILD_OUTPUT=1` ([Limits](https://vercel.com/docs/functions/limitations)) (3) เวลา cold start (4) หน้า Next.js ยังทำงานปกติไหม ถ้า spike ไม่ผ่านให้เปลี่ยนไป Plan B ทันที วิธีนี้ทำได้ไม่ยากถ้าแยกโค้ด Python ไว้ในโฟลเดอร์ของตัวเองตั้งแต่แรก

### 4.5 กันการชนของ route (Plan A)
| กฎ | เหตุผล |
|---|---|
| URL `/api/*` ใช้กับ Python เท่านั้น และ**ห้ามสร้าง `app/api/`** | มีรายงานจากชุมชนว่าชนกันจน 404 ([#9087](https://community.vercel.com/t/issue-integrating-python-serverless-function-with-app-router/9087)) |
| ถ้าวันหนึ่งต้องมี Next.js Route Handler ให้ใช้ prefix อื่น เช่น `app/internal/.../route.ts` | ทีมงาน Vercel ในกระทู้เดียวกันเคยแนะนำให้เปลี่ยนชื่อ `app/api` |
| ใน `api/` มีแค่ entry file บาง ๆ ส่วน helper ให้ขึ้นต้นด้วย `_` หรือวางไว้นอก `api/` | [Advanced Configuration](https://vercel.com/docs/functions/configuring-functions/advanced-configuration) |
| หน้า `/demo` (client component) ส่ง `fetch('/api/summarize')` ไปที่ origin เดียวกัน จึงไม่ต้องตั้ง CORS | |
| ตอน dev ถ้าไม่ใช้ `vercel dev` ให้ใส่ rewrite เฉพาะ dev ใน `next.config` ชี้ไป Python server ที่รันบนเครื่อง ตาม pattern ของ digitros | [digitros/nextjs-fastapi](https://github.com/digitros/nextjs-fastapi) **[unverified ว่าใช้ได้กับ Next 16]** |

### 4.6 ข้อควรระวังอื่น
| ข้อควรระวัง | ทางแก้ | แหล่ง |
|---|---|---|
| Python bundle ดึง `node_modules`/`.next` เข้ามาด้วยจนเกิน limit (มีเคสใน community ที่ build error เรื่อง 250 MB) | `excludeFiles` เช่น `"{node_modules/**,.next/**,data/**,notebooks/**,docs/**,tests/**}"` **[unverified ว่า glob นี้ครอบ node_modules จริง]** | [Community #1202 (2024)](https://community.vercel.com/t/python-vercel-function-within-nextjs-project/1202), [Python runtime](https://vercel.com/docs/functions/runtimes/python) |
| Library หนักอย่าง ML lib หรือ binary ทำให้ bundle ใหญ่ | ใช้ NB/k-NN ที่เขียนเองและอ่านพารามิเตอร์จาก JSON, ไม่ใส่ pandas/sklearn ใน runtime deps แต่ย้ายไปไว้ใน dev group | [Limits](https://vercel.com/docs/functions/limitations) |
| ขนาดของ PyThaiNLP และ dictionary newmm | วัดจาก spike | **[unverified]** |
| PDF > 4.5 MB | เช็กขนาดฝั่ง client แล้วแสดงข้อความแจ้ง | [Limits](https://vercel.com/docs/functions/limitations) |
| ถ้ามีทั้ง `pyproject.toml` และ `requirements.txt` ไม่รู้ว่า Vercel จะเลือกใช้ไฟล์ไหน | ใช้ไฟล์เดียวเป็นแหล่งจริงของ runtime deps | **[unverified]** |
| `pyproject.toml` ที่ root ทำให้ Vercel ตรวจ framework ผิดหรือเปล่า (ในเมื่อ project ตั้งเป็น Next.js) | ห้ามใส่ fastapi/flask ใน deps เพื่อไม่ให้ trigger preset และให้ spike ตรวจ | **[unverified]** |

---

## 5. Convention ระดับ repo

| ไฟล์/โฟลเดอร์ | Convention | แหล่ง |
|---|---|---|
| `docs/` | แยกเป็น `docs/decisions/` (ADR), `docs/architecture.md`, `docs/data/` (อธิบาย schema และ label guideline), `docs/report/` (รายงานส่งอาจารย์) | ข้อเสนอของผู้เขียน ([ADR site](https://adr.github.io/) ไม่ได้กำหนดชื่อโฟลเดอร์) |
| ADR | ตามรูปแบบ Nygard: **Title, Status, Context, Decision, Consequences**, เลขเรียงขึ้นอย่างเดียวและ "Numbers will not be reused", ถ้าเปลี่ยนการตัดสินใจให้ทำเครื่องหมาย superseded แทนการลบ ต้นฉบับใช้ `doc/arch/adr-NNN.md` | [Nygard 2011](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), [adr.github.io](https://adr.github.io/) |
| `.env.example` | ใส่ชื่อตัวแปรโดยไม่มีค่าจริง และต้องเขียน `!.env.example` เพราะ template ของ Next.js ignore `.env*` ทั้งหมด ตัวแปรที่ขึ้นต้นด้วย `NEXT_PUBLIC_` จะถูก inline ลง bundle ฝั่ง browser ดังนั้น `DATABASE_URL` ต้อง**ไม่มี**prefix นี้ | [Next.js env (2026-08-25)](https://nextjs.org/docs/app/guides/environment-variables), [gitignore template](https://raw.githubusercontent.com/vercel/next.js/canary/packages/create-next-app/templates/app-tw/ts/gitignore) |
| `.editorconfig` | `root = true`, `charset = utf-8`, `end_of_line = lf`, `insert_final_newline`, กำหนด indent ของ `*.py` = 4 และ `*.{ts,tsx,json}` = 2 (ช่วยกัน CRLF บน Windows) | [editorconfig.org](https://editorconfig.org/) |
| `.gitignore` | รวมของ Next.js (`node_modules`, `.next/`, `.vercel`, `.env*`, `next-env.d.ts`) กับของ Python (`.venv/`, `__pycache__/`, `*.pyc`) และ**ข้อมูลดิบ** (`data/raw/`, `data/interim/`, `*.pdf`) รวมถึง `CLAUDE.local.md` | [gitignore template](https://raw.githubusercontent.com/vercel/next.js/canary/packages/create-next-app/templates/app-tw/ts/gitignore), [Claude memory docs](https://code.claude.com/docs/en/memory) |
| README | หัวข้อแนะนำ: ภาพรวม, สถาปัตยกรรมแบบย่อ, วิธีรันบนเครื่อง (web/pipeline), env, โครงสร้างโฟลเดอร์, ทีม/เครดิต/แหล่งข้อมูล | ข้อเสนอ (ไม่มีมาตรฐานทางการ) |
| `.github/workflows/*.yml` | ต้องอยู่ใน `.github/workflows` เท่านั้น ใช้ทำ CI ขั้นต่ำ: lint+typecheck (npm) และ pytest (uv) | [GitHub Actions quickstart](https://docs.github.com/en/actions/get-started/quickstart) |
| `CLAUDE.md` | วางที่ `./CLAUDE.md` หรือ `./.claude/CLAUDE.md`, `CLAUDE.local.md` สำหรับใช้ส่วนตัวให้ gitignore, ไฟล์ใน subdirectory โหลดเมื่อจำเป็น, `.claude/rules/*.md` ใช้แยกกฎตามหัวข้อหรือตาม path ได้ และ Claude Code อ่าน `AGENTS.md` ได้ด้วย (create-next-app สร้างไฟล์นี้ให้) | [Claude Code memory](https://code.claude.com/docs/en/memory) |

---

## 6. ข้อเสนอโครงสร้างแบบยืดหยุ่น (Plan A, single-root)

```
/                         ← repo root = Vercel project root
├─ app/                   หน้าเว็บ (App Router): / , /history , /demo  — ห้ามมี app/api/
│   └─ <route>/_components/   component เฉพาะหน้านั้น (private folder)
├─ components/            UI ที่ใช้ร่วมกันหลายหน้า (Tailwind เขียนเอง)
├─ lib/                   โค้ด TS ฝั่ง server/shared: db client (Neon), query, types, format วันที่ไทย
├─ public/                static assets (ไอคอน, รูปภูมิภาค)
├─ api/                   Python serverless entry เท่านั้น (บาง ๆ) เช่น summarize.py → /api/summarize
├─ src/<pkg>/             Python pipeline package (prep → classify → extract → generate) ใช้ร่วมกันทั้ง local และ api
├─ scripts/               CLI/สคริปต์รันบนเครื่อง: รัน pipeline ทั้งชุด, export JSON, load เข้า Neon
├─ models/                พารามิเตอร์โมเดลที่ train แล้ว (JSON เล็ก ๆ) ที่ api ต้องอ่าน — commit ได้
├─ db/                    schema.sql / migrations ของ Neon
├─ data/                  ข้อมูล (raw/ interim/ ถูก gitignore; มี README อธิบายแหล่งและวิธีได้มา)
├─ notebooks/             สำรวจข้อมูล/ทดลอง (ไม่ถูก deploy)
├─ tests/                 pytest ของ Python package (+ fixtures ข้อความตัวอย่างสั้น ๆ)
├─ docs/                  decisions/ (ADR), architecture.md, data/, report/
├─ research/              ผลค้นคว้า R1, R2, ... (อาจย้ายเข้า docs/research/ ภายหลัง)
├─ .github/workflows/     CI: lint/typecheck web + pytest
├─ .claude/ , CLAUDE.md   คำสั่งสำหรับ Claude Code (AGENTS.md ถ้า create-next-app สร้างมา)
├─ package.json, next.config.ts, tsconfig.json, eslint.config.mjs, postcss.config.mjs
├─ pyproject.toml (+ uv.lock), .python-version
├─ vercel.json            functions: excludeFiles / maxDuration / regions สำหรับ api/**/*.py
├─ .env.example, .editorconfig, .gitignore, README.md
```

| ส่วน | ความมั่นคง | อาจเปลี่ยนตอน build เพราะ |
|---|---|---|
| `app/`, `public/`, `components/`, `lib/` | คงที่ (เป็น convention ของ Next.js) | ถ้า feature เกิน 3 ให้ย้ายไปเป็น `features/<name>/` (ดูกฎ 7) |
| `api/` + `vercel.json` | **ไม่แน่นอน** ขึ้นอยู่กับผล spike | ถ้า spike ไม่ผ่านจะย้ายไป Plan B: `web/` + `pipeline/` ด้วย Services |
| `src/<pkg>/` | คงที่ในหลักการ | อาจเปลี่ยนเป็น flat `<pkg>/` ที่ root ถ้า import บน Vercel ง่ายกว่า |
| `models/` | อาจเปลี่ยน | ถ้าไฟล์ใหญ่หรือต้องเปลี่ยนบ่อย อาจไปเก็บใน DB แทน |
| `data/` โครงย่อย | ปรับได้ | ค่อยเพิ่ม `processed/`, `labels/` เมื่อจำเป็น |
| `research/` | ชั่วคราว | อาจรวมเข้า `docs/` |
| ชื่อ `<pkg>` | ยังไม่กำหนด | ตั้งตอน Phase 0 (ควรสั้น ตัวพิมพ์เล็ก เช่น `tmd_summary`) **[ข้อเสนอ]** |

**ทางเลือกที่ไม่แนะนำตอนนี้:** monorepo แบบ `apps/` + `packages/` (turborepo/pnpm workspace) เพราะใช้เครื่องมือเพิ่มโดยไม่จำเป็น และ Vercel ให้ทางเลือกแบบ "single framework" หรือ "Services" ที่ง่ายกว่าอยู่แล้ว ([Structure your application (2026-07-16)](https://vercel.com/kb/guide/structure-your-application))

---

## 7. กฎการเพิ่มโฟลเดอร์ใหม่ (ให้โครงสร้างโตได้โดยไม่รก)

| # | กฎ |
|---|---|
| 1 | **ก่อนสร้างโฟลเดอร์ระดับบนสุดใหม่** ให้ถามก่อนว่ามีโฟลเดอร์เดิมที่ใส่ได้หรือเปล่า ถ้าต้องสร้างจริงให้เขียน ADR สั้น ๆ และเพิ่มหนึ่งบรรทัดในตาราง README |
| 2 | **ชื่อโฟลเดอร์** ใช้ภาษาอังกฤษ ตัวพิมพ์เล็ก แยกคำด้วย `-` (ฝั่ง Python package ใช้ `_`) ห้ามมีช่องว่างหรือภาษาไทย (Vercel ไม่ให้ชื่อ function มีช่องว่าง) ([Limits](https://vercel.com/docs/functions/limitations)) |
| 3 | **โค้ดที่ใช้แค่หน้าเดียว** ให้วางใน `app/<route>/_components` หรือ `_lib` เมื่อมีหน้าที่สองต้องใช้ด้วยค่อยย้ายขึ้นไป `components/` หรือ `lib/` |
| 4 | **ทิศทาง import:** `components`/`lib` ห้าม import จาก `app/` และเมื่อมี `features/` แล้ว ห้าม feature import กันเอง (ตาม bulletproof-react) ([ref](https://github.com/alan2207/bulletproof-react/blob/master/docs/project-structure.md)) |
| 5 | **เกณฑ์การย้ายเป็น `features/`:** เมื่อ `components/` มีเกิน ~15 ไฟล์ หรือเริ่มมีหลาย domain ชัดเจน (เช่น forecast, history, demo) ให้ย้ายทีละ feature ไม่ต้องย้ายทั้งหมดในครั้งเดียว **[เกณฑ์เป็นข้อเสนอ]** |
| 6 | **`api/` มีแค่ entry file** ที่อ่าน request → เรียก `<pkg>` → ส่ง JSON กลับ ไม่มี logic อยู่ในนี้ ถ้ามี helper ให้ขึ้นต้นด้วย `_` |
| 7 | **Python:** logic ทั้งหมดอยู่ใน `src/<pkg>/<stage>/` สคริปต์ใน `scripts/` มีหน้าที่แค่เรียกใช้ package ส่วน test วางคู่กับ stage ใน `tests/<stage>/` |
| 8 | **ข้อมูล:** ไฟล์ข้อมูลใหม่ทุกไฟล์ต้องอยู่ใต้ `data/` ซึ่งถูก ignore ไว้แล้ว ยกเว้น fixture เล็ก (<100 KB) ใน `tests/fixtures/` และพารามิเตอร์โมเดลใน `models/` |
| 9 | **ไฟล์ที่ deploy:** เมื่อเพิ่มโฟลเดอร์ที่ Python function ไม่ต้องใช้ ให้เพิ่มเข้า `excludeFiles` ใน `vercel.json` ด้วยเสมอ |
| 10 | **เอกสาร:** การตัดสินใจเชิงสถาปัตยกรรมทุกเรื่องให้บันทึกเป็น `docs/decisions/NNNN-ชื่อ.md` ห้ามลบ ADR เก่า แต่ให้ mark ว่า superseded |
| 11 | **ทบทวนทุกจบ Phase:** ลบโฟลเดอร์ที่ว่างหรือไม่ได้ใช้ และอัปเดตตารางใน README กับ `CLAUDE.md` ให้ตรงกับของจริง |

---

## สิ่งที่ยังไม่ได้ตรวจ

| # | เรื่อง | วิธีปิด |
|---|---|---|
| 1 | Python function บน Vercel (แบบ `api/`) มี project root อยู่ใน `sys.path` หรือไม่ และ Vercel ติดตั้งตัวโปรเจกต์เองจาก `pyproject.toml` ด้วยหรือเปล่า | Spike deploy |
| 2 | ถ้าโปรเจกต์ framework = Next.js และมี `pyproject.toml` ที่ root ยังได้ `api/*.py` เป็น function ตามปกติไหม และ preset detection ทำงานอย่างไร | Spike deploy |
| 3 | ไฟล์ dependency ของ `api/*.py` ต้องอยู่ที่ root หรือใน `api/` และถ้ามีทั้ง `pyproject.toml` กับ `requirements.txt` Vercel เลือกไฟล์ไหน | Spike / ถาม community |
| 4 | glob ใน `excludeFiles` ตัด `node_modules/**` และ `.next/**` ออกจาก Python bundle ได้จริงไหม | ดู build log ด้วย `VERCEL_ANALYZE_BUILD_OUTPUT=1` |
| 5 | ขนาดจริงของ PyThaiNLP (รวม dictionary ของ newmm) และ PDF lib ใน bundle รวมถึงเวลา cold start | Spike |
| 6 | Services ตั้ง `root` เป็น repo root (`./`) ให้ Next.js ได้ไหม และ service หนึ่ง import โค้ดนอก root ของตัวเองได้หรือไม่ (เพื่อดูว่า Plan B ยังเป็น single-root ได้ไหม) | อ่าน Services docs เพิ่มหรือ spike |
| 7 | Rewrite เฉพาะตอน dev ใน `next.config` ไปยัง Python server บนเครื่องยังใช้ได้กับ Next 16/Turbopack ไหม และ `vercel dev` บน Windows เสิร์ฟ `api/*.py` ได้ไหม | ลองบนเครื่องทีม |
| 8 | เลข patch ล่าสุดของ Next.js (16.x) | `npm view next version` |
| 9 | Repo ของ Vercel template "Next.js FastAPI Starter" อยู่ที่ไหนจริง (ลิงก์ `vercel/examples/python/nextjs-fastapi` ได้ 404) | เปิดจากหน้า template |
| 10 | การเปลี่ยน default region บน Hobby (เช่นเป็น `sin1`) ใช้ขั้นตอนไหน และ Neon ฟรีมี region ใกล้ไทยตรงกันไหม | อ่าน region docs + Neon docs (อยู่ใน research ฉบับอื่น) |
| 11 | ไม่ได้เปิดอ่าน repo ของ bulletproof-react ส่วน Next.js App Router (`apps/`) ลงรายละเอียด และไม่ได้อ่านบทความ Unkey RFC (เปิดไม่ได้) | ไม่จำเป็นต่อการตัดสินใจตอนนี้ |
