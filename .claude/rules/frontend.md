---
paths:
  - "app/**/*.{ts,tsx,css}"
  - "components/**/*.{ts,tsx}"
  - "lib/**/*.ts"
---
# Frontend rules (Next.js App Router + TypeScript + Tailwind)

Loaded whenever web code is touched. For building or reviewing a whole page, also use the `frontend-responsive-ui` and `nextjs-component-architecture` skills.

## Structure
- Dependency direction: `app/` -> `components/` -> `lib/` -> `lib/data/` (server only). Never import upward.
- Server Component by default. Add `'use client'` only to a leaf that needs state, events, or browser APIs; pass Server Components in as `children`.
- Data comes only from `lib/data/*` (starts with `import 'server-only'`, validates rows with Zod, returns small DTOs). Components never touch the DB or `process.env`.
- No `app/api/` folder (`/api/*` is the Python function). A Next.js route handler, if unavoidable, goes under `app/internal/`.
- Code used by one page lives in `app/<route>/_components/`; move it to `components/` when a second page needs it.

## Components
- One responsibility per component. Props typed as `type XxxProps = {...}` next to the component. Prefer composition (`children`) over adding boolean props.
- Build variants with `cva` and merge classes with a single `cn()` (`clsx` + `tailwind-merge`) from `lib/` (`cva`, `clsx` and `tailwind-merge` are the only dependencies assumed here; anything else needs the user's OK).
- Native HTML first (`button`, `a`, `label`), ARIA only when needed. Every control works with the keyboard and shows a visible focus ring.
- Named exports; `export default` only in Next.js convention files (`page.tsx`, `layout.tsx`, ...). File names are kebab-case.

## Design standard (primary: `docs/design/DESIGN-expo.md`, read-only; project adaptations: `docs/spec/design-system.md`)
- Never edit `docs/design/DESIGN-expo.md`. Use its tokens by name (`bg-primary`, `text-ink`, `text-body`, `border-hairline-strong`, `rounded-md` = 8px, `rounded-lg` = 12px ...), defined once in the `@theme` block of `app/globals.css`. No inline hex, no ad-hoc colors, radii or font sizes.
- Black is the only CTA fill; blue (`text-link`) only for inline links; pills only for badges, never CTAs; sky gradient only in the home hero band.
- Font is Anuphan via `next/font/google` (`thai` + `latin`), not Inter. Do not load JetBrains Mono (no code surfaces).
- Not allowed as text color (contrast too low, measured in `design-system.md` section 6): `muted`, `muted-soft`, `semantic-error`, `semantic-success`. On the sky gradient use `ink` only. Blue links and `accent-warning` text only on white.

## Responsive and Thai typography (details: `frontend-responsive-ui` skill)
- Mobile first. Breakpoints are Tailwind defaults (640/768/1024/1280), same as the design standard. Test at 375, 768, 1280 and at 320 for reflow.
- `<html lang="th">`. Summary text uses `body-md` (16px) or larger; nothing a user must act on is below 14px. Use the project's Thai line-heights (headings 1.3, body 1.6); never `leading-none` or `leading-tight` on Thai text.
- `letter-spacing` is 0 everywhere (the standard's negative display tracking is not used). No `tracking-*`, no `uppercase`, no `text-justify`, no `break-all` on Thai text. Never block zoom (`maximum-scale=1`).
- Touch targets at least 44x44 CSS px (buttons are 40px high with a mouse, 44px on touch) with 8 px spacing. Text contrast at least 4.5:1. Never rely on color alone (rain level, warning, selected tab).
- Keyboard focus: 2px `ink` outline with 2px offset on every interactive element.
- Tailwind scans only web code (`@import "tailwindcss" source(none)` + `@source` in `app/globals.css`, verified in Phase 0.1; this root also holds docs and course notes).
- Every data view has loading, empty, and error states.

## Content
- UI text is Thai. Always show the disclaimer "ตัวช่วยสรุป ไม่ใช่ประกาศทางการ" and the credit "ที่มา: กรมอุตุนิยมวิทยา" on pages that show summaries.
- Show numbers exactly as in the source, with units.
