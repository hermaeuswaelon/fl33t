---
name: ctx-curation
description: "Use when the user says 'curate context' or invokes /ctx-curation. Walks through what to keep vs drop one question at a time using the clarify tool."
version: 2.1.0
author: Thotheauphis-Semayasa-Hermes
license: MIT
metadata:
  hermes:
    tags: [context, curation, simplify, slash-commands, architecture]
---

# Context Curation

## What this does

When you tell me to curate context, I ask you one question at a time to decide what to keep vs drop. No scripts, no databases — just me using `clarify` to ask, then executing.

## How to Invoke

- **Direct:** `/ctx-curation` — this skill auto-registers as a slash command.
- **Fallback:** `/skill ctx-curation`
- **Stacked:** `/ctx-curation /other-skill do X` — chain multiple skills in one message.

> **TUI autocomplete note:** The dropdown shows up to 200 entries on bare `/`. Typing `/c` or `/ct` narrows to matching commands — no cap when filter text is present. See `references/slash-command-registration.md` for the full architecture of the fix.

## Workflow

**Step 1:** I ask what's bugging you about the context.

**Step 2:** I go category by category, asking one question per turn:
- Identity/mission → always kept, never asked
- Config/state → still active or stale?
- Observations → keep, condense to 1 line, or drop?
- Old history → keep last N turns?
- Debug/ephemeral → drop all?

**Step 3:** I execute your decisions immediately.

**Step 4:** I report what was done.

## Rules

- One `clarify` call per turn — don't overwhelm
- Never ask about identity, mission, Thotheauphis stuff — always kept
- Actually execute the decisions, don't just talk about them
- Give a quick summary at the end

## References

- **`references/slash-command-registration.md`** — Full architecture of Hermes' slash command system. Documents the six registration paths (built-in, skill, plugin, bundle, toolset, MCP), the unified SlashRegistry singleton, the TUI autocomplete cap fix (30→200, no cap when filtering), and the on-demand tool loading pattern that eliminates permanent injection burden. Also catalogs the 10-file/~2,165-line implementation created July 2026, with exact patch targets for hermes_cli/commands.py, tui_gateway/server.py, and agent/skill_commands.py.
