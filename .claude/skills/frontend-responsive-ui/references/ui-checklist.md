# UI review checklist

Run through this for every new or changed page. Items are written for this project; the ideas follow common web interface guidelines and WCAG 2.2. Mark each item pass, fail or not applicable, and list failures with the file.

## Contents
1. Layout and responsive
2. Thai text
3. Interaction and focus
4. Forms and upload
5. States and feedback
6. Content
7. Performance
8. Screenshots to take

## 1. Layout and responsive
- [ ] Works at 320, 375, 768, 1024, 1280 px; no horizontal page scroll at 320 px.
- [ ] Single column on mobile; two columns from 640, three from 1024 (grid of `docs/design/DESIGN-expo.md`); menu collapses to a hamburger under 768.
- [ ] Container max width 1200 px on wide screens; text measure about 65ch.
- [ ] No fixed heights on text; cards grow with content.
- [ ] Safe areas respected on phones (notches); nothing hides under a sticky header.
- [ ] Page zoomed to 200 percent still usable.

## 2. Thai text
- [ ] `lang="th"` on `<html>`; Anuphan loaded through `next/font/google` (no Inter, no JetBrains Mono).
- [ ] Summary text at least 16 px (`body-md`), nothing actionable under 14 px; line-height body 1.6, headings 1.3.
- [ ] No `leading-none`, `leading-tight`, `tracking-*`, `uppercase`, `text-justify`, `break-all` on Thai; `letter-spacing` is 0.
- [ ] Tone marks and vowels not clipped in headings, buttons, chips, badges.
- [ ] Long unbroken strings wrap (`overflow-wrap: anywhere`).
- [ ] Thai digits are not mixed with Arabic digits for the same value; years in Buddhist era match the source format.

## 3. Interaction and focus
- [ ] Every control reachable and usable by keyboard; tab order follows the visual order.
- [ ] Visible focus on every control (2 px `ink` outline, 2 px offset); focus never fully hidden by sticky UI.
- [ ] Targets at least 44x44 px on touch screens (buttons 40 px high with a mouse), spaced at least 8 px.
- [ ] Links are links, actions are buttons; no click handlers on plain `div`.
- [ ] Tabs for regions follow the tab pattern (roles, arrow keys) or are plain links/buttons with `aria-current`.

## 4. Forms and upload
- [ ] File input has a visible label; accepts only PDF; size checked in the browser (max 4 MB) before sending.
- [ ] Inputs at least 16 px so mobile browsers do not zoom.
- [ ] Submit shows a busy state; double submit prevented.
- [ ] Errors appear next to the control and are announced (`aria-live`); they say what to do.

## 5. States and feedback
- [ ] Loading skeleton for data views; empty state explains why there is no data; error state offers retry.
- [ ] Unsupported file, too large, extraction failed, empty file: four distinct messages in Thai (the four error codes of the data contract).
- [ ] Warning or rain levels use text plus icon, not color alone; contrast at least 4.5:1 (3:1 for UI parts).
- [ ] Design standard: only tokens of `docs/design/DESIGN-expo.md` by name (no inline hex, radii or font sizes); black is the only CTA fill; blue only for inline links on white; pills only on badges; sky gradient only in the home hero band; no `muted` / `semantic-error` / `semantic-success` as text color; text on the gradient is `ink`.
- [ ] Selected tab/chip is distinguishable without color or border alone (the `hairline-strong` border is only 1.35:1 against white).

## 6. Content
- [ ] Disclaimer and TMD credit visible on every page that shows a summary.
- [ ] Numbers and units copied exactly from the source; "ร้อยละ N ของพื้นที่" never shown as a probability.
- [ ] General advice labeled "ข้อแนะนำทั่วไป".
- [ ] Page titles and headings are meaningful and in order (one `h1`).

## 7. Performance
- [ ] Fonts through `next/font`; images sized and lazy where below the fold.
- [ ] No client JavaScript for static content; `'use client'` only on leaves.
- [ ] Data fetched once on the server and cached; no request waterfalls.

## 8. Screenshots to take (and describe)
375x812 mobile, 768x1024 tablet, 1280x800 desktop, plus 320 wide. For each page and for loading, empty and error states.
