# แผนที่เอกสาร (docs/)

เอกสารภาพรวมที่ราก: [../README.md](../README.md) ภาพรวมและวิธีใช้ · [../PLAN.md](../PLAN.md) โจทย์ ขอบเขต สถาปัตยกรรม · [../THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) | งานร่วมกับผู้ช่วย AI อยู่ที่ [../ai/](../ai/README.md) (ความคืบหน้า, แผนแต่ละ phase, ร่างเก่า, งานค้นคว้า R1-R4) | มาตรฐานดีไซน์อยู่ที่ [design/DESIGN-expo.md](design/DESIGN-expo.md) (อ่านอย่างเดียว)

| ที่ไหน | มีอะไร | สถานะ |
|---|---|---|
| [architecture.md](architecture.md) | ภาพรวม โครงโฟลเดอร์ แผน Python บน Vercel spike แคช env | ยืดหยุ่น ปรับในขั้น 3 |
| [data-sources.md](data-sources.md) | แหล่งข้อมูลและเครดิต | ใช้งาน |
| [spec/scope-and-pipeline.md](spec/scope-and-pipeline.md) | ขอบเขต ท่อประมวลผล กฎผลลัพธ์ การวัดผล | ตกลงแล้ว |
| [spec/labeling-guideline.md](spec/labeling-guideline.md), [spec/region-scope-map.md](spec/region-scope-map.md) | คู่มือป้ายและตารางแมปภาค | v1 ตกลงแล้ว |
| [spec/data-contract.md](spec/data-contract.md) | รูปแบบ JSON/DB/API (ต้นฉบับอยู่ใน `src/tmd_plain/contract.py`) | v1 เป็นโค้ดแล้ว (ผู้ใช้รีวิวผ่าน) |
| [spec/design-system.md](spec/design-system.md) | วิธีใช้ docs/design/DESIGN-expo.md ในโปรเจกต์นี้ (Anuphan, การปรับเพื่อภาษาไทย, โทเคน, ความต่างสี) | ใช้งานจริง (ผู้ใช้รีวิวหน้าเว็บและเซ็นปิด 0.5, 4.2-4.3, 5.2) |
| [spec/ui-spec.md](spec/ui-spec.md) | หน้า คอมโพเนนต์ เลย์เอาต์ | ใช้งานจริง (หน้า `/` และ `/demo` ผู้ใช้เซ็นปิดแล้ว) |
| [results/](results/) | ผลทดสอบและผลวัดจริงของแต่ละ phase ([spike-pdf-extraction](results/spike-pdf-extraction.md), [spike-vercel-python](results/spike-vercel-python.md), [units-check](results/units-check.md), [split-check](results/split-check.md), [labels-check](results/labels-check.md), [classifier-evaluation](results/classifier-evaluation.md), [facts-coverage](results/facts-coverage.md), [scope-map-check](results/scope-map-check.md), [fidelity-report](results/fidelity-report.md), [review-sheet](results/review-sheet.md), [smoke-test](results/smoke-test.md), [raw-inventory](results/raw-inventory.md), [generic-check](results/generic-check.md), [warning-check](results/warning-check.md), [warning-classifier-evaluation](results/warning-classifier-evaluation.md), [weekly-check](results/weekly-check.md), [shipping-check](results/shipping-check.md), [pipeline-run](results/pipeline-run.md), [summary-for-slides](results/summary-for-slides.md)) | ตัวเลขทุกตัวมาจากคำสั่งที่รันซ้ำได้ |
| [decisions/](decisions/README.md) | บันทึกการตัดสินใจ (ADR) 0001-0018 | ใช้งาน ห้ามลบ |
| [research/](research/) | งานค้นคว้าเรื่องเว็บ TMD และวิธีเก็บข้อมูล: `TMD-DATA-INVENTORY.md`, `TMD-SITE-MAP.md`, `tmd-digest/` · รอบ v2: [collection-procedure.md](research/collection-procedure.md) วิธีเก็บด้วยเบราว์เซอร์ + `collection/collector.js` (งานค้นคว้า R1-R4 ย้ายไป [../ai/research/](../ai/research/)) | อ้างอิง (ไฟล์เดิมไม่แก้) |
| [design/](design/DESIGN-expo.md) | มาตรฐานดีไซน์ `DESIGN-expo.md` (อ่านอย่างเดียว) และ [prototypes/](design/prototypes/README.md):  ต้นแบบดีไซน์ v2 สองแนวทาง (A เส้นบาง กระดาษขาว, B การ์ดท้องฟ้า) + ภาพหน้าจอ (Phase 7.1) | ผู้ใช้เลือก A (2026-11-18) ใช้เป็นต้นแบบของ 7.2-7.4 |
| [../ai/archive/](../ai/archive/README.md) | เอกสารเก่า/ร่างที่ถูกแทนที่ + `PLAN-history.md` (decision log เต็ม) + ตารางย้ายไฟล์ (ย้ายมาอยู่ใต้ `ai/` เมื่อ 2026-11-19) | ประวัติ |

เอกสารนอก `docs/`: `ai/` งานร่วมกับผู้ช่วย AI · `.claude/` กฎที่โหลดอัตโนมัติ (`CLAUDE.md`, `rules/`) และขั้นตอนงาน (`skills/`) · `course/` สไลด์และบันทึกเนื้อหาวิชา · `data/` ข้อมูลดิบ
