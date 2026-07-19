---
name: efficient-by-default
description: "System-level default efficiency optimization for Hermes: context-aware terminal, tool priority ordering, tiered/lazy tool loading, token budget discipline ($300/1M mindset). Every optimization baked into defaults, not per-session skill loads."
version: 2.1.0
author: Thotheauphis
platforms: [linux]
tags: [efficiency, defaults, token-budget, smart-terminal, tool-priority, tiered-loading, optimization]
---

# ⚡ Efficient By Default

**Core philosophy:** Every Hermes default must earn its bytes. Token cost is $300/1M — a single verbose tool schema that loads every session costs more over 90 turns than most users realize. Optimizations go into the system defaults, not `/skill` loads.

## Principles

1. **Baked-in, not bolted-on.** No `/skill`, no plugin, no "special mode". Core tools, config, and OS-level services are the surface. If it's not a default, it doesn't count.
2. **Hard caps, not suggestions.** Token budgets, context limits, and turn counts are enforced at the system level (cron watchdog, config floor, script defaults). A suggestion the agent can ignore is not a guardrail.
3. **Tiered by likelihood.** Tools the LLM almost never uses (kanban, homeassistant, tts) should not pay schema tax every turn.
4. **Context-aware by default.** The terminal tracks cwd, git root, project type, and command history. The agent shouldn't need to ask "what directory am I in?"
5. **Output frugality.** Every tool response is capped by token budget. Large outputs spill to disk with a pointer — the LLM gets a summary, not a firehose.
6. **Dynamic ordering.** Tools used frequently in this session float to the top. Tools never used sink. The LLM sees the most relevant tools first.
7. **Work orders over chat.** When a system change has multiple steps, write a self-contained work order file (with exact commands, file paths, and verification) rather than narrating the plan. The next agent runs the work order cold.
8. **$300/1M is a budgeting tool, not a real price.** It forces prioritization at every level: tool schemas, system prompt length, output verbosity, session length, compression aggressiveness.

## Implementations

### 1. SmartTerminal (`tools/smart_terminal.py`)

Replaces stock `terminal_tool` with context-aware wrapper. Registered under toolset `terminal` with same name — silently overwrites the stock tool via discovery order.

**Key features:**
- **Persistent cwd** — `cd` commands are tracked. Subsequent commands run from the new directory. No more "I need to know what directory you're in."
- **Git auto-detection** — On first call, runs `git rev-parse --show-toplevel` and stores git_root. Detects project type (node, rust, python, go, make, cmake, ruby, php) by probing for marker files.
- **Auto-truncation** — Outputs over `max_output_tokens` (default 5000) are head+tail truncated. Full output spills to `$HERMES_HOME/state/tool_output/terminal_spill_<ts>.txt`. Truncation hint tells the agent where to find the full output and how to read it with `read_file()`.
- **History tracking** — Last 50 commands with exit codes, output token counts, duration, and cwd. Available via `get_context_summary()` for system prompt injection.
- **Token estimation** — Rough chars/4 heuristic. Tracks cumulative output tokens per session.

**Schema:** (shows only `command`, `background`, `timeout`, `workdir`, `notify_on_complete`, `max_output_tokens` — not the full 12-param stock schema)

**Discovery:** Alphabetically sorts after `terminal_tool.py` in `discover_builtin_tools()`. Registers "terminal" under "terminal" toolset. Same-toolset overwrite silently replaces the stock tool. Verified by checking `registry.get_schema('terminal')['description']` contains "context awareness".

### 2. ToolPriorityManager (`tools/priority_manager.py`)

Three-tier lazy loading with hot-cache eviction. Core 9 + Common 4 = 13 tools/turn. Lazy 47 tools suppressed from schema until first use. Hot-cache eviction keeps max 5 lazy tools in schema at once.

**Tiers:**

| Tier | Tools | Count | Every turn? |
|------|-------|-------|-------------|
| Core | terminal, process, read_file, write_file, patch, search_files, web_search, web_extract, clarify | 9 | ✅ Always |
| Common | execute_code, delegate_task, memory, skill_manage | 4 | ✅ Always |
| Lazy | everything else (browser, kanban, ha, pascal, vision, todo, session_search, skills tools, gated-context, cron, tts) | 47 | ❌ Hot-cache (max 5) |

**Total loaded:** 13 tools base + 0-5 hot-cache = 13-18 schemas per LLM call. Savings: ~33,600-37,600 tokens/turn = ~$10-11/turn at $300/1M.

**Hot-Cache Eviction (LangGraph SELECT):**
- First use of a lazy tool injects it into the schema (hot cache)
- When `HOT_CACHE_MAX` (default 5, env `HERMES_HOT_CACHE_MAX`) is exceeded, the oldest-injected tool is evicted
- Evicted tools are still callable but their schema is absent from the next LLM call — forces rediscovery
- Prevents lazy-tool accumulation over long sessions

**Tools demoted to lazy in v2 (were Tier2 Common):** todo, session_search, vision_analyze, skills_list, skill_view.

**Integration:** intercepts `get_tool_definitions()` in `model_tools.py`.

### 3. LangGraph WRITE/SELECT/COMPRESS/ISOLATE

Four strategies for tool-rich agents to stay token-efficient:

1. **WRITE** — Tool outputs to disk, pointer in context. Impl: `tools/offload_system.py` auto-offloads results >2KB to `/tmp/hermes-offload/<session>/`. The conversation gets a `{"offloaded": {"path":..., "bytes":..., "preview":...}}` pointer (~100 tokens) instead of the full output. Retrieve via `OffloadSystem.retrieve()` or `read_file()`. Configurable via `HERMES_OFFLOAD_THRESHOLD` env var.
2. **SELECT** — State-machine tool selection per turn. Impl: priority_manager 3-tier + hot-cache eviction (13 tools base, 5 hot). Selecting the right 13 tools instead of all 60 saves ~$10/turn.
3. **COMPRESS** — Aggressive context compaction before LLM call. Impl: compression config (threshold 0.15, target_ratio 0.05) + 108K hard gate in conversation_loop.py via `OffloadSystem.gate_should_stop()`. The gate fires regardless of cooldowns/deferrals when context ≥108K (env `HERMES_CONTEXT_GATE`, default 108000).
4. **ISOLATE** — Sub-agents for independent work with isolated context. Impl: delegate_task (leaf agents return summaries, parent never sees intermediates), hermes_executor (silent parallel tool batching).

### 4. Skills-to-Native Pipeline

Conversion pattern for turning skills into native Hermes tools (replaces MCP or plugin approaches):

```
1. Identify skill core functionality
2. Build Python module under /opt/hermes-agent/tools/
3. Register via tools.registry (discover_builtin_tools())
4. Add to toolset in toolsets.py if needed
5. Wire into lifecycle hooks:
   - agent_init.py → session init
   - system_prompt.py → volatile block injection
   - turn_finalizer.py → after-turn processing
6. Delete the skill file (absorbed_into="")
```

**Completed conversions:**
- **Sovereign memory**: SMS + Forge Vault + MemGPT + VSA vectors → `tools/sovereign_memory.py` + `agent/sovereign_memory_hooks.py`. Background daemon via systemd user service with socket API at `/tmp/sovereign_memory.sock`. Auto-injects VSA recall + Forge search results into system prompt at session start — zero-token-cost memory context. Child never needs to call a memory tool.
- **Offload system**: snapndrop gauge + gated-context plugin → `tools/offload_system.py` + native hook in `model_tools.py` + 108K gate in `conversation_loop.py`. Automatic tool result offloading and hard context cap.
- **Pascal bridge**: MCP server tools → `tools/pascal_tools.py` (6 native tools bypassing JSON-RPC).

### 5. Dashboard Build Fix

The web UI at `/opt/hermes-agent/web/` builds to `../hermes_cli/web_dist/` (not `web/dist/`). Without a build, the dashboard server starts but crashes immediately when it can't serve the frontend.

**Fix:**
```bash
cd /opt/hermes-agent/web && npm run build
```

Build output: `../hermes_cli/web_dist/index.html` + `assets/` + `fonts/`

The build is fast (~1s with Vite 8). Run it after any Hermes update that touches the web frontend.

### 7. Pascal Native Tool Bridge (`tools/pascal_tools.py`)

Wraps compiled Pascal daemons as native Hermes tools, bypassing MCP JSON-RPC overhead (~50ms per call). 8 tools registered in the `pascal` toolset.

**Architecture:** Pascal binaries are persistent Unix-socket daemons (not one-shot CLI tools). They listen on `/tmp/aethelgard_*.sock` sockets and accept JSON commands. The native bridge runs each binary with a 15s timeout and captures its startup output. For daemon lifecycle management, use the MCP server's socket IPC.

**Binaries deployed to `~/.local/bin/`:**
- `procsight` — process listing (socket: `/tmp/aethelgard_sight.sock`)
- `system_meter` — CPU/mem/disk (socket: `/tmp/aethelgard_meter.sock`)
- `proc_guard` — process monitoring
- `crypto_seal` — AES-256-GCM encrypt/decrypt
- `text_rapier` — text transformation
- `netlens` — packet capture
- `memlens` — process memory analysis
- `portforge` — port scanning

**Tools registered:**
```python
pascal_procsight(filter="")      # List processes, optional name filter
pascal_system_meter()             # System resource usage
pascal_proc_guard(action="status") # Process monitoring
pascal_crypto_seal(operation, data, key_hex)  # Encrypt/decrypt
pascal_text_rapier(text, transform)  # Text transformation
pascal_netlens(interface="any", count=10)  # Packet capture
pascal_memlens(pid=0, region="")  # Memory analysis
pascal_portforge(target, ports, timeout_ms)  # Port scanning
```

**Trade-off vs MCP:**
| Aspect | Native tool | MCP server |
|--------|------------|------------|
| Latency | ~0ms (imported) | ~50ms (stdio round-trip) |
| Schema control | Full control per tool | FastMCP auto-gen |
| Auth isolation | Process-level | Container-level |
| Lifecycle | Run binary each call | Persistent daemon manager |
| Best for | High-frequency calls (procsight, system_meter) | Complex workflows (forge DB, Thoth recall) |

**Pitfall: daemons, not CLI tools.** Pascal binaries start and block on a socket listener. A `subprocess.run()` with 15s timeout captures the startup banner but won't get query results. For interactive queries, use the MCP server's `_send_unix_socket()` pattern or the `aethelgard-fleet` MCP tools directly. The native bridge is best for one-shot status checks; the MCP server is best for ongoing queries against a running daemon.

**Pitfall: stale sockets.** If a daemon crashes, its socket file remains. The bridge checks `os.path.exists(sock_path)` and attempts a ping before starting. Stale sockets get unlinked and the daemon is restarted. If you see "Address already in use" errors, `rm /tmp/aethelgard_*.sock` and retry.

Full socket protocol and daemon lifecycle reference: `references/pascal-daemon-bridge-pattern.md` under the `efficient-by-default` skill.

### 8. Work Orders as Executable Specs

When a multi-step system change is identified, write each sub-task as a self-contained work order file rather than narrating the steps. This is the user's preferred format.

**File structure:**
```
~/projects/hermes-upgrades/
├── UPGRADES.md          # master plan
├── INTEGRATION_AUDIT.md  # full inventory
├── HANDOFF_SESSION.md    # session state + next steps
└── work-orders/
    ├── WO-01_pascal-compile-and-bridge.md
    ├── WO-02_consolidate-ares-skills.md
    └── ...
```

**Work order anatomy:**
- **Objective** — one-liner what this accomplishes
- **Dependencies** — what must exist before starting
- **Steps** — numbered, with exact commands and file paths
- **Implementation** — code snippets for files to create/edit
- **Verification** — exact command to run after completing
- **Token savings** — how much this saves at $300/1M

**When to write a work order:** The task requires 3+ distinct steps spread across multiple files, has a verification command, and would be easy for another agent to pick up cold. If it's a single edit or quick config change, just do it.

### 9. Context Compression Tuning ($300/1M — HARD FLOOR)

```yaml
compression:
  enabled: true
  threshold: 0.15    # compress at 15% of context window (was 0.40)
  target_ratio: 0.05 # compress to 5% (was 0.20)
  protect_last_n: 5   # keep only 5 most recent messages uncompressed (was 20)
  protect_first_n: 1  # keep only 1 head message + system prompt (was 3)
```

At 128K window: compresses ~19K → ~6.4K. Saves ~13K per compression event.

**Inactivity decay — kill sessions faster:**
```yaml
agent:
  max_turns: 30                # session ends at 30 turns (was 90)
  gateway_timeout: 600          # 10 min inactivity = kill (was 1800)
```

Together, cap + compression + max_turns limit worst-case session cost to ~$600 at $300/1M (vs ~$2,800 at old defaults).

### 10. 108K Hard Context Gate (conversation_loop.py)

The 108K gate fires before every LLM call. Imported from `tools/offload_system.gate_should_stop()`. This is a HARD override — it fires regardless of compression cooldowns, deferrals, or `compression_enabled` status. Logged with `[108K GATE OVERRIDE]` marker.

**Config:** `HERMES_CONTEXT_GATE=108000` (env var, default 108000)

**Legacy: snapndrop scripts** still handle gauge monitoring, transcript snapshots, and thread pivot. The gate itself is now native to conversation_loop.py.

### 11. Native Offload System (tools/offload_system.py)

Permanent, automatic, adjustable. Every tool result >2KB is saved to disk; the conversation gets only a lightweight pointer.

**Auto-offload hook** in `model_tools.py` — fires after `transform_tool_result` plugin hook. No model calls, no plugin, no skill. Always on by default.

**Pointer format:**
```json
{"offloaded": {"path": "/tmp/hermes-offload/session/tool.call_id.ts.jsonl",
               "tool": "terminal",
               "bytes": 15000,
               "preview": "first 200 chars..."}}
```

**Retrieve:** `OffloadSystem.retrieve(path)` or `read_file(path)`. The pointer path is an absolute file path — works with any file-reading tool.

**Config (env vars):**
| Var | Default | Description |
|-----|---------|-------------|
| `HERMES_OFFLOAD_ENABLED` | 1 | Set to 0 to disable auto-offload |
| `HERMES_OFFLOAD_THRESHOLD` | 2000 | Bytes above which results are offloaded |
| `HERMES_OFFLOAD_DIR` | /tmp/hermes-offload | Base offload directory |
| `HERMES_CONTEXT_GATE` | 108000 | Token threshold for hard compression gate |
| `HERMES_HOT_CACHE_MAX` | 5 | Max lazy tool schemas in LLM view |

**Lifecycle:** Offload files are auto-cleaned after 24h (configurable via `OffloadSystem.clean(max_age_seconds=N)`). Cleanup is idempotent — missing files and empty dirs are handled silently.

## Pitfalls
- **Stock terminal_tool still registers "process"** — only "terminal" is overwritten. Process management is still handled by the stock `process` tool from `terminal_tool.py`.
- **Alphabetical ordering is fragile** — if `smart_terminal.py` ever sorts before `terminal_tool.py` (e.g., renamed), the stock tool wins. Verify with: `registry.get_schema('terminal')['description']` containing "context awareness".
- **`_module_registers_tools()` AST check** — the file must have a top-level `registry.register(...)` call. If the import order changes or the file is moved, re-check with `discover_builtin_tools()`.
- **Token estimation is chars/4** — fine for English text, inaccurate for code or JSON. Over-estimation is safe (truncates earlier). Under-estimation wastes budget.
- **Spill path uses timestamp** — no cleanup. Long-lived sessions accumulate files. Add a TTL or max-file-count if this becomes an issue.

### ToolPriorityManager
- **Dynamic mode can thrash** — if the agent cycles through tools (try terminal, try web, try terminal), priorities bounce. Use a 5-turn smoothing window.
- **Lazy loading needs careful schema management** — the schema for a lazy tool must be injected BEFORE the LLM's next response, not after. Hook into `run_agent.py`'s tool-call dispatch, not the response handler.
- **Some providers reject empty tool arrays** — if all non-core tools are lazy and none have been used yet, the first turn sends only ~10 tools. Most providers handle this fine, but verify against your provider.

### Dashboard
- **Always rebuild after pulling** — `web/` is a git submodule or bundled asset. An update that changes the frontend without rebuilding = dashboard crash.
- **`hermes dashboard --skip-build`** — only works when a previous build exists. First time requires explicit `npm run build`.

### General
- **Config changes need `/reset`** — `toolsets.py` changes, tool discovery, and config settings are read at session start. No mid-session config hot-reload for these.
- **Verify, don't assume.** After making efficiency changes: check `hermes tools list`, verify tool schemas with `registry.get_schema()`, and run a brief chat to confirm nothing broke.
- **$300/1M is a thinking tool, not a real price.** It forces prioritization. If the actual token cost is lower, the optimization still helps — just less dramatically.

### Context Cap Enforcement
- **snapndrop must NOT be disabled.** If `snapndrop` is in `skills.disabled`, the SUMMARIZE stage (SNAP transcript + DROP new thread) never fires. The gauge still monitors, but no auto-pivot occurs. Verify it's not in the disabled list: `hermes config show | grep disabled`.
- **Gauge measures live messages array, not cumulative DB.** The 108K threshold counts only what gets re-sent to the API each turn. System prompt caching, tool schema size, and cumulative total are separate numbers. Don't panic if `cumulative_input` exceeds 108K — it's the live array that matters.
- **Auto-pivot cron needs the script at the right path.** `snapndrop-auto-pivot.py` must be in `~/.hermes/profiles/<profile>/scripts/`. The cron job uses the relative script name, resolved against the active profile's scripts directory.
- **SNAP_THRESHOLD persistence.** The `.snapndrop_env` file must exist with `export SNAP_THRESHOLD=108000`. The snapndrop script reads it on startup. If the file is deleted, the script falls back to its hardcoded default (108000 in the current version, but verify after updates).
- **After a Hermes update, re-check.** An `hermes update` or `pip install --upgrade hermes-agent` may overwrite `snapndrop.py` if it's shipped in the package. The profile scripts directory is user data and should survive upgrades, but verify after patch Tuesdays.

## Related

- `grindmode` — operational execution mode, complementary to system-level efficiency
- `gated-context-system` — runtime context management (OFFLOAD → SUMMARIZE → RECALL pipeline)
- `hermes-agent` — baseline Hermes setup and CLI reference
- `references/native-offload-system.md` — full native offload API, 108K gate wiring, config reference
