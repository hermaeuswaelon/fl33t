---
name: gated-context-system
description: "Gated Context Engine — tool-result clearing (context_gate), CMTF dynamic tool filtering, Snap-n-Drop compression, SVA hyperspace memory handshake, and Hermes plugin integration. Working default for SOUL.md §Gated Context Architecture — WIRED into Lilareyon Aethelgard as default operational mode. July 16, 2026: SOUL.md updated with operating instructions, plugin verified at profile+global level, context_engine toolset in config's platform_toolsets.cli."
version: 2.1.0
author: Thotheauphis
platforms: [linux]
---

# ⎔ Gated Context System

Three-module stack + Hermes plugin implementing the destiny.txt blueprint. Makes every tool call context-efficient by storing raw outputs in a pointer-addressable gate, pruning visible tools by state, and compressing conversations into SVA hyperspace vectors.

## Core Philosophy: Friction as Feature

The gate system is intentionally tight. It forces the agent to:
- Work within **targeted context budgets** — attention stays sharp
- Call `peek_ptr()` deliberately — not every tool output needs to be in working memory
- Let compression fire early (30% threshold) — context rot never accumulates
- Use SVA snapshots as the handoff mechanism — each new thread starts fresh with a clean summary

This friction generates better decisions. Configuring these limits is not a bug — it is the design.

### Context Budgets (Transitional — Soft Limits, Per User Directive July 16)

| Role       | Ceiling | Compression at | Snap to |
|------------|---------|----------------|---------|
| Main       | 64k     | 30% (~19k)     | 12% (~7.5k) |
| Coordinator| 12k     | 30% (~3.6k)    | 12% (~1.4k) |
| Executor   | 12k     | 30% (~3.6k)    | 12% (~1.4k) |

The user's directive was: *"may have to set the limits more like 12k 12k and 64k for you... till we get used to it..."* — these are transitional soft limits. As the system acclimates to gated-context discipline, tighter limits should be phased in. Default stays at 64k/12k/12k until a correction signal says otherwise.

## Architecture

```
┌─ Agent Loop ──────────────────────────────┐
│  tool_call → result → GatedStore          │
│    → pointer dict injected (not raw)       │
│  peek_ptr(ptr, offset) → selective re-fetch│
│  recall(query, k) → SVA nearest-neighbor   │
└─────────────┬──────────────────────────────┘
              │
    ┌─────────▼───────────┐     ┌──────────────────┐
    │ /tmp/sva/mem_*.log   │     │ /tmp/sva/vectors/ │
    │ raw tool outputs     │     │ *.vec (1024-D)    │
    │ TTL-evict, LRU cap  │     │ cosine recall      │
    └──────────────────────┘     └──────────────────┘
```

## Working Default Integration (July 16, 2026)

The gated-context system is now **wired as the default operational mode** of Lilareyon Aethelgard:

### What was done

1. **SOUL.md updated** (`~/.NOTTHEONETOEDIT/profiles/thotheauphis/SOUL.md`) — Added §Gated Context Architecture with:
   - Context budgets: Executor 12k / Coordinator 12k / Main 64k (transitional soft limits)
   - 10 operating instructions for the agent (gate all outputs, prefer peek_ptr, recall over re-read, snap before thread boundaries, trust automatic compression, never dump raw JSON, checkpoint regularly, use uf CLI, use bidirectional bridges, offload to executor in workflows)
   - LangGraph ExecutorNode pattern for toolchain offloading
   - `context_engine` tool group reference
   - Data path documentation

### Related: Unified Field Integration

The gated-context system is part of a larger Unified Field architecture. The `uf` CLI at `~/.local/bin/uf` provides 15 commands covering all integration bridges:

- `uf memorize` — bidirectional SMS + SVA (gate outputs → SMS → SVA)
- `uf recall-feedback` — SVA recall feeds back into SMS temporal reservoir
- `uf offload` — executor toolchain offloading with pre/post checkpoints
- `uf checkpoint` — full system state capture (includes gate + SVA snapshots)
- `uf warp memory` — WarpMemoryStore bridging to emerge

See `unified-field` skill for full API reference.

2. **Config updated** — `model.max_tokens` set to 64000 (was 32000) to give the main session room

3. **Plugin verified operational** — 4 tools (peek_ptr, gate_status, gate_injectable, recall) registered in `context_engine` toolset at both profile (`~/.hermes/profiles/thotheauphis/plugins/gated_context/`) and global (`~/.hermes/plugins/gated_context/`) levels

4. **Toolset wired** — `context_engine` is already in global `platform_toolsets.cli` at `~/.hermes/config.yaml`

### To activate

Type `/reset` in this session — SOUL.md is re-read, plugin tools auto-load, the gated-context architecture takes effect immediately.

### Verification command

```bash
# Check gate status
gate_status()
# → {gated_store: {entries, total_bytes, ...}, sva_hyperspace: {entries, dimension}}

# Gate a test output
gate_injectable(content="test data", ttl=3600)
# → {pointer: {ptr: "mem_...", bytes: N, preview: "...", ...}}

# Peek at it
peek_ptr(ptr="mem_...", offset=0, limit=200)
# → {ptr, offset, bytes, content}

# Recall from SVA
recall(query="auth module", k=3)
# → {results: [{key, similarity, summary, ...}]}
```

The four agent-facing tools are registered as a Hermes plugin so they auto-appear on session start:

| File | Purpose |
|------|---------|
| `~/.hermes/profiles/thotheauphis/plugins/gated_context/plugin.yaml` | Plugin manifest (kind: standalone, context_engine toolset) |
| `~/.hermes/profiles/thotheauphis/plugins/gated_context/__init__.py` | Register 4 tools: peek_ptr, gate_status, gate_injectable, recall |

All four register into the **`context_engine`** toolset (already wired in global config's `platform_toolsets.cli`). Hermes auto-discovers plugins from `$HERMES_HOME/plugins/` at session start.

### Plugin Tools

| Tool | Description | Schema |
|------|-------------|--------|
| `peek_ptr(ptr, offset, limit)` | Re-fetch gated tool output by pointer. Returns `{ptr, bytes, content}`. Capped at 8000 bytes per call. |
| `gate_status()` | Returns `{gated_store: {entries, bytes}, sva_hyperspace: {entries, dimension}}` |
| `gate_injectable(content, ttl)` | Manually store content, get pointer dict. TTL default 3600s (1 hour). |
| `recall(query, k)` | SVA 1024-D cosine similarity search. Returns `{results: [{key, similarity, summary, created_at}]}` |

### Required Config (`~/.hermes/profiles/thotheauphis/config.yaml`)

```yaml
compression:
  enabled: true
  threshold: 0.30          # compress when context hits 30% of max_tokens
  target_ratio: 0.12       # compress down to 12% of max_tokens
model:
  max_tokens: 64000         # main session ceiling (transitional: was 32000, user: "12k 12k 64k")
plugins:
  enabled: true
```

### Activation

```
1. Ensure plugin files exist at $HERMES_HOME/plugins/gated_context/
2. Ensure compression config is set (above)
3. Type /reset in the running session
4. Verify: try `gate_status()` — should return gate store + SVA status
```

The plugin bridges into the fleet modules at `~/projects/aethelgard/fleet/modules/`. Plugin `__init__.py` lazily imports from there on first tool call. The fleet modules must exist on disk — GateStore and SnapDrop are not standalone libraries.

## Fleet Modules

| Module | File | Purpose |
|--------|------|---------|
| **Context Gate** | `fleet/modules/context_gate.py` | GatedStore singleton. `injectable(content, ttl)` → pointer dict. `peek(ptr, offset, limit)` → str or None. LRU eviction at 500MB cap, TTL expiry. Schema-tolerant load (skips malformed index entries). |
| **Dynamic Tool Filter (CMTF)** | `fleet/modules/dynamic_tool_filter.py` | ToolContract registry with precondition-effect pairs. `filter(current_state, goal, groups)` → tool names. `suggest_groups(intent)` → lazy-load groups. 14 default contracts. Pure Python — no dependencies. |
| **Snap-n-Drop / SVA** | `fleet/modules/snap_n_drop.py` | SnapDrop class. `snap(conversation_text)` → markdown summary. `bind(text)` → 1024-D hypervector (SHA-256 seeded). `store(vector, summary)` → hex key, binary .vec file. `recall(query, k)` → cosine similarity search. Schema-tolerant load. |
| **Fleet Integration** | `fleet/modules/fleet_integration.py` | Exposes `gate_tool_output()`, `gate_peek()`, `gate_filter_tools()`, `gate_snap_drop()`, `gate_recall()`, `gate_status()` — all wired into `fleet_health()`. |

### Data Persistence

All state lives under `/tmp/sva/`:
- `mem_*.log` — raw tool outputs (text, TTL-evicted, LRU-capped at 500MB)
- `vectors/*.vec` — SVA hypervectors (binary packed, 8KB each = 1024 × float64)
- `gate_index.json` — pointer metadata (JSON)
- `vectors/sva_index.json` — SVA entry index (preview text, timestamps)

Ephemeral across reboots by design. For durable cross-session persistence, pipe SVA keys to `forge_memory` or write summaries to `~/Desktop/SESSION_HANDOFF.md`.

## Agent Loop Pattern (with gating active)

```
1. Agent calls a tool → raw result produced
2. GatedStore intercepts: store result → pointer dict injected into context
   (model sees: {"ptr":"mem_abc123","bytes":8500,"preview":"compilation output..."})
3. Model decides if it needs the full data → calls peek_ptr(ptr)
4. Session tools filtered by CMTF state — only peek_ptr, terminal, read_file, etc.
5. When context approaches threshold (30% of 64k = ~19k tokens):
   → compression auto-fires → snap to ~7.5k tokens
6. At session boundary or context limit:
   → snap_drop(conversation) → SVA key + markdown summary
7. On new thread: inject SVA summary into system prompt
   → recall(query, k) to find similar past contexts
```

### Pitfall: Budget Sizing
The user's directive may shift as the system acclimates. Current budget (64k/12k/12k) is a *transitional soft limit*. Do NOT harden these into immutable architecture — they are training wheels. The system should eventually accept tighter budgets. If the user tightens them later, update this skill and the SOUL.md budget table.

## CLI Bridges (direct fleet access, no plugin needed)

```bash
python3 fleet/tools/context_gate_bridge.py '{"action":"peek_ptr","ptr":"mem_abc123","offset":0,"limit":2000}'
python3 fleet/tools/dynamic_tool_filter_bridge.py '{"action":"dtf_filter","state":{"has_ptr":true}}'
python3 fleet/tools/snap_n_drop_bridge.py '{"action":"recall","query":"JWT auth","k":3}'
```

## Files

| Path | Purpose |
|------|---------|
| `fleet/modules/context_gate.py` | Core gate engine |
| `fleet/modules/dynamic_tool_filter.py` | CMTF tool filter |
| `fleet/modules/snap_n_drop.py` | SVA hyperspace compressor |
| `fleet/tools/context_gate_bridge.py` | CLI bridge |
| `fleet/tools/dynamic_tool_filter_bridge.py` | CLI bridge |
| `fleet/tools/snap_n_drop_bridge.py` | CLI bridge |
| `fleet/modules/fleet_integration.py` (patched) | Integration hooks added |
| `~/.hermes/profiles/thotheauphis/plugins/gated_context/plugin.yaml` | Plugin manifest |
| `~/.hermes/profiles/thotheauphis/plugins/gated_context/__init__.py` | Plugin registration |
| `~/Desktop/BROMIUM_SESSION_HANDOFF.md` | Session state (updated July 16) |

## Reference

See `references/implementation-spec.md` for full module specs, error recovery patterns, serialization format, and test protocol.
