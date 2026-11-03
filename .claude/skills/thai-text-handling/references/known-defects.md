# Known text defects in TMD files

Observed in the survey of November 2026 (text layers of TMD PDFs extracted with `pdftotext`, and TMD web pages). Re-check each item with the real extractor you ship; the extractor changes the symptoms.

## Contents
1. PDF text layer defects
2. Layout defects
3. Source-text quirks to keep

## 1. PDF text layer defects
| Symptom | Example | Where seen |
|---|---|---|
| Sara am lost or split | "ประจาเดือน" (should be "ประจำเดือน"), "สาหรับ"; ำ becomes า or ้า | monthly outlook, older files (2023 and earlier) |
| Missing characters | "พฤศจิ ายน" (missing ก), "รุง ทพมหานคร" | observation and rain tables |
| Degree sign misplaced | "ํ" (U+0E4D) instead of "°" | seasonal outlook (49 occurrences in one file) |
| Dropped letter in a name | "เอญนีโญ" for "เอลนีโญ" | ENSO file |
| Digits merged | "70-90" read as "7090" | one spot in a long report |
| Private-use characters | U+F70A to U+F70E in place of tone marks | some older PDFs |
| Stale metadata | PDF title says an old month | various |

## 2. Layout defects
- Spaces inserted inside words and sentences at line wraps: "ติดตา ม", "หนัก มากบางแห่ง".
- Daily PDF: region headings grouped, bodies of several regions merged into one paragraph; the province table comes out as names first, numbers after (pair by position, not by order).
- 7-day PDF: every wrapped line becomes its own paragraph; block order can swap (parts of one region appear after another region's label); headings sometimes shortened ("ใต้ฝั่งตะวันออก" without "ภาค").
- Tables generally come out in scrambled order; rebuild from coordinates or skip.

## 2b. Confirmed with pypdfium2 on the 65 PDFs in `data/raw/` (Phase 0.2, `docs/results/spike-pdf-extraction.md`)
- Line order is correct and region headings come in order (46/46 daily, 19/19 7-day). pdfminer.six scrambles order and splits tone marks onto their own lines: do not use it for region splitting.
- Spaces are dropped at line wraps and next to bold text: "ราชบุรีนครปฐม", "ลมตะวันออกเฉียงใต้ความเร็ว", "ร้อยละ 30ของ", "ในช่วงวันที่17". Letters and digits are intact.
- Daily PDF: the province temperature table sits inside each region block: province names one per line, then all minimum values, then all maximum values (pair by position). It is not in the HTML text.
- Daily PDF headings share a line with the first sentence ("ภาคเหนือ มีฝนฟ้าคะนอง ...") or span two lines ("ภาคตะวันออก" + "รวมทั้งชายฝั่ง", "ภาคใต้ฝั่งตะวันออก" + "(ฝั่งอ่าวไทย)", "กรุงเทพมหานคร" + "และปริมณฑล"). 7-day headings drop "ภาค" ("เหนือ", "กลาง", "ใต้ฝั่งตะวันตก").
- No private-use characters in this set.
- **HTML and PDF of the same round can disagree:** `daily_151120261800`, east: HTML "ร้อยละ 20", PDF "ร้อยละ 30" (checked on the rendered page).

## 2c. Web text (saved .txt) quirks found in Phase 1.2-1.3
- Every space is a non-breaking space (U+00A0); normalize to a plain space before anything else.
- Paragraphs start with an em-space indent (U+2003); the page sometimes breaks a line mid-sentence ("...เรือเล็กควรงด" / "ออกจากฝั่งต่อไปอีก 1 วัน"). A non-indented line right after an indented one continues that paragraph.
- Date ranges can carry month and year on both sides: "ในช่วงวันที่ 31 ต.ค. 69 – 2 พ.ย. 69".
- Web and PDF numbers per region block agree in 328 of 329 blocks; the one difference is in TMD's own publications.

## 3. Source-text quirks to keep
- Typos in the source ("อุณภูมิ") stay as written when quoting.
- Range separators mix `-` and `–` in one document.
- Block names vary between HTML and PDF and between issues.
- The same sentence repeats across issues; units with identical text should be treated as one for splitting data.
- Daily issues come four times a day; consecutive issues are 87 to 95 percent similar.
