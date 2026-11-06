# 0014 สคริปต์โหลดข้อมูลเข้า Neon เป็น Node แทน Python (psycopg)

Status: accepted (2026-11-17) · แทนข้อ Q5 ใน `plans/README.md` (`psycopg[binary]` สำหรับสคริปต์โหลด)

Context
- Phase 4.1 ทำ `scripts/load_to_neon.py` ด้วย `psycopg[binary]` 3.x (Q5) แต่บนเครื่องทีม (Windows) นำเข้า psycopg ไม่ได้: "DLL load failed while importing pq: An Application Control policy has blocked this file" ส่วนแบบ pure Python ก็ต้องใช้ libpq ซึ่งไม่มีในเครื่อง
- เว็บใช้ `@neondatabase/serverless` 1.2.1 (ADR 0004) อยู่แล้ว เป็น JavaScript ล้วนต่อผ่าน HTTPS ไม่มีไฟล์ DLL ทดสอบแล้วว่าต่อ Neon จากเครื่องนี้ได้
- Node 24 ที่ติดตั้งรันไฟล์ TypeScript ได้เอง (type stripping) จึงนำเข้า Zod schema ของเว็บ (`lib/contract/issue.ts`) มาตรวจไฟล์ก่อนโหลดได้
- ผู้ใช้เลือกทางนี้ (2026-11-17) แทนการเพิ่ม dependency Python ใหม่ (pg8000) หรือการปลดบล็อกใน Windows

Decision
- `scripts/load-to-neon.mts` แทน `scripts/load_to_neon.py` (ลบไฟล์ Python และ extra `load` ใน `pyproject.toml`): ตรวจทุกไฟล์ใน `data/processed/` ด้วย Zod ชุดเดียวกับที่เว็บอ่าน + ชื่อไฟล์ตรง `doc_type/issue_id` → upsert ทุกไฟล์ในธุรกรรมเดียวด้วย `DATABASE_URL_DIRECT` (SQL เดิม) → `POST /internal/revalidate`
- รันด้วย `npm run load:neon` (`-- --dry-run` = ตรวจไฟล์อย่างเดียว) ไม่มี dependency ใหม่
- `tsconfig.json` เปิด `allowImportingTsExtensions` (ใช้ได้เพราะ `noEmit`) เพื่อให้ไฟล์ `.mts` นำเข้า `../lib/contract/issue.ts` แบบที่ Node รันได้; Vitest รวม `scripts/**/*.test.ts`

Consequences
- ท่อประมวลผลยังเป็น Python ทั้งหมด (ADR 0003) เปลี่ยนแค่เครื่องมือโหลดหลังบ้าน ตัวตรวจสัญญาตอนโหลดกลายเป็น Zod (ฝั่งที่เว็บใช้จริง) ส่วน Pydantic ยังเป็นต้นฉบับของสัญญาและมีเทสต์เทียบชื่อฟิลด์ของสองฝั่งอยู่แล้ว
- ต้องใช้ Node ≥ 22.18 / 23.6 ที่รันไฟล์ `.mts` ได้โดยไม่ต้องตั้งค่า (เครื่องนี้ 24.19) ระบบที่ Node เก่ากว่าต้องอัปเกรด
- คำเตือน `MODULE_TYPELESS_PACKAGE_JSON` ถูกปิดใน npm script เพราะ `package.json` ไม่ได้ตั้ง `"type": "module"` (ตั้งแล้วอาจกระทบ config อื่นของ Next.js จึงไม่เปลี่ยน)
