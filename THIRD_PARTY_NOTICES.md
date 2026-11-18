# Third-party notices

The skills and rules in `.claude/` are **written from scratch for this project**. They are informed by the public material below. No text was copied from these repositories; the authors did not read the original files line by line and relied on summaries from a research pass (see `docs/decisions/0008-md-and-skills.md`). The sources are credited for the ideas they contributed. Each project's own license file is the authority; copyright holder names were not verified here.

| Source | License | What informed us |
|---|---|---|
| https://github.com/anthropics/skills `frontend-design` | Apache-2.0 (LICENSE.txt checked) | design note before code, quality floor (responsive, focus, accessibility), user-centered copy |
| https://github.com/anthropics/skills `webapp-testing` | Apache-2.0 (LICENSE.txt checked) | reconnaissance-then-action browser checks, screenshots at several viewports |
| https://github.com/obra/superpowers `writing-plans`, `brainstorming`, `verification-before-completion`, `test-driven-development`, `systematic-debugging` | MIT | phase planning structure, evidence before completion claims, red-green for pure logic, short debugging method |
| https://github.com/vercel-labs/agent-skills `composition-patterns`, `react-best-practices`, `deploy-to-vercel` | MIT (per repository) | composition over boolean props, a few high-priority React rules, order of deploy checks |
| https://github.com/vercel-labs/web-interface-guidelines | MIT | interface checklist topics (interaction, layout, forms, states, content, performance) |
| https://github.com/boom-vitt/claude-thai-skills `thai-text-processing`, `thai-date-format` | MIT | Unicode normalization, Thai text pitfalls, Buddhist-era dates |
| https://github.com/wshobson/agents (python-development, tailwind-design-system) | MIT | reference for Python layout and Tailwind v4 syntax |

## Font and design standard (used by the web app)

| Item | License / origin | How it is used |
|---|---|---|
| **Anuphan** font, https://github.com/cadsondemak/Anuphan (Cadson Demak; a Thai Loopless extension of IBM Plex) | SIL Open Font License 1.1 (as reported by the GitHub repository API on 2026-11-16; check the repository's OFL.txt before shipping) | Loaded through `next/font/google` (or self-hosted with its license text if that fails). The Plex Latin design is credited by the Anuphan README to https://github.com/IBM/plex |
| `docs/design/DESIGN-expo.md`, a design-system analysis of the Expo marketing site, provided by the user | Not stated in the file. Treated as the user's reference document; read-only | Source of design tokens and component rules. Only token values and rules are reused; no Expo logo, name, imagery or copy is used in the app |

Inter and JetBrains Mono, which `docs/design/DESIGN-expo.md` names, are not used.

Other sources used for conventions: Google engineering practices and style guides, PEP 8 / 257 / 686, Next.js, Vercel, Claude Code and WCAG 2.2 documentation. These are cited in the research files kept outside this repository.

If any text is later copied or adapted closely from the projects above, add the license text and a note of the changes here and in the skill folder.
