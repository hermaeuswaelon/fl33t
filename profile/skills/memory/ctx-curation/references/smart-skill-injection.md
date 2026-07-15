# Smart Skill Injection System
*Created July 2026 — major token reduction via keyword-based skill activation*

## Overview

The default Hermes prompt injects **all 157 skill names + descriptions** into the system prompt every turn (~5,147 tokens). Smart skill injection replaces this with **context-aware activation**: only skills matching the current task are loaded.

## Architecture

### Files Created/Modified

| File | Change |
|------|--------|
| `agent/skill_selector.py` | **New** — 31 keyword sets × 20 categories + tool routing |
| `agent/prompt_builder.py` | +`priority_categories` param + cache key |
| `agent/system_prompt.py` | Wires selector → `build_skills_system_prompt(priority_categories=...)` |

### How It Works

```python
# In system_prompt.py build_system_prompt_parts():
if agent.valid_tool_names:
    priority_cats = select_relevant_skill_categories(
        user_message=system_message,
        valid_tool_names=agent.valid_tool_names,
        active_toolsets=avail_toolsets,
    )
skills_prompt = _r.build_skills_system_prompt(
    available_tools=agent.valid_tool_names,
    available_toolsets=avail_toolsets,
    compact_categories=_compact_cats or None,
    priority_categories=priority_cats if priority_cats else None,
)
```

The selector receives: user message, available tool names, active toolsets.

### Keyword Mapping (31 sets → 20 categories)

```python
ROUTING_RULES = [
    ({"code", "debug", "git", "refactor", "python", "rust", ...}, "software-development"),
    ({"github", "gh ", "pr ", "pull request", "issue", "repo", ...}, "github"),
    ({"paper", "arxiv", "research", "literature", "survey", ...}, "research"),
    ({"model", "train", "inference", "llm", "gguf", "quantiz", ...}, "mlops"),
    ({"data", "chart", "plot", "notebook", "pandas", "numpy", ...}, "data-science"),
    ({"click", "mouse", "keyboard", "screenshot", "cua", "automation", ...}, "computer-use"),
    # ... 25 more mappings
]
```

### Tool-Based Routing

| Tool Available | Category Expanded |
|----------------|-------------------|
| `web_search`, `web_extract` | research |
| `terminal` | software-development |
| `computer_use` | computer-use |
| `vision_analyze` | creative |
| `text_to_speech` | media |
| `browser_navigate` | openclaw-imports |
| `skill_view`, `skill_manage` | memory |
| `delegate_task` | autonomous-ai-agents |
| `x_search` | social-media |

## Token Savings

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Skills index | ~5,147 tok | ~1,000-2,000 tok | **~65%** |
| Per-turn overhead | Fixed 157 skills | 15-30 relevant skills | Dynamic |
| Context window freed | — | ~3,500 tok | More room for conversation |

## Cache Key

The `priority_categories` frozenset is now part of the skills prompt cache key (in `prompt_builder.py`):

```python
cache_key = (
    str(skills_dir),
    tuple(str(d) for d in external_dirs),
    tuple(sorted(str(t) for t in (available_tools or set()))),
    tuple(sorted(str(ts) for ts in (available_toolsets or set()))),
    _platform_hint,
    tuple(sorted(disabled)),
    tuple(sorted(compact_categories or ())),
    tuple(sorted(priority_categories or ())),  # NEW
)
```

This means: different task contexts → different cached skill indexes → no cache collision.

## Triggering

Automatic on every turn where:
- A user message is present (`system_message` in `build_system_prompt_parts`)
- Tools are available (`agent.valid_tool_names` non-empty)

Falls back gracefully: if selector errors, `priority_cats = None` → full index (old behavior).

## Verification

Test the selector independently:

```python
from agent.skill_selector import select_relevant_skill_categories

# Coding task
cats = select_relevant_skill_categories(
    user_message="debug the login flow",
    valid_tool_names={"terminal", "read_file", "write_file"},
    active_toolsets={"tool.terminal", "tool.file"},
)
# → frozenset({'software-development', 'github', 'memory'})

# Research task
cats = select_relevant_skill_categories(
    user_message="find latest papers on GRPO",
    valid_tool_names={"web_search", "web_extract"},
    active_toolsets={"tool.web"},
)
# → frozenset({'research', 'mlops', 'memory'})
```

## Pitfalls

1. **Keyword collisions** — "scan" matches both `computer-use` (port scan) and `pentesting` (vuln scan). Deny list `NEVER_PRIORITY` handles known noise (e.g. `yuanbao`).
2. **Over-eager matching** — broad terms like "search" match multiple categories. The deny list + keyword weight tuning controls this.
3. **Tool-only tasks** — if user sends empty message but tools are available, selector still runs (tool-based routing catches it).
4. **Cache collision risk** — `priority_categories` is now in cache key. Many different task types = more cache entries. LRU cap at 64 entries prevents unbounded growth.
5. **Fallback behavior** — if selector fails or returns empty, system falls back to full index (or `compact_categories`). No hard failure.

## Related Files

- `agent/skill_selector.py` — core logic (31 rules, tool mapping, deny list)
- `agent/prompt_builder.py:1445-1460` — `build_skills_system_prompt` signature + cache key
- `agent/system_prompt.py:350-380` — `coding_compact_skill_categories` call + `select_relevant_skill_categories` wiring
- `agent/coding_context.py:305-310` — existing `_NON_CODING_SKILL_CATEGORIES` (15 categories) — now supplemented by selector

## Future Work

- [ ] Learn keyword weights from usage (reinforcement)
- [ ] Skill co-occurrence graph for predictive loading
- [ ] Per-skill activation history for decay scheduling
- [ ] Integration with `ctx_curate` tool for manual override