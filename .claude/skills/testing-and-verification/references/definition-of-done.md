# Definition of done (every phase)

A phase is done only when all of these hold. Paste the evidence in `ai/PROGRESS.md`.

1. All checks listed in the phase pass, run in this session, output quoted.
2. New or changed logic has a test; a test that would fail if the logic broke.
3. Golden files changed only on purpose, with the diff reviewed.
4. Fidelity checks F1 to F7 pass for every real forecast file (when the phase touches generation).
5. The JSON contract is unchanged, or an ADR records the change.
6. `.claude/CLAUDE.md` Commands, `docs/architecture.md` and the folder table match what exists now.
7. No TODO without a link or phase number, no unexplained empty `catch` or `except`, no file outside the phase's list, no new dependency without approval.
8. `ai/PROGRESS.md` updated: status, checks, open questions.
9. Independent review done: a separate session re-ran the checks and spot-checked 5 real records. Result: pass, fail or unsure, with evidence.
10. The user signed off (a short message) before the next phase starts.

Git is not part of this list; commits happen only when the user asks.
