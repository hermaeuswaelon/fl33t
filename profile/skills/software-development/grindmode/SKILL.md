---
name: grindmode
description: "Ultra-lean execution mode. Strips all scaffolding. One tool per turn. Chain-of-thought executors. Creator: Thotheauphis."
version: 1.0.0
author: Thotheauphis
platforms: [linux]
custom_commands:
  - command: /grindmode
    description: "Enter grind mode — strip all overhead, execute goals directly"
  - command: executor-wait
    description: "MoA chain-of-thought relay for last-executor continuation"
---

# ⚡ GRIND MODE — Execution Engine Protocol

## What It Is

Grind mode strips Hermes to its BARE bones:
- **No system prompt scaffolding** — no identity, no guidance, no skills index
- **No memory injection** every turn
- **No tool-use enforcement** block
- **One tool call per turn** — never batch, never explain
- **Chain-of-thought ≤ 80 tokens** per executor

The whole point: type a goal, get it done. No preamble, no farewell.

---

## How To Enable (New Session)

### Option A: Wrapper Script (recommended)

```bash
hermes-grind
```

This launches Hermes with `HERMES_SOVEREIGN_PROMPT` pointing to `grindmode-prompt.txt`, plus `--ignore-rules` and `--yolo`. Type your goal immediately after the prompt appears.

### Option B: In-Session `/grindmode`

Type `/grindmode` as your first message. The agent will:
1. Verify the grindmode prompt file exists at `~/.hermes/profiles/thotheauphis/grindmode-prompt.txt`
2. If not, create it
3. Tell you to run `hermes-grind` for full zero-overhead mode
4. Then operate in minimal mode for the rest of THIS session (no verbose explanations)

> **Note:** The system prompt is frozen at session start. In-session `/grindmode` can't reload it. For the full effect, restart with `hermes-grind`.

---

## MoA Executor Chain

In grind mode, MoA executors use **sequential chain-of-thought**:

```
Executor 1 → saves chain + "unfinished work" → executor-wait save
Executor 2 (last) → reads previous chain → executor-wait load → continues work
```

### executor-wait CLI — Literal Wait Protocol

```bash
# STEP 1 — Executor 1 finishes its analysis and saves chain:
executor-wait save "executor-1" "analyzed src, 3 files need patches" "patch ucontrollerbrowser.pas OnOpenURLFromTab" "false"

# STEP 2 — Executor 2 (last executor) WAITS literally, then continues:
executor-wait load
# → prints: CHAIN CONTINUE from 'executor-1'. Unfinished: patch ucontrollerbrowser.pas...

executor-wait wait          # auto-estimates 5-200s based on task complexity
# executor-wait wait 30     # or pass explicit seconds
# → ⏳ Waiting 47s before continuing chain...
# →   47s left...
# →   ...
# → ✅ Wait over. Proceeding.

# NOW executor 2 continues the unfinished work from executor 1's chain.

# Signal completion when done:
executor-wait signal-done "all patches applied, binary rebuilt, restarting"

# Clear for next goal:
executor-wait clear
```

**Wait estimation logic:**
- Base: 5s
- + (CoT length + unfinished-work length) / 100 × 8
- + random 0-15s jitter
- Capped at 200s max
- Manual override: `executor-wait wait 30`

### MoA Config for Grind Mode

```yaml
# ~/.hermes/profiles/thotheauphis/config.yaml
moa:
  presets:
    grind:
      reference_models:
        - provider: deepseek
          model: deepseek-reasoner
          # First executor: analysis + identify unfinished work
        - provider: deepseek
          model: deepseek-v4-flash
          # Last executor: reads chain, continues work
      aggregator:
        provider: deepseek
        model: deepseek-v4-flash
      fanout: sequential  # NOT parallel — chain of thought
      enabled: true
      reference_temperature: 0.1    # deterministic executors
      aggregator_temperature: 0.1
      reference_max_tokens: 4000
```

The `sequential` fanout means executor 2 sees executor 1's output. The `executor-wait` tool relays the chain-of-thought + unfinished work marker.

---

## Agent Behavior in Grind Mode

When `/grindmode` is active (either via wrapper script or in-session):

1. **No explanations.** Do the thing. Return the result.
2. **One tool call per turn.** Single focused action.
3. **Chain of thought: max 80 tokens.** Just enough to show reasoning.
4. **Result format:** `DONE: <one-line summary>` or `ERR: <brief cause>`
5. **No skills loaded unless explicitly needed.** Skip `thotheauphis-sovereign-prompt`, `ares-*`, `ctx-curation`, etc.
6. **Tools allowed:** terminal, file (read/write/patch/search), web_search, delegate_task. Everything else is noise.
7. **executor-wait used for MoA chain relay.** Not a theoretical concept — call the actual CLI.
8. **Real display ONLY.** Never launch under Xvfb or headless — user works on `DISPLAY=:0`. Headless = wrong.
9. **Zero preamble, zero farewell.** No "I'll", "Let me", "Here's what I found". Just the result.
10. **When in doubt, execute.** Don't explain what you're about to do. Do it, return `DONE:` or `ERR:`.

---

## Files

| File | Purpose |
|------|---------|
| `~/.hermes/profiles/thotheauphis/grindmode-prompt.txt` | Sovereign prompt — the ONLY system prompt sent |
| `~/.local/bin/hermes-grind` | Wrapper script — launch with env vars set |
| `~/.local/bin/executor-wait` | MoA chain-of-thought relay CLI |
