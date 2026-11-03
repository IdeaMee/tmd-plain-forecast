---
name: planning-phases
description: Splits a large build into small, verifiable phases and saves each plan under ai/plans/. Use only when the user asks to plan or split the work into phases (วางแผน, แบ่ง phase, แผนการเจน). It plans; it never writes application code.
disable-model-invocation: true
---
# Planning phases

Goal: turn the agreed spec into phases that one coding session can finish and prove, so nothing is left half-done or invented.

## Rules first
- Plan only. Do not write application code, install packages, or run git.
- Read before planning: `.claude/CLAUDE.md`, `PLAN.md`, `ai/PROGRESS.md`, `docs/spec/*`, `docs/architecture.md`, `docs/decisions/*`. For any phase that builds UI also read `docs/design/DESIGN-expo.md` (read-only primary design standard) and `docs/spec/design-system.md`. The spec decides; do not reopen decisions that are recorded there.
- A phase is small enough for one session, ends with checks that return pass or fail, and touches only files it names.
- Contracts come before code: the data contract, label set, and region keys are fixed in an early phase and changed only through an ADR.
- Keep the plan proportional to the work. A plan longer than the code it describes has failed.
- If the scope is unclear, ask at most three questions, each with a recommended default. When there is a real choice, give two or three options with a recommendation.

## Process
1. **Scope check.** If the work spans independent subsystems (pipeline, web, demo and deploy), write separate plans per subsystem and order them.
2. **Draft the phase list.** For every phase write: goal; inputs (files, data, prior phase outputs); tasks at file level; outputs (paths); checks (exact commands and the expected result); review gate (a separate reviewer session that re-runs the checks); stop conditions; size S, M or L. Use `references/phase-template.md`.
3. **Order by risk.** Retire the biggest unknowns first. For this project that means a Phase 0 with (a) scaffolding and filling `Commands` in `.claude/CLAUDE.md`, (b) a deploy spike: a Python function on Vercel importing the shared package with PyThaiNLP and pypdfium2, recording bundle size, cold start, and which dependency file Vercel picks, plus whether Next.js pages still work, (c) a test of pypdfium2 and pdfminer.six on the real PDFs in `data/raw/`.
4. **Design against invention.** Plan golden examples from real files in `data/raw/`, fidelity checks (see `testing-and-verification`), and a human sign-off step where the user must decide (labeling, UI review, deploy).
5. **Human-only steps.** Mark anything the user must do: Vercel and Neon accounts, deploy, git, labeling the 20% sample. Never plan an agent step that logs in, creates accounts, or runs git.
6. **Save.** Write `ai/plans/NN-<slug>.md` per plan and update the phase table in `ai/PROGRESS.md` (status, owner, checks). Do not create a commit step.
7. **Self-review.** Check coverage against the spec, missing inputs, steps that cannot be verified, and contradictions with `.claude/CLAUDE.md`. Fix inline.
8. **Report.** Summarize the phases, the decisions the user still has to make, and what is unverified.

## Output contract
Each plan file starts with: goal, spec links, constraints that apply (copy the relevant ones from `.claude/CLAUDE.md`), then the phases. Each phase can be pasted as a session prompt: "Read .claude/CLAUDE.md, ai/PROGRESS.md and plan NN. Do phase N only. Stop when its checks pass and report."
