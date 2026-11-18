# R4 — Engineering conventions สำหรับ skills/docs ของโปรเจกต์

> ค้นคว้าเมื่อ 2026-11-16 · ทุกข้ออ้างมีลิงก์ · วันที่/เวอร์ชันใส่ไว้เมื่อหน้าเว็บแสดง · `[unverified]` = ยังไม่ได้ยืนยันกับแหล่งต้นทางโดยตรง
> ขอบเขต: research only (ไม่ install, ไม่แตะ git)

---

## 0. สรุปสั้น (TL;DR)

- **Comment = อธิบาย "ทำไม" ไม่ใช่ "ทำอะไร"** — ถ้าโค้ดต้องมี comment บอกว่าทำอะไร ให้ทำโค้ดให้ง่ายขึ้นแทน (ยกเว้น regex/อัลกอริทึมซับซ้อน) ([Google eng-practices](https://google.github.io/eng-practices/review/reviewer/looking-for.html))
- **Comment ภาษาไทยทำได้อย่างมีเหตุผล**: PEP 8 ยอมรับว่าเขียน comment ภาษาอื่นได้ถ้าโค้ดจะไม่ถูกอ่านโดยคนที่ไม่รู้ภาษานั้น ([PEP 8](https://peps.python.org/pep-0008/)) แต่ **identifier ต้องเป็น ASCII/อังกฤษ** ([Google TS guide](https://google.github.io/styleguide/tsguide.html), [PEP 8](https://peps.python.org/pep-0008/))
- **Next.js แนะนำ Data Access Layer (DAL) สำหรับโปรเจกต์ใหม่** + `server-only` + ส่ง DTO น้อยที่สุดไป Client Component ([Next.js Data Security, lastUpdated 2026-10-06](https://nextjs.org/docs/app/guides/data-security))
- **Contract Python↔TS ที่ประหยัดที่สุด**: Pydantic → JSON Schema (Draft 2020-12) → `json-schema-to-typescript` (ได้ type) หรือ Zod `z.fromJSONSchema()` (ยัง experimental) ([Pydantic](https://pydantic.dev/docs/validation/latest/concepts/json_schema/), [json-schema-to-typescript](https://github.com/bcherny/json-schema-to-typescript), [Zod](https://zod.dev/json-schema))
- **Agent workflow**: ให้ agent มี "check ที่รันแล้วได้ pass/fail" เสมอ, CLAUDE.md สั้น (<200 บรรทัด), กฎที่ไม่มีข้อยกเว้นให้ใช้ hook, ทำทีละ feature + progress file + feature list ที่มีสถานะ `passes` ([Claude Code best practices](https://code.claude.com/docs/en/best-practices), [Memory docs](https://code.claude.com/docs/en/memory), [Anthropic: Effective harnesses, 2025-11-26](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents))
- **ไม่ over-engineer**: YAGNI + Rule of Three + "duplication is far cheaper than the wrong abstraction" ([Fowler 2015](https://martinfowler.com/bliki/Yagni.html), [Rule of three](https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming)), [Sandi Metz 2016](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction))

---

## 1. Code comments policy

### 1.1 หลักจากแหล่งทางการ

| หลัก | รายละเอียด | แหล่ง |
|---|---|---|
| Why > What | Comment ควรอธิบายว่า *ทำไม* โค้ดนี้มีอยู่ ไม่ใช่อธิบายว่าทำอะไร; ถ้าต้องอธิบาย what แปลว่าควร simplify โค้ด (ยกเว้น regex, อัลกอริทึมซับซ้อน) | [Google eng-practices: What to look for](https://google.github.io/eng-practices/review/reviewer/looking-for.html) |
| อย่าบรรยายโค้ด | Python guide 3.8.5: "never describe the code" — สมมติว่าคนอ่านรู้ Python ดีกว่าเรา | [Google Python Style Guide §3.8.5](https://google.github.io/styleguide/pyguide.html) |
| Comment ที่ขัดกับโค้ดแย่กว่าไม่มี | "Comments that contradict the code are worse than no comments" — แก้โค้ดต้องแก้ comment ด้วย | [PEP 8](https://peps.python.org/pep-0008/) |
| Inline comment ใช้น้อย | เว้น ≥2 space จากโค้ด, ไม่บอกสิ่งที่เห็นชัดอยู่แล้ว | [PEP 8](https://peps.python.org/pep-0008/) |
| Docstring สำหรับ public API | Module, exported function/class, public method ควรมี docstring; ใช้ `"""` ; บรรทัดแรกเป็นประโยคคำสั่ง (imperative) จบด้วยจุด; ไม่ซ้ำ signature | [PEP 257](https://peps.python.org/pep-0257/) |
| Docstring แบบ Google | ใส่ `Args:` / `Returns:` / `Raises:` เมื่อมีประโยชน์; ต้องพอให้ "เขียนการเรียกฟังก์ชันได้โดยไม่ต้องอ่านโค้ดข้างใน" | [Google Python §3.8.3](https://google.github.io/styleguide/pyguide.html) |
| JSDoc vs `//` (TS) | `/** */` = สิ่งที่ *ผู้ใช้* โค้ดต้องอ่าน; `//` = เรื่อง implementation; comment หลายบรรทัดใช้ `//` หลายบรรทัด ไม่ใช้ `/* */` | [Google TS Style Guide](https://google.github.io/styleguide/tsguide.html) |
| ไม่ใส่ type ใน JSDoc | "JSDoc type annotations are redundant in TypeScript source code" — `@param`/`@return` ใส่เฉพาะเมื่อเพิ่มข้อมูล | [Google TS Style Guide](https://google.github.io/styleguide/tsguide.html) |
| Document top-level exports | ทุก export ระดับบนสุดควรมีคำอธิบายที่ไม่ใช่แค่ทวนชื่อ | [Google TS Style Guide](https://google.github.io/styleguide/tsguide.html) |
| catch ว่างต้องอธิบาย | ถ้า `catch` ไม่ทำอะไร ต้องมี comment บอกเหตุผล | [Google TS Style Guide](https://google.github.io/styleguide/tsguide.html) |
| TODO format | `TODO(link-or-bug): คำอธิบาย` — ใช้ลิงก์ issue ไม่ใช้ชื่อคน | [Google Python §3.12](https://google.github.io/styleguide/pyguide.html) |
| TSDoc | มาตรฐาน doc comment ของ TS (Microsoft) — tags หลัก `@param`, `@returns`, `@remarks`, `@example`, `@deprecated`; มี `eslint-plugin-tsdoc` | [tsdoc.org](https://tsdoc.org/) |

### 1.2 Comment ภาษาไทยในซอร์สโค้ด

**ข้อเท็จจริงด้านเทคนิค**
- Python 3 ใช้ UTF-8 เป็น default source encoding (PEP 3120, Final) → ไม่ต้องใส่ `# -*- coding: utf-8 -*-` ([PEP 3120](https://peps.python.org/pep-3120/), [PEP 8](https://peps.python.org/pep-0008/))
- Google JS guide: source file ต้อง encode เป็น UTF-8; ใช้อักขระ Unicode จริงหรือ escape แล้วแต่อันไหนอ่านง่ายกว่า ([Google JS Style Guide §2.2, §2.3.3](https://google.github.io/styleguide/jsguide.html))
- **Windows gotcha**: ก่อน Python 3.15 การ `open()` บน Windows ใช้ encoding ตาม locale (เช่น cp874 สำหรับไทย `[unverified ชื่อ codepage]`); PEP 686 ทำให้ UTF-8 mode เป็น default ตั้งแต่ Python 3.15 แต่ PEP ยังแนะนำให้ระบุ `encoding="utf-8"` ชัดเจน ([PEP 686](https://peps.python.org/pep-0686/))
- **JSON ภาษาไทย**: `json.dumps` default `ensure_ascii=True` จะ escape ไทยเป็น `\uXXXX` → ใช้ `ensure_ascii=False` ถ้าอยากให้ไฟล์อ่านได้ ([Python json docs](https://docs.python.org/3/library/json.html))
- **Identifier**: Google TS guide กำหนด identifier ใช้ ASCII letters/digits/underscore เท่านั้น; PEP 8 บังคับ ASCII สำหรับ stdlib และแนะนำคำอังกฤษ ([Google TS](https://google.github.io/styleguide/tsguide.html), [PEP 8](https://peps.python.org/pep-0008/)) → **ชื่อตัวแปร/ฟังก์ชัน/ไฟล์เป็นอังกฤษเสมอ comment/docstring เป็นไทย**
- **ภาษาของ comment**: PEP 8 แนะนำ comment เป็นอังกฤษ *ยกเว้น* แน่ใจว่าโค้ดจะไม่ถูกอ่านโดยคนที่ไม่พูดภาษานั้น ([PEP 8](https://peps.python.org/pep-0008/)) → ทีมไทย + ผู้ตรวจไทย = เข้าเงื่อนไข

**Tooling กับข้อความไทย**
- **Prettier ไม่จัดรูป/ไม่ wrap เนื้อหา comment** ("left as-is") และ `printWidth` เป็น guideline ไม่ใช่ hard limit ([Prettier rationale](https://prettier.io/docs/rationale))
- **Ruff `line-length`** (default 88): นับจำนวนอักขระ ยกเว้นบรรทัดที่มี East Asian characters/emoji จะนับตาม unicode width ([Ruff settings](https://docs.astral.sh/ruff/settings/)); มี issue ว่า E501 แจ้งเตือนเกินจริงกับอักษรจีน ([ruff#3902](https://github.com/astral-sh/ruff/issues/3902))
- ภาษาไทยไม่ใช่ East Asian wide → Ruff น่าจะนับเป็น "จำนวนอักขระ (code point)" ซึ่งรวมสระ/วรรณยุกต์ที่เป็น combining mark (กว้าง 0 บนจอ) → บรรทัดไทยถูกนับยาวกว่าที่ตาเห็น `[unverified — อนุมานจาก doc + UAX#11]`; ไลบรารี width หลายตัวมีปัญหากับ Thai spacing marks (Mc) ([wcwidth spec](https://wcwidth.readthedocs.io/en/stable/_sources/specs.rst.txt), [string-width issue](https://oss.issuehunt.io/r/sindresorhus/string-width?tab=closed))
- **ข้อเสนอเชิงปฏิบัติ**: comment ไทยให้อยู่บรรทัดของตัวเอง (ไม่ต่อท้ายโค้ดยาว ๆ), ตัดประโยคเอง, ถ้า E501 รบกวนเฉพาะ comment ไทยให้ผ่อน line-length หรือ ignore E501 (Ruff doc แสดง `ignore = ["E501"]`) ([Ruff settings](https://docs.astral.sh/ruff/settings/))

### 1.3 Comment policy ที่เสนอ (ร่าง)

1. ภาษา: comment/docstring เป็น **ไทย** สั้น กระชับ; ศัพท์เทคนิคคงเป็นอังกฤษ (เช่น "แคช DTO ไว้ต่อ request") — [PEP 8](https://peps.python.org/pep-0008/)
2. Identifier, ชื่อไฟล์, commit message, log message เป็น **อังกฤษ/ASCII** — [Google TS](https://google.github.io/styleguide/tsguide.html), [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
3. เขียน comment เมื่อ: เหตุผลไม่ชัดจากโค้ด, workaround, ข้อจำกัดภายนอก (เช่น รูปแบบรายงาน), regex, สูตร ML — [Google eng-practices](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
4. ห้าม comment ที่ทวนโค้ด/ทวนชื่อ/ทวน type — [Google TS](https://google.github.io/styleguide/tsguide.html), [Google Python §3.8.5](https://google.github.io/styleguide/pyguide.html)
5. Public function ใน `lib/` และ pipeline step: docstring/JSDoc 1 บรรทัด (สิ่งที่ทำ + input/output สำคัญ) — [PEP 257](https://peps.python.org/pep-0257/), [Google TS](https://google.github.io/styleguide/tsguide.html)
6. Python docstring: `"""ประโยคเดียวจบ."""`; ใส่ `Args/Returns/Raises` เฉพาะเมื่อไม่ชัดจาก type hint — [Google Python §3.8.3](https://google.github.io/styleguide/pyguide.html)
7. TS: `/** */` บน export, `//` ในตัวฟังก์ชัน, ไม่ใส่ `{type}` ใน JSDoc — [Google TS](https://google.github.io/styleguide/tsguide.html)
8. TODO: `TODO(#issue หรือ phase-N): ...` ไม่ใส่ชื่อคน — [Google Python §3.12](https://google.github.io/styleguide/pyguide.html)
9. `catch`/`except` ที่กลืน error ต้องมี comment บอกเหตุผล — [Google TS](https://google.github.io/styleguide/tsguide.html)
10. แก้โค้ด = ตรวจ comment รอบ ๆ ด้วย; comment ล้าสมัยให้ลบ — [PEP 8](https://peps.python.org/pep-0008/), [Google eng-practices](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
11. ไฟล์ทั้งหมด UTF-8 (ไม่มี BOM `[unverified ว่า tool ใดมีปัญหากับ BOM]`); Python เปิดไฟล์ด้วย `encoding="utf-8"` เสมอ — [PEP 686](https://peps.python.org/pep-0686/)
12. Comment ไทยวางบรรทัดของตัวเอง ไม่ต่อท้ายบรรทัดโค้ดยาว — อนุมานจาก [Ruff settings](https://docs.astral.sh/ruff/settings/), [PEP 8](https://peps.python.org/pep-0008/)

---

## 2. Naming, file/function size, modularity

### 2.1 Naming

| | TypeScript | Python |
|---|---|---|
| Type/Class/Interface | `UpperCamelCase` (ไม่มี prefix `I`) | `CapWords`; exception ลงท้าย `Error` |
| ตัวแปร/ฟังก์ชัน/property | `lowerCamelCase` | `lower_with_under` |
| ค่าคงที่ global | `CONSTANT_CASE` | `CAPS_WITH_UNDER` |
| Private | ไม่ใช้ `_` นำหน้า (ใช้ `private`/ไม่ export) | `_single_leading` |
| ตัวย่อ | ถือเป็นคำเดียว: `loadHttpUrl` | หลีกเลี่ยงตัวย่อที่คนนอกไม่รู้ |
| แหล่ง | [Google TS](https://google.github.io/styleguide/tsguide.html) | [PEP 8](https://peps.python.org/pep-0008/), [Google Python §3.16](https://google.github.io/styleguide/pyguide.html) |

- Google Python: ไม่ฝัง type ในชื่อ (`id_to_name_dict`), หลีกเลี่ยงชื่อตัวเดียวยกเว้น counter/`e`/`f` ([Google Python §3.16](https://google.github.io/styleguide/pyguide.html))
- **ชื่อไฟล์ TS**: Google ใช้ `snake_case` แต่ตัวอย่างใน Next.js docs ใช้ kebab-case เช่น `app/ui/like-button.tsx` ([Next.js Server & Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components)) → เลือก kebab-case ให้เข้ากับ ecosystem Next.js และใช้สม่ำเสมอ (Next.js บอกเองว่า "unopinionated" ให้เลือกแล้ว consistent — [Project structure](https://nextjs.org/docs/app/getting-started/project-structure))
- **Exports**: Google TS: ใช้ named export, ห้าม default export, export เฉพาะที่ใช้ข้างนอก, ห้าม `export let`, ใช้ `import type` ([Google TS](https://google.github.io/styleguide/tsguide.html)). ข้อยกเว้น: ไฟล์ convention ของ Next.js (`page.tsx`, `layout.tsx` ฯลฯ) ต้อง `export default` ตามตัวอย่างใน docs ([Next.js docs](https://nextjs.org/docs/app/getting-started/server-and-client-components))

### 2.2 ขนาดไฟล์/ฟังก์ชัน และ modularity

- **ไม่มีตัวเลขทางการสำหรับขนาดฟังก์ชัน/ไฟล์** ในแหล่งที่ตรวจ; สิ่งที่ใกล้ที่สุดคือขนาด change: ~100 บรรทัดสมเหตุสมผล, ~1000 มักใหญ่เกิน ([Google: Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html)) → ตัวเลขในกฎของเราเป็น **heuristic ของทีม** ไม่ใช่มาตรฐาน
- **Over-engineering**: reviewer ควรจับโค้ดที่ generic เกินจำเป็น/เพิ่ม functionality ที่ยังไม่ใช้ — "solve the problem they know needs to be solved now" ([Google eng-practices](https://google.github.io/eng-practices/review/reviewer/looking-for.html))
- **YAGNI**: feature ล่วงหน้ามีต้นทุน build/delay/carry/repair; แต่ YAGNI ใช้ได้เมื่อโค้ดแก้ง่าย (refactoring + self-testing code) ([Fowler, 2015-05-26](https://martinfowler.com/bliki/Yagni.html))
- **Rule of three** (Don Roberts ผ่าน Fowler *Refactoring*): ครั้งที่ 3 ค่อย refactor; เป็น heuristic ไม่ใช่กฎตายตัว ([Wikipedia](https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming)), [understandlegacycode](https://understandlegacycode.com/blog/refactoring-rule-of-three/))
- **Wrong abstraction**: "duplication is far cheaper than the wrong abstraction" — ถ้า abstraction เริ่มมี parameter + if เพิ่มเรื่อย ๆ ให้ inline กลับแล้วค่อย extract ใหม่ ([Sandi Metz, 2016-01-20](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction))
- **Pure functions**: React กำหนดว่า component ต้อง pure (input เดียวกัน → JSX เดียวกัน, ไม่แก้ตัวแปรที่มีอยู่ก่อน render); side effect ไปอยู่ใน event handler, `useEffect` เป็นทางเลือกสุดท้าย ([React: Keeping Components Pure](https://react.dev/learn/keeping-components-pure))
- **Dependency direction (UI → lib → data)**: Next.js แนะนำ DAL เป็น "internal library" ที่รันเฉพาะ server, ตรวจสิทธิ์, คืน DTO; และ "only the Data Access Layer should access `process.env`" ([Next.js Data Security](https://nextjs.org/docs/app/guides/data-security)) → ทิศทาง `app/` (route/UI) → `lib/` (pure logic) → `data/`/DAL (DB, env) ; ชั้นล่างห้าม import ชั้นบน `[ทิศทาง lib↔data เป็นข้อเสนอของเรา]`
- **Mixing approaches**: Next.js แนะนำ "choosing one data fetching approach and avoiding mixing them" ([Next.js Data Security](https://nextjs.org/docs/app/guides/data-security))
- **ความสม่ำเสมอ**: เมื่อ guide ไม่ได้ระบุ ให้ทำตามโค้ดในไฟล์/โฟลเดอร์เดียวกัน; style fix แยกจาก change ที่ไม่เกี่ยว ([Google TS – Policies](https://google.github.io/styleguide/tsguide.html))

---

## 3. React/Next.js component design (App Router)

- **Presentational vs container**: Dan Abramov (ผู้เผยแพร่ pattern นี้ ปี 2015) เพิ่ม update ปี 2019 ว่าไม่แนะนำให้แยก component แบบนี้อีกแล้ว (hooks แทนได้) ([Medium original](https://medium.com/@dan_abramov/7ca2f9a7c7d0) — ต้นฉบับโหลดไม่ได้ (403), ข้อความยืนยันผ่าน [LogRocket](https://blog.logrocket.com/?p=3608) `[partially verified]`)
- **ใน App Router รูปแบบใหม่ที่ใกล้เคียง** = Server Component (ดึงข้อมูล) ส่ง props ให้ Client Component (interactive) — ตัวอย่าง `Page` ดึง `getPost()` แล้วส่ง `likes` ให้ `<LikeButton>` ([Next.js Server & Client Components, lastUpdated 2026-10-05](https://nextjs.org/docs/app/getting-started/server-and-client-components))
- ใช้ Client Component เมื่อต้องการ state/event handler, lifecycle (`useEffect`), browser API, custom hooks; ใช้ Server Component เมื่อดึงข้อมูล, ใช้ secret, ลด JS, ปรับ FCP (แหล่งเดียวกัน)
- **ดัน `'use client'` ลงล่างสุด**: ใส่เฉพาะไฟล์ interactive; ทุกอย่างที่ไฟล์ `'use client'` import จะเข้า client bundle (แหล่งเดียวกัน)
- **Props ที่ส่งเข้า Client Component ต้อง serializable** (แหล่งเดียวกัน); ส่งเฉพาะ field ที่ต้องใช้ — Next.js ชี้ว่า props interface ที่รับ object ใหญ่เกินเป็น "bad props interface" ([Data Security](https://nextjs.org/docs/app/guides/data-security))
- **Interleaving / composition**: ส่ง Server Component เป็น `children` ของ Client Component ได้ (slot pattern เช่น `<Modal><Cart/></Modal>`) ([Next.js](https://nextjs.org/docs/app/getting-started/server-and-client-components)); React docs: component ที่มี `children` เหมือนมี "hole" ให้ parent เติม — เหมาะกับ wrapper (panel, grid) ([React: Passing Props](https://react.dev/learn/passing-props-to-a-component))
- **Spread props ใช้อย่างประหยัด**: "If you're using it in every other component, something is wrong" — มักแปลว่าควรแยก component และส่ง children ([React: Passing Props](https://react.dev/learn/passing-props-to-a-component))
- **Context provider**: เป็น Client Component ที่รับ `children` และวาง "as deep as possible" ([Next.js](https://nextjs.org/docs/app/getting-started/server-and-client-components))
- **`server-only`**: import ในไฟล์ที่มี secret/DB → build error ถ้าถูก import ฝั่ง client ([Next.js](https://nextjs.org/docs/app/getting-started/server-and-client-components))
- **Data fetching/business logic อยู่ที่ไหน**: DAL สำหรับโปรเจกต์ใหม่ (server-only, auth check, คืน DTO), Server Action บาง ๆ แล้ว delegate ไป DAL, validate input ทุกครั้ง, ไม่ทำ mutation ระหว่าง render ([Data Security](https://nextjs.org/docs/app/guides/data-security))
- **Folder**: Next.js "unopinionated"; มี 3 กลยุทธ์ (ไฟล์อยู่นอก `app`, อยู่ใน top-level ของ `app`, แยกตาม feature/route); `_folder` = private ไม่ถูก route; `(group)` = จัดกลุ่มไม่กระทบ URL; "choose a strategy … and be consistent" ([Project structure, lastUpdated 2026-07-21](https://nextjs.org/docs/app/getting-started/project-structure))
- **Variants ด้วย cva**: `cva(base, { variants, compoundVariants, defaultVariants })` ให้ class ตาม props แบบ type-safe; cva@1.0 อยู่ในสถานะ beta ([cva docs](https://cva.style/docs), [Variants](https://cva.style/docs/getting-started/variants)); รวม class ที่ชนกันด้วย `tailwind-merge` (`twMerge` — ตัวหลังชนะ; รองรับ Tailwind v4.0–4.3) ([tailwind-merge](https://github.com/dcastil/tailwind-merge)). การใช้คู่กับ `clsx` เป็น pattern ทั่วไป `[unverified ในแหล่งทางการ]`
- **Accessibility**: "No ARIA is better than Bad ARIA" ([WAI-ARIA APG](https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/)); First Rule of ARIA = ใช้ native HTML element ที่มี semantics/behavior ในตัวก่อน, และ interactive ARIA control ต้องใช้ keyboard ได้ ([W3C Using ARIA](https://www.w3.org/TR/using-aria/) — หมายเหตุ: เอกสารสถานะ Discontinued Draft, 2026-02-24)
- **Lint**: `eslint-config-next/core-web-vitals` (+ `/typescript`) แนะนำสำหรับโปรเจกต์ส่วนใหญ่; `next lint` ถูกถอดตั้งแต่ Next.js 16 → ใช้ ESLint CLI ([Next.js ESLint, lastUpdated 2026-10-15](https://nextjs.org/docs/app/api-reference/config/eslint)). หน้า reference ระบุ recommended rules จาก react, react-hooks, next — ไม่ได้ระบุ jsx-a11y ชัดเจน `[unverified ว่ารวม jsx-a11y หรือไม่]`; ใช้คู่ Prettier ผ่าน `eslint-config-prettier` (แหล่งเดียวกัน)
- **Rule ใน plugin**: `@next/next/no-async-client-component` — Client Component ห้ามเป็น async (แหล่งเดียวกัน)

---

## 4. Python pipeline design

- **Typed data models**: Pydantic `BaseModel.model_json_schema()` สร้าง JSON Schema (Draft 2020-12 / OpenAPI 3.1); มี `mode='validation'` vs `'serialization'` ([Pydantic JSON Schema](https://pydantic.dev/docs/validation/latest/concepts/json_schema/)). สำหรับข้อมูลภายในที่ไม่ต้อง validate ใช้ `@dataclass(frozen=True)` ได้ ([Python dataclasses](https://docs.python.org/3/library/dataclasses.html)) → ข้อเสนอ: Pydantic ที่ "ขอบ" (input/output/contract), dataclass ภายในถ้าต้องการเบา `[ข้อเสนอของเรา]`
- **Type annotations**: ใส่ใน public API, ใช้ `X | None` ([Google Python §2.21, §3.19](https://google.github.io/styleguide/pyguide.html))
- **Pure transformation steps**: แนวคิดเดียวกับ React purity — input เดียวกันได้ output เดียวกัน, ไม่แก้ state ภายนอก ([React](https://react.dev/learn/keeping-components-pure)); แยก I/O (อ่าน/เขียนไฟล์) ไว้ขอบนอก ("functional core, imperative shell" — [Destroy All Software](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell) `[เนื้อหา screencast ไม่ได้ตรวจ]`)
- **Configuration แยกจากโค้ด**: 12-Factor: config คือสิ่งที่ต่างกันระหว่าง deploy (credential, DB URL) เก็บใน env; litmus test = เปิด repo เป็น public ได้โดยไม่หลุด credential; ค่าภายใน app ไม่นับเป็น config ([12factor.net/config](https://12factor.net/config)) → ค่า hyperparameter/path ของ pipeline ใส่ไฟล์ config (เช่น YAML/TOML) แยก, secret ใส่ `.env` `[ข้อเสนอของเรา]`; Next.js ระบุ `.env*` ไม่ควร track ใน git ([Project structure](https://nextjs.org/docs/app/getting-started/project-structure))
- **Deterministic outputs**: `json.dumps(..., sort_keys=True, ensure_ascii=False, indent=2)` — Python docs ระบุ `sort_keys` "useful for regression tests" ([Python json](https://docs.python.org/3/library/json.html)); fix random seed + เรียง input file ตามชื่อ `[ข้อเสนอของเรา]`
- **Logging vs print**: `print()` สำหรับ output ปกติของ CLI; `logger.info/debug` สำหรับเหตุการณ์ระหว่างทำงาน; error ที่ควร raise ให้ raise; ใช้ `logger = logging.getLogger(__name__)`; library ไม่ควรเพิ่ม handler นอกจาก `NullHandler` ([Logging HOWTO, Python 3.15 docs](https://docs.python.org/3/howto/logging.html)); เรียก log ด้วย string literal + `%s` ไม่ใช่ f-string ([Google Python §3.10.1](https://google.github.io/styleguide/pyguide.html))
- **Error handling**: ใช้ built-in exception (`ValueError`) สำหรับ precondition, ห้ามใช้ `assert` validate, ห้าม bare `except:`, `try` block สั้นที่สุด ([Google Python §2.4.4](https://google.github.io/styleguide/pyguide.html))
- **Line length**: PEP 8 = 79 (ทีมตกลงได้ถึง 99), Google = 80, Ruff default = 88 ([PEP 8](https://peps.python.org/pep-0008/), [Google Python §3.2](https://google.github.io/styleguide/pyguide.html), [Ruff](https://docs.astral.sh/ruff/settings/)) → เลือก Ruff default 88 แล้วจบ
- **Golden-file / snapshot tests**:
  - `syrupy` 7.x: fixture `snapshot`, `assert actual == snapshot`, `pytest --snapshot-update`, เก็บใน `__snapshots__/` และ commit ด้วย; มี `JSONSnapshotExtension`; ต้องการ Python 3.11+, pytest 8+ ([syrupy](https://syrupy-project.github.io/syrupy/))
  - `pytest-regressions`: `data_regression.check(data)`, regenerate ด้วย `--force-regen`, ไฟล์ expected ต้อง commit ([pytest-regressions](https://pytest-regressions.readthedocs.io/en/latest/overview.html))
  - ทางเลือกไม่ต้องติดตั้งเพิ่ม: เขียนเทียบไฟล์ JSON ใน `tests/golden/` เอง (ประหยัด dependency) `[ข้อเสนอของเรา]`

---

## 5. Shared contracts ระหว่าง Python ↔ TypeScript

| แนวทาง | Flow | ข้อดี | ข้อเสีย | แหล่ง |
|---|---|---|---|---|
| **A. Pydantic เป็น source of truth** | Pydantic → `model_json_schema()` → JSON Schema → `json2ts` → `.d.ts` | Python เป็นฝั่งผลิตข้อมูลอยู่แล้ว; schema Draft 2020-12 | ได้แค่ *type* (ไม่มี runtime validation ฝั่ง TS); `json2ts` ไม่แปล `minimum/pattern` ฯลฯ | [Pydantic](https://pydantic.dev/docs/validation/latest/concepts/json_schema/), [json-schema-to-typescript](https://github.com/bcherny/json-schema-to-typescript) |
| A′. `pydantic-to-typescript` | `pydantic2ts --module ... --output ...` | คำสั่งเดียว | ต้องมี `json2ts` ติดตั้งอยู่ดี; repo เล็ก (437 stars) | [pydantic-to-typescript](https://github.com/phillipdupuis/pydantic-to-typescript) |
| **B. JSON Schema ไฟล์เป็น source of truth** | `schema/*.json` → `datamodel-codegen` (Python) + `json2ts` (TS) | ภาษากลาง ไม่ผูกฝั่งใด | ต้องเขียน JSON Schema มือ; สอง generator | [datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator), [json-schema-to-typescript](https://github.com/bcherny/json-schema-to-typescript) |
| **C. Zod เป็น source of truth** | Zod → `z.toJSONSchema()` (Draft 2020-12 default) → `datamodel-codegen` | TS ได้ runtime validation | Python กลายเป็นฝั่งตาม; บาง type (date, transform, bigint) แปลงไม่ได้ | [Zod JSON Schema](https://zod.dev/json-schema) |
| D. JSON Schema → Zod | `z.fromJSONSchema()` | ได้ runtime validation จาก schema กลาง | **experimental** ไม่อยู่ใน stable API | [Zod JSON Schema](https://zod.dev/json-schema) |

- `zod-to-json-schema` **deprecated** ("As of November 2025 … no longer be actively maintained") → ใช้ Zod v4 native ([repo](https://github.com/StefanTerdell/zod-to-json-schema))
- `json-schema-to-typescript`: core model คือ draft 4; ignore `if/then/else`, `prefixItems`; ต้องใช้ Node ≥22.19 (16.x รองรับ Node 16–20) ([repo](https://github.com/bcherny/json-schema-to-typescript))
- `datamodel-code-generator`: input JSON Schema/OpenAPI ฯลฯ → output Pydantic v2, dataclasses, TypedDict, msgspec ([repo](https://github.com/koxudaxi/datamodel-code-generator))
- **ข้อเสนอสำหรับโปรเจกต์เล็ก**: แนวทาง A — Pydantic ใน pipeline เป็นต้นฉบับ, export JSON Schema เข้า `shared/schema/` แล้ว generate `.d.ts`; commit ไฟล์ที่ generate และมี check "regenerate แล้ว diff ต้องว่าง" ใน verification gate. ถ้าฝั่ง web ต้อง validate ข้อมูลจาก DB/upload ค่อยเขียน Zod เฉพาะจุดนั้น (rule of three) `[ข้อเสนอของเรา]`
- ทางเลือกที่ถูกที่สุด (0 tools): เขียน TS type มือ + contract test ที่โหลด JSON ตัวอย่างจาก pipeline มา parse — เหมาะถ้า schema มี <5 model `[ข้อเสนอของเรา]`

---

## 6. Workflow conventions

- **Conventional Commits 1.0.0**: `type(scope)!: description`; `feat`→MINOR, `fix`→PATCH, `BREAKING CHANGE:`/`!`→MAJOR; types อื่นจาก commitlint config-conventional: `build, chore, ci, docs, style, refactor, perf, test` ([conventionalcommits.org](https://www.conventionalcommits.org/en/v1.0.0/))
- **Small PRs/CLs**: "one self-contained change"; ~100 บรรทัดสมเหตุสมผล ~1000 ใหญ่เกิน; แยก refactor ออกจาก feature/bugfix; change ต้องมี test ([Google: Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html))
- **ADR (Nygard 2011)**: Title / Context / Decision ("We will …") / Status (proposed, accepted, deprecated, superseded) / Consequences; เลขรันต่อเนื่อง ไม่ reuse; ไม่ลบ ADR เก่าแต่ mark superseded ([Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html), [adr.github.io](https://adr.github.io/))
- **Testing pyramid**: unit เยอะ เร็ว, ชั้นกลางน้อยลง, E2E น้อยที่สุด; หลีกเลี่ยง "ice-cream cone"; ดัน test ลงชั้นล่างให้มากที่สุด ([Ham Vocke on martinfowler.com, 2018-02-26](https://martinfowler.com/articles/practical-test-pyramid.html))
- **Testing trophy** (ทางเลือกฝั่ง web): static → unit → integration (เยอะสุด) → E2E; "Write tests. Not too many. Mostly integration." ([Kent C. Dodds, 2021-06-03](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications))
- **Next.js testing**: Vitest/Jest สำหรับ unit, Playwright/Cypress สำหรับ E2E; async Server Components → แนะนำ E2E แทน unit ([Next.js Testing, lastUpdated 2026-02-03](https://nextjs.org/docs/app/guides/testing))
- **Agentic coding (Claude Code docs)**:
  - "Give Claude a check to run" — สิ่งที่รันแล้วได้ pass/fail (test, build exit code, linter, script diff กับ fixture, screenshot); บรรทัดที่มีค่าที่สุดใน CLAUDE.md คือคำสั่งรัน check ([Best practices](https://code.claude.com/docs/en/best-practices))
  - CLAUDE.md เก็บเฉพาะสิ่งที่ agent หาจากโค้ดเองไม่ได้: คำสั่ง test/typecheck/lint, จุดที่โค้ดหลอกตา, การตัดสินใจที่ไม่อยู่ใน repo, เรื่องที่ต้องแก้ซ้ำ 2 ครั้ง; target <200 บรรทัด ([Best practices](https://code.claude.com/docs/en/best-practices), [Memory](https://code.claude.com/docs/en/memory))
  - Instruction ต้อง "concrete enough to verify" เช่น "Use 2-space indentation" ไม่ใช่ "Format code properly" ([Memory](https://code.claude.com/docs/en/memory))
  - Procedure ของทีมใส่ใน skill (`.claude/skills/<name>/SKILL.md`) เพราะโหลดเต็มเฉพาะตอนใช้; กฎเฉพาะ path ใส่ `.claude/rules/` + `paths:` ([Best practices](https://code.claude.com/docs/en/best-practices))
  - กฎที่ "ไม่มีข้อยกเว้น" → hook/deny rule ไม่ใช่ CLAUDE.md; แต่อย่ามี hook เยอะ ([Best practices](https://code.claude.com/docs/en/best-practices))
  - ให้คนที่ไม่ได้เขียนโค้ดรีวิว (`/code-review` ใน subagent ใหม่) และ `/verify` รันแอปจริงหลังเสร็จ ([Best practices](https://code.claude.com/docs/en/best-practices))
  - เขียน SPEC.md แล้วเริ่ม session ใหม่จาก spec = "written definition of done" ([Best practices](https://code.claude.com/docs/en/best-practices))
- **Long-running agent harness (Anthropic, 2025-11-26)**: progress file + git history ให้ session ใหม่เข้าใจสถานะ; feature list เป็น JSON มี flag `passes` (เลือก JSON เพราะ model แก้ผิดน้อยกว่า Markdown); ทำทีละ feature; `init.sh` สตาร์ตแอปเพื่อ smoke test ก่อนเริ่มงาน; ทดสอบ end-to-end แบบผู้ใช้ก่อน mark done; commit เป็น checkpoint ([Effective harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents))
- **Definition of Done**: ไม่พบแหล่งมาตรฐานเดียวที่ตรวจแล้ว → DoD ด้านล่างประกอบจาก Google small CLs (มี test, docs อัปเดต) + Claude Code (check ผ่าน) + harness (E2E ก่อน mark passes) `[สังเคราะห์]`

---

## 7. Draft rule lists (ใช้ใส่ skills)

### 7.1 `code-quality-and-reuse` (16 ข้อ)

1. ชื่อ identifier/ไฟล์เป็นอังกฤษ ASCII; TS: `UpperCamelCase` type, `lowerCamelCase` ค่า, `CONSTANT_CASE` ค่าคงที่ global — [Google TS](https://google.github.io/styleguide/tsguide.html)
2. Python: `lower_with_under` / `CapWords` / `CAPS_WITH_UNDER`; private ด้วย `_` ตัวเดียว — [PEP 8](https://peps.python.org/pep-0008/)
3. ตัวย่อเป็นคำเดียว (`parseHtml`, `TmdReport`), ไม่ตัดตัวอักษรกลางคำ — [Google TS](https://google.github.io/styleguide/tsguide.html)
4. ไม่ฝัง type ในชื่อ (`items_list` ✗) — [Google Python §3.16](https://google.github.io/styleguide/pyguide.html)
5. TS ใช้ named export; `export default` เฉพาะไฟล์ convention ของ Next.js — [Google TS](https://google.github.io/styleguide/tsguide.html), [Next.js](https://nextjs.org/docs/app/getting-started/server-and-client-components)
6. Export เฉพาะสิ่งที่ใช้นอก module; ใช้ `import type` เมื่อใช้เป็น type อย่างเดียว — [Google TS](https://google.github.io/styleguide/tsguide.html)
7. ไม่สร้าง class รวม static method เพื่อจัดกลุ่ม — export ฟังก์ชันตรง ๆ — [Google TS](https://google.github.io/styleguide/tsguide.html)
8. ทิศทาง dependency: `app/` → `components/` → `lib/` (pure) → DAL/`data/` (server-only); ห้าม import ย้อนขึ้น — [Next.js Data Security](https://nextjs.org/docs/app/guides/data-security) `[ทิศทางละเอียดเป็นข้อเสนอ]`
9. Logic คำนวณเป็น pure function (ไม่มี I/O, ไม่แก้ argument) แยกจากโค้ดที่อ่าน/เขียน — [React purity](https://react.dev/learn/keeping-components-pure)
10. ทำเฉพาะสิ่งที่ต้องใช้ตอนนี้ — ไม่มี option/parameter "เผื่ออนาคต" — [Google eng-practices](https://google.github.io/eng-practices/review/reviewer/looking-for.html), [YAGNI](https://martinfowler.com/bliki/Yagni.html)
11. Rule of three: ซ้ำครั้งที่ 3 ค่อย extract เป็น helper กลาง — [Rule of three](https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming))
12. Abstraction ที่เริ่มมี flag/if ตามผู้เรียก → inline กลับแล้ว extract ใหม่ — [Sandi Metz](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)
13. ค้นหา helper เดิมใน `lib/` ก่อนเขียนใหม่ (ห้ามมีฟังก์ชันทำงานซ้ำสองที่) — [Google TS – Policies (ทำตามโค้ดเดิม)](https://google.github.io/styleguide/tsguide.html) `[สังเคราะห์]`
14. Config/secret แยกจากโค้ด; `process.env` อ่านเฉพาะใน DAL/ไฟล์ config — [12factor](https://12factor.net/config), [Next.js](https://nextjs.org/docs/app/guides/data-security)
15. ไฟล์/ฟังก์ชันเกินขนาดที่ทีมตกลง (เช่น ฟังก์ชัน ~40 บรรทัด, ไฟล์ ~200–300 บรรทัด) = สัญญาณให้แยก ไม่ใช่กฎตายตัว `[heuristic ของทีม — ไม่มีแหล่งทางการ]`; ขนาด change ~100 บรรทัด — [Google Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html)
16. Refactor/style แยก commit จาก feature/bugfix — [Google Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html), [Google TS – Policies](https://google.github.io/styleguide/tsguide.html)

### 7.2 `nextjs-component-architecture` (16 ข้อ)

1. Default = Server Component; ใส่ `'use client'` เฉพาะไฟล์ที่ต้องมี state/event/effect/browser API — [Next.js](https://nextjs.org/docs/app/getting-started/server-and-client-components)
2. ดัน client boundary ลงไปที่ leaf (เช่น ปุ่ม/ช่องค้นหา) ไม่ทำทั้ง layout เป็น client — [Next.js](https://nextjs.org/docs/app/getting-started/server-and-client-components)
3. ดึงข้อมูลใน Server Component (page/layout) ผ่าน DAL แล้วส่ง props ลงไป — [Next.js](https://nextjs.org/docs/app/getting-started/server-and-client-components)
4. DAL: `import 'server-only'`, คืน DTO เฉพาะ field ที่ UI ใช้ — [Data Security](https://nextjs.org/docs/app/guides/data-security)
5. Props ของ Client Component ต้อง serializable และแคบ (ไม่ส่ง DB row ทั้งก้อน) — [Next.js](https://nextjs.org/docs/app/getting-started/server-and-client-components), [Data Security](https://nextjs.org/docs/app/guides/data-security)
6. Server Action บาง: validate input → เรียก DAL → `revalidatePath`; คืนเฉพาะที่ UI ต้องใช้ — [Data Security](https://nextjs.org/docs/app/guides/data-security)
7. ห้าม mutation ระหว่าง render — [Data Security](https://nextjs.org/docs/app/guides/data-security), [React purity](https://react.dev/learn/keeping-components-pure)
8. Component เป็น pure: props เป็น read-only, side effect อยู่ใน event handler, `useEffect` เป็นทางสุดท้าย — [React](https://react.dev/learn/keeping-components-pure)
9. Composition > configuration: wrapper (Card, Panel, Section) รับ `children` แทนการเพิ่ม prop ทีละตัว — [React: Passing Props](https://react.dev/learn/passing-props-to-a-component)
10. ส่ง Server Component เป็น `children` ของ Client Component เมื่อต้องซ้อนกัน — [Next.js](https://nextjs.org/docs/app/getting-started/server-and-client-components)
11. ใช้ spread props เฉพาะ component ที่ forward ให้ native element (เช่น `Button` → `<button>`) — [React](https://react.dev/learn/passing-props-to-a-component)
12. Props type: `type XxxProps = {...}` ประกาศคู่ component; extend `React.ComponentProps<'button'>` เมื่อห่อ native element `[convention — ไม่ได้ตรวจแหล่งทางการ]`
13. Variants ด้วย `cva` + `VariantProps`; รวม className ด้วย `twMerge` เพื่อให้ caller override ได้ — [cva](https://cva.style/docs/getting-started/variants), [tailwind-merge](https://github.com/dcastil/tailwind-merge)
14. Native HTML ก่อน ARIA (`<button>`, `<a>`, `<label>`); ทุก control ใช้ keyboard ได้ — [W3C Using ARIA](https://www.w3.org/TR/using-aria/), [APG](https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/)
15. Context provider เป็น client wrapper รับ `children` วางลึกที่สุด — [Next.js](https://nextjs.org/docs/app/getting-started/server-and-client-components)
16. โครงสร้างโฟลเดอร์: เลือก 1 strategy (แนะนำ `app/` ไว้ route, `components/`, `lib/` นอก `app`) ใช้ `_private` / `(group)` ตามต้องการ และสม่ำเสมอ — [Project structure](https://nextjs.org/docs/app/getting-started/project-structure)

### 7.3 `python-pipeline-standards` (15 ข้อ)

1. แต่ละ step เป็นฟังก์ชัน pure: รับ data model → คืน data model; I/O อยู่ใน runner ชั้นนอก — [React purity (หลักเดียวกัน)](https://react.dev/learn/keeping-components-pure) `[ประยุกต์]`
2. Data model ที่ขอบ (input/output/contract) ใช้ Pydantic; ภายในใช้ `@dataclass(frozen=True)` ได้ — [Pydantic](https://pydantic.dev/docs/validation/latest/concepts/json_schema/), [dataclasses](https://docs.python.org/3/library/dataclasses.html)
3. Type hints ทุก public function; ใช้ `X | None` — [Google Python §2.21](https://google.github.io/styleguide/pyguide.html)
4. Docstring ไทย 1 บรรทัดสำหรับทุก step/public function — [PEP 257](https://peps.python.org/pep-0257/)
5. ค่า config (path, threshold, k, hyperparameter) อยู่ไฟล์ config แยก; secret อยู่ env/`.env` (ไม่ commit) — [12factor](https://12factor.net/config), [Next.js project structure (.env)](https://nextjs.org/docs/app/getting-started/project-structure)
6. เปิดไฟล์ด้วย `encoding="utf-8"` เสมอ — [PEP 686](https://peps.python.org/pep-0686/)
7. เขียน JSON ด้วย `ensure_ascii=False, sort_keys=True, indent=2` — [Python json](https://docs.python.org/3/library/json.html)
8. Output deterministic: fix seed, เรียง input, ไม่ใส่ timestamp ในไฟล์ผลลัพธ์ (หรือแยก metadata) `[ข้อเสนอ]` — สนับสนุนโดย [Python json (regression tests)](https://docs.python.org/3/library/json.html)
9. `logger = logging.getLogger(__name__)`; `print()` เฉพาะ output ที่ผู้ใช้ CLI ต้องเห็น — [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
10. Log ด้วย `logger.info("... %s", value)` ไม่ใช้ f-string — [Google Python §3.10.1](https://google.github.io/styleguide/pyguide.html)
11. Config logging ที่ entrypoint เท่านั้น; module อื่นไม่เพิ่ม handler — [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
12. Error: raise built-in exception ที่ชัด (`ValueError`), ไม่ใช้ `assert` validate, ไม่ bare `except:`, `try` สั้น — [Google Python §2.4.4](https://google.github.io/styleguide/pyguide.html)
13. ข้อมูลเสีย 1 รายการ: log warning + ข้ามพร้อมนับจำนวน (ไม่ล้มทั้ง pipeline) — [Logging HOWTO (warning/error ที่ไม่ raise)](https://docs.python.org/3/howto/logging.html) `[ประยุกต์]`
14. Golden-file test สำหรับ output ของแต่ละ step (syrupy หรือ pytest-regressions หรือเทียบ JSON เอง) และ commit ไฟล์ expected — [syrupy](https://syrupy-project.github.io/syrupy/), [pytest-regressions](https://pytest-regressions.readthedocs.io/en/latest/overview.html)
15. Lint/format ด้วย Ruff (line-length 88); ผ่อน E501 ถ้าชนกับ comment ไทย — [Ruff](https://docs.astral.sh/ruff/settings/)

### 7.4 `testing-and-verification` (15 ข้อ)

1. ทุก task ต้องจบด้วย check ที่รันแล้วได้ pass/fail (test/typecheck/lint/build/diff fixture) — [Claude Code best practices](https://code.claude.com/docs/en/best-practices)
2. คำสั่ง check ทั้งหมดอยู่ใน CLAUDE.md (สั้น, คัดลอกรันได้) — [Best practices](https://code.claude.com/docs/en/best-practices)
3. กฎที่ไม่มีข้อยกเว้น (เช่น typecheck ต้องผ่าน) บังคับด้วย Stop hook/CI ไม่ใช่แค่เขียนใน CLAUDE.md — [Best practices](https://code.claude.com/docs/en/best-practices)
4. Unit test เยอะและเร็วสำหรับ pure function (tokenize, NB/k-NN, regex extract, template) — [Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
5. Golden/snapshot test สำหรับ output pipeline และ template ข้อความ; อัปเดต snapshot ต้องดู diff ก่อน commit — [syrupy](https://syrupy-project.github.io/syrupy/), [pytest-regressions](https://pytest-regressions.readthedocs.io/en/latest/overview.html)
6. Contract test: JSON ที่ pipeline ผลิตต้อง validate ผ่าน schema ที่เว็บใช้ — [Practical Test Pyramid (contract tests)](https://martinfowler.com/articles/practical-test-pyramid.html)
7. Web: Vitest สำหรับ `lib/` และ component ที่ไม่ async — [Next.js Testing](https://nextjs.org/docs/app/guides/testing)
8. Async Server Component / flow หลัก (หน้าแรก, ดูสรุป, upload PDF) ทดสอบด้วย E2E (Playwright) จำนวนน้อย — [Next.js Testing](https://nextjs.org/docs/app/guides/testing), [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
9. Static checks ก่อนเสมอ: `tsc --noEmit`, ESLint (`eslint-config-next/core-web-vitals` + typescript), Ruff — [Testing Trophy](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications), [Next.js ESLint](https://nextjs.org/docs/app/api-reference/config/eslint)
10. Test ต้อง fail เมื่อโค้ดพัง และไม่ซับซ้อน — [Google eng-practices](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
11. ห้ามลบ/แก้ test เพื่อให้ผ่าน — [Effective harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
12. Feature list (JSON) มี `passes`; เปลี่ยนเป็น true ได้หลังผ่าน E2E/ดูผลจริงเท่านั้น — [Effective harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
13. เริ่ม session ใหม่: อ่าน progress file + git log → รัน smoke check (`init` script) ก่อนเริ่ม feature ใหม่ — [Effective harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
14. ทำทีละ feature/phase; จบด้วยอัปเดต progress file — [Effective harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
15. UI change: ตรวจในเบราว์เซอร์จริง (`/verify` หรือ screenshot) + review โดย subagent ที่ไม่ได้เขียนโค้ด — [Best practices](https://code.claude.com/docs/en/best-practices)

**DoD ร่าง** (ใช้ทุก phase): check ทั้งหมดผ่าน · มี test ใหม่/แก้สำหรับ logic ที่เปลี่ยน · golden ไม่เปลี่ยนโดยไม่ตั้งใจ · docs/CLAUDE.md อัปเดตถ้าคำสั่งเปลี่ยน ([Google eng-practices – Documentation](https://google.github.io/eng-practices/review/reviewer/looking-for.html)) · progress file อัปเดต · commit ตาม Conventional Commits (เมื่อผู้ใช้สั่ง) ([Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/))

### 7.5 Comment policy (12 ข้อ — ดู §1.3)

ใช้ §1.3 ข้อ 1–12 ตามนั้น

### 7.6 Workflow (เสริม, สั้น)

- Commit message เป็นอังกฤษตามกฎข้อ 2 ของ comment policy เช่น `feat(pipeline): add rainfall extractor` — [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
- PR/commit ละเรื่องเดียว ~≤300 บรรทัดสำหรับโปรเจกต์นี้ `[ตัวเลขของทีม]` — [Google Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html)
- การตัดสินใจสำคัญ (เช่น เลือกแนวทาง contract A, เลือก DAL) เขียน ADR สั้นใน `docs/adr/NNNN-title.md` (Context/Decision/Status/Consequences) — [Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html)
- CLAUDE.md < 200 บรรทัด; procedure ยาวย้ายไป skill; กฎเฉพาะโฟลเดอร์ใช้ `.claude/rules/` — [Memory](https://code.claude.com/docs/en/memory), [Best practices](https://code.claude.com/docs/en/best-practices)

---

## สิ่งที่ยังไม่ได้ตรวจ

1. **Ruff กับข้อความไทย**: doc บอกว่าใช้ unicode width เฉพาะบรรทัดที่มี East Asian/emoji — ยังไม่ได้ทดสอบจริงว่าบรรทัดภาษาไทย (มีสระ/วรรณยุกต์ combining) ถูกนับเป็น code point หรือ width; ควรทดลองด้วยไฟล์ตัวอย่างก่อนตั้ง line-length
2. **Prettier `getStringWidth`** กับภาษาไทย (เฉพาะบรรทัดโค้ดที่มี string ไทย) — โหลด source ไม่ได้ (404)
3. Codepage default ของ Windows ภาษาไทย (cp874) — ไม่ได้ยืนยันจากแหล่ง Microsoft
4. ข้อความเต็มของ update ปี 2019 ของ Dan Abramov — Medium ตอบ 403, ยืนยันผ่านแหล่งรองเท่านั้น
5. `eslint-config-next` รวม `jsx-a11y` หรือไม่ — หน้า reference ไม่ได้ระบุ
6. API `VariantProps` ของ cva และสถานะ cva@1.0 beta vs `class-variance-authority` 0.7.x — ดูเฉพาะหน้า docs หลัก/variants
7. เวอร์ชันล่าสุดของ `json-schema-to-typescript`, `datamodel-code-generator`, `pydantic-to-typescript` — repo ไม่แสดงเลข release
8. Google TS guide หัวข้อ TODO format — ไม่ได้อ่านส่วนนั้น (ใช้ของ Google Python แทน)
9. Functional core / imperative shell — อ้างแค่ชื่อ screencast ไม่ได้ดูเนื้อหา
10. ตัวเลขขนาดฟังก์ชัน/ไฟล์ (40 / 200–300 บรรทัด) และขนาด PR 300 บรรทัด เป็น heuristic ของทีม ไม่มีแหล่งทางการรองรับ
11. Props typing convention (`React.ComponentProps<'button'>`) และ `clsx + twMerge` (`cn` helper) — เป็น convention ชุมชน ไม่ได้ตรวจแหล่งทางการ
12. ไม่ได้ตรวจแหล่ง Thai-specific (เช่น style guide ของบริษัทไทย) สำหรับการเขียน comment ไทย — ไม่พบแหล่งทางการในการค้นรอบนี้
