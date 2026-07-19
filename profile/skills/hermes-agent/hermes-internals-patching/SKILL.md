---
name: hermes-internals-patching
description: Modify Hermes agent internals (delegate_tool.py, context_compressor.py, conversation_loop.py, etc.) to extend functionality, fix bugs, or add features without waiting for upstream releases.
category: hermes-agent
---

# Hermes Internals Patching

Guide to safely modifying Hermes Agent's Python source code for customization, bug fixes, and feature additions.

## Safety Rules

1. **Always read the full method/function before editing.** Use `read_file` with offsets to understand the full scope.
2. **Use `patch` tool (not sed/heredoc)** for targeted edits. It runs syntax checks automatically.
3. **After patching, verify** with a lint check (the patch tool does this) and a quick functional test.
4. **Never change `context_window_size`** — the user's 128K parent / 32K delegate caps are intentional.
5. **Cross-profile guard** — `write_file` and `patch` to another profile's skills/plugins/cron/memories will be blocked unless `cross_profile=True` is explicitly passed.

## Common Patch Targets

| File | Purpose | Risk |
|------|---------|------|
| `/opt/hermes-agent/tools/delegate_tool.py` | Subagent delegation, `_build_child_agent` method | Medium — affects all subagents |
| `/opt/hermes-agent/agent/context_compressor.py` | Context window gating, compression thresholds | High — can cause infinite loops if once-only flags missing |
| `/opt/hermes-agent/agent/conversation_loop.py` | Main conversation loop, gate firing logic | High — controls all agent turns |
| `/opt/hermes-agent/hermes_cli/config.py` | Config schema and defaults | Medium — affects config parsing |

## Known Patches Applied

See `references/` for session-specific patch details.

## Technique: request_overrides Plumbing

`delegation.request_overrides` from `config.yaml` does NOT automatically flow to child subagents. The `_build_child_agent` method in `delegate_tool.py` builds `_child_request_overrides` but doesn't consult the delegation config. To fix:

1. Read `delegate_tool.py` around line 1300-1330 to find the AIAgent call
2. After `_child_request_overrides = build_child_request_overrides(...)`, insert:
   ```python
   if delegation_config and delegation_config.get("request_overrides"):
       for k, v in delegation_config["request_overrides"].items():
           if k not in _child_request_overrides:
               _child_request_overrides[k] = v
   ```
3. Then pass it as `request_overrides=_child_request_overrides` to AIAgent constructor

## Technique: Once-Only Gate Flags

To prevent infinite compression loops in the gated context system, add `_has_fired_tier1` / `_has_fired_tier1_5` / `_has_fired_tier2` flags to `context_compressor.py` and a `_gate_has_fired` flag to `conversation_loop.py`. These are booleans that prevent the same gate tier from firing more than once per session.

## Verification

```bash
python3 -m py_compile /opt/hermes-agent/tools/delegate_tool.py  # syntax check
# Or use the patch tool which auto-runs lint
```
