---
name: thai-text-handling
description: Use when cleaning, tokenizing or extracting values from Thai text, especially text pulled from TMD PDFs (private-use characters, broken sara am, spaces inside words, merged region blocks), or when formatting Thai dates and numbers. (ข้อความไทย, ตัดคำ, PyThaiNLP, newmm, PDF, พ.ศ., ทำความสะอาดข้อความ)
---
# Thai text handling

Defects observed in real TMD files: `references/known-defects.md`. Read it before writing a cleaning rule.

## Order of operations
1. Extract text: `pypdfium2` first, `pdfminer.six` as fallback. Never PyMuPDF in shipped code.
2. Map private-use characters (U+F700 to U+F71A) back to real Thai marks.
3. `unicodedata.normalize('NFC', text)`.
4. `pythainlp.util.normalize` and `reorder_vowels` (fixes tone/vowel order and nikhahit + sara aa).
5. Repair line wraps: PDF text inserts spaces and breaks inside words and sentences. Rejoin lines before splitting; a space inside a Thai word is not a boundary.
6. Split into region blocks (headings), date-range blocks (7-day), then clause units (rules in `docs/spec/labeling-guideline.md`).
7. Tokenize with `newmm` and the weather dictionary (terms like ฝนฟ้าคะนอง, ร้อยละ, ส่วนมาก, ตะวันออกเฉียงเหนือ, น้ำป่าไหลหลาก). `Intl.Segmenter` (ICU) splits these wrongly, so tokenization stays in Python.

## Rules
- Keep text as extracted when quoting advice: do the cleaning once, then copy advice from the cleaned text exactly. Do not "fix" source typos (for example "อุณภูมิ").
- Number ranges appear with `-` and with `–`, sometimes with spaces. Normalize before matching and keep the original text for output.
- Dates use the Buddhist era. Full form "16 พฤศจิกายน 2569", short form "14 - 16 พ.ย. 69". Western year = Buddhist year minus 543. Parse into ISO dates; display in the source's style.
- Thai digits (๐ to ๙) may appear; convert for matching only.
- Region names vary: "กรุงเทพและปริมณฑล", "กรุงเทพมหานครและปริมณฑล", "ภาคใต้(ฝั่งตะวันออก)". Map all variants to the seven region keys.
- `\b` word boundaries do not work for Thai. Match on tokens or explicit character classes (not tested here; verify).
- Open files as UTF-8; write JSON with `ensure_ascii=False`.
- Daily PDF text layers merge region blocks and 7-day PDFs break lines mid-sentence. Detect region headings in the cleaned text; when a block cannot be separated, return an extraction error instead of guessing.

## Tests
Use real PDFs from `data/raw/` and small excerpts under `tests/fixtures/`. A cleaning test compares extracted text with a hand-checked expected text for at least 5 files before the extractor is accepted. Test that `ร้อยละ` and `ฟ้าคะนอง` stay whole tokens.

## Vercel
PyThaiNLP on Vercel needs `PYTHAINLP_READ_ONLY=1`, `PYTHAINLP_OFFLINE=1` and `PYTHAINLP_DATA` under `/tmp`; `api/summarize.py` sets them in code before importing (verified: spike 0.3 bundle 48 MB, live `/api/summarize` in Phase 5.1).
