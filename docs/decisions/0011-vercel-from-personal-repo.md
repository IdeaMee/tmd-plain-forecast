# 0011 Vercel deploy จาก repo ส่วนตัว และ push ไป 3 repo

Status: accepted (2026-11-16)

Context
- repo ส่งงานวิชาอยู่ใน GitHub organization 2 ที่ (`KhwamkhitMee/tmd-plain-forecast`, `IdeaMee/tmd-plain-forecast`) ทั้งคู่เป็น Public
- เอกสาร Vercel (Limits): "Vercel does not support connecting a project on your Hobby team to Git repositories owned by Git organizations" และผู้เขียน commit ต้องเป็นเจ้าของทีม Hobby
- ของฟรีเท่านั้น จึงไม่อัปเกรด Pro; ผู้ใช้พิจารณา GitHub Pages แล้วไม่เลือก เพราะตัด `/demo` และ Neon ออก

Decision
- สร้าง repo ส่วนตัว `Kanawatkha/tmd-plain-forecast` (Public) ไว้ให้ Vercel deploy อย่างเดียว
- remote `all` push ไปครบ 3 repo (`git push all main`) remote แยก: `khwamkhit`, `ideamee`, `kanawatkha`
- โปรเจกต์ Vercel `tmd-plain-forecast` ในทีม "kanawatkha's projects" (Hobby) ค่าเริ่มต้นของ Next.js (`npm run build`) โดเมน `tmd-plain-forecast.vercel.app`
- Neon: โปรเจกต์ `tmd-plain-forecast` (เดิมชื่อ `my-first-project`) AWS Singapore แผน Free, Postgres 18.7, ฐานข้อมูล `neondb`

Consequences
- เว็บอัปเดตเมื่อ push เข้า repo ส่วนตัวเท่านั้น ถ้าสมาชิกคนอื่น push เข้า repo ของ org อย่างเดียว เว็บจะไม่เปลี่ยน ต้องให้เครื่องที่มี remote `all` push ต่อ
- commit ที่สมาชิกคนอื่นเป็นผู้เขียนอาจทำให้ deploy อัตโนมัติถูกบล็อกบน Hobby (ตามเอกสาร) ถ้าเกิดให้ deploy ใหม่จากหน้า Vercel โดยเจ้าของบัญชี
- การยืนยันตัวตน 2FA ของ Vercel ผู้ใช้ต้องทำเอง
