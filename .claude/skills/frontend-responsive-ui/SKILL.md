---
name: frontend-responsive-ui
description: "Use when creating, changing or reviewing any page or component of the Thai forecast web app (Next.js + Tailwind): applying the design standard docs/design/DESIGN-expo.md with the Anuphan font, layout, responsive behavior on mobile, tablet and desktop, Thai typography, accessibility, and loading, empty and error states. (หน้าเว็บ, ดีไซน์, DESIGN-expo, Anuphan, responsive, มือถือ, แท็บเล็ต, UI, Tailwind, ฟอนต์ไทย)"
---
# Frontend: responsive UI for Thai text

The audience is the general public, mostly on phones, reading short Thai summaries. Clarity and speed beat decoration. Page and component specs: `docs/spec/ui-spec.md`.

## Design standard (read this before designing anything)
The primary standard is **`docs/design/DESIGN-expo.md`** (colors, type scale, radii, spacing, components, breakpoints). It is read-only: never edit it. How this project applies it, including the Anuphan font, the Thai adaptations (D1 to D10), the Tailwind token mapping and the measured contrast table, is in **`docs/spec/design-system.md`**. Where that file is silent, follow `docs/design/DESIGN-expo.md`; where this skill and `docs/design/DESIGN-expo.md` differ, `docs/design/DESIGN-expo.md` wins unless `design-system.md` lists the deviation. Never invent colors, radii or sizes: use tokens by name.

## Process
1. **Plan before code.** Write a short design note: which tokens and components of the standard each part uses, a wireframe per breakpoint, and the states of each data view (loading, empty, error, unsupported file). Show it to the user if the layout is new.
2. **Mobile first.** Build the single-column layout first, then add `sm:`/`md:`/`lg:` changes.
3. **Build** with hand-written components (`nextjs-component-architecture` for structure).
4. **Verify** with the checklist below and `references/ui-checklist.md`, using real screenshots (`testing-and-verification`).

## Layout standards (breakpoints and grids follow the standard)
| Width | Layout |
|---|---|
| under 640 | one column, 16 px side padding, hamburger menu under 768, region tabs as a horizontally scrolling chip row, 48 px between sections |
| 640 to 1024 | two columns of region cards, 24 px side padding |
| 1024 to 1280 | three columns, region tabs inline, 96 px between sections |
| over 1280 | content capped at 1200 px, centered |
- Tailwind default breakpoints (640, 768, 1024, 1280) already match the standard.
- Long text stays in a narrow measure (`max-w-prose`, about 65ch); the page can be wider than its text.
- Spacing uses the standard's 4 px scale. No fixed heights on text boxes (text must be able to grow).
- Tables of data: on mobile turn rows into cards or scroll inside the table only; the page itself never scrolls sideways (also at 320 px).

## Thai typography (values in `docs/spec/design-system.md` section 3.1)
- Font: **Anuphan** via `next/font/google` (`thai` + `latin` subsets), not Inter. `<html lang="th">`.
- Summary text uses `body-md` (16 px) or larger; nothing the user must act on is below 14 px.
- Line-height: headings 1.3, body 1.6 (the standard's Latin values 1.05 to 1.25 and 1.5 are too tight for stacked Thai tone marks). Never `leading-none` or `leading-tight` on Thai.
- `letter-spacing` 0 everywhere; no `tracking-*`, no justified text (left aligned), no uppercase, `word-break: normal` (never `break-all`). Long strings (URLs, station names) use `overflow-wrap: anywhere`.
- These Thai values follow common practice; no official number exists. Check them visually with Anuphan (Phase 0) and keep the table in `design-system.md` as the one source.

## Interaction and accessibility
- Touch targets at least 44x44 CSS px with at least 8 px between them (buttons are 40 px high with a mouse as in the standard; WCAG 2.2 minimum is 24 px).
- Text contrast at least 4.5:1, UI parts at least 3:1. Never use `muted`, `muted-soft`, `semantic-error` or `semantic-success` as text color; use `ink` on the sky gradient. Warning or rain levels use text and an icon, never color alone.
- Visible focus: 2 px `ink` outline with 2 px offset on every interactive element (design-system D8); sticky headers must not hide the focused element. Zoom to 200 percent must not break the layout. Never set `maximum-scale=1`.
- Native elements first. Every control has an accessible name. Upload dropzone: a real `<input type="file" accept="application/pdf">` with a label, keyboard operable.

## Content rules
- UI text in Thai, short, in the reader's words. Numbers keep the source's units and ranges.
- Every summary page shows the disclaimer "ตัวช่วยสรุป ไม่ใช่ประกาศทางการ" and "ที่มา: กรมอุตุนิยมวิทยา".
- Advice that applies to every region is labeled "ข้อแนะนำทั่วไป".
- Error messages say what happened and what to do next (for example the file is over 4 MB, or is not a TMD daily or 7-day forecast).

## Do not
Add animation for decoration, dark patterns, English Title Case copy, or UI libraries. Do not load design rules from the internet at run time; the checklist lives in `references/ui-checklist.md`.
