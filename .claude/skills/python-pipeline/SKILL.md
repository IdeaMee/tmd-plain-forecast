---
name: python-pipeline
description: "Use when adding or changing Python code in src/, api/ or scripts/: pipeline stages (prep, tokenize, classify with hand-written Naive Bayes or k-NN, extract, generate), the shared data contract, and the Vercel function entry for /demo. (ท่อประมวลผล, Naive Bayes, k-NN, Python, pipeline)"
---
# Python pipeline

The rules that always apply are in `.claude/rules/python.md`. This skill is the procedure for adding or changing a stage. Spec: `docs/spec/scope-and-pipeline.md`; contract: `docs/spec/data-contract.md`.

## The pipeline
| Step | Input -> output | Method |
|---|---|---|
| doctype | text or PDF -> `daily` / `sevenday` / unsupported | marker rules on headings; rejects shipping forecast and other TMD reports |
| 0 prep | raw text -> cleaned text, region blocks, date-range blocks, clause units, tokens | Thai fixes, region headings, discourse markers, PyThaiNLP `newmm` |
| 1 classify | unit -> `weather` / `advice` / `cause` / `other` | hand-written Naive Bayes (m-estimate, ML 08) compared with k-NN (ML 04) and a keyword baseline |
| 2 extract | region block -> facts (rain share, temperature ranges, wind, waves, provinces, periods) and advice scope | regex and the agreed region-scope map |
| 3 generate | facts + advice -> plain Thai lines per region | templates + glossary + TMD thresholds |

Region blocks are structured lines and count as `weather` by position; the classifier runs on the overview paragraphs and the caution section only.

## Adding or changing a stage
1. Read the spec and contract for that stage. If the contract must change, stop and write an ADR first.
2. Write the input and output models (Pydantic at boundaries, frozen dataclasses inside).
3. Write the test first from a real example in `data/raw/` (small excerpt in `tests/fixtures/`), including the expected output as a golden file.
4. Implement the stage as a pure function in `src/tmd_plain/<stage>/`. Config values go to the config file.
5. Wire it in the runner (`scripts/`) and the function entry (`api/`) without adding logic there.
6. Run the checks from `testing-and-verification`, including fidelity checks F1 to F7 when generation is affected.
7. Update `ai/PROGRESS.md`.

## Hand-written models
- Naive Bayes: bag of words over `newmm` tokens (TF-IDF optional; pick one formula and record it, the course slide is inconsistent). m-estimate smoothing. Log probabilities. Parameters saved as JSON in `models/` (small, committed). Check against a hand-computed example.
- k-NN: same features, distance as in the course notes, `k` from the config file. No sklearn, pandas or numpy in shipped code.
- Keyword baseline: written before looking at test results and independent of the labeling process.
- Evaluation: split by day, not by sentence; units with identical text stay in one split; report accuracy overall and on unseen-text units only; show 3 to 5 misclassified examples.

## Generation rules (never break)
- Every number, province and advice sentence comes verbatim from that region's source text. Advice is selected, never written.
- Use the agreed region-scope map to decide which overview advice a region gets: mentions of the region or its provinces, wide terms ("ประเทศไทยตอนบน" = north, northeast, central, east, Bangkok), sea terms, "บริเวณดังกล่าว" inherits the previous unit, no location means all seven regions marked as general advice. Never drop a warning when unsure: show it more widely.
- Explain levels only with TMD's own thresholds (rain levels, cold levels) and the glossary built from TMD definitions.
- Unsupported or garbled input returns a typed error object.

## Function entry (`api/`)
Accept a PDF (max 4 MB), check the type, extract text, run the same package, return the contract JSON or a typed error. Nothing is stored. Keep imports light at module load so cold start stays small; set `PYTHAINLP_READ_ONLY=1`.
