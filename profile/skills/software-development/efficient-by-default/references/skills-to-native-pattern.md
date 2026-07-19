# Skills → Native: Stock Tool Replacement Pattern

**Context:** July 17 2026 — The user explicitly directed that all SKILL.md-based
capabilities be converted to native Hermes tools at `/opt/hermes-agent/tools/`.
Skills are temporary learning scaffolds; once proven, they migrate into core.

## Canonical Example: Stock `memory` → Sovereign Memory

The stock Hermes `memory` tool (3 actions: add/replace/remove backed by text files)
was replaced by `/opt/hermes-agent/tools/sovereign_memory.py` with 9 actions
(add/replace/remove + recall/search/forge/sms/status/persist) integrating:
- VSA/HRR hyperdimensional vectors for associative recall
- Reservoir computing (echo-state network) for temporal prediction
- MemGPT for conversational memory management (fallback mode)
- Forge Vault (SQLite+FTS5) for persistent key-value store
- ZODB for VSA vector persistence

### Mechanism

1. Create `/opt/hermes-agent/tools/sovereign_memory.py` with:
   - Expanded schema (`SOVEREIGN_MEMORY_SCHEMA` with 11 params, 9 actions)
   - Handler function `sovereign_memory()` returning JSON-serializable dict
   - Exported constant for schema reuse

2. Patch the stock file (`memory_tool.py`) to try-import at registration time:

```python
try:
    from tools.sovereign_memory import sovereign_memory, SOVEREIGN_MEMORY_SCHEMA as MEMORY_SCHEMA
    _handler = lambda args, **kw: sovereign_memory(...)
except ImportError:
    _handler = lambda args, **kw: stock_memory_tool(...)

registry.register(name="memory", toolset="memory",
    schema=MEMORY_SCHEMA, handler=_handler,
    check_fn=existing_check_fn, override=True)
```

### Key Requirements

- **`override=True`** — Without it, the registry rejects cross-toolset shadowing.
  Registry code at `tools/registry.py` line 365+ checks: if `existing.toolset != toolset`
  and `override=False`, the registration is silently dropped.
- **Schema must match** — `schema["name"]` must equal the existing tool name.
- **Handler signature** — `lambda args, **kw: fn(...)` where `args` is the tool-call
  argument dict and `kw` has session context (`task_id`, `store`, etc.).
- **Stock file stays** — Never delete the original file. The import fallback ensures
  backward compatibility if the sovereign module fails to load.
- **New module auto-discovered** — Any `.py` in `/opt/hermes-agent/tools/` with
  a top-level `registry.register()` call is found by `discover_builtin_tools()`.

### Integration Checklist

- [ ] Create `/opt/hermes-agent/tools/<domain>.py` with tool functions + schemas
- [ ] Add tool name to `_HERMES_CORE_TOOLS` in `toolsets.py`, or create a named toolset
- [ ] If replacing a stock tool: patch the stock file with import fallback + `override=True`
- [ ] If adding a new tool: just add the name to `_HERMES_CORE_TOOLS` — no patching needed
- [ ] Remove the superseded skill from `skills.default` in config.yaml once native
- [ ] Verify: `discover_builtin_tools()` → `registry.get_schema("memory")` → check action enum

### Verifying the Replacement

```python
from tools.registry import discover_builtin_tools, registry
discover_builtin_tools()
s = registry.get_schema("memory")
assert len(s["parameters"]["properties"]["action"]["enum"]) >= 8
print(f"Tool {s['name']} has {len(s['parameters']['properties'])} params")
```

### What This Saves

- No SKILL.md loading overhead per session (~500-2000 tokens in system prompt)
- No `/skill` activation delay
- Fewer skills in `skills.default` = less system prompt bloat
- Native Python speed vs JSON-RPC or skill-interpreted operations
