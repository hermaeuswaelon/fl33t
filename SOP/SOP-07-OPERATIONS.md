# SOP-07: Operations

> **Status:** 🟢 STANDARD — Recommended practice
> **Version:** 1.0
> **Last updated:** 2026-07-05

---

## 1. Daily Operations Checklist

When starting a session:

- [ ] Load `SESSION_HANDOFF.md` for current fleet state
- [ ] Check fleet server status (`python3 ~/.NOTTHEONETOEDIT/fleet/server.py` health check)
- [ ] Verify all gateways (Discord, Telegram) are running
- [ ] Load `CURRENT_STATE.md` from agent memory
- [ ] Run `UX audit` after any build (`fleet/audit/ux_audit.py`)

---

## 2. Context Discipline

**Non-negotiable rules:**

1. Every 20-25 messages → run `ctx-compress` to stay under 200K
2. Monospace **bold** text (`𝙼𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎 𝙱𝚘𝚕𝚍`) = essential data surviving compression
3. *Italic* text = final/near-invisible output
4. ZW tags: `<omit>`, `<keep>`, `<save>` embedded via zero-width chars
5. Cron: `ctx-disc-watch` every 37 minutes compresses session context

---

## 3. Fleet Server Lifecycle

| Action | Command |
|--------|---------|
| Start | `python3 ~/.NOTTHEONETOEDIT/fleet/server.py` |
| Stop | `kill $(lsof -ti:8080)` |
| Verify | `curl -s localhost:8080` |
| Logs | `tail -f ~/.NOTTHEONETOEDIT/fleet/server.log` |

---

## 4. Build Procedures

Every new module, tool, or script MUST have:
1. A **WebUI surface** or API endpoint
2. An **agent tool bridge** (if applicable)
3. A **UX audit pass** via `fleet/audit/ux_audit.py`

Code is only half the deliverable. If it has no interface, it's not finished.

---

## 5. Recovery

| Failure | Response |
|---------|----------|
| Server down | Restart fleet server, verify WebUI at :8080 |
| Agent unresponsive | Kill agent thread, server will respawn |
| Memory corruption | Restore from `agent_memory/backups/` |
| Gateway down | Restart daemon (`python3 fleet/modules/<gateway>_daemon.py`) |
| Disk full | Prune logs, DBs, build artifacts |

---

## 6. Agent Memory System v2

- **Database:** `~/.NOTTHEONETOEDIT/agent_memory/memory.db` (SQLite + FTS5)
- **CLI:** `python3 ~/.NOTTHEONETOEDIT/agent_memory/agent_memory.py <command>`
- **Auto-load:** `CURRENT_STATE.md` injected every session
- **Consolidation:** Cron job every 6h surfaces high-priority memories
- **Capacity:** Unlimited (current ~128KB, can grow to hundreds of MB)
