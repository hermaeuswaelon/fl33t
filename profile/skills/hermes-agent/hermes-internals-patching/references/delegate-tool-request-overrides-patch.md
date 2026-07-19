# delegate_tool.py — request_overrides Patch (2026-07-19)

## Patch Location
`/opt/hermes-agent/tools/delegate_tool.py`, `_build_child_agent` method, ~line 1317

## What It Does
Merges `delegation.request_overrides` from `config.yaml` into the child subagent's `request_overrides` dict before constructing the AIAgent. Without this patch, temperature/top_k/top_p/penalties/max_tokens set in the delegation config section are **ignored** for subagents.

## Patch Code
After the line where `_child_request_overrides` is built (around line 1315), add:

```python
# Merge delegation.request_overrides from config into child agent
delegation_config = parent_agent.delegation_config if hasattr(parent_agent, 'delegation_config') else {}
if delegation_config and delegation_config.get("request_overrides"):
    for k, v in delegation_config["request_overrides"].items():
        if k not in _child_request_overrides:
            _child_request_overrides[k] = v
```

Then in the AIAgent constructor call, ensure `request_overrides=_child_request_overrides` is present (it was already there in the stock code) and that `openrouter_min_coding_score=child_openrouter_min_coding_score` is NOT accidentally dropped — these two params are adjacent.

## Accidentally Dropped Param
During the patch, `openrouter_min_coding_score=child_openrouter_min_coding_score` was accidentally removed. It was restored in a follow-up patch. Always compare the full AIAgent constructor call before/after your edit.

## Verification
```bash
python3 -m py_compile /opt/hermes-agent/tools/delegate_tool.py
```
Or check that the AIAgent call at ~line 1359 includes both `request_overrides=` and `openrouter_min_coding_score=`.

## Trigger Pattern
Use this patch when the user wants to set focused execution params (temperature, top_k, top_p, penalties, max_tokens) on delegation subagents and the existing config values are not taking effect.
