# 0005 ตัวอ่าน PDF: pypdfium2 ไม่ใช้ PyMuPDF

Status: accepted (2026-11-16)

Context: PyMuPDF เวอร์ชัน 2.1 (PyPI 2026-11-16) เป็น license AGPL-3.0 หรือ Artifex commercial, wheel ราว 63-69 MB และต้องลง onnxruntime, numpy, networkx ฯลฯ pypdfium2 5.15.2 เป็น BSD-3-Clause/Apache-2.0 wheel 2.7-5.4 MB ไม่มี dependency pdfminer.six เป็น MIT ราว 6.6 MB

Decision: `extract_text` ลอง pypdfium2 ก่อน แล้ว fallback เป็น pdfminer.six จากนั้นผ่านขั้นซ่อมข้อความไทย (PUA -> NFC -> `pythainlp.util.normalize`) ห้าม import PyMuPDF ในโค้ดที่ deploy (ใช้ในเครื่องเทียบได้เท่านั้น)

Consequences: ต้องทดสอบคุณภาพข้อความไทยจาก PDF จริงของ TMD ใน Phase 0 (ยังไม่เคยทดสอบ); pypdfium2 ไม่วิเคราะห์ layout จึงต้องแยกบล็อกภาคจากข้อความที่ซ่อมแล้ว
