---
name: nextjs-component-architecture
description: "Use when adding or changing React or Next.js code in app/, components/ or lib/: where components and data access go, Server versus Client Components, props and variants, and caching or revalidation for database reads. (คอมโพเนนต์, โครงสร้างเว็บ, Server Component, แคช)"
---
# Next.js component architecture (project conventions)

This skill holds our conventions only. Framework API details come from the docs bundled with the installed Next.js version (see `AGENTS.md` once it exists). Check an API there before using it; this Next.js is newer than your training data.

## Where things go
```
app/                 routes: /, /demo (no app/api/)
  <route>/_components/   used by that route only
components/
  ui/                primitives: Button, Card, Tabs, Badge, Alert, Skeleton
  layout/            Header, Footer, Container, Section
  features/          ForecastCard, RegionTabs, RoundPicker, AdviceList, UploadDropzone, ResultPanel, Disclaimer
lib/                 pure helpers, constants, types, Zod schemas
  data/              data-access layer (server only)
```
- Dependency direction: `app/` -> `components/` -> `lib/` -> `lib/data/`. Never import upward. Features do not import each other; share through `components/ui` or `lib/`.
- Code used by one route stays in `app/<route>/_components/`; move it up when a second route needs it. Move to `features/<name>/` only when `components/` passes about 15 files; do it one feature at a time.
- This skeleton may change during the build. Record changes in `docs/architecture.md`.

## Server and Client
- Default is a Server Component. Add `'use client'` only on the smallest leaf that needs state, events, effects or browser APIs (tabs, picker, dropzone).
- Fetch in the page or layout (server), pass small serializable props down. Pass Server Components into Client Components as `children`.
- Props to Client Components are narrow: never a whole DB row.

## Data access layer (`lib/data/`)
- Each file starts with `import 'server-only'`. It is the only place that reads `process.env` and talks to Neon (`@neondatabase/serverless`, plain SQL).
- Rows are validated with Zod and mapped to small DTOs. Zod schemas mirror the Python Pydantic models (`docs/spec/data-contract.md`).
- Reads use the cache with a tag so the loader can refresh data without a redeploy: `'use cache'` + `cacheTag('forecasts')` + `cacheLife('hours')` as a safety net. A secured route handler `app/internal/revalidate/route.ts` (secret from env) calls `revalidateTag`. `updateTag` is for Server Actions only; do not use it here. Verified in Phase 4.1: `revalidateTag("forecasts", { expire: 0 })` in `app/internal/revalidate/route.ts`, tested on the live site. Still check the bundled docs before using any other cache API.

## Components
- One job per component; typed props as `type XxxProps = {...}` beside it; prefer `children` over adding boolean props; spread props only when forwarding to a native element.
- Variants with `cva`; merge classes with the shared `cn()` (`clsx` + `tailwind-merge`) in `lib/`.
- Styling comes from the design tokens in the `@theme` block of `app/globals.css` (copied by name from `docs/design/DESIGN-expo.md`, see `docs/spec/design-system.md`); the font (Anuphan) is loaded once in `app/layout.tsx`. A component never carries its own hex color, radius or font size.
- No logic in components beyond display. Formatting (Thai dates, region labels) lives in `lib/` as pure functions and is reused everywhere.
- Named exports. `export default` only in Next convention files. File names kebab-case.
- Native HTML before ARIA; keyboard support on every control.
- No mutation or side effects during render; effects only when nothing else works.

## Reuse and size
- Search `lib/` and `components/` before writing a new helper. Extract on the third repetition.
- A file over about 200 to 300 lines or a function over about 40 lines is a prompt to split, not a rule (team heuristic).

## Testing
Vitest + Testing Library for `lib/` and non-async components. Async Server Components and the main flows (home, history, `/demo`) use a few Playwright tests. `next lint` no longer exists: run `eslint .` and `tsc --noEmit`.

## Constants worth centralizing
Region keys and Thai labels, doc type labels, disclaimer and credit text, upload limits (4 MB), cache tag names. One file each in `lib/` or a `config/` folder; no duplicates in components.
