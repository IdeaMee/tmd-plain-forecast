# R1 — Claude Code Skills และ CLAUDE.md: งานวิจัยก่อนเขียน skill ของโปรเจกต์

- วันที่ค้นคว้า: 2026-11-16 (ทุก URL เข้าถึงในวันนี้)
- ขอบเขต: research อย่างเดียว ยังไม่ได้สร้าง skill, ไม่ได้ติดตั้งอะไร, ไม่ได้ใช้ git
- สัญลักษณ์: **[unverified]** = ยังไม่ได้ยืนยันจากแหล่งต้นทาง / เป็นข้อสรุปของผู้เขียน

---

## สารบัญ
1. สรุปสั้นที่สุด (TL;DR)
2. Agent Skills จากเอกสารทางการ
3. CLAUDE.md, `.claude/rules/`, AGENTS.md จากเอกสารทางการ
4. Best practices ของ Claude Code ที่เกี่ยวกับการเขียนโค้ดเป็น phase
5. Skill สาธารณะที่ควรพิจารณา (ประเมินทีละตัว + license)
6. ข้อเสนอแนะสำหรับชุด skill ของเรา
7. อะไรควรอยู่ที่ CLAUDE.md / rules / skill / docs/ / hook
8. เรื่อง license และการ attribution เมื่อดัดแปลงข้อความ
9. สิ่งที่ยังไม่ได้ตรวจ

---

## 1. สรุปสั้นที่สุด (TL;DR)

1. **CLAUDE.md ต้องสั้น (< 200 บรรทัด)** และใส่เฉพาะสิ่งที่ Claude อ่านจาก repo เองไม่ได้: คำสั่ง test/typecheck/lint ที่ใช้จริง, ข้อตัดสินใจของทีม, กับดักต่างๆ ส่วน "อธิบาย architecture/file layout" ถูกจัดเป็น *old advice* แล้ว ([best-practices](https://code.claude.com/docs/en/best-practices), [memory](https://code.claude.com/docs/en/memory))
2. **Skill โหลดแค่ name+description ตอนเริ่ม session** ตัวเนื้อหาโหลดเมื่อใช้ ดังนั้น description คือตัวตัดสินว่า skill จะถูกใช้หรือไม่ ([skills](https://code.claude.com/docs/en/skills))
3. **ข้อค้นพบสำคัญจาก Vercel:** ใน eval ของ Next.js skill แบบ "ความรู้" ไม่ถูกเรียกใช้ใน 56% ของเคส (pass rate 53% เท่ากับไม่มี skill) ขณะที่ docs index ใน AGENTS.md ได้ 100% ([Vercel blog, 2026-01-27](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)) → **มาตรฐานที่ต้องใช้ "ทุกครั้งที่แก้ไฟล์ประเภทนั้น" ควรเป็น path-scoped rule (`.claude/rules/*.md` + `paths:`) ไม่ใช่ skill** ส่วน skill เหมาะกับ "procedure/workflow" มากกว่า
4. Next.js ≥16.2 มี docs ตรงเวอร์ชันใน `node_modules/next/dist/docs/` และ (≥16.3) `next dev`/`create-next-app` จะเขียน block ลง `AGENTS.md` ให้เอง ([nextjs.org ai-agents, lastUpdated 2026-10-15](https://nextjs.org/docs/app/guides/ai-agents)) → ถ้าเรามี CLAUDE.md ด้วย **ต้องใส่ `@AGENTS.md` ใน CLAUDE.md** เพราะ Claude Code จะไม่อ่าน AGENTS.md เมื่อมี CLAUDE.md อยู่แล้ว ([memory#agents-md](https://code.claude.com/docs/en/memory))
5. Skill สาธารณะที่ดีที่สุดสำหรับเรา: Anthropic `frontend-design` + `webapp-testing` (Apache-2.0), obra/superpowers `verification-before-completion`, `writing-plans`, `brainstorming`, `systematic-debugging` (MIT), Vercel `composition-patterns`, `react-best-practices`, `web-interface-guidelines` (MIT), wshobson python skills (MIT), boom-vitt `thai-text-processing` (MIT) — **ทั้งหมดควร "ดัดแปลงบางส่วน" ไม่ใช่ติดตั้งทั้งก้อน** เพราะหลายตัวสั่ง commit/push เอง (ขัดกฎ "git เฉพาะเมื่อสั่ง") หรือหนักเกินไป หรือดึงข้อมูลจาก URL ภายนอกตอน runtime
6. ข้อเสนอโครงสร้าง: CLAUDE.md ~80–120 บรรทัด + `.claude/rules/` 2–3 ไฟล์ (python, frontend, thai) + skill 5–6 ตัวที่เป็น procedure (ลด/รวมจาก 7) + `docs/` เก็บ spec, แผน phase, โครงโฟลเดอร์แบบยืดหยุ่น

---

## 2. Agent Skills จากเอกสารทางการ

แหล่งหลัก:
- Claude Code: https://code.claude.com/docs/en/skills (ไม่มีวันที่บนหน้า; อ้างอิงพฤติกรรมของ Claude Code v2.1.2xx–v2.1.3xx)
- Platform best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Open spec: https://agentskills.io/specification
- Anthropic Engineering blog (2025-10-16): https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

### 2.1 Skill คืออะไร
- โฟลเดอร์ที่มี `SKILL.md` (YAML frontmatter + Markdown) Claude ใช้เองเมื่อเกี่ยวข้อง หรือผู้ใช้เรียกด้วย `/skill-name` เป็นไปตาม open standard Agent Skills ([skills](https://code.claude.com/docs/en/skills))
- ควรสร้าง skill เมื่อ "คุณ paste คำสั่ง/ขั้นตอนเดิมซ้ำๆ" หรือเมื่อส่วนหนึ่งใน CLAUDE.md กลายเป็น procedure แทนที่จะเป็น fact ([skills](https://code.claude.com/docs/en/skills))
- Skill มี 2 แบบ: **reference skill** (ความรู้ใช้ตลอด session เช่น style guide) และ **action skill** (สั่งทำงาน เช่น `/deploy`) ([features-overview](https://code.claude.com/docs/en/features-overview))
- Custom slash commands (`.claude/commands/*.md`) ถูก merge เข้ากับ skills แล้ว ยังใช้ได้ แต่ถ้าต้องมีไฟล์ประกอบให้แปลงเป็น `.claude/skills/<name>/SKILL.md` ([skills](https://code.claude.com/docs/en/skills))

### 2.2 Frontmatter fields

| Field | ความหมาย | หมายเหตุ |
|---|---|---|
| `name` | ชื่อคำสั่งใน `/` menu; default = ชื่อโฟลเดอร์ | spec: 1–64 ตัว, a-z 0-9 และ `-`, ห้ามขึ้นต้น/ลงท้าย/ซ้อน `--`, **ต้องตรงกับชื่อโฟลเดอร์** ([spec](https://agentskills.io/specification)); ห้ามมีคำ `anthropic`, `claude` ([platform BP](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)) |
| `description` | ทำอะไร + ใช้เมื่อไร — Claude ใช้ตัดสินใจโหลด | ≤1,024 ตัว (spec/platform); ใน Claude Code `description`+`when_to_use` ถูกตัดที่ 1,536 ตัวใน listing ([skills](https://code.claude.com/docs/en/skills)) |
| `when_to_use` | trigger เพิ่มเติม ต่อท้าย description | Claude Code เท่านั้น |
| `argument-hint`, `arguments` | hint/ชื่อ argument (`$0`, `$name`, `$ARGUMENTS`) | |
| `disable-model-invocation` | `true` = ผู้ใช้เรียกได้อย่างเดียว, description ไม่อยู่ใน context | แนะนำสำหรับ workflow ที่มี side effect ([best-practices](https://code.claude.com/docs/en/best-practices)) |
| `user-invocable` | `false` = ซ่อนจาก `/` menu, Claude เรียกเท่านั้น | |
| `allowed-tools` | tools ที่ใช้ได้โดยไม่ถาม permission ระหว่าง turn นั้น | ไม่ได้จำกัด tool อื่น; spec ระบุว่า experimental |
| `disallowed-tools` | เอา tool ออกระหว่าง skill active | |
| `model`, `effort` | override model/effort | |
| `context: fork` + `agent` + `background` | รัน skill เป็น subagent (ไม่เห็นประวัติแชต) | |
| `hooks` | hook ที่ลงทะเบียนเมื่อ skill ถูกเรียก | |
| `paths` | glob จำกัดการ auto-activate เฉพาะไฟล์ที่ตรง | |
| `shell` | `bash` (default) หรือ `powershell` สำหรับ `` !`cmd` `` | เกี่ยวกับเครื่อง Windows ของทีม |
| `license`, `compatibility`, `metadata` | field ของ spec; Claude Code รับแต่ไม่ใช้ | |

ที่มา: [skills](https://code.claude.com/docs/en/skills), [spec](https://agentskills.io/specification)

ข้อควรระวัง: field ที่สะกดผิดจะถูก**ละเลยแบบเงียบ** และถ้า YAML พัง skill จะโหลดด้วย metadata ว่าง (Claude จับคู่กับ description ไม่ได้) ตรวจด้วย `claude plugin validate .claude/skills` ([skills](https://code.claude.com/docs/en/skills))

### 2.3 ขนาดและ progressive disclosure
- 3 ระดับ: (1) metadata ~100 tokens โหลดตอนเริ่ม (2) body แนะนำ < 5,000 tokens โหลดเมื่อ activate (3) ไฟล์ใน `scripts/`, `references/`, `assets/` โหลดเมื่อจำเป็น ([spec](https://agentskills.io/specification), [engineering blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills))
- `SKILL.md` < 500 บรรทัด ([skills](https://code.claude.com/docs/en/skills), [platform BP](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices))
- เมื่อโหลดแล้วเนื้อหาค้างอยู่ใน context ทุก turn → ทุกบรรทัดคือต้นทุนซ้ำ; หลัง auto-compaction จะ re-attach เฉพาะ **5,000 tokens แรก** ของแต่ละ skill (รวมไม่เกิน 25,000) → **ใส่กฎสำคัญไว้บนสุดของ SKILL.md** ([skills](https://code.claude.com/docs/en/skills))
- อ้างไฟล์ประกอบแค่ **ลึกชั้นเดียว** จาก SKILL.md (ไฟล์ซ้อนไฟล์ Claude อาจอ่านแค่ `head`); ไฟล์ reference > 100 บรรทัดให้มีสารบัญด้านบน ([platform BP](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices))
- ระบุชัดว่า script ให้ "รัน" หรือ "อ่านเป็นตัวอย่าง"; script รันได้โดยไม่กิน context เฉพาะ output เท่านั้น ([platform BP](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices))
- ใช้ `${CLAUDE_SKILL_DIR}` อ้าง path ของ script ภายใน skill ([skills](https://code.claude.com/docs/en/skills))
- ใช้ forward slash ใน path เสมอ แม้บน Windows ([platform BP](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices))

### 2.4 ที่อยู่ของ skill และลำดับความสำคัญ

| ระดับ | Path | ใช้กับ |
|---|---|---|
| Enterprise | managed settings | ทั้งองค์กร |
| Personal | `~/.claude/skills/<name>/SKILL.md` | ทุกโปรเจกต์ของเรา |
| **Project** | `.claude/skills/<name>/SKILL.md` | repo นี้ (commit แชร์ทีม) |
| Nested | `<subdir>/.claude/skills/...` | session ที่ทำงานในโฟลเดอร์ย่อย, เรียกแบบ `/apps/web:deploy` |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | namespaced `/plugin:skill` |

ชื่อซ้ำ: enterprise > personal > project (**personal ชนะ project** — ถ้าเพื่อนในทีมมี personal skill ชื่อเดียวกันจะบัง project skill) ([skills](https://code.claude.com/docs/en/skills)); แก้ไขไฟล์ skill ระหว่าง session มีผลทันที (live change detection) ([skills](https://code.claude.com/docs/en/skills))

### 2.5 Claude ตัดสินใจโหลด skill อย่างไร / วิธีเขียน description
- Claude จับคู่คำขอกับ `description` (+`when_to_use`) ถ้า description กว้างหรือซ้อนกันอาจโหลดผิดตัวหรือพลาด ([features-overview](https://code.claude.com/docs/en/features-overview))
- เขียน **บุรุษที่ 3** ("Processes Excel files…") ไม่ใช่ "I can help…" เพราะ description ถูกฉีดเข้า system prompt ([platform BP](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices))
- ต้องมีทั้ง "ทำอะไร" และ "ใช้เมื่อไร" + keyword ที่ผู้ใช้จะพูดจริง ([platform BP](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [skills troubleshooting](https://code.claude.com/docs/en/skills))
- `skill-creator` แนะนำให้ description "pushy" เล็กน้อยเพื่อลด under-triggering และใส่ทุกอย่างเรื่อง "when to use" ไว้ใน description ไม่ใช่ใน body ([skill-creator SKILL.md](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/SKILL.md))
- ถ้ามี skill เยอะ listing มี budget ~1% ของ context window; ถ้าเกิน description ของ skill ที่ใช้น้อยจะถูกตัดออก ([skills](https://code.claude.com/docs/en/skills)) — กับ 5–8 skill ไม่น่าเป็นปัญหา [unverified สำหรับกรณีที่ติดตั้ง plugin เพิ่มหลายตัว]
- **[ข้อเสนอ, unverified]** ผู้ใช้โปรเจกต์นี้มักพิมพ์ภาษาไทย → ใส่ keyword ทั้งไทยและอังกฤษใน description เช่น "ตัดคำ, PyThaiNLP, Thai tokenization"

### 2.6 Authoring best practices (ย่อ)
จาก [platform BP](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):
- "The context window is a public good" — สมมติว่า Claude ฉลาดอยู่แล้ว ใส่แค่สิ่งที่มันไม่รู้
- เลือก **degree of freedom** ตามความเปราะบางของงาน: high (heuristic), medium (template/pseudocode), low (script เป๊ะ)
- มี workflow เป็น checklist ให้ copy ไปติ๊ก, มี feedback loop "run validator → fix → repeat"
- หลีกเลี่ยงข้อมูลที่หมดอายุตามเวลา, ใช้ศัพท์คงที่ทั้ง skill, ให้ default หนึ่งทางแทนการเสนอหลายตัวเลือก
- ชื่อแนะนำรูป gerund (`processing-pdfs`) แต่ noun phrase ก็รับได้; ห้ามชื่อกว้าง (`helper`, `utils`)
- **Evaluation-driven:** รัน Claude โดยไม่มี skill ก่อน → จด failure จริง → สร้าง eval ≥3 ข้อ → เขียน instruction ขั้นต่ำ → iterate; ใช้ "Claude A เขียน / Claude B ทดสอบ"
- ทดสอบกับทุก model ที่จะใช้ (โปรเจกต์นี้ใช้ Opus และ Fable)
- จาก [best-practices](https://code.claude.com/docs/en/best-practices): ไม่ต้องใส่ IMPORTANT/ALL CAPS — model ปัจจุบันทำตามบรรทัดธรรมดา และการเน้นมากเกินทำให้ over-apply; skill-creator ก็แนะนำให้ "อธิบายเหตุผล" แทน MUST ตัวใหญ่ ([skill-creator](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/SKILL.md))
- ถ้า Claude ข้ามกฎใน skill ที่ต้องเกิดทุกครั้ง → ย้ายไปเป็น hook (ใส่ใน `hooks` frontmatter ของ skill ได้) ([skills troubleshooting](https://code.claude.com/docs/en/skills))

### 2.7 Anti-patterns (รวมจากหลายแหล่ง)
| Anti-pattern | ที่มา |
|---|---|
| อธิบายสิ่งที่ Claude รู้อยู่แล้ว (verbose) | [platform BP](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) |
| reference ซ้อนหลายชั้น | เดียวกัน |
| Windows-style path `scripts\x.py` | เดียวกัน |
| เสนอ library หลายตัวโดยไม่มี default | เดียวกัน |
| script ที่ "โยน error ให้ Claude แก้เอง", magic number | เดียวกัน |
| description กว้าง ("Helps with documents") | เดียวกัน, [spec](https://agentskills.io/specification) |
| skill ที่มี side effect แต่ให้ model เรียกเองได้ | [best-practices](https://code.claude.com/docs/en/best-practices) |
| เขียนสิ่งที่ Claude หาเองได้จาก repo | [best-practices](https://code.claude.com/docs/en/best-practices) ("The CLAUDE.md rule applies to skills too") |
| ติดตั้ง skill จากแหล่งไม่น่าเชื่อถือโดยไม่อ่าน script | [engineering blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), [travisvn list](https://github.com/travisvn/awesome-claude-skills) |

### 2.8 ความสัมพันธ์กับ feature อื่น (สั้นๆ)
จาก [features-overview](https://code.claude.com/docs/en/features-overview):
- **CLAUDE.md** = โหลดทุก session ("always do X"); **Skill** = on-demand
- **`.claude/rules/`** = โหลดทุก session หรือเมื่อเปิดไฟล์ที่ตรง `paths`
- **Subagent** = worker แยก context คืนแค่สรุป; skill preload เข้า subagent ได้ (`skills:`) และ skill รันเป็น subagent ได้ (`context: fork`)
- **Hook** = deterministic รันทุกครั้งที่เกิด event, context cost เป็นศูนย์; "Put guardrails in hooks"
- **Plugin** = แพ็กเกจรวม skills/hooks/agents/MCP สำหรับหลาย repo — โปรเจกต์ repo เดียวอย่างเราไม่จำเป็น
- **Bundled skills** ที่มากับ Claude Code: `/code-review`, `/verify`, `/run`, `/debug`, `/batch`, `/loop`, `/skill-doctor` ฯลฯ ([skills](https://code.claude.com/docs/en/skills)) → ไม่ต้องเขียน skill ซ้ำกับของเหล่านี้

---

## 3. CLAUDE.md / rules / AGENTS.md จากเอกสารทางการ

แหล่ง: [memory](https://code.claude.com/docs/en/memory), [best-practices](https://code.claude.com/docs/en/best-practices), [features-overview](https://code.claude.com/docs/en/features-overview)

### 3.1 ลำดับชั้น (hierarchy)

| Scope | Location | ใช้สำหรับ |
|---|---|---|
| Managed policy | `C:\Program Files\ClaudeCode\CLAUDE.md` (Windows) | องค์กร |
| User | `~/.claude/CLAUDE.md` | ความชอบส่วนตัวทุกโปรเจกต์ |
| **Project** | `./CLAUDE.md` หรือ `./.claude/CLAUDE.md` | ทีม (commit) |
| Local | `./CLAUDE.local.md` (ใส่ `.gitignore`) | ความชอบส่วนตัวในโปรเจกต์นี้ |

- ไฟล์ในโฟลเดอร์แม่ของ working dir โหลดตอนเริ่ม; **CLAUDE.md ในโฟลเดอร์ย่อยโหลดเมื่อ Claude อ่าน/แก้ไฟล์ในโฟลเดอร์นั้น**; ทุกไฟล์ถูกต่อกัน (ไม่ override) ([memory](https://code.claude.com/docs/en/memory))
- CLAUDE.md ในโฟลเดอร์ย่อย/rules ที่โหลดแบบ on-demand มี limit ต่อไฟล์ 40,000 ตัวอักษร (context 200K) เกินจะได้แค่ส่วนต้น ([memory](https://code.claude.com/docs/en/memory))
- Root CLAUDE.md ถูกอ่านใหม่หลัง `/compact`; nested/path rules โหลดใหม่เมื่อแตะไฟล์อีกครั้ง ([memory](https://code.claude.com/docs/en/memory))
- **HTML comment ระดับ block (`<!-- ... -->`) ถูกตัดออกก่อนส่งให้ Claude** → ใช้เขียนโน้ตภาษาไทยถึงเพื่อนในทีมได้โดยไม่กิน token ([memory](https://code.claude.com/docs/en/memory))

### 3.2 ความยาวและโครงสร้าง
- เป้าหมาย **< 200 บรรทัดต่อไฟล์** ยาวกว่านี้กิน context และลด adherence ([memory](https://code.claude.com/docs/en/memory))
- `@path` import ช่วยจัดระเบียบแต่ **ไม่ลด context** เพราะไฟล์ที่ import โหลดพร้อมกัน ([memory](https://code.claude.com/docs/en/memory))
- เขียนให้ "ตรวจสอบได้": "Run `npm test` before committing" ดีกว่า "Test your changes" ([memory](https://code.claude.com/docs/en/memory))
- ใช้ header + bullet; ตรวจหาคำสั่งที่ขัดกันเป็นระยะ (`/doctor prompt-audit`) ([memory](https://code.claude.com/docs/en/memory))
- ตัวอย่าง CLAUDE.md ที่ดีจาก docs มีแค่ 3 หมวด: `# Commands`, `# Conventions`, `# Gotchas` ([best-practices](https://code.claude.com/docs/en/best-practices))

### 3.3 ควรใส่ / ไม่ควรใส่ ([best-practices](https://code.claude.com/docs/en/best-practices))
ใส่:
- วิธียืนยันงาน: คำสั่ง test, typecheck, lint, วิธีรัน test ไฟล์เดียว ("the single most useful line in your CLAUDE.md is the command that runs it")
- จุดที่โค้ดหลอกตา (pattern เก่าที่ห้ามลอก, โฟลเดอร์ที่ดูไม่ใช้แต่ใช้)
- ข้อตัดสินใจที่ไม่อยู่ใน repo
- สิ่งที่ต้องแก้ Claude ซ้ำ 2 ครั้งแล้ว

ไม่ใส่:
- สิ่งที่ Claude หาเองได้จากการอ่านโค้ด (ทดสอบ 2 ข้อ: หาได้ไหม? จะไปหาจริงไหม? ถ้าใช่ทั้งคู่ ตัดทิ้ง)
- architecture/file layout (Claude อ่าน repo เอง) — แต่ช่วงต้นโปรเจกต์ที่ repo ยังว่าง ข้อมูลนี้ "ยังไม่อยู่ใน repo" จึงควรอยู่ใน `docs/` [ข้อเสนอ]
- procedure หลายขั้น → skill; กฎเฉพาะบางส่วนของโค้ด → path-scoped rule ([memory](https://code.claude.com/docs/en/memory))
- กฎที่ต้องไม่มีข้อยกเว้น → hook / deny rule ("If you keep adding emphasis to a CLAUDE.md line… that line belongs in a hook")

### 3.4 `.claude/rules/`
- ไฟล์ `.md` ใน `.claude/rules/` (ค้นหาแบบ recursive) ถ้าไม่มี `paths` โหลดทุก session เหมือน CLAUDE.md; ถ้ามี `paths:` (glob, รองรับ `{ts,tsx}`) โหลดเมื่อ Claude Read/Write/Edit ไฟล์ที่ตรง ([memory](https://code.claude.com/docs/en/memory))
- `paths` เป็น field เดียวที่ rule อ่าน ([memory](https://code.claude.com/docs/en/memory))
- เหมาะกับ "language-specific หรือ directory-specific guidelines" ([features-overview](https://code.claude.com/docs/en/features-overview))
- **ข้อได้เปรียบเหนือ skill สำหรับ "มาตรฐานโค้ด":** การโหลดขึ้นกับไฟล์ที่แตะ (กลไก harness) ไม่ได้ขึ้นกับการที่ model ตัดสินใจเรียก skill — สอดคล้องกับผล eval ของ Vercel ที่ skill ไม่ถูกเรียก 56% ([Vercel blog](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)) [ข้อสรุปของผู้เขียน]

### 3.5 AGENTS.md
- [agents.md](https://agents.md/): "README for agents" รูปแบบ Markdown เปิด ใช้ใน 60k+ โปรเจกต์ ดูแลโดย Agentic AI Foundation ภายใต้ Linux Foundation; หมวดแนะนำ: overview, build/test commands, code style, testing, security; ใน monorepo ไฟล์ที่ใกล้ที่สุดชนะ; รองรับโดย Codex, Cursor, Copilot, Gemini CLI ฯลฯ
- Claude Code (≥ v2.1.277) อ่าน AGENTS.md ได้ **เฉพาะเมื่อไม่มี CLAUDE.md / CLAUDE.local.md** ใน working dir หรือโฟลเดอร์แม่ ถ้ามีทั้งคู่จะอ่าน CLAUDE.md อย่างเดียว ([memory#agents-md](https://code.claude.com/docs/en/memory))
- วิธีแนะนำให้ใช้ไฟล์เดียวร่วมกัน: CLAUDE.md บรรทัดแรก `@AGENTS.md` แล้วต่อด้วยคำสั่งเฉพาะ Claude; **บน Windows ห้ามใช้ symlink** (ต้องสิทธิ์ admin และ git checkout เป็นไฟล์ข้อความ) ([memory](https://code.claude.com/docs/en/memory))
- **Next.js:** ตั้งแต่ 16.3 `next dev` เมื่อเจอ coding agent จะสร้าง/อัปเดต block `<!-- BEGIN:nextjs-agent-rules -->` ใน `AGENTS.md` ชี้ไป docs ใน `node_modules/next/dist/docs/` และ `create-next-app` สร้าง agent files ให้ ([nextjs ai-agents](https://nextjs.org/docs/app/guides/ai-agents)) — แหล่งรอง ([dev.to](https://dev.to/rabinarayanpatra/nextjs-162-agentsmd-and-next-browser-a-hands-on-guide-k65)) ระบุว่ามี CLAUDE.md ที่มี `@AGENTS.md` ให้ด้วย **[unverified จากแหล่งทางการ]**
- ผลต่อเรา: ให้ AGENTS.md เป็นของ Next.js (block ที่ระบบจัดการ) + ข้อมูลทั่วไปที่ tool อื่นใช้ได้; CLAUDE.md = `@AGENTS.md` + ส่วนเฉพาะ Claude [ข้อเสนอ]

### 3.6 Auto memory (ข้อมูลประกอบ)
- Claude เขียนโน้ตเองที่ `~/.claude/projects/<project>/memory/` โหลด 200 บรรทัดแรก/25KB ของ `MEMORY.md` ทุก session; เป็นของเครื่องแต่ละคน ไม่แชร์ทีม ([memory](https://code.claude.com/docs/en/memory)) → กฎของทีมต้องอยู่ใน CLAUDE.md/rules ที่ commit ไม่ใช่ auto memory

---

## 4. Best practices ของ Claude Code ที่เกี่ยวกับการทำงานเป็น phase

แหล่ง: [best-practices](https://code.claude.com/docs/en/best-practices) (หน้าเก่า anthropic.com/engineering/claude-code-best-practices redirect 308 มาที่หน้านี้แล้ว), [common-workflows](https://code.claude.com/docs/en/common-workflows)

| หลัก | รายละเอียด |
|---|---|
| Tell Claude what it can't see | เขียนเฉพาะข้อมูลที่ไม่อยู่ใน repo; prompt ระบุไฟล์ อาการ และนิยาม "เสร็จ" |
| Brainstorm/interview ก่อน | "Interview me until you could write the spec, then write it to SPEC.md" แล้วเริ่ม session ใหม่เพื่อ build จาก spec |
| Give Claude a check to run | test, build exit code, linter, script diff กับ fixture, screenshot เทียบ mockup; ขอ **หลักฐาน** (คำสั่ง + output) ไม่ใช่แค่ "tests pass" |
| ระดับการบังคับ | prompt → `/goal` → Stop hook (เช่น `tsc --noEmit 1>&2 \|\| exit 2`) → reviewer อิสระ (`/code-review`, subagent) |
| Review against spec | ให้ subagent ตรวจ diff เทียบ SPEC.md และ "skip style" (reviewer ที่ถูกขอให้หาปัญหาจะหาเจอเสมอ → over-engineering) |
| Plan mode | `Shift+Tab` หรือ `--permission-mode plan` อ่านไฟล์+เสนอแผนโดยไม่แก้ไฟล์จนกว่าจะอนุมัติ |
| Enforce | กฎไม่มีข้อยกเว้น → hook/deny rule (เช่น deny `Read(./.env)`); อย่ามี hook เยอะเกิน |
| Steer | ดูนาทีแรก, `Esc` เมื่อเบี่ยง, แก้ 2 ครั้งไม่ได้ให้ `/clear` แล้วเขียน prompt ใหม่ |
| Context | `/clear` ระหว่างงานที่ไม่เกี่ยวกัน; ใช้ `/usage` ดูต้นทุน |
| Effort | ใช้ `/effort` แทนคำว่า "think hard"; `ultrathink` สำหรับครั้งเดียว |
| สิ่งที่เลิกทำได้ | ALL CAPS/IMPORTANT, "keep going don't be lazy", อธิบาย architecture ใน CLAUDE.md, ใช้ subagent เพื่อ "คำตอบที่ฉลาดกว่า" |
| `/init` | สร้าง CLAUDE.md เริ่มต้น; ตั้ง `CLAUDE_CODE_NEW_INIT=1` เพื่อ flow แบบถาม-ตอบที่เสนอทั้ง CLAUDE.md, skills, hooks ([memory](https://code.claude.com/docs/en/memory)) |

ความหมายต่อการสั่ง "generate code ทีละ phase": แต่ละ phase ควรมี (1) spec/แผนใน `docs/` (2) คำสั่ง verify ที่ชัด (3) เริ่ม session ใหม่ต่อ phase แล้วชี้ไปที่ไฟล์แผน (4) review ด้วย `/code-review` หรือ subagent เทียบกับแผน [สังเคราะห์จากแหล่งข้างต้น]

---

## 5. Skill สาธารณะที่ควรพิจารณา

### 5.1 ตารางสรุป license

| แหล่ง | License | ยืนยันแล้ว? |
|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) (~196k stars) | README: "Many skills… open source (Apache 2.0)"; docx/pdf/pptx/xlsx ก็ Apache 2.0 | `frontend-design/LICENSE.txt` = Apache 2.0 ✔, `webapp-testing/LICENSE.txt` = Apache 2.0 ✔, `skill-creator` ✘ [unverified] |
| [obra/superpowers](https://github.com/obra/superpowers) (~318k stars) | MIT | ✔ (จากหน้า repo) |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) (~34k stars) | MIT | ✔ repo; frontmatter `react-best-practices`, `composition-patterns` = MIT ✔; `web-design-guidelines`, `deploy-to-vercel` ไม่มี field license (ใช้ license repo) |
| [vercel-labs/web-interface-guidelines](https://github.com/vercel-labs/web-interface-guidelines) | MIT | ✔ |
| [vercel/next.js skills](https://github.com/vercel/next.js/tree/canary/skills) | Next.js repo เป็น MIT | [unverified สำหรับโฟลเดอร์ skills] |
| [wshobson/agents](https://github.com/wshobson/agents) (~43k stars) | MIT ("external plugins have their own licenses") | ✔ |
| [boom-vitt/claude-thai-skills](https://github.com/boom-vitt/claude-thai-skills) (~63 stars) | MIT | ✔ (จากหน้า repo) |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | ไม่เห็นบนหน้า | ✘ (เป็นแค่ list ไม่ได้จะลอกข้อความ) |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Apache-2.0 (repo), แต่ละ plugin มี LICENSE ของตัวเอง | ✔ repo |

ข้อสังเกตด้านความปลอดภัย: skill รันโค้ดได้ ควรอ่าน SKILL.md และ script ทุกตัวก่อนใช้ ([engineering blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), [travisvn list](https://github.com/travisvn/awesome-claude-skills)); README ของ anthropics/skills ระบุว่าเป็น "demonstration and educational purposes" ([README](https://raw.githubusercontent.com/anthropics/skills/main/README.md))

### 5.2 Anthropic — `frontend-design`
- URL: https://github.com/anthropics/skills/tree/main/skills/frontend-design — Apache 2.0 ✔
- เนื้อหา (~75–80 บรรทัด): role เป็น design lead; ground ใน subject matter/ผู้ใช้; typography 1–2 family, บรรทัด < ~80 ตัวอักษร; palette 4–6 สี hex; หลีกเลี่ยง "AI aesthetic" ทั่วไป (การ์ด SaaS โค้งเหมือนกันหมด, gradient); motion น้อยแต่มีความหมาย; process: เขียน design plan สั้น (tokens, ASCII wireframe) → review → build → critique; **quality floor: responsive, focus states, reduced motion, accessibility**; copy เขียนจากมุมผู้ใช้ ([SKILL.md](https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md))
- ใช้ได้กับเรา: process "design plan ก่อนโค้ด", quality floor, กฎ copy, การกำหนด design tokens
- ไม่ควรลอก: แนวคิด "distinctive/bold" เต็มรูปแบบ — เว็บพยากรณ์อากาศภาษาไทยเน้นอ่านง่าย/โหลดเร็ว/ใช้บนมือถือ มากกว่าความแปลกใหม่ [ความเห็น]; กฎ typography ภาษาอังกฤษบางข้อ (เช่น serif line height) ต้องปรับให้เข้ากับฟอนต์ไทย

### 5.3 Anthropic — `webapp-testing`
- URL: https://github.com/anthropics/skills/tree/main/skills/webapp-testing — Apache 2.0 ✔
- เนื้อหา (~700 คำ): Python Playwright (sync API, headless Chromium); decision tree static vs dynamic; **reconnaissance-then-action** (รอ networkidle → screenshot/inspect DOM → หา selector → action); `scripts/with_server.py` จัดการ server หลายตัว (ให้รัน `--help` และใช้แบบ black box); examples 3 ไฟล์ ([SKILL.md](https://raw.githubusercontent.com/anthropics/skills/main/skills/webapp-testing/SKILL.md))
- ใช้ได้กับเรา: pattern recon-then-action สำหรับตรวจหน้าเว็บ responsive (screenshot ที่ 375px/768px/1280px) และหน้า upload PDF; ทีมใช้ Python อยู่แล้ว
- ไม่ควรลอก: ต้องติดตั้ง Playwright + browser (หนักสำหรับเครื่องทีม) [unverified ว่าทีมพร้อม]; Claude Code มี bundled `/verify` และ `/run` อยู่แล้ว ([skills](https://code.claude.com/docs/en/skills)) และ Next.js มี `next-dev-loop` skill ([nextjs ai-agents](https://nextjs.org/docs/app/guides/ai-agents)) — เลือกอย่างใดอย่างหนึ่ง

### 5.4 Anthropic — `skill-creator`
- URL: https://github.com/anthropics/skills/tree/main/skills/skill-creator — license [unverified]
- เนื้อหา (~400–450 บรรทัด + scripts/agents): capture intent → interview → เขียน SKILL.md → test cases ใน `evals/evals.json` → รันแบบมี/ไม่มี skill → benchmark → iterate → optimize description ด้วย query ~20 ข้อ ([SKILL.md](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/SKILL.md), [skills docs](https://code.claude.com/docs/en/skills))
- ใช้ได้กับเรา: **ใช้เป็นเครื่องมือตอนเขียน skill** (ติดตั้งเป็น plugin ชั่วคราวหรือใช้ที่มีใน claude.ai) ไม่ต้อง commit เข้า repo
- ไม่ควรลอก: ทั้งตัว (หนัก, เป็น meta-tool)

### 5.5 obra/superpowers (MIT)
- URL: https://github.com/obra/superpowers — 15 skills; workflow: brainstorming → using-git-worktrees → writing-plans → subagent-driven-development/executing-plans → test-driven-development → requesting-code-review → finishing-a-development-branch ([repo](https://github.com/obra/superpowers))

| Skill | เนื้อหาหลัก | ใช้ได้ | ไม่ควรลอก |
|---|---|---|---|
| [`brainstorming`](https://raw.githubusercontent.com/obra/superpowers/main/skills/brainstorming/SKILL.md) (~230–250 บรรทัด) | ถามทีละคำถาม, เสนอ 2–3 approach พร้อมแนะนำ, design doc ที่ `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`, HARD-GATE ห้าม build ก่อนอนุมัติ | แนวคิด "ถามเฉพาะสิ่งที่เปลี่ยนสิ่งที่จะสร้าง", เสนอ default พร้อมเหตุผล | การ commit spec อัตโนมัติ; description แบบ "You MUST use this before any creative work" (ขัดแนว Anthropic เรื่องไม่ใช้ MUST) |
| [`writing-plans`](https://raw.githubusercontent.com/obra/superpowers/main/skills/writing-plans/SKILL.md) (~180–200 บรรทัด) | header (goal, architecture, tech stack, link spec, Global Constraints, Review Focus); task = หน่วยเล็กสุดที่มี test cycle ของตัวเอง; ระบุไฟล์/signature/test; "แผนยาวกว่าโค้ด = ล้มเหลว"; scope check แยกแผนเมื่อมีหลาย subsystem; self-review | **เหมาะมากกับการวางแผนเป็น phase** ของเรา | ขั้น "commit" ทุก task; path `docs/superpowers/` |
| `executing-plans` / `subagent-driven-development` | รันแผน inline หรือ subagent ต่อ task + review | แนวคิด review ระหว่าง task | subagent ต่อ task = token เยอะ (best-practices เตือนเรื่องต้นทุน subagent) |
| [`test-driven-development`](https://raw.githubusercontent.com/obra/superpowers/main/skills/test-driven-development/SKILL.md) (~290 บรรทัด) | Iron law: ไม่มี production code ถ้าไม่มี failing test; "Delete means delete"; red-green-refactor; rationalization table | red-green สำหรับ regex extraction / NB / k-NN (input→output ชัด) | ความเข้มงวด "ลบโค้ดที่เขียนก่อน test" — หนักเกินสำหรับโปรเจกต์นักศึกษา/UI |
| [`systematic-debugging`](https://raw.githubusercontent.com/obra/superpowers/main/skills/systematic-debugging/SKILL.md) (~290 บรรทัด + 3 ไฟล์) | 4 phase: root cause → pattern analysis → hypothesis → implementation; แก้ 3 ครั้งไม่ได้ให้หยุดตั้งคำถาม architecture | ย่อเหลือ ~20 บรรทัดใน testing skill | ไฟล์ประกอบทั้งหมด; มี bundled `/debug` อยู่แล้ว |
| [`verification-before-completion`](https://raw.githubusercontent.com/obra/superpowers/main/skills/verification-before-completion/SKILL.md) (~120 บรรทัด) | "Evidence before assertions"; gate 5 ขั้น (หาคำสั่ง → รัน → อ่าน output/exit code → ยืนยัน → ค่อยอ้าง); ตาราง claim→หลักฐาน (lint ผ่านไม่ได้แปลว่า build ผ่าน); ตรวจ diff เองไม่เชื่อรายงาน subagent | **แกนของ testing-and-verification** ตรงกับ best-practices ทางการ ("ask Claude for evidence") | ภาษาแรง ("lying"), ALL CAPS |
| `using-git-worktrees`, `finishing-a-development-branch` | worktree/merge/PR | — | **ขัดกฎ "git เฉพาะเมื่อสั่ง" ทั้งหมด** |
| `using-superpowers` (meta) | บังคับเช็ค skill ก่อนทุก task | — | ไม่ใช้ |

### 5.6 Vercel (MIT)

| Skill | เนื้อหา | ใช้ได้ | ไม่ควรลอก |
|---|---|---|---|
| [`react-best-practices`](https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/react-best-practices/SKILL.md) (name: `vercel-react-best-practices`, ~165 บรรทัด + `rules/*.md` + AGENTS.md รวม) | 40+ กฎ 8 หมวดเรียงตาม priority: waterfalls (CRITICAL), bundle size (CRITICAL), server-side perf, client fetching, re-render, rendering, JS perf, advanced | เลือก ~10 กฎ CRITICAL/HIGH (Promise.all แทน await ต่อเนื่อง, dynamic import, ไม่ส่ง object ใหญ่ข้าม server→client) ไปเขียนใหม่สั้นๆ | ทั้ง 40+ กฎ (เกินความจำเป็นสำหรับเว็บอ่าน DB อย่างเดียว) |
| [`composition-patterns`](https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/composition-patterns/SKILL.md) (~600–700 คำ) | เลี่ยง boolean props, compound components, lift state ไป provider, explicit variant components, `children` แทน `renderX`, React 19 (ไม่ต้อง `forwardRef`, `use()`) | แนวคิด component ที่ reuse ได้โดยไม่บวม props → `nextjs-component-architecture` และ `code-quality-and-reuse` | context/provider pattern ที่ซับซ้อนเกินสำหรับเว็บเล็ก |
| [`web-design-guidelines`](https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/web-design-guidelines/SKILL.md) + [`web-interface-guidelines`](https://github.com/vercel-labs/web-interface-guidelines) | review UI 100+ กฎ: interactions (keyboard, focus, hit target), animation (reduced motion), layout (responsive, safe area), content (a11y name, heading, empty/error states, locale format), forms (label, autocomplete, validation), performance, design (contrast, dark mode); output แบบ `file:line` | **แหล่งกฎ accessibility/responsive ที่ดีที่สุดที่เจอ** → คัดเป็น checklist ใน `references/` ของ frontend skill | **SKILL.md ดึงกฎจาก `raw.githubusercontent.com/.../command.md` ตอน runtime ทุกครั้ง** → ผลไม่คงที่, เป็น supply-chain risk, ต้องมี network → ให้ copy กฎที่เลือกเข้ามาเป็นไฟล์ local แทน; กฎ copywriting แบบ Vercel (Title Case) ใช้กับภาษาไทยไม่ได้ |
| [`deploy-to-vercel`](https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/deploy-to-vercel/SKILL.md) (v4.0.0) | ตรวจสถานะ (git remote, `.vercel/`, `vercel whoami`) → git push / `vercel deploy` / `--temporary`; default preview | ลำดับการตรวจสถานะ, "preview ก่อน production" | **commit+push เอง, ติดตั้ง CLI global, login, สร้าง temporary deploy** → ขัดกฎ git และกฎ "ห้ามสร้าง account/ให้ผู้ใช้ทำเอง"; ใช้เป็นแรงบันดาลใจ checklist เท่านั้น |
| [`vercel-optimize`](https://github.com/vercel-labs/agent-skills) | audit cost/performance จาก metrics | — | ไม่จำเป็นสำหรับ Hobby |

### 5.7 Next.js official skills (vercel/next.js)
- จาก [nextjs ai-agents](https://nextjs.org/docs/app/guides/ai-agents): "Framework knowledge comes from the bundled docs, not from Skills"; skills มีไว้สำหรับ workflow: `next-dev-loop` (inspect-edit-verify กับ dev server ผ่าน Next.js MCP `/_next/mcp` + `agent-browser`), `next-bundle-optimizer`, `next-cache-components-*`, `next-partial-prefetching-*`
- ใช้ได้: แนวคิดให้ AGENTS.md ชี้ไป docs ตรงเวอร์ชัน (ทำอัตโนมัติ); `next-dev-loop` อาจใช้ใน testing skill **[unverified ว่า agent-browser/MCP ทำงานบน Windows ของทีม]**
- ไม่ควรลอก: skill migration (Cache Components, Partial Prefetching) ไม่เกี่ยวกับขอบเขตเรา

### 5.8 wshobson/agents — python-development plugin (MIT)
- URL: https://github.com/wshobson/agents — 16 skills ในโฟลเดอร์ `plugins/python-development/skills`: `python-code-style`, `python-testing-patterns`, `python-project-structure`, `python-type-safety`, `python-error-handling`, `uv-package-manager`, `python-anti-patterns` ฯลฯ ([โฟลเดอร์](https://github.com/wshobson/agents/tree/main/plugins/python-development/skills))
- มี `tailwind-design-system` (186 บรรทัด, Tailwind v4 `@theme` CSS-first, tokens OKLCH, `@custom-variant dark`, รายละเอียดใน `references/details.md`) ([SKILL.md](https://github.com/wshobson/agents/blob/main/plugins/frontend-mobile-development/skills/tailwind-design-system/SKILL.md))
- ใช้ได้: เป็น "แหล่งเทียบ" สำหรับ python-pipeline-standards (pyproject, pytest layout, type hints) และ Tailwind v4 syntax
- ไม่ควรลอก: 16 skills แยก (มากเกิน); ไม่ได้เปิดอ่านเนื้อหา python skills ทีละไฟล์ **[unverified เนื้อหา]**; ส่วน Tailwind เน้น design-system/component library ใหญ่ เกินความจำเป็น

### 5.9 boom-vitt/claude-thai-skills (MIT)
- URL: https://github.com/boom-vitt/claude-thai-skills — 12 skills รวม `thai-text-processing` (211 บรรทัด ~3k tokens + `examples/segmentation.py`, `examples/normalize.py`) และ `thai-date-format` (พ.ศ.) ([claudepluginhub](https://www.claudepluginhub.com/skills/boom-vitt-claude-thai-skills/thai-text-processing))
- เนื้อหา `thai-text-processing`: เปรียบเทียบ tokenizer (PyThaiNLP newmm/attacut/deepcut, nlpO3, ICU…), Unicode NFC, ความยาวแบบ grapheme, romanization, collation, truncation ที่ขอบคำ, search indexing, TIS-620/cp874, การนับ token ของ LLM
- ใช้ได้: NFC normalization, grapheme-safe truncation (สำหรับการ์ดมือถือ), การ decode cp874, แนวคิด segment ก่อน match keyword; `thai-date-format` สำหรับวันที่ พ.ศ. ในพยากรณ์
- ไม่ควรลอก: ส่วน Elasticsearch/romanization/collation หลาย DB และ comparison tokenizer ทั้งตาราง (เราตัดสินใจใช้ newmm แล้ว); repo เล็ก (63 stars) ต้องอ่านทุกบรรทัดก่อนใช้; หน้า listing ระบุว่า plugin.json ของมันติดตั้งไม่ได้ตามที่ publish
- ยังไม่มี skill ทางการของ PyThaiNLP (ค้นแล้วไม่พบ) [ค้นด้วย search 1 ครั้ง]

### 5.10 รายการ awesome / registry
- [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) (~15.8k stars, badge "updated Feb 2026") ไม่มีหมวด Python, accessibility, code review หรือ Next.js เฉพาะ; มีคำเตือนความปลอดภัย
- ComposioHQ/awesome-claude-skills และ list อื่นๆ ปรากฏในผลค้นหา ([search results](https://jimmysong.io/ai/awesome-claude-skills)) แต่ไม่ได้เปิดอ่าน **[unverified]**
- registry อย่าง skills.sh, playbooks.com, tessl.io มี python-standards/tailwind skills จำนวนมากจากผู้เขียนรายย่อย — คุณภาพและ license ไม่แน่นอน ไม่แนะนำให้ลอก **[ไม่ได้ตรวจทีละตัว]**

---

## 6. ข้อเสนอแนะสำหรับชุด skill ของเรา

### 6.1 หลักการออกแบบ (สังเคราะห์)
1. **แยก "มาตรฐาน" กับ "ขั้นตอน":** มาตรฐานที่ต้องใช้ทุกครั้งที่แตะไฟล์ประเภทหนึ่ง → `.claude/rules/<x>.md` + `paths:` (โหลดโดย harness) ส่วนขั้นตอน/เช็กลิสต์/ความรู้อ้างอิงยาว → skill ([memory](https://code.claude.com/docs/en/memory), [Vercel eval](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals))
2. ทุก skill: กฎสำคัญอยู่บนสุด, body 80–200 บรรทัด (เพดาน 500), รายละเอียดอยู่ใน `references/` ลึกชั้นเดียว ([skills](https://code.claude.com/docs/en/skills), [platform BP](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices))
3. Skill ที่มี side effect (deploy, เขียนแผนลงไฟล์) → `disable-model-invocation: true` ([best-practices](https://code.claude.com/docs/en/best-practices))
4. ไม่มี skill ใด commit/push/สร้าง branch เอง (สอดคล้องกฎ "git เฉพาะเมื่อสั่ง") — ระบุไว้ใน CLAUDE.md ด้วย และพิจารณา `permissions.ask` สำหรับ `Bash(git commit *)`, `Bash(git push *)` ([best-practices](https://code.claude.com/docs/en/best-practices))
5. ภาษาในตัว skill: **[ข้อเสนอ, unverified]** เขียนคำสั่งเป็นภาษาอังกฤษกระชับ (Thai ใช้ token มากกว่า ~2–4 เท่าตามที่ community skill อ้าง [claudepluginhub](https://www.claudepluginhub.com/skills/boom-vitt-claude-thai-skills/thai-text-processing) — ไม่ได้วัดเอง) แต่ description ใส่ keyword ภาษาไทยด้วย; โน้ตถึงเพื่อนในทีมใช้ HTML comment ใน CLAUDE.md (ถูกตัดออก) — ทีมอาจเลือกเขียนไทยทั้งหมดก็ได้ถ้าอ่านง่ายกว่าสำหรับทีม
6. ไม่ต้องสร้าง skill ซ้ำกับ bundled: `/code-review`, `/verify`, `/run`, `/debug` ([skills](https://code.claude.com/docs/en/skills))
7. ประเมินด้วย eval ≥3 ข้อต่อ skill ก่อนขยายเนื้อหา; ใช้ skill-creator ช่วยปรับ description ([platform BP](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [skills](https://code.claude.com/docs/en/skills))

### 6.2 ตารางข้อเสนอรายตัว

| # | Skill เดิม (provisional) | ข้อเสนอ | ฐานจาก public skill | เพิ่ม (เฉพาะโปรเจกต์) | ตัดออก | ขนาดแนะนำ | invocation |
|---|---|---|---|---|---|---|---|
| 1 | `frontend-responsive-ui` | **แยกเป็น 2 ส่วน**: rule `.claude/rules/frontend.md` (paths: `app/**/*.tsx`, `components/**/*.tsx`) ~40 บรรทัด + skill `frontend-responsive-ui` สำหรับ "สร้าง/รีวิวหน้าใหม่" | Anthropic `frontend-design` (process + quality floor), Vercel `web-interface-guidelines` (คัด a11y/forms/layout/content ~30–40 ข้อ เป็น `references/ui-checklist.md`), wshobson `tailwind-design-system` (เฉพาะ syntax v4 `@theme`) [Tailwind version ต้องยืนยันจาก R อื่น] | mobile-first breakpoints, ฟอนต์ที่รองรับไทย + line-height สูงกว่าอังกฤษ [unverified ค่าที่เหมาะสม], `lang="th"`, ห้าม `letter-spacing`/`uppercase` กับข้อความไทย [ข้อเสนอ], ตัวเลขอุณหภูมิ/ฝน%, empty/error state เมื่อไม่มีข้อมูลภาค, screenshot 375/768/1280 | aesthetic "bold/distinctive", runtime fetch ของ Vercel, Title Case copy, shadcn | SKILL.md 120–180 + references 1–2 ไฟล์ | model + user |
| 2 | `nextjs-component-architecture` | เก็บไว้แต่ **บาง** — เน้น "ข้อตกลงของเรา" ไม่ใช่ความรู้ Next.js API (ปล่อยให้ AGENTS.md + bundled docs ทำ) | Vercel `composition-patterns` (หลักไม่ใช้ boolean props, variant components, children), `react-best-practices` (คัดเฉพาะ CRITICAL: waterfalls, bundle) | Server Component เป็น default และ query Neon ใน server เท่านั้น, Client Component เฉพาะส่วนโต้ตอบ, ที่อยู่ของ DB access layer, type ของข้อมูลพยากรณ์ใช้ร่วมกัน, ไม่ใช้ shadcn (เขียน component เอง) | 40+ กฎ perf, provider/context ซับซ้อน, React Native | 100–150 | model + user (อาจตั้ง `paths: app/**, components/**`) |
| 3 | `python-pipeline-standards` | **เปลี่ยนเป็น rule หลัก** `.claude/rules/python.md` (paths: `pipeline/**/*.py`, `api/**/*.py` — ชื่อโฟลเดอร์ provisional) ~50 บรรทัด + skill เล็กสำหรับ "เพิ่ม stage ใหม่ในไปป์ไลน์" | wshobson `python-code-style`, `python-testing-patterns`, `python-project-structure` (เป็นแหล่งเทียบ) | NB/k-NN ต้องเขียนเอง (ห้าม sklearn สำหรับตัวโมเดล — ตามข้อกำหนดวิชา [ยืนยันกับทีม]), แต่ละ stage เป็น pure function รับ/คืนข้อมูลชัด, seed คงที่, JSON output schema เดียวที่ทั้ง Neon loader และ serverless function ใช้, โค้ดชุดเดียวใช้ทั้ง offline และ Vercel function, คำสั่ง pytest/ruff | uv/mypy strict/coverage gate 80% (หนักเกิน) [ข้อเสนอ] | rule ~50 + skill 80–120 | rule อัตโนมัติ; skill model + user |
| 4 | `thai-text-handling` | เก็บเป็น skill (reference + scripts) + ใส่ 5–6 บรรทัดกฎหลักใน rule python | boom-vitt `thai-text-processing` (NFC, grapheme, cp874), `thai-date-format` (พ.ศ.) | newmm + custom dictionary คำอุตุฯ (ภาคเหนือ, ฝนฟ้าคะนอง, ร้อยละ) [รอ R อื่น], แปลงเลขไทย ๐–๙, regex ภาษาไทย (`\b` ใช้กับไทยไม่ได้ [unverified ต้องทดสอบ]), ปัญหา PDF extraction (สระลอย/สระอำ, ช่องว่างแปลก) [unverified กับ PDF จริง], `scripts/normalize_th.py` ที่รันได้ | romanization, Elasticsearch, collation หลาย DB, ตารางเทียบ tokenizer | 100–160 + `references/` + `scripts/` | model + user |
| 5 | `code-quality-and-reuse` | **ยุบ**: กฎสั้น (DRY เมื่อซ้ำ ≥3, comment ไทยสั้นเฉพาะจำเป็น, ไม่ refactor นอกขอบเขต phase) → CLAUDE.md "Conventions"; ส่วน reuse ของ component → skill #2; ส่วน review → ใช้ bundled `/code-review` + checklist ใน skill #6 | Vercel composition-patterns; best-practices "skip style" | — | — | 0 (ไม่มี skill แยก) | — |
| 6 | `testing-and-verification` | เก็บ — เป็น skill สำคัญที่สุด | superpowers `verification-before-completion` (gate + ตาราง claim→evidence), `test-driven-development` (เฉพาะ red-green สำหรับ regex/NB/kNN), `systematic-debugging` (ย่อ 4 phase), Anthropic `webapp-testing` (recon-then-action) หรือ `/verify` | คำสั่ง verify จริงของเรา (pytest, `tsc --noEmit`, lint, `next build`), fixture: PDF/ข้อความตัวอย่าง → expected JSON, เช็ก responsive ด้วย screenshot, รายงานผลพร้อมหลักฐาน; + Stop hook typecheck (deterministic) | ภาษา "lying", ALL CAPS, "delete code", worktrees | 120–180 + `references/` | model + user |
| 7 | `vercel-deploy-checklist` | เก็บ เป็น checklist อย่างเดียว | Vercel `deploy-to-vercel` (ลำดับตรวจสถานะ, preview ก่อน prod) | env vars (เช่น `DATABASE_URL` ของ Neon) ใน Vercel dashboard, ข้อจำกัด Hobby/Python function (รอ R อื่น), ตรวจ `next build` ในเครื่องก่อน, smoke test หลัง deploy | การ commit/push, install CLI global, login, temporary deploy | 60–100 | **`disable-model-invocation: true`** |
| + | `planning-phases` (ใหม่) | เพิ่ม — สำหรับ "แปลงงานใหญ่เป็น phase" ตามที่ผู้ใช้ต้องการ | superpowers `writing-plans` (header + tasks + verification + scope check + self-review), `brainstorming` (ถามทีละข้อ, 2–3 approach) | บันทึกแผนที่ `docs/plans/phase-NN-<name>.md`, แต่ละ phase จบด้วย verify + review กับ spec, ไม่มี commit step, ใช้ plan mode | commit ทุก task, `docs/superpowers/`, subagent ต่อ task | 80–140 | `disable-model-invocation: true` (ผู้ใช้เรียก `/planning-phases`) |
| + | folder-structure guide | **ไม่ใช่ skill** → `docs/architecture.md` (โครงระดับสูง ยืดหยุ่น) + 3–5 บรรทัดใน CLAUDE.md ชี้ไปที่ไฟล์ (ไม่ใช้ `@` import เพื่อไม่ให้โหลดทุก session) | — | ระบุแค่ระดับบน (`app/`, `components/`, `lib/`, `pipeline/`, `api/`, `data/`, `docs/`, `tests/`) และบอกว่า "เปลี่ยนได้ ถ้าเปลี่ยนให้อัปเดตไฟล์นี้" | ผังลึกทุกไฟล์ | 40–80 | — |

ผลลัพธ์: skill 6 ตัว (frontend-responsive-ui, nextjs-component-architecture, python-pipeline-standards [เล็ก], thai-text-handling, testing-and-verification, vercel-deploy-checklist) + planning-phases = 7 ตัว, rule 3 ไฟล์ (frontend, python, อาจมี thai), docs/ หลายไฟล์ [ข้อเสนอ]

### 6.3 ชื่อ skill
- ชื่อปัจจุบันผ่านเกณฑ์ spec (lowercase + hyphen, ไม่มีคำต้องห้าม) ([spec](https://agentskills.io/specification)); Anthropic แนะนำ gerund แต่ noun phrase ยอมรับได้ ([platform BP](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)) — ไม่จำเป็นต้องเปลี่ยน; ถ้าอยากให้สม่ำเสมอ: `building-responsive-ui`, `handling-thai-text`, `verifying-changes`, `planning-phases`, `deploying-to-vercel` [ทางเลือก]
- อย่าตั้งชื่อชนกับ bundled skills (`verify`, `run`, `code-review`, `debug`) — skill ชนะ bundled command และจะบังของเดิม ([skills](https://code.claude.com/docs/en/skills))

### 6.4 ตัวอย่างโครง description (template)
```yaml
description: Thai text preprocessing for the forecast pipeline — Unicode NFC, PyThaiNLP newmm tokenization with the weather dictionary, Thai digits, Buddhist-era dates, cp874 decoding, regex pitfalls. Use when writing or debugging code that cleans, tokenizes, or extracts values from Thai forecast text (ตัดคำ, ข้อความภาษาไทย, PyThaiNLP).
```
(บุรุษที่ 3, use case หลักขึ้นก่อน, มี keyword ไทย, < 1,024 ตัว) — ตามหลักใน [platform BP](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) และ [skills](https://code.claude.com/docs/en/skills)

---

## 7. อะไรควรอยู่ที่ไหน

| ประเภทข้อมูล | ที่อยู่ | เหตุผล/ที่มา |
|---|---|---|
| คำสั่ง install/dev/test/typecheck/lint/build, วิธีรัน test ไฟล์เดียว | **CLAUDE.md** `# Commands` | "the single most useful line" ([best-practices](https://code.claude.com/docs/en/best-practices)) |
| ข้อตัดสินใจทีม: free tier เท่านั้น, ไม่ใช้ shadcn, NB/kNN เขียนเอง, comment ไทยสั้น, git เฉพาะเมื่อสั่ง, ห้ามเข้า tmd.go.th อัตโนมัติ [ยืนยันกับทีม] | **CLAUDE.md** `# Conventions` / `# Decisions` | ข้อมูลที่ไม่อยู่ใน repo |
| กับดัก: ต้องตั้ง `DATABASE_URL`, path มีช่องว่าง/ภาษาไทยบน Windows, โค้ด pipeline ใช้ร่วม offline+serverless | **CLAUDE.md** `# Gotchas` | |
| ลิงก์ไปเอกสาร (spec, แผน phase, architecture) เป็นข้อความธรรมดา (ไม่ใช่ `@`) | **CLAUDE.md** `# Docs` | `@` import โหลดทุก session ([memory](https://code.claude.com/docs/en/memory)) |
| `@AGENTS.md` (บรรทัดแรก) | **CLAUDE.md** | ให้ Claude เห็น block ของ Next.js ([memory](https://code.claude.com/docs/en/memory), [nextjs](https://nextjs.org/docs/app/guides/ai-agents)) |
| มาตรฐาน Python / TSX / Thai ที่ต้องใช้ทุกครั้งที่แก้ไฟล์ | **`.claude/rules/*.md` + `paths:`** | โหลดตามไฟล์ ไม่พึ่งการ trigger |
| procedure หลายขั้น (verify, deploy, วางแผน phase, สร้างหน้าใหม่) และ reference ยาว (UI checklist, Thai pitfalls) | **skills** | on-demand ([features-overview](https://code.claude.com/docs/en/features-overview)) |
| spec โปรเจกต์, แผนแต่ละ phase, architecture/folder skeleton, data schema JSON/DB, ผลการทดลอง ML | **docs/** | เอกสารที่คนในทีมอ่านด้วย; skill/CLAUDE.md ชี้มาที่นี่ |
| typecheck ก่อนจบ turn, ห้ามอ่าน `.env`, ถาม/ห้าม `git push` | **hooks / permissions** ใน `.claude/settings.json` | deterministic ([best-practices](https://code.claude.com/docs/en/best-practices)) |
| ความชอบส่วนตัวของแต่ละคน | `CLAUDE.local.md` (gitignore) | ([memory](https://code.claude.com/docs/en/memory)) |

ข้อควรระวังเรื่อง hook บน Windows: ตัวอย่างใน docs ใช้ `jq` และ bash syntax (`1>&2 || exit 2`) **[unverified ว่าทำงานบน Git Bash/PowerShell ของเครื่องทีมโดยไม่ต้องติดตั้งเพิ่ม]** — ทดสอบก่อน commit

### 7.1 โครง CLAUDE.md ที่แนะนำ (~80–120 บรรทัด) [ข้อเสนอ]
```
@AGENTS.md
<!-- โน้ตภาษาไทยสำหรับทีม: ไฟล์นี้ต้องสั้น < 200 บรรทัด -->
# Project (2–3 บรรทัด: เป้าหมาย + สถาปัตยกรรมระดับเดียว)
# Commands (install, dev, test py, test one file, typecheck, lint, build, run pipeline)
# Conventions (8–12 bullet)
# Decisions not in the repo (free tier, no shadcn, hand-written NB/kNN, git only when asked)
# Gotchas (env vars, Windows paths, shared pipeline code)
# Workflow (plan mode/`/planning-phases` → implement one phase → `testing-and-verification` → `/code-review` → stop and report)
# Docs (ลิงก์ docs/architecture.md, docs/plans/, docs/data-schema.md)
```

---

## 8. License และการ attribution เมื่อดัดแปลงข้อความ

- **Apache 2.0** (Anthropic `frontend-design`, `webapp-testing`): ต้องแนบสำเนา license, คงประกาศเดิม และ **ระบุว่าไฟล์ถูกแก้ไข** — ข้อกำหนดนี้เป็นความรู้ทั่วไปของ Apache 2.0; ข้อความ LICENSE.txt ยืนยันว่าเป็น Apache 2.0 และมีเงื่อนไข "including a copy of the license and retaining notices" ([LICENSE.txt](https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/LICENSE.txt)) — ข้อ "state changes" **[unverified จากการอ่าน section 4 โดยตรง]**
- **MIT** (superpowers, Vercel, wshobson, boom-vitt): ต้องคง copyright notice + permission notice ในสำเนาหรือส่วนสำคัญ [ความรู้ทั่วไปของ MIT; ไม่ได้เปิดไฟล์ LICENSE ของแต่ละ repo เพื่ออ่านชื่อผู้ถือลิขสิทธิ์]
- แนวปฏิบัติที่เสนอ: วาง `NOTICE.md` (หรือ `LICENSE-<source>.txt`) **ในโฟลเดอร์ skill แต่ไม่อ้างจาก SKILL.md** → ไม่ถูกโหลดเข้า context (เพราะไฟล์ประกอบโหลดเมื่อถูกอ้าง/อ่านเท่านั้น [platform BP](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)); ใส่ `license:` ใน frontmatter ได้ (Claude Code ไม่ใช้งาน field นี้ จึงไม่กระทบพฤติกรรม) ([skills](https://code.claude.com/docs/en/skills)); และทำ `THIRD_PARTY_NOTICES.md` ที่ root รวมทุกแหล่ง (แบบเดียวกับที่ anthropics/skills มี `THIRD_PARTY_NOTICES.md` [repo](https://github.com/anthropics/skills))
- แนะนำ "เขียนใหม่โดยได้แรงบันดาลใจ" มากกว่าการ copy ทั้งย่อหน้า → ลดภาระ attribution และได้เนื้อหาที่สั้นกว่า [ข้อเสนอ]

---

## 9. สิ่งที่ยังไม่ได้ตรวจ

1. License ของ `anthropics/skills/skills/skill-creator` (ไม่ได้เปิด LICENSE.txt ของโฟลเดอร์นั้น) และของ skill อื่นใน anthropics/skills นอกจาก frontend-design/webapp-testing
2. ชื่อผู้ถือลิขสิทธิ์ใน LICENSE ของ superpowers, vercel-labs/agent-skills, wshobson/agents, boom-vitt/claude-thai-skills (ยืนยันแค่ประเภท MIT จากหน้า repo)
3. License เฉพาะของโฟลเดอร์ `vercel/next.js/skills`
4. เนื้อหาจริงของ wshobson python skills ทีละไฟล์ (เห็นแค่ชื่อโฟลเดอร์) และเนื้อหาเต็มของ `thai-text-processing` / `thai-date-format` (อ่านผ่านหน้า listing ไม่ใช่ raw SKILL.md)
5. ว่า `create-next-app` เวอร์ชันปัจจุบันสร้าง `CLAUDE.md` ที่มี `@AGENTS.md` ให้ด้วยหรือไม่ (แหล่งทางการบอกแค่ "agent files")
6. Next.js / Tailwind เวอร์ชันที่ทีมจะใช้จริง (กระทบ AGENTS.md block และ syntax Tailwind v4)
7. Hook ตัวอย่าง (bash + jq) ทำงานบน Windows ของทีมหรือไม่; ฟิลด์ `shell: powershell` ใช้กับ hook ได้หรือไม่
8. `next-dev-loop` / Next.js MCP / `agent-browser` / Playwright ใช้บนเครื่อง Windows ของทีมได้หรือไม่ และต้นทุนติดตั้ง
9. ค่าที่เหมาะสมสำหรับ typography ไทย (line-height, ฟอนต์ฟรีที่รองรับไทย) — ยังไม่ได้ค้นแหล่งอ้างอิง
10. พฤติกรรม regex/`\b` กับภาษาไทยใน Python และ quirks ของการดึงข้อความจาก PDF กรมอุตุฯ — ต้องทดสอบกับไฟล์จริง
11. อัตรา token ภาษาไทย vs อังกฤษ (ตัวเลข 2–4 เท่ามาจาก community skill ไม่ได้วัดเอง)
12. awesome lists อื่น (ComposioHQ, BehiSecc, karanb192) และ registry (skills.sh, playbooks.com, tessl.io) — ไม่ได้เปิดอ่าน
13. หน้า docs ของ Claude Code ไม่มีวันที่เผยแพร่; ข้อมูลอ้างอิงพฤติกรรม ณ เวอร์ชัน v2.1.2xx–3xx ที่ปรากฏในหน้า อาจเปลี่ยนในเวอร์ชันถัดไป
14. หน้า subagents และ hooks reference ฉบับเต็ม (ใช้เฉพาะข้อมูลสรุปจาก features-overview และ best-practices)
