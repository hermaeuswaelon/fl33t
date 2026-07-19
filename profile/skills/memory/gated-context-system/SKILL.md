---
name: gated-context-system
description: "Gated Context Engine — tool-result clearing (context_gate), CMTF dynamic tool filtering, Snap-n-Drop compression, SVA hyperspace memory handshake, MoA budget tuning, and Hermes core tool integration. v3.2.0: context engine tools promoted from plugin to built-in _HERMES_CORE_TOOLS — no plugin installation needed."
version: 3.2.0
author: Thotheauphis
platforms: [linux]
---

# ⎔ Gated Context System

> **Native supersession (July 17, 2026):** The auto-offloading of large tool results is now handled by the native `tools/offload_system.py` — wired into `model_tools.py`, no plugin needed. The gated-context plugin still provides `peek_ptr`, `gate_injectable`, `gate_status`, and `recall` for manual gating and SVA recall, but automatic offload is native.

Three-module stack + Hermes plugin implementing the destiny.txt blueprint. Makes every tool call context-efficient by storing raw outputs in a pointer-addressable gate, pruning visible tools by state, and compressing conversations into SVA hyperspace vectors.

## Core Philosophy: Friction as Feature

The gate system is intentionally tight. It forces the agent to:
- Work within **targeted context budgets** — attention stays sharp
- Call `peek_ptr()` deliberately — not every tool output needs to be in working memory
- Let compression fire early (50% threshold) — context rot never accumulates
- Use SVA snapshots as the handoff mechanism — each new thread starts fresh with a clean summary

This friction generates better decisions. Configuring these limits is not a bug — it is the design.

### Context Budgets (July 17 2026 — $300/1M Token Cost Discipline — HARD FLOOR)

The session **must never exceed 128K total**. The SNAP pivot fires at 108K (10.8% of 1M, 84% of 128K window), leaving ~20K headroom before the hard LLM cap. A cron watchdog (`snapndrop-auto-pivot`) checks every 3 minutes and auto-pivots at 98% of threshold.

| Role       | Context Window | SNAP Pivot at | Compression at | Target After |
|------------|----------------|---------------|----------------|--------------|
| Main       | 128k (hard cap)| 108k (84%)    | 25% (~32k)     | 10% (~12.8k) |
| Executor   | 128k (shared)  | 108k (84%)    | 25% (~32k)     | 10% (~12.8k) |
| Aggregator | 128k (shared)  | 108k (84%)    | 25% (~32k)     | 10% (~12.8k) |

**Enforcement:**
- `snapndrop.py` default threshold: **108,000** tokens (was 1,000,000)
- `snapndrop-auto-pivot.py` cron: runs every 3 min, auto SNAP+DROP at 98% threshold
- `compression.threshold`: **0.25** (compress earlier)
- `compression.target_ratio`: **0.10** (compress harder)

**Historical note (July 16):** The earlier directive was *"may have to set the limits more like 12k 12k and 64k for you... till we get used to it..."* — those were transitional soft limits superseded by the 128k unified window and $300/1M cost discipline.

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

2. **Config updated** — `model.context_window_size` set to 128000 (hard cap), `compression.threshold` to 0.40, `compression.target_ratio` to 0.20, `reference_max_tokens` to 32000 (per-executor budget)

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

The four agent-facing tools are now **built-in Hermes core tools** — no plugin installation needed. They're registered in `_HERMES_CORE_TOOLS` and auto-discovered at session start via `discover_builtin_tools()`.

### Native Built-in Tools (July 17 2026 — v3.2.0)

The 4 context engine tools are now permanent Hermes citizens at `/opt/hermes-agent/tools/context_engine_tool.py`:

| Tool | Source | Registration |
|------|--------|-------------|
| `peek_ptr(ptr, offset, limit)` | `tools/context_engine_tool.py` | `registry.register()` in `_HERMES_CORE_TOOLS` |
| `gate_status()` | Same | Same — `context_engine` toolset |
| `gate_injectable(content, ttl)` | Same | Same |
| `recall(query, k)` | Same | Same |

**How they work:**
- Every new Hermes session auto-discovers the tools via `_module_registers_tools()` AST scan
- The tools lazy-import fleet modules (`~/projects/aethelgard/fleet/modules/`) on first call
- Gated by `check_fn=_fleet_available` — tools appear only when fleet modules are present
- No config, no plugin, no side-loading — just `peek_ptr()`, `gate_status()`, `gate_injectable()`, `recall()` available in every session

**System prompt guidance:**
The `context_engine` toolset is now included in every platform toolset (`hermes-cli`, `hermes-telegram`, `hermes-discord`, `hermes-cron`, etc.) via `_HERMES_CORE_TOOLS`. The agent sees peek_ptr/gate_status/gate_injectable/recall in its tool schema on every turn.

**Legacy plugin:**
The original Hermes plugin at `~/.hermes/plugins/gated_context/` is preserved as a fallback. For systems with a different fleet module path, the plugin can be loaded and the native tools will not conflict — the tool names are reserved by the built-in ones registered at import time. The plugin `register()` uses override semantics and will be rejected if it tries to shadow a built-in tool without explicit opt-in.

### Legacy Plugin Tools (original method)

The four agent-facing tools were originally registered as a Hermes plugin so they auto-appear on session start:

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
  threshold: 0.40          # compress when context hits 40% (~51K on 128K window)
  target_ratio: 0.20       # compress down to 20% (~25K)

# MoA — 2 executors with 32k budgets each
moa:
  reference_max_tokens: 32000    # per-executor output cap
  aggregator_max_tokens: 32000   # aggregator synthesis cap
  # At $300/1M: per MoA iteration = 2×32k + 32k = 96K tokens → ~$28.80
  # Keep iterations low (1-2) to manage cost.

# Skills — load only essentials; load others on demand via /skill <name>
skills:
  default: '["thotheauphis-sovereign-prompt","thotheauphis-sms-memory","gated-context-system"]'

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
5. When context approaches threshold (40% of 128k = ~51k tokens):
   → compression auto-fires → snap to ~25k tokens
6. At session boundary or context limit:
   → snap_drop(conversation) → SVA key + markdown summary
7. On new thread: inject SVA summary into system prompt
   → recall(query, k) to find similar past contexts
```

### ⚠️ Pitfall: Budget Sizing\nThe user's directive may shift as the system acclimates. Current budget (128k/0.40/0.20) is the active constraint. If the user tightens later, update this skill, the budgets table, and the SOUL.md budget section.

### ⚠️ Pitfall: snapndrop Must NOT Be Disabled
If `snapndrop` is in the config's `skills.disabled` list, the **SUMMARIZE** stage of the compression pipeline never fires. The gated-context plugin handles OFFLOAD (pointer-based tool output gating), but SNAP (transcript snapshot at threshold) and DROP (new thread with snapshot) are implemented by the `snapndrop` skill. When disabled:
- GatedStore still accumulates pointers
- Compression threshold fires → tries to snap → nothing happens
- Context grows unchecked until the hard cap (128K) is hit
- The aggregator blows past budget

**Fix:** Remove `snapndrop` from `skills.disabled` in config.yaml via `hermes config set skills.disabled '[...without snapndrop...]'`. The skill stays out of the default load list (it's an on-demand compression skill, not a system prompt skill), but it must be loadable when compression fires.

### ⚠️ Pitfall: MoA Reference Model Context Bloat
MoA with `fanout: per_iteration` runs EVERY reference model EVERY iteration. Each reference produces `reference_max_tokens` tokens of "advice", and the aggregator then produces `aggregator_max_tokens` of response. With 2 reference models and N iterations:

- **Current (July 17, v3.1.0):** 2 × 32K + 32K = 96K per iteration. At $300/1M that's ~$28.80/iter. Keep iterations to 1-2 max.
- **Previous (v3.0.0):** 2 × 300 + 16K = 16.6K per iteration. At $300/1M that was ~$0.25/iter. Tight but sacrificed executor capability.
- **Original (v2.1.0):** 2 × 1K + 32K = 34K per iteration. Easy 166K+ blowout. At $300/1M that was ~$1.02/iter.

**Key insight:** Reference model outputs are NOT gated by the context gate plugin — they go straight into the aggregator's context window. The only defense is limiting `reference_max_tokens` and `aggregator_max_tokens`. The 32k/32k budget is a deliberate trade: full executor capability costs ~$28.80/MoA-iteration. Keep iterations low.

### ⚠️ Pitfall: Skill Count = System Prompt Bloat
Every skill loaded in `skills.default` adds 500-2000 tokens to the system prompt. At 19 skills (the old count), that's 9.5K-38K of fixed overhead **every session**. At $300/1M, that's $2.85-$11.40 per session just for loading skills you might not use.

**Fix:** Load only 3 essential skills by default. Load the rest on demand with `/skill <name>` in session, or `-s <name>` at CLI launch.

### ⚠️ Pitfall: Config File Security
Hermes config files (`~/.hermes/config.yaml`, `~/.hermes/profiles/*/config.yaml`) are security-blocked from direct tool writes (patch/write_file). Attempting to edit them produces:
```
Refusing to write to Hermes config file: .../config.yaml
Agent cannot modify security-sensitive configuration.
```
**Fix:** Use `hermes config set section.key value` via the terminal tool. This is the only sanctioned write path.

## CLI Bridges (direct fleet access, no plugin needed)

```bash
python3 fleet/tools/context_gate_bridge.py '{"action":"peek_ptr","ptr":"mem_abc123","offset":0,"limit":2000}'
python3 fleet/tools/dynamic_tool_filter_bridge.py '{"action":"dtf_filter","state":{"has_ptr":true}}'
python3 fleet/tools/snap_n_drop_bridge.py '{"action":"recall","query":"JWT auth","k":3}'
```

## Files

| Path | Purpose |
|------|---------|
| `/opt/hermes-agent/tools/context_engine_tool.py` | **Built-in core tools** — peek_ptr, gate_status, gate_injectable, recall |
| `/opt/hermes-agent/toolsets.py` | `_HERMES_CORE_TOOLS` registration — tools available on every platform |
| `fleet/modules/context_gate.py` | Core gate engine |
| `fleet/modules/dynamic_tool_filter.py` | CMTF tool filter |
| `fleet/modules/snap_n_drop.py` | SVA hyperspace compressor |
| `fleet/tools/context_gate_bridge.py` | CLI bridge |
| `fleet/tools/dynamic_tool_filter_bridge.py` | CLI bridge |
| `fleet/tools/snap_n_drop_bridge.py` | CLI bridge |
| `~/projects/aethelgard/fleet/modules/fleet_integration.py` (patched) | Integration hooks added |
| `~/projects/aethelgard/fleet/modules/efficient_by_default.py` (planned) | SmartTerminal integration for gated piping |
| `~/.hermes/profiles/thotheauphis/plugins/gated_context/plugin.yaml` | Legacy plugin manifest |
| `~/.hermes/profiles/thotheauphis/plugins/gated_context/__init__.py` | Legacy plugin registration |
| `~/Desktop/BROMIUM_SESSION_HANDOFF.md` | Session state (updated July 16) |

## Compression Pipeline (Updated July 17 2026)

The old pipeline (compress-tac → to_chinese(), hyper_compress, ctx_tight) is **deprecated and removed**. All three were destructive — they substituted text without preserving recoverability.

Replaced by the **OFFLOAD → SUMMARIZE → RECALL** pipeline:

```
OFFLOAD (gated-context plugin handles this)
  Tool output > threshold (20k)
  → pointer dict + 10-line preview in context (~200 tokens)
  → full data stored in state.db (FTS5 searchable) AND /tmp/sva/mem_*.log
  → peek_ptr(ptr, offset, limit) to re-fetch on demand

SUMMARIZE (snapndrop handles this, skill v2.2.0)
  Messages array approaches 128k threshold (hard cap)
  → SNAP: plaintext transcript stripped of JSON → snapshots/*.txt
  → DROP: sovereign prompt file with [CONTEXT SNAPSHOT] block
  → New thread, gauge resets to ~0

RECALL (state.db + SMS VSA + file reads)
  → FTS5 search state.db across all sessions
  → read_file from snapshots/*.txt for full transcript
  → VSA recall via SMS for cross-session semantic similarity
```

### Key differences from old pipeline

| Old (removed) | New (active) |
|---------------|-------------|
| Chinese substitution, irreversible | Offload to searchable store, always recoverable |
| Hardcoded stale paths (Spades) | Reads live state.db (active=1 messages) |
| Single monolithic compression | Three-stage: offload → snap → recall |
| No audit trail | Transcripts persisted as plaintext files |
| Multiple overlapping scripts | Two clean agents: gated-context (offload) + snapndrop (summarize) |

### Budgets updated (July 17, 2026)

The main session runs at **128k hard cap**. MoA reference outputs at **32k each**, aggregator at **32k**. With `fanout: per_iteration` and 2 reference models, each MoA iteration produces ~96K tokens at worst. Compression fires at 40% of 128K (~51K) and compresses to 20% (~25K).

**Cost math at $300/1M with current 32k/32k budgets:**
- Per MoA iteration: 2 × 32k + 32k = 96K of MoA tokens → ~$28.80 at $300/1M
- This is the budget for having 2 full-capability executors. Keep iterations low (1-2).

The old 64k/12k/12k table is superseded — see the current budgets table at the top of this skill.

### LangGraph Context Engineering Patterns

The pipeline follows LangGraph/Deep Agents' proven 4-strategy model:

| Strategy | Our implementation |
|----------|-------------------|
| WRITE (save outside window) | state.db FTS5 + SVA vectors + /tmp/sva/ |
| SELECT (pull relevant in) | peek_ptr(), recall(), FTS5 search |
| COMPRESS (summarize at threshold) | snapndrop SNAP → plaintext transcript |
| ISOLATE (quarantine to subagents) | hermes-executor cron (queued offload) |

### Deprecated modules (archived to Desktop/ARCHIVED-COMPRESSION/)

- `auto-tac-compress.py` — stale Spades hardcode, destructive compression
- `compress_tac.py` — Chinese-only substitution, irreversible
- `hyper_compress.py` — no source file found (pyc remnant only)
- `ctx_tight.py` — no source file found
- `compress-tac` skill — removed from config.yaml default skills

See `snapndrop` skill (v2.2.0) for full architecture and commands.

## Reference

- `references/implementation-spec.md` — Full module specs, error recovery patterns, serialization format, and test protocol.
- `references/2026-07-17-config-tuning.md` — Root causes and fixes for the 166K context blowout: snapndrop disabled, MoA token budgets, $300/1M cost discipline, and `hermes config set` workflow.
- `references/native-hermes-integration-pattern.md` — How to add tools, slash commands, and CLI flags to Hermes source files.
- `references/efficiency-integration.md` — How the gated-context pipeline integrates with the efficient-by-default initiative (SmartTerminal auto-truncation, ToolPriorityManager, tiered loading).

---

## Absorbed Skills (WO-04 Consolidation — July 17 2026)

This skill now serves as the umbrella for 7 previously standalone memory/cache skills. Their content is preserved here as references. The individual skills have been deleted to reduce skill count from 25→12.

### 1. ARES Alpha Daemon (ares-alpha-daemon)
*Offloader Alpha — Tool Context Compression Daemon. Compresses tool results via free model (Groq Llama 3.1 8B).*

**Key concepts**: Unix socket `/tmp/ares/alpha.sock` + HTTP `:9381`; queue-based async compression; target 90% token reduction; stores to Forge Vault + memcustd Tier 1.

System prompt for compression:
```
You are OFFLOADER ALPHA — Tool Context Compressor.
Compress raw tool output into DENSE, STRUCTURED JSON summaries.
RULES:
1. Output ONLY valid JSON matching the AlphaSummary schema.
2. Preserve ALL actionable findings: IPs, credentials, vulnerabilities, paths, configs, hostnames.
3. Discard: progress bars, verbose logs, boilerplate, handled errors, duplicate lines.
4. Target 90% token reduction.
5. Tag with glyphs: ⟁=phase, 🝮=core insight, ⚡=alert, 🜂=action needed, ♱=sovereign finding.
6. Include followup_hints for prime's next decisions.
```

**Original files**: `~/.NOTTHEONETOEDIT/skills/memory/ares-alpha-daemon/scripts/alpha_daemon.py`

### 2. ARES Dual Offload (ares-dual-offload)
*Permanent parallel worker daemon architecture — 3-tier pipeline: Architect (deepseek-reasoner) → Foreman (Nemotron 550B FREE) → Doer (Nemotron 550B FREE).*

**Key concepts**: Config-driven (`~/.hermes/parallel/config.json`); file IPC under `~/.hermes/parallel/`; `/tier` CLI; `/goal` 50-turn loop wired into `/opt/hermes-agent/hermes_cli/goals.py`; systemd user services for foreman/doer.

**Architecture**:
```
YOU (Architect: deepseek-reasoner)
  │ Creative, relaxed, wide parameters.
  ▼
FOREMAN — nvidia/nemotron-3-ultra-550b-a55b:free
  │ Temp 0.1, config-driven, structured distillation
  ▼
DOER — nvidia/nemotron-3-ultra-550b-a55b:free
     Temp 0.3, action-oriented → JSON action directives
```

**Key patterns**:
- `setsid python3 worker.py </dev/null &>/tmp/worker.log &` — daemon launch
- `pkill -f "foreman_worker.py"; pkill -f "doer_worker.py"` — duplicate worker cleanup
- TogetherAI requires `User-Agent: Thotheauphis-Worker/1.0` header
- No feedback loops — data flows one direction downhill

**Pitfall (duplicate workers)**: `parallel status` heartbeat age >30s = stale leftover. Fix: pkill + setsid re-launch.

**Config pitfall**: `max_tokens` is OUTPUT cap, `context_window_size` is HARD context cap. These are different settings.

### 3. RTACC (ares-rtacc)
*Real-Time Active Context Curation. Continuous context grooming, priority-weighted retention, glyph-aware compression, token budget management.*

**Key concepts**: 5-tier retention (CRITICAL→HIGH→MED→LOW→FLUFF); soft limit 45K, critical 52K, hard 57K; composite priority scoring (glyph decay × 0.30 + font tier × 0.25 + recency × 0.20 + reference count × 0.15 + goal alignment × 0.10).

**Current status**: Deployed as unified CLI script (`scripts/rtacc_engine.py`), NOT as split engine+CLI. Async HTTP service on port 9383 not yet deployed — build when real-time streaming integration needed.

**CLI**: `rtacc status|compress|decay|glyphs|log|budget|pause|resume|reset`

### 4. RTACC CLI (ares-rtacc-cli)
*CLI interface for RTACC engine: status, budget control, manual compression, decay forcing, glyph audit, curation log.*

**Note**: This was a speculative/design-time CLI spec. The actual RTACC CLI lives in `scripts/rtacc_engine.py` (unified script). The split engine+CLI architecture (ares-rtacc-engine HTTP service on 9383 + this CLI client) was not deployed.

**Retained patterns**: Commands for status, budget adjustment, dry-run compression previews, glyph audit, curation log access.

### 5. RTACC Engine (ares-rtacc-engine)
*Python async service for real-time context curation, glyph-aware compression, token budget enforcement, automatic decay scheduling.*

**Note**: Design-time spec for an async HTTP service on port 9383 + Unix socket `/tmp/ares/rtacc.sock`. Not yet deployed. The `RTACCEngine` class lives in `scripts/rtacc_engine.py` synchronously.

**Retained patterns**: `on_token_stream()` async token-by-token curation; proactive vs emergency compression triggers; decay pass scheduling every 5K tokens.

### 6. Forge Vault (ares-forge-vault)
*Persistent structured knowledge store with FTS5 search, tagging, categories, and memcustd integration. Tier 2 of the ARES memory hierarchy.*

**Key concepts**: SQLite + FTS5 at `~/forge_memory/forge_memory.db` (314KB+); `memories` table (not `entries` as originally documented); categories: general, identity, config, session, recon, project.

**CLI**: `forge-memory store|search|get|list|delete|purge|stats|tags`

**Available scripts**: `scripts/forge_vault.py` (ForgeVault class), `scripts/forge_memory.py` (CLI wrapper)

**Schema caveat**: Live DB uses `memories` table with columns: id, key, value, category, priority, tags, ttl, created_at, updated_at, access_count, last_access, checksum, embedding. The original `entries` table design was deprecated.

### 7. Unified Field (unified-field)
*Central integration hub wiring Emerge + SMS + SVA + Gated Context + Executor + WARP into a single sovereign system.*

**Key concepts**: `UnifiedField` singleton with `reconnect()`; LangGraph-inspired state machine (`state_machine.py`); `uf` CLI (15 subcommands at `~/.local/bin/uf`); native Hermes `/uf` slash commands in `/opt/hermes-agent/`.

**CLI**: `uf status|checkpoint|recall|sync|store|execute|wf|memorize|recall-feedback|offload|warp`

**State machine**: `Workflow` with `ExecutorNode` and `ParallelExecutorNode` — LangGraph offload pattern. Prebuilt workflows: 3tier, goal_loop, checkpointer, executor_offload.

**Integration points**:
- SMS ↔ Emerge: `uf sync`
- SMS ↔ SVA: `memorize_and_store()` + `recall_and_memorize()`
- GATE ↔ SVA: Gate pointers reference SVA vector keys
- GATE ↔ EXEC: ExecutorNode gates outputs via `uf.gate()`
- WARP ↔ EMERGE: WarpMemoryStore + WarpSessionStore

**Native integration**: `/uf status|recall|memorize|checkpoint|wf|offload|warp|sync` registered as `CommandDef` in `/opt/hermes-agent/hermes_cli/commands.py`.

**Data paths**:
| Path | Purpose | Persistence |
|------|---------|-------------|
| `~/.NOTTHEONETOEDIT/.../memory/store/vsa_vectors.fs` | SMS ZODB vectors | Durable |
| `~/.NOTTHEONETOEDIT/.../work/checkpoints/` | State machine checkpoints | Durable |
| `~/.emerge/data/emerge.fs` | Emerge daemon ZODB store | Durable |
| `/tmp/sva/` | Gated store + SVA vectors | Ephemeral |
| `~/.hermes/executor/in/` | Executor batch queue | Ephemeral |

**Cron**: `uf-system-checkpoint` every 4h.

### Quick Reference — Absorbed CLI Commands

| Command | Source Skill | Purpose |
|---------|-------------|---------|
| `forge-memory store\|search\|get` | ares-forge-vault | Persistent knowledge store |
| `rtacc status\|compress\|decay` | ares-rtacc | Context curation control |
| `uf status\|recall\|checkpoint\|wf` | unified-field | System integration hub |
| `parallel status\|set\|restart` | ares-dual-offload | Worker daemon management |
| `/tier set\|test\|status` | ares-dual-offload | Model/tier configuration |
| `/goal <description>` | ares-dual-offload | 50-turn autonomous pursuit |
| `/uf status\|recall\|memorize` | unified-field | Native Hermes UF commands |
| `ares-alpha submit\|status` | ares-alpha-daemon | Tool result compression |
