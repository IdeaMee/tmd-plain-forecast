# Phase template

Copy this block for each phase in `ai/plans/NN-<slug>.md`.

```
## Phase N: <name>   [size S/M/L]   [owner: agent | user | both]

Goal: one sentence, observable.

Inputs
- files / data / outputs of earlier phases (exact paths)

Tasks
1. ... (file-level, names the files created or changed)

Outputs
- paths and what each contains

Checks (all must pass; paste real output in ai/PROGRESS.md)
- `<command>` -> expected result
- golden / fixture comparisons (named files)
- contract check (JSON validates against the schema)

Review gate
- Separate reviewer session re-runs the checks, spot-checks 5 real records against the source, looks for TODOs, numbers without a source, files outside this list, and silent contract changes. Reviewer does not edit code.

Human steps
- what the user must do or approve (or "none")

Stop conditions
- two failed verifications, unclear contract, missing data -> stop and ask

Out of scope
- what this phase must not touch
```

## Progress table row (ai/PROGRESS.md)

| Phase | Plan | Owner | Status | Checks passed | User sign-off |
|---|---|---|---|---|---|
