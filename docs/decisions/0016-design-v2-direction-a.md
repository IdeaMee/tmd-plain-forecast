# 0016 ดีไซน์ v2 แนวทาง A "เส้นบาง กระดาษขาว" + โทเคนการเคลื่อนไหว

Status: accepted (2026-11-18, ผู้ใช้เลือก "Direction A" หลังดูต้นแบบ Phase 7.1)

Context: ผู้ใช้ขอปรับดีไซน์ทั้งเว็บ เพิ่มทรานสิชัน/อนิเมชัน และเมนูมือถือแบบแผงเต็มความกว้าง (แผน 07) โดยต่อยอดจาก `DESIGN-expo.md` (อ่านอย่างเดียว) ซึ่งไม่กำหนดการเคลื่อนไหว ("Animation timings ... out of scope") ผู้ช่วยทำต้นแบบ 2 แนวทาง (`docs/design/prototypes/a.html`, `b.html`) ทั้งสองผ่านความต่างสี 4.5:1, พื้นที่กด 44 px, ไม่มี scroll แนวนอน และ reduced-motion

Decision:
- ใช้แนวทาง A: พื้นขาว การ์ดขอบ `hairline-strong` ไม่มีเงาตอนพัก (โฮเวอร์ยกขึ้น 2 px + เงา `card-hover`), แถบหัว gradient ท้องฟ้าเดิม, ตัวเลือกชนิดแบบ segmented (พื้น `surface-strong` ก้อนดำที่ตัวเลือก), ชิปภาคมุม 8 px ตัวที่เลือกพื้นดำ + เครื่องหมายถูก, ตัวเลือกรอบแบบ `<details>` แถววันละแถว, เมนูมือถือเป็นรายการหีบเพลงเต็มความกว้าง
- โทเคนใหม่บันทึกเป็นข้อ D11-D13 ใน `docs/spec/design-system.md`: `num-tint`, `warning-tint`, `shadow-panel`, duration/ease/stagger และอนิเมชัน 4 แบบ
- กติกาเดิมที่ผู้ใช้ตกลง: เคลื่อนแค่ transform/opacity, ไม่ทำอนิเมชันกับค่าตัวเลข, เคารพ `prefers-reduced-motion`, ไม่เพิ่ม dependency (ใช้ CSS + `<ViewTransition>` ของ React ในแผน 7.3-7.4)
- โทเคนเฉพาะแนวทาง B (`canvas-sky`, `sky-band`, `sky-strong`, `shadow-card-rest/raise`) ไม่ใช้

Consequences: หน้าใหม่ทุกหน้า (แผน 08-12) ใช้ส่วนประกอบใน `components/ui/` ที่ปรับแล้ว · ค่าการเคลื่อนไหวแก้ได้ที่ `@theme` ใน `app/globals.css` ที่เดียว · ยังต้องตัดสินจุดเปลี่ยนเมนูเดสก์ท็อป (ต้นแบบใช้ 1024 px, แผน 7.3 เขียน 768) ก่อน Phase 7.3
