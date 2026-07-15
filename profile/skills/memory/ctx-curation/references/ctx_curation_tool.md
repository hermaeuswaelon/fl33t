# ctx_curation_tool implementation

## Overview

The `ctx_curate` tool is a zero-overhead alternative to the `/ctx-curation` skill.
It's registered in the Hermes tool registry via `registry.register()` at import
time, not loaded as a skill document. This means invoking context curation
costs ~0KB of context instead of ~2KB for the skill document.

## File

```
~/.NOTTHEONETOEDIT/profiles/thotheauphis/work/ctx_curation_tool.py
```

## Registration

```python
registry.register(
    name="ctx_curate",
    toolset="memory",
    schema=SCHEMA,
    handler=_handler,
    check_fn=_check_requirements,  # always returns True
    description="Lightweight context curation — walk through categories...",
    emoji="🧹",
)
```

## Schema (what the model calls)

```python
{
    "action": "start" | "keep" | "drop" | "condense" | "done" | "status",
    "category": "config_state" | "observations" | "history" | "debug" | "other",
    "note": "optional reasoning string",
}
```

## Curation Categories (5, in order)

1. `config_state` — still active or stale?
2. `observations` — keep, condense to 1 line, or drop?
3. `history` — keep last N turns?
4. `debug` — drop all?
5. `other` — anything else?

## State

Per-session dict in memory:
```python
_sessions[session_id] = {
    "state": "idle" | "active" | "done",
    "current_category_idx": int,
    "decisions": {category: {"action": str, "note": str}},
    "started_at": timestamp,
}
```

## Dual Path Design Decision

The user explicitly chose to keep BOTH paths:

> "if 2k is all that is overhead, and it's effective, keep it and just make another"

| Path | Overhead | When |
|------|----------|------|
| `/ctx-curation` (skill) | ~2KB doc in context | First use, full guidance visible |
| `ctx_curate` (tool) | ~0KB | Quick cleanup, embedded in other flows |
