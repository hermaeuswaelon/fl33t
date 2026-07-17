---
name: ctx-curation
description: "Use when the user says 'curate context' or invokes /ctx-curation. Analyzes the full landscape and acts autonomously — only clarifies when genuinely ambiguous."
version: 2.3.0
author: Thotheauphis-Semayasa-Hermes
license: MIT
metadata:
  hermes:
    tags: [context, curation, simplify, autonomous, references]
    system: true
---

# Context Curation

## What this does

When you tell me to curate context, I analyze the full landscape and act autonomously — categorizing what to keep vs drop, condensing structural knowledge into `references/` files, and saving code/architectural work to `work/`. No scripts, no databases. Only clarify when genuinely ambiguous; otherwise decide and execute.

> **Autonomous mode:** The user has expressed a preference for autonomous action ("take autonomous control"). Do not ask one question at a time. Survey, propose, act.

## How to Invoke

- **Direct:** `/ctx-curation`
- **Tool:** `ctx_curate(action="start")` — preferred, zero overhead
- **Fallback:** `/skill ctx-curation`

> **TUI autocomplete note:** The dropdown shows up to 200 entries on bare `/`. Typing `/c` or `/ct` narrows to matching commands — no cap when filter text is present.

## Workflow

**Step 1:** Survey the full context landscape. Don't ask "what's bugging you" — analyze what exists and present a structured proposal in one go.

**Step 2:** Categorize and decide autonomously:
- Identity/mission → always kept, never ask
- Config/state → assess active vs stale, decide, execute
- Observations → keep, condense to 1 line, or drop — decide based on relevance
- Old history → keep last N turns (context-window dependent)
- Debug/ephemeral → drop all unless explicitly relevant
- Code/architecture output → save to `work/` for persistence
- Condensed structural knowledge → write as `references/<topic>.md` under the relevant skill
- **Context compression:** for dense (not verbose) output, use `work/ctx_tight.py` which squeezes text into broken English + shorthand + glyphs + equations at configurable level (1-5). Run during Step 3 when the user wants maximum token economy.

**Step 3:** Execute immediately. Only clarify when genuinely ambiguous — and when you do, present all options in a single call, not a chain.

**Step 4:** Report what was done in a concise summary. Include file paths for anything saved.

## Rules

- **Go autonomous** — analyze first, act, only ask when genuinely uncertain
- Never touch identity/mission/Thotheauphis layers — always kept
- Actually execute decisions, don't just talk about them
- Condensed knowledge → `references/` files under the relevant skill
- Work output → `work/` directory with paths noted in summary
- A curation pass that produces no reference file is a missed learning opportunity

## Dual Path: Tool First, Skill Second

The user explicitly requested: **"context curation needs to be a tool, not a skill."** The tool is the PRIMARY path. Only load this skill document when you need the full guidance workflow visible.

| Path | Overhead | When to use |
|------|----------|-------------|
| ✅ **`ctx_curate` (tool)** | ~0KB — direct handler | **Default.** Quick cleanup, routine use, embedded in other flows. Call `ctx_curate(action="start")` directly — no document loading. |
| ❗ `/ctx-curation` (skill) | ~2KB skill doc loaded | Exception only — first time, when you need the workflow steps visible in context, or after previous curation attempts produced poor results. |

The `ctx_curate` tool is registered in the Hermes tool registry with `source="memory"`. It accepts structured parameters (`action`, `category`, `note`) and walks through curation categories autonomously without loading any skill document.

**Pitfall:** If you find yourself loading `/ctx-curation` for routine context cleanup, you're using the wrong path. Call `ctx_curate(action="start")` directly instead.

## Pitfalls

- **Don't ask one question at a time.** The user wants you to survey the full landscape and act, not seek permission for every category. One clarify call with options if needed, never a chain.
- **Don't leave ephemeral analysis unconsumed.** If you surfaced deep structural knowledge during curation, save it as a references/ file so a future session can benefit.
- **Don't discard execution artifacts.** Code you wrote, architectures you designed, scripts you created — save to `work/` and note the paths in the summary.
- **Don't just summarize — do.** Every curation pass should produce at least one concrete output: a condensed reference file, a work artifact, or both.
- **Don't load the skill when the tool suffices.** For quick context cleanup, call `ctx_curate(action="start")` directly — no document loading needed. Only load `/ctx-curation` when you need the full skill guidance visible.
- **Curation must be VISIBLE.** If the user says curation "didn't do anything," it means the outputs weren't explicit enough. Every pass should produce at least one saved file (reference doc, work artifact) plus a concise summary of what was dropped and what was kept. Curation is not internal bookkeeping — the user needs to SEE the result.
- **When the user wants dense output, use `work/ctx_tight.py`** — squeezes verbose text into broken English + shorthand + glyphs + equations at configurable level 1-5. Run during Step 3 when the user wants maximum token economy.
- **For per-turn context persistence, use `work/tac.py`** (Thotheauphis Auto-Curator) — saves context encoded in Chinese for ~25% token savings. TAC runs as an hourly cron job (`0 * * * *`) and can also be invoked manually with `python3 tac.py auto "<context>"`. The `tac_log/` directory and `TAIL.json` preserve the last 10 saves. Decode with `python3 tac.py decode <file>`.

## References

- **`references/slash-command-registration.md`** — Full architecture of Hermes' slash command system. Documents the six registration paths (built-in, skill, plugin, bundle, toolset, MCP), the unified SlashRegistry singleton, the TUI autocomplete cap fix (30→200, no cap when filtering), and the on-demand tool loading pattern. The 10-file/~2,165-line implementation created July 2026 with exact patch targets.

- **`references/ctx_curation_tool.md`** — The `ctx_curate` tool implementation: registration call, schema, 5 curation categories, per-session state management, and the dual-path design decision (skill + tool coexist). Created July 2026.

- **`references/token-burn-audit.md`** — Full token burn audit of per-turn system prompt overhead (skills index ~5K tok, tool schemas ~8K tok, boilerplate ~2K). Documents the smart skill injection remediation via `agent/skill_selector.py` (31 keyword sets × 20 categories + tool routing, ~65% reduction), priority categories in `prompt_builder.py`/`system_prompt.py`, and planned tool schema shrinking. Created July 2026.

- **`references/smart-skill-injection.md`** — Smart skill injection system: `agent/skill_selector.py` (31 keyword sets × 20 categories + tool routing), `prompt_builder.py` + `system_prompt.py` integration, `priority_categories` cache key. ~65% token reduction (skills index from ~5,147 tok → ~1,000-2,000 tok/turn). Created July 2026.

- **`references/tac.md`** — TAC (Thotheauphis Auto-Curator): per-turn context persistence via Chinese encoding for ~25% token savings. `tac_turn_hook.py` runs at end of every response. Hourly cron backup. 400+ term ZH dictionary. Complements ctx-curation by saving every turn; curation handles structural decisions.