---
name: testing-and-verification
description: Use before reporting any task or phase as done, when writing or running tests, and when debugging a failure. Requires running the real check commands and quoting their output; covers pytest, Vitest, Playwright viewport screenshots, golden files, contract tests, and the output-fidelity checks for the forecast summaries. (ตรวจก่อนบอกว่าเสร็จ, ทดสอบ, กันหลอน, debug)
---
# Testing and verification

## The gate (evidence before claims)
Do not say "done", "fixed" or "passing" until you have:
1. Found the exact command that proves the claim (see `Commands` in `.claude/CLAUDE.md`).
2. Run it fresh in this session.
3. Read the full output and exit code, not only the last line.
4. Confirmed it supports the claim.
5. Only then stated the claim, with the command and the key output.

| Claim | Needs | Not enough |
|---|---|---|
| Tests pass | pytest / Vitest output with 0 failures | an earlier run, "should work" |
| Types are fine | `tsc --noEmit` exit 0 | ESLint passing |
| Lint is clean | ESLint and Ruff output | the type check passing |
| Build works | `next build` exit 0 | lint passing |
| Pipeline output is right | fixture diff + fidelity checks (below) | the script finishing without error |
| UI works | screenshots at 375, 768, 1280 viewed and described | the component rendering in a unit test |
| Subagent finished | the diff and the checks you ran yourself | the subagent's report |

If a check cannot run (missing tool, path problem), say so. Never report a check as passed that you did not run. Never edit or delete a test to make it pass; if a test is wrong, say why and ask.

## What to test
- Pure logic (tokenize, clean text, region split, regex extraction, Naive Bayes, k-NN, templates): unit tests, written first when input and output are clear (red, then green, then tidy). Check Naive Bayes against a hand-computed example.
- Pipeline stages: golden files built from real files in `data/raw/` (small excerpts under `tests/fixtures/`). Read the diff before updating a snapshot.
- Contract: JSON written by the pipeline validates against the schema the web app uses (`docs/spec/data-contract.md`).
- Web: Vitest for `lib/` and non-async components. Async Server Components and the main flows (home page, history, `/demo` upload) get a few Playwright end-to-end tests, not unit tests.
- Static checks always run first: `tsc --noEmit`, ESLint (`eslint .`), Ruff.

## Output fidelity checks (run on every real forecast file and all 7 regions)
- F1 every number or range in a region's summary exists in that region's source block.
- F2 every province name exists in the source.
- F3 every advice sentence is a verbatim substring of the source after whitespace normalization.
- F4 no "โอกาส ... %" or "ความน่าจะเป็น" wording appears.
- F5 a region's summary has no number found only in another region's block.
- F6 running twice gives identical output.
- F7 empty, garbled, or wrong-type input returns a friendly typed error, never a crash or a guess.

## UI verification
Open the page in a real browser at 375, 768 and 1280 px (and 320 px for reflow). Look for overflow, clipped Thai tone marks, tap targets under 44 px, missing loading/empty/error states, and focus visibility. Describe what you saw. Full checklist: `frontend-responsive-ui`.

## Debugging, short form
1. Reproduce and read the full error. 2. Find the last place the data was still correct. 3. Form one hypothesis and test it with the smallest change. 4. Fix the cause, add a test for it. If three fixes fail, stop and question the design with the user.

## Report format
What was done; each check with its command and result; what was skipped or uncertain; what the reviewer should look at. See `references/definition-of-done.md`.

## Hooks
A Stop hook that runs the type check is a reasonable guardrail, but it is untested on this Windows setup. Do not add hooks or change settings without asking.
