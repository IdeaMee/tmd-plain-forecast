-- role อ่านอย่างเดียวสำหรับเว็บบน Vercel (DATABASE_URL) รันหลัง schema.sql ด้วย role เจ้าของ (neondb_owner)
-- ผู้ใช้ตั้งรหัสผ่านเองแทน <ตั้งรหัสผ่านเอง> ห้ามเก็บรหัสผ่านจริงในไฟล์นี้หรือใน repo
-- สร้างด้วย SQL ไม่ใช่ปุ่ม Add role ในหน้า Neon (role ที่สร้างจากหน้าเว็บได้สิทธิ์กว้างเกินที่เว็บต้องการ)
create role web_reader with login password '<ตั้งรหัสผ่านเอง>';

grant connect on database neondb to web_reader;
grant usage on schema public to web_reader;
grant select on forecast_issue to web_reader;
alter default privileges in schema public grant select on tables to web_reader;
