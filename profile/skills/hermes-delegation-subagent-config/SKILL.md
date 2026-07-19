---
name: hermes-delegation-subagent-config
description: Configure Hermes subagent delegation (parallel workers) with specific model parameters via delegation.request_overrides. Covers the patch needed in delegate_tool.py to enable config-driven temperature/top_p/penalties for subagents.
category: CORE
triggers:
  - user asks to set up a "parallel worker" or "helper" model
  - need to change delegation/subagent model parameters
  - setting temperature, top_p, top_k, penalties on subagents
  - configuring Qwen or other models as delegation workers
  - MoA is dead — parallel workers use delegation now
---

# Hermes Delegation / Subagent Configuration

## Architecture Context

- **MoA (Mixture-of-Agents) is dead.** The 3-tier pipeline (Architect→Foreman→Doer) no longer runs reference models.
- **The "parallel worker" is now the delegation (subagent) model** — used by `delegate_task` to spawn child agents.
- Subagent model config lives in `~/.hermes/profiles/<profile>/config.yaml` under the `delegation:` key.

## Default Config (before change)

```yaml
delegation:
  model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
  parameters: ""
  provider: openrouter
  reasoning_effort: none
```

## What Works Out of the Box

The delegation config directly supports:
- `model` — model name string (e.g. `qwen/qwen-2.5-coder-32b-instruct`)
- `provider` — provider string (e.g. `openrouter`)
- `base_url`, `api_key`, `api_mode` — custom endpoint overrides
- `reasoning_effort` — subagent reasoning level
- `max_iterations`, `max_concurrent_children`, `max_spawn_depth`
- `child_timeout_seconds`, `orchestrator_enabled`

## Config-Driven Model Parameters (Patch Required)

The `delegation` config **does NOT** natively support `temperature`, `top_p`, `top_k`, `frequency_penalty`, `presence_penalty`, `repetition_penalty`, or `max_tokens` as recognized fields.

To pass these, a **code patch** is needed in `tools/delegate_tool.py`:

### Patch: Add `delegation.request_overrides` support

In `_build_child_agent()`, BEFORE the `AIAgent(...)` constructor call, add:

```python
# Merge any request_overrides from delegation config on top of the
# resolved base overrides. This lets users set temperature/top_p/etc.
# per-model for subagents without modifying the parent agent.
_deleg_req_overrides = dict(delegation_cfg.get("request_overrides", {}) or {})
_base_req_overrides = (
    dict(override_request_overrides or {})
    if override_provider
    else dict(getattr(parent_agent, "request_overrides", {}) or {})
)
_base_req_overrides.update(_deleg_req_overrides)
_child_request_overrides = _base_req_overrides
```

Then pass `request_overrides=_child_request_overrides` instead of the old inline expression.

### Config After Patch

```yaml
delegation:
  model: qwen/qwen-2.5-coder-32b-instruct
  provider: openrouter
  reasoning_effort: none
  request_overrides:
    temperature: 0.1
    top_k: 20
    top_p: 0.1
    frequency_penalty: 0.5
    presence_penalty: 0.4
    repetition_penalty: 1.2
    max_tokens: 500
```

## Parameter Details for Focused Execution

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `temperature` | 0.1 | Minimal randomness — deterministic focused output |
| `top_k` | 20 | Restrict to top 20 tokens per step |
| `top_p` | 0.1 | Narrow nucleus sampling — high precision |
| `frequency_penalty` | 0.5 | Mild reduction of token repetition |
| `presence_penalty` | 0.4 | Slight encouragement to cover new topics |
| `repetition_penalty` | 1.2 | Stronger penalty for repeated n-grams |
| `max_tokens` | 500 | Output budget for subagent responses |

## Reasoning Budget Note

Qwen 2.5 Coder **does not support** a `reasoning_budget` parameter — it is not a reasoning model (unlike DeepSeek-R1). The `reasoning_budget` concept only applies to models with explicit reasoning/thinking token allocation. For Qwen, this parameter is silently ignored by OpenRouter.

## How Request Overrides Flow

1. `config.yaml` → `_load_config()` → `delegation_cfg` dict
2. `_build_child_agent()` reads `delegation_cfg.get("request_overrides", {})`
3. Merged on top of `override_request_overrides` (from credential resolution)
4. Passed to `AIAgent(...)` constructor as `request_overrides`
5. In `chat_completions.py`, `api_kwargs.update(overrides)` merges into the API call

## Pitfalls

- The `delegation.parameters` field (empty string in config) is **NOT parsed** by the runtime — it's vestigial. Do not use it.
- Without the delegate_tool.py patch, `request_overrides` in config has no effect on subagents.
- The `parameters` field in `_resolve_delegation_credentials` refers to OpenRouter provider preferences, NOT model generation params.
- Subagents inherit parent's `request_overrides` when `override_provider` is NOT set. When it IS set (e.g. delegation.provider: openrouter), they get ONLY the override — hence why merging is needed.

## Verification

After patching and configuring:
1. Run a task that uses `delegate_task` (e.g. research a topic with a subagent)
2. Check `/tmp/<subagent>.log` or Hermes logs for the API call — verify temperature=0.1 etc. appear in the request
3. Or inspect `hermes-cli` output — focused execution should produce shorter, more deterministic responses
