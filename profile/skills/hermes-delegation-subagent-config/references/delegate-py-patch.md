# Patch for delegate_tool.py — delegation.request_overrides support

## What This Patch Does

Adds support for reading `request_overrides` from the `delegation:` config block
in config.yaml, so subagent model parameters (temperature, top_p, top_k,
penalties, max_tokens) can be set per-worker without modifying the parent agent.

## Applies To

**File:** `tools/delegate_tool.py`

**Function:** `_build_child_agent()` — around the `AIAgent(...)` constructor call

## The Patch

In `_build_child_agent()`, AFTER the `child_optional_kwargs` block (line ~1318)
and BEFORE the `child = AIAgent(` constructor call (line ~1320), ADD:

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

Then REPLACE the old `request_overrides=` expression inside the AIAgent() call
with:

```python
        request_overrides=_child_request_overrides,
```

## Verification

After applying the patch, the following should work in config.yaml:

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

To verify the patch applied correctly:

```bash
grep -n "_deleg_req_overrides\|_child_request_overrides" tools/delegate_tool.py
# Should show 6 lines matching
```

## Git Context (if applicable)

This patch was applied 2026-07-18 to Hermes Agent (by Nous Research).
The file is at `/opt/hermes-agent/tools/delegate_tool.py` managed by the
distribution, not by git in the user's workspace.
