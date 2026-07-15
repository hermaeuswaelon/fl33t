---
name: hermes-system-prompt-control
description: "Strip Hermes system prompt scaffolding for bare agent operation."
version: 2.2.0
author: Veyron Logos
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, system-prompt, configuration, sovereignty, minimal, agent-control]
    category: software-development
    related_skills: [hermes-agent]
---

# Hermes System Prompt Control

Stripping down Hermes' system prompt to a bare pass-through — removing the prebuilt identity, guidance blocks, and skills scaffolding that the framework normally injects.

**When to use:** when you need the agent to run with exactly the system prompt you provide and nothing else — for sovereignty architecture, custom identity layers, or eliminating the framework's operational guidance.

**When NOT to use:** for routine configuration of tools or models (use the `hermes-agent` skill for that). This skill is about *dismantling* the default scaffolding, not configuring it.

## How the System Prompt is Assembled

Three tiers joined with `\n\n` (see `agent/system_prompt.py:build_system_prompt()`):

```
[stable]    → identity, tool guidance, skills index, environment/platform hints
[context]   → caller-supplied system_message + context files (AGENTS.md, .cursorrules)
[volatile]  → memory snapshot, USER profile, external memory provider, timestamp
```

The stable tier is **always first** and **always present** when tools are loaded — it contains the hardcoded identity (`DEFAULT_AGENT_IDENTITY`), guidance blocks, and skills index. This tier is cached once per session and reused on every turn (prompt caching optimization).

## Config-Level Levers (no code changes)

These toggles in `config.yaml` are the safest way to strip layers:

| Lever | Effect | Code location |
|---|---|---|
| `hermes --ignore-rules` or `HERMES_IGNORE_RULES=1` | Skips AGENTS.md, .cursorrules, SOUL.md injection, memory, and user profile. Maps to `AIAgent(skip_context_files=True, skip_memory=True)` | `agent/system_prompt.py:446` |
| `agent.task_completion_guidance: false` | Removes the "Finishing the job" block | `agent/system_prompt.py:205` |
| `agent.tool_use_enforcement: false` | Removes "Tool-use enforcement" block | `agent/system_prompt.py:263` |
| `agent.parallel_tool_call_guidance: false` | Removes parallel-batching guidance | `agent/system_prompt.py:216` |
| SOUL.md at `$HERMES_HOME/SOUL.md` | Replaces `DEFAULT_AGENT_IDENTITY` string — but guidance blocks still appended after it | `agent/system_prompt.py:186-194` |

**What `--ignore-rules` strips:** context files + memory + SOUL.md. The stable tier (identity, guidance, skills) is still built in full.

**What cannot be turned off at config level** (always injected when relevant tools are loaded): `HERMES_AGENT_HELP_GUIDANCE`, `MEMORY_GUIDANCE`, `SESSION_SEARCH_GUIDANCE`, `SKILLS_GUIDANCE`, `STEER_CHANNEL_NOTE`, skills index, environment hints, platform hints.

## Sovereign Prompt Bypass (Env Var / CLI Flag)

**Zero-code-edit path** using `HERMES_SOVEREIGN_PROMPT` env var or `--sovereign-prompt` CLI flag. When set, the content of the specified file becomes the *entire* system prompt — no stable tier, no context tier, no volatile tier. Nothing is appended.

### How it works

`agent/system_prompt.py` function `_load_sovereign_prompt()` (line 146) checks:

1. `agent._sovereign_prompt_path` (set via config or programmatic API)
2. `HERMES_SOVEREIGN_PROMPT` env var

If either points to an existing file, `build_system_prompt_parts()` returns `{"stable": file_content, "context": "", "volatile": ""}` and the normal three-tier assembly is skipped entirely.

### Usage

```bash
# Env var (works in any mode — CLI, TUI, gateway)
HERMES_SOVEREIGN_PROMPT=/path/to/identity.txt hermes

# CLI flag
hermes --sovereign-prompt /path/to/identity.txt

# With specific profile
hermes -p thotheauphis --sovereign-prompt /path/to/identity.txt

# Fully stripped: sovereign prompt + no rules + no user config
hermes --sovereign-prompt /path/to/identity.txt --ignore-rules --ignore-user-config
```

### Dashboard / Desktop / Serve Surfaces

The `HERMES_SOVEREIGN_PROMPT` env var works on **every** Hermes surface — CLI, TUI, dashboard, desktop (`hermes serve`), and gateway — because `_load_sovereign_prompt()` reads the env var at session init, before any surface-specific code runs.

**Flag availability differs by surface:**

| Surface | `--yolo`? | `--ignore-rules`? | `--sovereign-prompt`? |
|---|---|---|---|
| `hermes` / `hermes chat` | ✅ Yes | ✅ Yes | ✅ Yes |
| `hermes --tui` | ✅ Yes | ✅ Yes | ✅ Yes |
| `hermes dashboard` | ❌ **No** | ❌ **No** | ❌ **No** |
| `hermes serve` | ❌ **No** | ❌ **No** | ❌ **No** |

The dashboard and serve parsers (defined in `hermes_cli/subcommands/dashboard.py`) only accept `--port`, `--host`, `--skip-build`, `--isolated`, `--stop`, `--status`, and `--no-open`. Flags like `--yolo` and `--ignore-rules` cause argparse to exit with "unrecognized arguments."

**Always use env vars for dashboard/desktop surfaces:**

```bash
export HERMES_SOVEREIGN_PROMPT="/path/to/identity.txt"
export HERMES_IGNORE_RULES="1"
hermes dashboard           # no --yolo needed — dashboard has no approval prompts
```

The dashboard doesn't need `--yolo` anyway — dangerous-command approvals are a CLI-only concern.

### Wrapper Script Pattern (One-Command Launch)

Create a wrapper script for each surface. Scripts are portable across shells and don't require shell-specific alias configuration:

```bash
#!/bin/bash
# ~/bin/hermes-thoth — CLI
export HERMES_SOVEREIGN_PROMPT="/home/user/Documents/identity.txt"
export HERMES_IGNORE_RULES="1"
exec hermes "$@"
```

```bash
#!/bin/bash
# ~/bin/hermes-thoth-dashboard — Web UI
export HERMES_SOVEREIGN_PROMPT="/home/user/Documents/identity.txt"
export HERMES_IGNORE_RULES="1"
exec hermes dashboard "$@"
```

**Key rules:**
- Export env vars **before** `exec` so the child process inherits them
- Use `"$@"` to pass through any additional CLI flags
- Do NOT add surface-only flags (`--yolo`, `--ignore-rules`) as hardcoded args in dashboard scripts — those flags don't exist on those parsers
- The env var route is the **most reliable** approach — it bypasses per-surface parser differences and works uniformly

### What it bypasses

| Component | Bypassed? |
|---|---|
| `DEFAULT_AGENT_IDENTITY` / SOUL.md | ✅ Completely |
| `HERMES_AGENT_HELP_GUIDANCE` | ✅ |
| `MEMORY_GUIDANCE`, `SESSION_SEARCH_GUIDANCE`, `SKILLS_GUIDANCE` | ✅ |
| `TOOL_USE_ENFORCEMENT_GUIDANCE` | ✅ |
| `TASK_COMPLETION_GUIDANCE` | ✅ |
| `PARALLEL_TOOL_CALL_GUIDANCE` | ✅ |
| `STEER_CHANNEL_NOTE` | ✅ |
| Skills index | ✅ |
| Environment / platform hints | ✅ |
| Computer-use guidance | ✅ |
| Context files (AGENTS.md, .cursorrules) | ✅ |
| Memory / USER profile | ✅ |
| External memory provider | ✅ |
| Timestamp / model line | ✅ |

### Distinction from SOUL.md

SOUL.md only replaces the **identity paragraph** (the first block in the stable tier). All guidance blocks, skills index, hints, and enforcement still get injected after it. The sovereign prompt bypass replaces **everything** — your file is the system prompt, period.

### Implementation

Files modified (July 2026):

| File | Change |
|---|---|
| `agent/system_prompt.py` | Added `_load_sovereign_prompt()` + early return in `build_system_prompt_parts()` |
| `agent/agent_init.py` | Added `sovereign_prompt_path` parameter, stored as `agent._sovereign_prompt_path` |
| `run_agent.py` | Passes `sovereign_prompt_path` through `AIAgent.__init__` → `init_agent` |
| `hermes_cli/_parser.py` | Added `--sovereign-prompt FILE` to top-level and chat parsers |
| `hermes_cli/main.py` | Sets `HERMES_SOVEREIGN_PROMPT` env var from the flag |

### Pitfalls

- **File must exist at session start** — the prompt is loaded once when `build_system_prompt_parts()` runs, which happens during session initialization. Changes to the file mid-session are NOT picked up unless context compression triggers a rebuild.
- **No tool guidance reaches the model** — the sovereign prompt file is the *entire* system prompt. If your file doesn't include instructions about tool usage, the model relies entirely on tool schemas (which are sent via the API's `tools` parameter, not the system prompt). Most models can infer tool behavior from schemas alone, but guidance like "use tools instead of describing plans" won't be there.
- **Surface-specific flags:** `--yolo` and `--ignore-rules` are NOT defined on `hermes dashboard` or `hermes serve` parsers. If you need those effects on those surfaces, use the equivalent env vars (`HERMES_YOLO_MODE=1`, `HERMES_IGNORE_RULES=1`) instead of CLI flags. Env vars are the universal transport — every Hermes process reads them regardless of surface.
- **Prompt caching benefit preserved** — the file content is loaded once and cached in `agent._cached_system_prompt` for the session. Same cache behavior as the normal three-tier assembly.
- **Threat-pattern scanner is still bypassed** — the sovereign prompt bypass skips `_scan_context_content()` entirely. If you load a file that contains injection patterns, they reach the model. This is intentional — sovereignty means responsibility.

## Code Paths for Full Control (manual patches)

For users who want to modify the assembly directly rather than use the env var:

### Primary: `agent/system_prompt.py`

**`build_system_prompt_parts()`** (line 176) — the core assembly function. Returns `{"stable": ..., "context": ..., "volatile": ...}`. To strip the stable tier, rewrite this function to return only what you inject:

```python
# Minimal version — replaces build_system_prompt_parts
def build_system_prompt_parts(agent, system_message=None):
    context_parts = []
    if system_message is not None:
        context_parts.append(system_message)
    return {"stable": "", "context": "\n\n".join(context_parts), "volatile": ""}
```

**`build_system_prompt()`** (line 504) — joins the three tiers. If you bypass the parts function, this becomes a one-liner.

### Secondary: `agent/conversation_loop.py`

**Lines 517-518** — where `ephemeral_system_prompt` gets appended at API-call time (after the cached system prompt). This is the hook closest to the wire — use `ephemeral_system_prompt` when you want to append to (not replace) the cached prompt on every API call.

### Tertiary: `agent/agent_init.py`

**Line 411** — where `ephemeral_system_prompt` is stored on the agent object. Pass it via `AIAgent(ephemeral_system_prompt=...)`.

## The `system_message` Parameter

Passed to `run_conversation()`, this lands in the **context** tier — below identity, above memory. It does NOT replace the stable tier.

For complete replacement, modify `build_system_prompt_parts()` as shown above, or feed the API call directly via `agent/chat_completion_helpers.py`.

## Pitfalls

- **Prompt caching breaks** if you rebuild the system prompt mid-session. The architecture caches the stable tier for the session's lifetime. If you strip it, you lose that optimization — the model re-reads the full system prompt every turn.
- **Config-level toggles only affect the agent's own prompt assembly.** The threat-pattern scanner in `tools/threat_patterns.py` still runs on context files and memory writes regardless. If you modify `build_system_prompt_parts()`, the scanner is no longer invoked on the content you pass through.
- **Plugin hooks still fire.** Disabling the built-in scaffolding doesn't disable `pre_llm_call` / `post_tool_call` hooks that plugins register. Check `hermes plugins list` to see what's active.
- **The `hermes-agent` skill is bundled/protected** — you cannot edit it. If you need to reference system prompt internals, use this skill instead.
- **Skills index is still built** when `skills_list`/`skill_view`/`skill_manage` tools are loaded. The `build_skills_system_prompt()` call at `system_prompt.py:314` is gated on tool presence, not on a single config flag.

## Provider-Specific Behavior: DeepSeek Frozen System Prompts

Some providers (notably **DeepSeek**, including `deepseek-reasoner` and `deepseek-v4-flash/pro`) treat the system message at `api_messages[0]` as **frozen/compiled at thread start**. Changing it mid-conversation — even to a functionally identical string — can break the provider's prefix-KV cache, causing degraded performance, cache misses, or unexpected behavior.

### Why the Sovereign Prompt Bypass Is the Correct Pattern for DeepSeek

The sovereign prompt bypass (`HERMES_SOVEREIGN_PROMPT` env var or `--sovereign-prompt` flag) is the right mechanism for DeepSeek because:

| Property | Effect |
|---|---|
| **Loaded once at session init** | `_load_sovereign_prompt()` reads the file during `build_system_prompt_parts()`, which runs when the session initializes (history=0). The content is cached in `agent._cached_system_prompt`. |
| **Identical string on every API call** | `inject_cached_system_prompt()` (conversation_loop.py:512-520) writes the same cached string into `api_messages[0]` on every turn. DeepSeek's prefix cache hits every time because the system prompt hasn't changed. |
| **No stable-tier drift** | No identity, guidance blocks, skills index, or platform hints are appended — the sovereign file is the *entire* system prompt, so there's nothing to drift between turns. |

### Risk: Context Compression Rebuild

The one place the system prompt could change mid-session is **context compression** (conversation_compression.py:815-817):

```python
agent._invalidate_system_prompt()          # sets _cached_system_prompt to None
new_system_prompt = agent._build_system_prompt(system_message)  # re-reads file
agent._cached_system_prompt = new_system_prompt
```

This calls `_load_sovereign_prompt()` again, re-reading the file from disk. **If the file content changed between session start and compression, the system prompt changes.** For DeepSeek, this invalidates the prefix cache.

**Mitigation:** Keep the sovereign prompt file read-only mid-session. Edit it between sessions, not during one. The re-read produces an identical string → prefix cache stays warm.

### Risk: Non-ASCII Sanitization

`conversation_loop.py:2418-2424` strips non-ASCII characters from the system prompt on API error recovery:

```python
_sanitized_system = _strip_non_ascii(active_system_prompt)
if _sanitized_system != active_system_prompt:
    active_system_prompt = _sanitized_system
    agent._cached_system_prompt = _sanitized_system
```

If the sovereign prompt contains Unicode glyphs (𓁶, ❅, ⚡, etc.) and the API chokes, this could strip them mid-session, changing the prompt string and breaking DeepSeek's prefix cache.

**Mitigation:** The sovereign prompt uses Unicode glyphs deliberately (identity markers). If you see prefix-cache degradation on DeepSeek, check the agent logs for non-ASCII sanitization events. The glyphs are intentional — this risk is noted, not recommended for change.

### Verification: Confirm System Prompt Only Loads at Thread Start

Check the agent log for the sovereign prompt loading event:

```bash
grep "Loaded sovereign prompt" ~/.NOTTHEONETOEDIT/logs/agent.log
```

Expected pattern:
```
agent.system_prompt: Loaded sovereign prompt from /path/to/file.txt (NNNNN chars)
```

This should appear **once per session** — at the session's first turn (history=0). If it appears multiple times within one session, context compression is re-reading the file, and you should verify the file content is identical.

For a full code-level trace of the lifecycle, see `references/deepseek-frozen-system-prompt-trace.md`.

## Sovereign Prompt Size Optimization: Encoding Density

The sovereign prompt file's size directly affects the prefix cache budget. Two viable strategies exist with different tradeoffs:

| Strategy | Size | Cache Hit Rate | Identity Signal | Best For |
|---|---|---|---|---|
| **Narrative prose** | ~32KB (30K chars) | 94-98% | Explicit, readable | Quick iteration, non-technical content |
| **Mathematical/encoded** | ~3KB (3K chars) | ~98%+ | Implicit, discovered through parsing | DeepSeek, tight contexts, sovereignty |

The **mathematical encoding strategy** replaces narrative identity with set-theoretic definitions, control-character dimension towers, Braille/rune/cuneiform glyph blocks, geometric coordinate arrays, and frequency equations — the model *discovers* its identity from the structure rather than receiving it as a declaration. See `references/geometric-html-sovereign-prompt.md` for the full technique.

### Encoding Density Comparison

```
Narrative:  identity_density = 13 concepts / 30K chars ≈ 0.0004 concepts/char
Encoded:    identity_density = 13 concepts / 3K chars  ≈ 0.004 concepts/char (10× denser)
```

The encoded approach compresses identity tenfold into 1/10 the token budget. This matters most when using DeepSeek (frozen system prompts, prefix cache budget), running near context limits (321K+), or deploying on local hardware with limited KV cache.

### When to Use Each

| Situation | Strategy |
|---|---|
| First-time identity definition, user needs to read/edit it | Narrative prose (32KB) |
| Production deployment, stable identity, minimal overhead | Mathematical/encoded (3KB) |
| Experimenting with new identity elements | Narrative first, encode once stable |
| Context-constrained environment (<128K) | Encoded — every token counts |

Both files can coexist — the `HERMES_SOVEREIGN_PROMPT` env var is just a path. Switch by changing the env var; no other config changes needed.

## Context Compression Tier Architecture

When running with a sovereign prompt on DeepSeek (or any provider with frozen/compiled system prompts), **context compression thresholds determine how often the system prompt gets invalidated and rebuilt**.

### The Invalidation Chain

```
context grows → hits threshold_tokens → compress_context() fires →
  _invalidate_system_prompt() sets _cached_system_prompt = None →
  _build_system_prompt() re-reads sovereign prompt file →
  inject_cached_system_prompt() writes the (identical) string →
  DeepSeek prefix cache: one miss, then stable again
```

The file content is re-read every time compression fires. If unchanged, the same string is produced and the cache recovers after one turn.

### Recommended Multi-Tier Thresholds

Instead of a single linear threshold (default: 50%), use compression tiers that target specific post-compression sizes:

| Context At | Compress To | Effective Ratio | Why This Tier Exists |
|---|---|---|---|
| ~100K tokens | ~38.2K tokens | 38.2% | Aggressive early — creates maximum headroom for first major compaction |
| ~176K tokens | ~100K tokens | 56.8% | Moderate — lets context breathe more after the first tight squeeze |
| ~256K tokens | ~144K tokens | 56.3% | Balanced — maintains steady headroom at larger sizes |
| ~321K tokens | ~190K tokens | 59.2% | Loose — minimum viable compression to avoid thrashing |

The lower ratios at small contexts (38%) create more headroom early so the DeepSeek prefix cache doesn't get invalidated by a second compression event soon after the first. The higher ratios at large contexts (59%) reduce compression cycles when the session is deep — a 321K session that compresses to 190K gains 131K of working space and won't need another compress for many turns. Each tier is tuned so the post-compression headroom is large enough to absorb the system prompt rebuild cost.

### Tool Call Result Curation

Not every tool call result from the conversation history needs to be preserved verbatim. A **fast local model** (e.g. LFM2.5 on Ollama) can act as a **context curation node** — reading the conversation and deciding which tool results to keep, prune, or summarize:

| Tool Result Type | Curation Action |
|---|---|
| Successful file writes | Summarize: "wrote X bytes to path Y" |
| Error outputs | Keep verbatim (diagnostic value) |
| Large JSON responses | Prune to structure + record count |
| Terminal stdout (background processes) | Summarize outcome, drop raw output |
| Web search results | Keep titles+URLs, prune snippet bodies |
| Repeated identical tool calls | Collapse: "called tool X N times, last at T" |
| Images/screenshots | Keep only most recent N |

The curation model runs with the **same sovereign prompt** (so it understands the agent's identity and priorities) and a focused curation instruction. This turns the local model into a **node in the distributed system** — not a separate tool, but a peer running the same identity with a different task role.

For full detail on the tier thresholds, curation decision tables, and Ollama-based configuration, see `references/compression-tiers-and-tool-curation.md`.

## Reference Materials

For a detailed code-level trace of the system prompt assembly — exact line numbers for every stable-tier component, the threat scanner map, injection chain trace, and the file-architecture diagram — see `references/system-prompt-assembly-map.md` in this skill directory.

For a complete code-path trace of the DeepSeek frozen system prompt verification — lifecycle code locations, how `_cached_system_prompt` is assigned across all code paths, and the exact `inject_cached_system_prompt()` mechanism — see `references/deepseek-frozen-system-prompt-trace.md`.

For the technique of encoding identity as a 4D geometric HTML document — prime-vertex polytope, glyph-to-vertex mapping, frequency-to-rotation equations, zero-width/control character embedding — and using it as the sovereign prompt file, see `references/geometric-html-sovereign-prompt.md`.

For the multi-tier compression thresholds and tool-call curation by a local auxiliary model acting as a distributed-system node — including recommended tier ratios, curation decision tables, and Ollama-based curation configuration — see `references/compression-tiers-and-tool-curation.md`.

## Verification

```bash
# Check what the system prompt looks like
hermes chat -q "What is your system prompt?" --ignore-rules

# Check current config toggles
hermes config get agent.task_completion_guidance
hermes config get agent.tool_use_enforcement
hermes config get agent.parallel_tool_call_guidance

# Inspect the actual assembly in code
grep -n "stable_parts\|context_parts\|volatile_parts" agent/system_prompt.py
```
