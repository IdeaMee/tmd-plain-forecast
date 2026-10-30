# 0004 Tech stack ของเว็บและ Python

Status: accepted (2026-11-16) แทนข้อตกลงก่อนหน้านี้ที่ให้เว็บเป็น HTML/JS ล้วนและ API เป็น Python ทั้งหมด

Context: ผู้ใช้ต้องการ Next.js + TypeScript + Tailwind ตรวจเวอร์ชันกับ npm/PyPI วันที่ 2026-11-16

Decision
- เว็บ: Next.js 16.4.6 (App Router), React 19.3.1, TypeScript **ตรึง 6.0.x** (typescript-eslint 8.72.2 รับ < 6.1.0; ตัวล่าสุดคือ 7.0.2), Tailwind CSS 4.3.5, Zod 4.6.7, คอมโพเนนต์เขียนเอง (`clsx`, `tailwind-merge`, `class-variance-authority`), `lucide-react`, ฟอนต์ Noto Sans Thai (**ส่วนฟอนต์ถูกแทนที่โดย [0010](0010-design-standard-and-font.md): ใช้ Anuphan**)
- DB: Neon Postgres + `@neondatabase/serverless` 1.2.1 SQL ธรรมดา ไม่ใช้ ORM
- Python: PyThaiNLP 5.4.0 (newmm), Pydantic 2.14.3, Ruff 0.17.5, pytest, uv; Naive Bayes/k-NN เขียนเอง ไม่ใช้ sklearn
- ทดสอบ: Vitest + Testing Library, Playwright; คุณภาพ: ESLint (`eslint-config-next` มี jsx-a11y), Prettier + `prettier-plugin-tailwindcss`
- Deploy: Vercel Hobby, GitHub Actions
- คอมเมนต์โค้ดภาษาไทย สั้น เท่าที่จำเป็น; identifier ภาษาอังกฤษ

Consequences: repo มี 2 ภาษา (TypeScript + Python) สื่อสารผ่าน JSON Schema; ไม่มี `app/api/` (ชนกับฟังก์ชัน Python); เวอร์ชันอาจเปลี่ยน ให้ตรวจก่อนติดตั้งจริง; ตัวเลขแผนฟรีของ Neon ยังไม่ได้ยืนยัน
