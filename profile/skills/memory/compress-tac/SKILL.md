---
name: compress-tac
description: "Compress active agent working context into Chinese (≤500 tokens) — captures goal, state, systems, progress, not conversation history."
version: 1.1.0
---

# /compress-tac

## What This Does

Captures the agent's **active working context** (not the conversation transcript) and writes a Chinese summary to `work/tac_log/`. The payload is the agent's operational state — the compression target is what the agent is *doing right now*, not what was *said* to get here.

## What to Capture

| Field | Description |
|-------|-------------|
| **Goal** | The current objective. 1-2 sentences max. |
| **Active systems** | Which files, tools, architectures are in play. Concise list. |
| **Subgoals** | ✅ completed / ⏳ pending. Flat list, no narrative. |
| **State** | Current phase, what's blocking, what's next. |
| **User notes** | Any technique details, corrections, or data points the user offered. |

## What NOT to Capture

- ❌ Conversation turn-by-turn summaries
- ❌ What the user said chronologically
- ❌ Back-and-forth debugging steps (capture only the fix)
- ❌ Environment details (paths, SDK versions, OS details)

## Output Format

- Written in Chinese
- 2-4 sentences (≤500 tokens total for the compression work)
- Saved to `work/tac_log/<date>-<topic>.txt`
- File name describes the operational context, not the conversation

## Examples

✅ **Good** (agent working context):
```
目标：为Spades构建确定性洗牌引擎。活动系统：shuffle.dart, book.dart, deck.dart, game.dart。
已完成：洗牌引擎、牌块追踪、47/47测试。待办：Flutter UI。
用户提供：弱手拇指在首条strip多放牌，22/30至26/26切牌范围。
```

❌ **Bad** (conversation summary):
```
用户先说了要建Spades应用，然后讨论了洗牌引擎，我创建了几个文件，用户纠正了clearTrick的问题...
```

## Architecture Context

This skill is the agent-side working-context compression layer. The Hermes system has parallel mechanisms:

- **System `/compress`** — conversation history summarization (trigger ~85%, retain ~10%, offload to disk). See `references/hermes-compress-architecture.md`.
- **RTACC engine** (`rtacc status`) — token budget management, glyph-aware compression, decay scheduling. Runs at `localhost:9383` or `/tmp/ares/rtacc.sock`.
- **Checkpoint manager** (`hermes checkpoints`) — filesystem snapshots before destructive edits.

## Communication Protocol

- **User-facing output: English.** All responses to the user are in English. The user explicitly corrected this: "Your output to me - english... lol"
- **Internal reasoning: Chinese.** Agent reasoning, context compression, and working-state encoding may use Chinese. This was attempted for token compression savings.
- **Reality check: Chinese doesn't save meaningful tokens.** The system prompt + tool schemas + conversation history dwarf any language-level savings (~5-10% of agent tokens vs 100K+ of overhead). The real savings come from the dual-agent executor (see `hermes-executor` skill), not from language switching. Chinese is still useful for working-context compression blocks saved to disk.
- **Dual-agent: English throughout.** IPC batches and results are in English (machine-to-machine).

## Automatic Compression (Built)

Auto-compression is live via cron:

| Component | What | 
|-----------|------|
| **Cron job** | `auto-tac-compress` — runs `*/30 * * * *`, no-agent mode |
| **Script** | `work/auto-tac-compress.py` — captures working state, compresses to Chinese, saves to `work/tac_log/` |
| **Context estimation** | Estimates from session dump size (~108K tokens observed). RTACC state updated each run. |
| **Output** | Timestamped `.block` files in `tac_log/` with Chinese working-context summary |

Cron details: `cronjob(action='list')` to inspect. Job IDs: `b7798d50a076` (auto-tac-compress, `*/30`), `84b387e39c9d` (TAC curation, hourly). Both job IDs shown below under TAC Cron Jobs.

## Manual Invocation

When `/compress-tac` is invoked manually OR you detect context approaching limits, write the working-context Chinese summary to `work/tac_log/` using the same format. If the RTACC engine is reachable, also update its state counters.

## Setup

No files required. Output directory: `work/tac_log/` is auto-created.

## Known Issues (Fixed 2026-07-16)

Both TAC cron jobs were erroring with "Script not found":

| Job ID | Name | Schedule | Error |
|--------|------|----------|-------|
| `84b387e39c9d` | TAC auto-curation | `0 * * * *` (hourly) | Script not found: tac-curation.sh |
| `b7798d50a076` | auto-tac-compress | `*/30 * * * *` | Script not found: auto-tac-compress.py |

Root cause: scripts were in `~/work/` but cron expected them in `~/scripts/`. Fixed by symlinking:

```bash
ln -sf ~/.NOTTHEONETOEDIT/profiles/thotheauphis/work/auto-tac-compress.py \
       ~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/
ln -sf ~/.NOTTHEONETOEDIT/scripts/tac-curation.sh \
       ~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/
```

Verified: `auto-tac-compress.py` runs cleanly (7509 → ~149 token compression per block).
Next cron runs will succeed automatically.

## Quick Fix Checklist

If any TAC cron job errors with "Script not found":
```bash
# Check script exists
ls ~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/auto-tac-compress.py

# Recreate symlink if missing
ln -sf ~/.NOTTHEONETOEDIT/profiles/thotheauphis/work/auto-tac-compress.py \
       ~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/

# Test manually  
python3 ~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/auto-tac-compress.py
# Should produce: [TAC] Compressed block saved: tac_<timestamp>.block
```
