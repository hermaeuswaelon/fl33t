---
name: hermes-internal-debugging
description: "Debug why an internal Hermes system/plugin/tool isn't firing, loading, or dispatching correctly."
version: 1.0.0
author: Auto-generated
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, debugging, plugins, memory, tool-dispatch, troubleshooting]
    related_skills: [hermes-system-health, systematic-debugging, hermes-agent, snapndrop]
---

# Hermes Internal Debugging

Systematic approach to investigating why an internal Hermes component (tool, plugin, memory system, MCP server) isn't loading, dispatching, or responding as expected. NOT for general application debugging — this is for Hermes Agent's own internals.

## Trigger Conditions

- A tool the user installed/configured isn't appearing in the tool list
- A plugin's YAML says it provides tools but the tools aren't callable
- Memory recall/search returns empty even though `add()` succeeded
- A slash command or handler isn't firing
- Config changes aren't reflected after `/reset`

## Principle: Phase 0 First

Before adding any new integration surface (Phase 1+), always fix the broken plumbing first (Phase 0). From this session: "Fix broken plumbing before adding new surfaces. Test fixes against real behavior, not just against your description of the fix." A fix that isn't verified against the actual dispatch chain is just a new unverified claim.

## Investigation Methodology

### 1. Trace the Dispatch Chain

When a tool call silently fails or returns empty:

```
LLM calls tool "memory" (action="recall")
  → run_agent.py receives tool_call response
  → model_tools.py: handle_function_call() builds _dispatch()
  → tools/registry.py: dispatch(name, args, **kwargs)
  → entry.handler(args, **kwargs)   # the lambda registered with the registry
```

Read the actual dispatch code. Do NOT assume how kwargs flow — read `model_tools.py::_dispatch()` and `tools/registry.py::dispatch()` to see exactly what kwargs are injected.

Key finding from this session: `dispatch()` calls `handler(args, **kwargs)` where kwargs = `{task_id, session_id, user_task}`, NOT `{store}`. The handler lambda's `**kw` captures these but `store` is never passed through. The handler must work with its own internal persistence (or default `store=None`).

### 2. Check the Handler Registration

Two places a tool's handler can be registered:

A. **Built-in tool file** (e.g., `tools/memory_tool.py`): uses `registry.register()`. The handler lambda's first positional param receives `args` (the tool call args dict).
B. **Plugin** (e.g., `~/.hermes/plugins/gated_context/`): uses `plugin.yaml` + `register(ctx)` function. Plugin `register()` receives a context object with `register_tool()`.

Always check:
- What's the handler? A lambda or a named function?
- Does it accept `(args, **kw)` signature?
- Are all fields it tries to read from `args` actually present in the tool schema?

### 3. Plugin Loading — Three Gates to Check

When a plugin's tools don't appear:

**Gate 1 — Location:**
```
get_hermes_home() → ~/.hermes/profiles/<profile>/
Plugin dir → get_hermes_home() / "plugins" / <plugin-name>/
```
The plugin scanner only checks the **active profile's** plugins dir, NOT the default `~/.hermes/plugins/`. If the plugin YAML is in the default home, it won't be found under an active profile.

**Gate 2 — `plugins.enabled` is a list, not a boolean:**
```yaml
# BROKEN — _get_enabled_plugins() returns None → nothing loads
plugins:
  enabled: true

# CORRECT — list of plugin names
plugins:
  enabled:
    - gated-context
```
`_get_enabled_plugins()` (in `hermes_cli/plugins.py`) only accepts a **list**. A boolean `true` causes it to return `None`, which the loader at line 1381 treats as "nothing enabled" — silently skipping every standalone plugin. There is no warning or error log.

The earliest clue is `hermes plugins list` showing the plugin with `enabled: false` even though you set `enabled: true`.

**Gate 3 — Kind and opt-in:**
- `kind: standalone` (default for user plugins): needs explicit name in `plugins.enabled`
- `kind: backend`: auto-loads if bundled; user-installed still gated by `plugins.enabled`
- `kind: platform`: auto-loaded when corresponding env var is set

Check the plugin YAML's `kind` field to understand which gate applies.

### 4. Memory System — SovereignMemory Path Tracing

The memory tool has TWO code paths, switched by `_SMS_ACTIVE`:

**SMS path** (`_SMS_ACTIVE = True`, when `tools.sovereign_memory` is importable):
```
memory tool dispatch
  → _memory_handler = lambda args, **kw: sovereign_memory(args.get(...))
  → sovereign_memory() checks _get_sms() for SovereignMemoryIntegration
  → _get_sms() lazy-imports from SMS_SRC (must be on sys.path)
  → dispatch action: recall → _vsa_recall() → sms.vsa.associative_recall()
```

**Fallback path** (`_SMS_ACTIVE = False`):
```
  → memory_tool(action, target, content, store=kw.get("store"))
  → MemoryStore class methods
```

**Key pitfalls:**
- `SMS_SRC` must point to the live profile's `memory/sms/src/`, NOT a backup/snapshot directory
- `ZODB_STORE` (VSA vector persistence) must be inside the profile, not a stale backup path
- `_get_sms()` silently catches all exceptions and returns `None` — VSA recall returns `{}` with no log
- SovereignMemoryIntegration's `_encode_message(query, dim)` must be called first to convert strings to vectors before `associative_recall(vec)`
- The session flag `--ignore-user-config` makes the `memory` tool report "not available" even when memory is fully configured

### 5. Output Offloading & Reading Large Files

When investigating code, Hermes's `max_output_tokens` budget (~5000 tokens per tool call) causes terminal/read_file output to be saved to `/tmp/hermes-offload/<session>/` with only a head+tail preview returned.

**Workaround for targeted file reading:**
```python
python3 -c "
with open('/opt/hermes-agent/hermes_cli/plugins.py') as f:
    lines = f.readlines()
for i in range(START, min(END, len(lines))):
    print(f'{i+1}|{lines[i]}', end='')
"
```

This produces compact output that stays within the inline budget. Also useful: `grep -n` for line numbers first, then read only the needed range.

## Verification Checklist

After patching, verify each layer independently:

```
1. Syntax check:  python3 -c "py_compile.compile('patched_file.py', doraise=True)"
2. Import check:  python3 -c "from module import Thing; print(thing)"
3. Path check:    assert str(path).startswith(str(get_hermes_home()))
4. Logic check:   Run targeted pytest (python3 -m pytest tests/tools/test_foo.py -v -p no:xdist)
5. Runtime check: Start fresh session (/reset) and exercise the tool
```

## Pitfalls

- **Config boolean vs list:** `plugins.enabled: true` is silently treated as "nothing enabled." Must be a list.
- **Silent failures in `_get_sms()`:** The `except Exception: return None` in `_get_sms()` swallows ALL errors — import failures, init failures, everything. No log except at DEBUG level. Check with `grep -i sms` in the log.
- **Plugin location under profiles:** `get_hermes_home()` returns the **profile** dir (`~/.hermes/profiles/<name>/`), not the default `~/.hermes/`. Plugins go under the profile's `plugins/` subdirectory.
- **Session flags:** `--ignore-rules` and `--ignore-user-config` disable plugin loading. If the session was launched with these flags, plugins/memory will be unavailable even if configured correctly.
- **`-n 0` pytest:** The Hermes pyproject.toml has `addopts = "-n auto"` via xdist. If xdist isn't installed, pass `-p no:xdist` instead of `-n 0`.
- **Python 3.14:** This system runs Python 3.14 (3.14.4). Most code works, but some C extensions may need explicit `-C` build flags. Always use `python3`, never `python`.
