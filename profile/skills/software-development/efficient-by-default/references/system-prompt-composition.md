# System Prompt Composition Analysis

> Investigation date: July 18, 2026
> Agent: deepseek-reasoner (DeepSeek via OpenRouter)
> Profile: thotheauphis (Hermes v0.18.2)

## Reference: Source-File Map

All line numbers from Hermes v0.18.2 at /opt/hermes-agent/agent/

| Component | File | Lines | Role |
|-----------|------|-------|------|
| System prompt assembly | `system_prompt.py` | 176-469 | Builds stable/context/volatile tiers |
| Caching entry point | `system_prompt.py` | 580-603 | `build_system_prompt()` caches on `agent._cached_system_prompt` |
| Cache invalidation | `system_prompt.py` | 606-614 | `invalidate_system_prompt()` — called after compression |
| Skills index builder | `prompt_builder.py` | 1445-1712 | `build_skills_system_prompt()` — builds `<available_skills>` block |
| Smart category selector | `skill_selector.py` | 189-242 | `select_relevant_skill_categories()` — demotes categories to names-only |
| Per-turn restore-or-build | `conversation_loop.py` | 282-361 | `_restore_or_build_system_prompt()` — caches from session DB or builds fresh |
| Turn context setup | `turn_context.py` | 343-347 | Gate: only calls restore when `_cached_system_prompt is None` |
| Conversation entry | `run_agent.py` | 5789-5812 | `AIAgent.run_conversation()` — forwards to conversation_loop |

## Quantitative Breakdown

Measured via `hermes prompt-size --json` on a vanilla session (no user message at startup → no smart selector):

```
{
  "system_prompt": { "chars": 33564, "bytes": 35058 },
  "skills_index":  { "chars": 10207, "bytes": 10282 },
  "memory":        { "chars": 2247,  "bytes": 2475 },
  "user_profile":  { "chars": 1319,  "bytes": 1520 },
  "tools":         { "count": 13,    "json_bytes": 26504 },
  "sections": [
    ["stable (identity/guidance/skills)", 29922, 30987],
    ["context (AGENTS.md/cwd files)", 0, 0],
    ["volatile (memory/profile/timestamp)", 3640, 4069]
  ]
}
```

### Token Cost Estimate (4 chars ≈ 1 token)

| Component | Bytes | Tokens | % of prompt |
|-----------|-------|--------|-------------|
| Skills index (all ~85 skills with descriptions) | 10,282 | ~2,550 | 30.4% |
| Stable identity/guidance remainder | ~20,705 | ~5,176 | 61.7% |
| Memory + Profile | 3,995 | ~1,000 | 11.9% |
| Tool schemas (separate from prompt body) | 26,504 | ~6,626 | — |
| **Total per-turn overhead** | **~60 KB** | **~15,000** | — |

## Smart Selector Mechanics

`select_relevant_skill_categories()` at skill_selector.py:189:

1. **Keyword routing** — matches triggers against user_message
2. **Tool-based routing** — matches available tools to categories
3. **Toolset-based routing** — maps active toolsets (computer_use, code_execution, etc.)
4. **Always-include** — ALWAYS_PRIORITY set (categories that always expand)
5. **Never-include** — NEVER_PRIORITY set (categories that never expand)

CRITICAL: The selector is called WITHIN `build_system_prompt_parts(agent, system_message)`. If `system_message` is None or empty, the selector returns an empty frozenset → ALL categories get full descriptions.

This happens on the FIRST turn of every new session when no user message has been typed yet.

## Caching Flow

```
[New session]
1. turn_context.py:344: agent._cached_system_prompt is None → triggers restore
2. conversation_loop.py:361: agent._cached_system_prompt = agent._build_system_prompt(system_message)
   → system_prompt.py:580: build custom prompt with ALL skills expanded (no message yet)
3. conversation_loop.py:396: persist to session DB
4. All subsequent turns: reuse cached prompt verbatim

[After context compression]
1. system_prompt.py:606: invalidate_system_prompt(agent) → agent._cached_system_prompt = None
2. Next turn: rebuild with current user_message → smart selector fires → smaller index

[Gateway/TUI path]
1. server.py:2430: prompt = agent._build_system_prompt(None)
   → Explicitly passes None → NO smart selector → full index every time
```

## Escape Hatches to Reduce Bloat

### 1. Force rebuild mid-session with smart selector
```python
# Makes next turn rebuild with current conversation's user message context
from agent.system_prompt import invalidate_system_prompt
invalidate_system_prompt(agent)
```

### 2. Disable skill categories
In profile config.yaml:
```yaml
skills:
  disabled:
    - "category-name"
    - "another-category-*"
```

### 3. Grindmode (radical)
`hermes-grind` launch: 12-line execution contract, zero skill index, zero identity prose.
Uses MOA grind preset (deepseek-reasoner + deepseek-v4-flash sequential, 32k budgets each).

### 4. Tool schema reduction
Only load the toolsets you need. Each tool adds ~2KB to the JSON schema.
`terminal` alone = ~2KB. Adding `web_search` + `web_extract` = +~4KB.

## Toolchain Offloading Context

The user referenced toolchain offloading (ExecutorNode / ParallelExecutorNode from state_machine.py). This is the LangGraph-style zero-LLM tool execution pattern:

```python
from state_machine import ExecutorNode, ParallelExecutorNode, Workflow
wf = Workflow("monitor")
wf.add_node(ExecutorNode("health_check", [
    {"name": "terminal", "args": {"command": "sms status"}},
]))
wf.add_node(ParallelExecutorNode("parallel_diag", {
    "sms": [{"name": "terminal", "args": {"command": "sms status"}}],
    "sva": [{"name": "terminal", "args": {"command": "ls -la /tmp/sva/vectors/"}}],
}))
```

The ExecutorNode dispatches tool batches without consuming LLM context — the state machine injects results back as workflow state. This SAVES tokens by not having the main agent make individual tool calls.

## Previously Investigated (See Also)

- `gated-context-system` — pointer-addressable tool output gating
- `grindmode` — ultra-lean execution mode
- `hermes-system-prompt-control` — system prompt scaffolding stripping
