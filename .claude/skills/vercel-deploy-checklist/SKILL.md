---
name: vercel-deploy-checklist
description: Checklist for preparing and verifying a Vercel Hobby deployment of the forecast app (environment variables, Python function limits, region, smoke tests). Use only when the user asks to prepare or check a deployment (deploy, เดโมจริง, ขึ้น Vercel). It tells the user what to do; it never deploys, logs in, installs a CLI, creates accounts, or runs git.
disable-model-invocation: true
---
# Vercel deploy checklist

The agent prepares and verifies. The user performs account, login, git and deploy steps. Say clearly which step belongs to whom.

## 1. Before deploying (agent checks locally)
- `eslint .`, `tsc --noEmit`, web tests, `next build`, Python tests: all pass with output quoted.
- No secrets in the repo; `.env.example` lists every variable; `data/raw/` is gitignored and absent from the commit.
- No `app/api/` folder; `/api/*` is Python only.
- `vercel.json`: `excludeFiles` removes `node_modules`, `.next`, `data`, `docs`, `tests`, `notebooks` and anything else the Python function does not need; function region set near the Neon database (Singapore): `regions: ["sin1"]` works on Hobby (verified in spike 0.3).
- Python dependency file: one source of truth (the Phase 0 spike records which file Vercel used). Do not add FastAPI or Flask unless the plan says so.
- TypeScript is pinned to 6.0.x in `package.json`.

## 2. Environment variables (user sets them in the Vercel dashboard)
- `DATABASE_URL`: pooled, read-only role (web app).
- `DATABASE_URL_DIRECT`: only on the laptop that runs the loader; never on Vercel.
- `REVALIDATE_SECRET`: on Vercel and in the loader environment.
- `PYTHAINLP_READ_ONLY=1` and `PYTHAINLP_DATA` under `/tmp`: set in `api/summarize.py` code, so not needed in the dashboard.
- Never prefix secrets with `NEXT_PUBLIC_`. Changing a value needs a new deployment.

## 3. Limits to respect (Hobby)
Request body 4.5 MB (the browser checks PDF size first); Python bundle 500 MB; function duration 300 s; memory 2 GB. Neon Free scales to zero after about 5 minutes idle: the first query after idle is slower, and the cache hides most of it.

## 4. After the user deploys (agent verifies, user supplies the URL)
Run the 15 smoke cases and record results: home page loads daily and 7-day with all seven regions; history picker; region tabs on mobile; `/demo` accepts a real TMD daily PDF and a 7-day PDF; rejects a shipping forecast PDF, a non-PDF, an oversize file, and an empty file with the right Thai message; summaries carry the disclaimer and credit; loading new data through the loader updates the site without a redeploy; response times noted for the first and second request; 320 px and 375 px screenshots.

## 5. If something fails
Record the failure and stop. If the Python function cannot import the package or exceeds limits, the fallback in `docs/architecture.md` applies (Vercel Services with `web/` and `pipeline/`, or running `/demo` locally for the presentation). Do not improvise a new architecture; ask the user.
