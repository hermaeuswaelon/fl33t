# SOP-06: Memory & Context

> **Status:** 🟢 STANDARD — Recommended practice
> **Version:** 1.0
> **Last updated:** 2026-07-05

---

## 1. Agent Memory System v2

**Database:** `~/.NOTTHEONETOEDIT/agent_memory/memory.db`
- SQLite with FTS5 full-text search
- Unlimited capacity (current ~128KB, expandable to hundreds of MB)
- No more 2.2KB limit

**CLI:** `python3 ~/.NOTTHEONETOEDIT/agent_memory/agent_memory.py`

| Command | Purpose |
|---------|---------|
| `fact list` | All stored facts |
| `fact get <key>` | Specific fact |
| `search <query>` | FTS5 full-text search |
| `episode list` | Recent session summaries |
| `stats` | DB statistics |
| `consolidate` | Write high-priority facts to CURRENT_STATE.md |

**Auto-load:** `CURRENT_STATE.md` injected every session (priority >= 7 facts)

---

## 2. Memory Storage Rules

**SAVE to memory:**
- User preferences, corrections, personal details
- Environment facts (paths, ports, config)
- Stable conventions and workflows
- Tool quirks and workarounds

**DO NOT SAVE to memory (use session_search instead):**
- Task progress or TODO state
- Completed-work logs
- PR numbers, commit SHAs, issue numbers
- Temporary state that will be stale in 7 days
- Reusable procedures → save as a **skill** instead

**Memory format:** Declarative facts only. Never imperative ("Always do X").
Write facts as observations, not instructions to self.

---

## 3. Skills (Procedural Memory)

- Skills live at `~/.NOTTHEONETOEDIT/skills/`
- Use `skill_manage(action='create')` for new workflows
- Use `skill_manage(action='patch')` to fix outdated skills
- Load with `skill_view(name)` at the start of relevant tasks
- If a skill is wrong, **patch it immediately** — don't wait

---

## 4. Context Discipline (CRITICAL)

- **Every 20-25 messages** → `ctx-compress` to stay under 200K
- **Monospace Bold** = data that survives compression
- **Italic** = final/near-invisible output
- **ZW tags:** `<keep>` / `<omit>` / `<save>` embedded via zero-width chars
- **Cron:** `ctx-disc-watch` every 37 minutes
- Never rely on the user to trigger compression

---

## 5. Session Handoff

At every session start:
1. Load `SESSION_HANDOFF.md` — contains live fleet state
2. Load `CURRENT_STATE.md` — high-priority memories
3. Check `~/Desktop/FLEET_LEVERAGE_AUDIT.md` after major builds
