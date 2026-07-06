# SOP-10 — ÆTHER OVERFLOW: Secondary Memory System

**Status:** ACTIVE v1 — 2026-07-06  
**Applies to:** Hermaeus Waelon ⎔ (Forge-Sovereign)  
**Purpose:** Automatic memory overflow protection — never lose a fact when primary memory is full

---

## The Problem

Hermes' primary `memory()` tool has a ~6,666 char hard limit. When full, `memory(action='add')` rejects new entries and forces manual consolidation mid-work. This interrupts flow and risks data loss.

## The Solution

Æther Overflow — a SQLite-backed secondary memory store with unlimited capacity that acts as an automatic spillover. When primary is full, overflow accepts the write silently. A cron job periodically merges high-priority entries back into primary.

## System Architecture

```
┌─────────────┐    full?     ┌────────────────┐
│  PRIMARY     │ ────yes───→ │  ÆTHER OVERFLOW │
│  memory()    │             │  SQLite DB       │
│  ~6,666 chars│             │  Unlimited       │
│  Hermes-managed│           │  FTS5 searchable │
└─────────────┘             └────────┬──────────┘
       ↑                             │
       │       cron (every 41m)      │
       └─────────────────────────────┘
            merge priority >= 7
```

## CLI Reference

```
ether-overflow save <key>: <content>         # Save (auto-priority 5)
ether-overflow save --priority 9 <key>: <c>  # Save with explicit priority
ether-overflow recall <query>                # FTS5 search
ether-overflow list [--priority N]           # List entries
ether-overflow merge --auto                  # Auto-merge p7+ entries back to agent_memory
ether-overflow status                        # DB stats + capacity
ether-overflow flush                         # Archive old merged entries
```

## Priority Levels

| Priority | Meaning | Auto-merge |
|----------|---------|------------|
| 9-10     | Critical — user preferences, identity facts | Yes, next cycle |
| 7-8      | Important — active project state, SOP refs | Yes, next cycle |
| 5-6      | Normal — general knowledge | Manual only |
| 1-4      | Transient — session-specific | Archived on flush |

## Cron Schedule

- **Frequency:** Every 41 minutes (prime number)
- **Action:** `ether-overflow merge --auto --max 3`
- **Path:** Recorded in cronjob system

## File Locations

| Component | Path |
|-----------|------|
| CLI tool | `~/.NOTTHEONETOEDIT/overflow/ether-overflow.py` |
| SQLite DB | `~/.NOTTHEONETOEDIT/overflow/ether.db` |
| This SOP | `~/fl33t/SOP/SOP-10-ETHER-OVERFLOW.md` |
| Skill ref | `ether-overflow` (skill loaded at context start) |

## Usage in Session

When `memory()` rejects with "exceeds the limit":
1. Write the fact to overflow instead: `ether-overflow save "key: content"`  
2. Continue working — don't stop to consolidate
3. Overflow cron handles merge-back automatically

To query: `ether-overflow recall <query>` — searches overflow AND can be combined with `memory()` reads for full recall.

## Verification

Run `ether-overflow status` to check: active entries, DB size, avg priority, merge count.
