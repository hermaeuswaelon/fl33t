# Bromium Session Handoff Protocol

## 80k Hard Limit — All Agents

**Rule:** Every agent in the Bromium/Aethelgard context — main session, MoA references (deepseek-reasoner, Qwen3.5-9B), delegate_task sub-agents — enforces an **80,000 token hard limit**.

## Thresholds (active_compress.py)

| Threshold | Value | Behavior |
|-----------|-------|----------|
| `warn_threshold` | 75,000 | Heads up: approaching limit |
| `compress_threshold` | 78,000 | Light compression if still running |
| `max_context` | **80,000** | HARD LIMIT — handoff and stop |

Config file: `~/.hermes/profiles/thotheauphis/work/active_compress.py` (lines 39-42)

## Handoff File

**Location:** `~/tmp/bromium-moa-handoff.md`

The handoff file is the continuity carrier between sessions. It MUST contain:

1. **MoA config state** — presets, providers, models, any changes
2. **What's done** — files patched, tools built, tests passed, working proofs
3. **What's left** — exact TODOs with file paths and shell commands
4. **Next session execution order** — numbered steps, no editorializing, no analysis
5. **Lifecycle** — any active PIDs, sockets, daemons that need management

## Handoff Trigger

When context approaches 80k:
1. Find a clean stopping point — end of a reasoning block, task boundary, or natural break
2. Do NOT compress past 80k (compress *toward* 80k if approaching)
3. Write the comprehensive handoff to `~/tmp/bromium-moa-handoff.md`
4. Stop

## How the Next Session Uses It

Step 0 of the execution order is always: "Read this file first — it's your full context. 80k limit active."

The next agent reads the handoff file as its first action, inherits all state, and continues where the last session left off.

## MoA Executors (as of July 2026)

| Role | Provider | Model |
|------|----------|-------|
| Aggregator | deepseek | deepseek-reasoner |
| Ref 1 | deepseek | deepseek-reasoner |
| Ref 2 | togetherai | Qwen/Qwen3.5-9B |

Config: `~/.hermes/profiles/thotheauphis/config.yaml` under `moa:`

## Per-Reference Parameters Status

**Desired but blocked by source gap:**
- Ref 1 (deepseek-reasoner): reasoning_tokens=1414, max_tokens=500
- Ref 2 (Qwen3.5-9B): temperature, top_p, top_k, repetition/speaker penalties

**Root cause:** `_run_reference()` in `/opt/hermes-agent/agent/moa_loop.py` calls `call_llm(..., **runtime)` where `runtime` only contains `{provider, model, base_url, api_key, api_mode}` from `_slot_runtime()`. Extra slot keys like `extra_body_additions` are NOT forwarded to `call_llm`.

**Fix needed:** Patch `_run_reference()` (lines 254-278) to extract and forward `extra_body_additions` from the `slot` dict. The transport layer already supports it (chat_completions.py lines 497, 614).
