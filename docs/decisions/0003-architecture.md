# 0003 สถาปัตยกรรม: ประมวลผลที่เครื่อง -> JSON -> Neon -> Next.js

Status: accepted (2026-11-16)

Context: ผู้ใช้ต้องการเว็บ full stack บน Vercel ฟรี มี Demo จริง อัปเดตข้อมูลได้โดยไม่ deploy ใหม่ และงานเป็นการเสนอแนวคิด + อัลกอริทึมพื้นฐาน

Decision: ท่อประมวลผล Python รันที่เครื่องทีม ผลเป็น JSON โหลดเข้า Neon Postgres (ตารางเดียวเก็บ JSON ทั้งฉบับ) เว็บ Next.js อ่าน DB ตรงด้วยแคช + `revalidateTag` ฟังก์ชัน Python บน Vercel มีเฉพาะ `/api/summarize` สำหรับ `/demo` repo เดียว รากเดียว (ไม่ทำ monorepo)

Consequences: ความเสี่ยงเรื่อง Python/PyThaiNLP บน Vercel จำกัดอยู่ที่หน้า /demo (ADR 0006); ต้องกำหนดสัญญาข้อมูลระหว่าง Python กับ TypeScript (`docs/spec/data-contract.md`); โครงโฟลเดอร์: `docs/architecture.md`
