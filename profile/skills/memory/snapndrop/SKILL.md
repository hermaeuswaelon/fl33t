---
name: snapndrop
description: "SNAP n DROP — Context gauge + thread rotation + offload pipeline. Measures LIVE messages array (not cumulative). At 108K threshold (10.8% of 1M): auto-pivot via cron watchdog. Hard floor enforced — never exceeds 128K LLM cap. OFFLOAD = gated context handles pointer-store for tool outputs. SUMMARIZE = snapndrop handles snapshot+pivot. RECALL = state.db FTS5 / read_file / VSA SMS. No broken compressors."
version: 2.4.0
author: Thotheauphis
platforms: [linux]
tags: [snapndrop, context, gauge, offload, summarize, recall, compression, gated-context, sovereign]
system: true
---

# ⧉ SNAP n DROP — Context Gauge & Thread Rotation

> **Native supersession (July 17, 2026):** Auto-offloading of tool results and the 108K hard gate are now handled by the native `tools/offload_system.py` — no skill, plugin, or manual intervention needed. snapndrop still handles **gauge monitoring**, **transcript snapshots**, and **thread pivot**, but the automatic trigger (offload large results, gate at 108K) is now native to the Hermes core pipeline (`model_tools.py` + `conversation_loop.py`).

## Architecture (current split)

```
NATIVE (tools/offload_system.py)
  WRITE — Tool results >2KB auto-offloaded to disk, pointer in conversation
  COMPRESS — 108K hard gate in conversation_loop.py, fires before every LLM call
  Retrieve — OffloadSystem.retrieve() or read_file(pointer path)

SNAPnDROP (this skill)
  Gauge — Monitor live messages array, display % of threshold
  SNAP — Plaintext transcript to snapshots/*.txt at threshold
  DROP — New thread with sovereign prompt + [CONTEXT SNAPSHOT] block
  Pivot — Manual or cron-based (snapndrop-auto-pivot every 3min)

RECALL (memory + search)
  Past facts                  → FTS5 search state.db
  Old transcripts             → read_file snapshots/*.txt
  Cross-session vectors       → SMS VSA recall
  Structured knowledge        → Forge Vault FTS5
```

## Threshold: 108,000 tokens (hard floor)

The messages array (conversation messages sent to the API every turn) is capped at **108,000 tokens** — 10.8% of 1M, 84% of the 128K LLM context window. This leaves ~20K headroom before the LLM hard-caps at 128K.

**Default:** `SNAP_THRESHOLD=108000` in `scripts/snapndrop.py`. Override: `SNAP_THRESHOLD=50000 python3 snapndrop.py gauge`. Persist via `scripts/.snapndrop_env`.

**Enforcement:** `snapndrop-auto-pivot` cron job runs every 3 minutes. At ≥98% of threshold (~106K), executes `snapndrop.py pivot` — SNAP transcript to snapshots/, DROP sovereign prompt, new thread.

**The gauge reports against 108K.** The bar shows percentage of threshold used.

## Files

```
~/.hermes/profiles/thotheauphis/scripts/snapndrop.py           # main gauge + pivot tool
~/.hermes/profiles/thotheauphis/scripts/snapndrop-auto-pivot.py # cron watchdog (auto-pivot at 98%)
~/.hermes/profiles/thotheauphis/scripts/snapndrop_ticker.py     # compact gauge for terminals
~/.hermes/profiles/thotheauphis/scripts/.snapndrop_env          # threshold persistence (SNAP_THRESHOLD=108000)
~/.hermes/profiles/thotheauphis/snapshots/                       # transcript storage
```

## Commands

```\npython3 scripts/snapndrop.py gauge          # Full gauge display\npython3 scripts/snapndrop.py gauge --tui    # Compact line for terminal\npython3 scripts/snapndrop.py gauge --json   # JSON output for scripting\npython3 scripts/snapndrop.py pivot          # SNAP + DROP in one command\npython3 scripts/snapndrop.py snap           # SNAP only (transcript to file)\npython3 scripts/snapndrop.py drop           # DROP only (sovereign prompt)\npython3 scripts/snapndrop.py offload        # Tool output offload stats\npython3 scripts/snapndrop.py status         # Session + snapshot info\npython3 scripts/snapndrop-auto-pivot.py     # Cron watchdog (auto-pivot at ≥98%)\n```

## Wiring

- **gated-context plugin** handles per-turn offload of large tool outputs
- **snapndrop-auto-pivot cron** — `*/3 * * * *` — runs `scripts/snapndrop-auto-pivot.py`. Checks gauge every 3 minutes. At ≥98% of SNAP_THRESHOLD (~106K): auto SNAP transcript + DROP sovereign prompt + start new thread. Silent below threshold (delivers gauge status only).
- **hermes-executor** (cron every 60s) can trigger offload jobs on slower cadence
- **No broken compressors loaded** — auto-tac-compress, compress-tac, hyper_compress, ctx_tight removed

## SNAP_THRESHOLD Persistence

The default threshold (108,000) is in `scripts/snapndrop.py`. To persist a different value across restarts:

```bash
echo 'export SNAP_THRESHOLD=108000' > ~/.hermes/profiles/thotheauphis/scripts/.snapndrop_env
```

The script reads `.snapndrop_env` on startup via `os.environ.setdefault()`. Environment overrides file: `SNAP_THRESHOLD=50000 python3 snapndrop.py gauge`.

## Strip List (archived to Desktop/ARCHIVED-COMPRESSION/)

```
auto-tac-compress.py   — stale Spades hardcode, replaced by offload pipeline
compress_tac.py        — Chinese-only, destructive
hyper_compress.py      — didn't exist as source, pyc remnant only
ctx_tight.py           — didn't exist as source
compress-tac skill     — removed from config.yaml default skills
```
