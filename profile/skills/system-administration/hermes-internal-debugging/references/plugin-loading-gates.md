# Plugin Loading — Gate Analysis

Exact code locations discovered during 2026-07-17 Phase 0 investigation.

## Gate 1 — `_get_enabled_plugins()`

**File:** `/opt/hermes-agent/hermes_cli/plugins.py`
**Lines:** 243–268

```python
def _get_enabled_plugins() -> Optional[set]:
    """
    * None → key missing or malformed. Callers treat as "nothing enabled"
    * set() → empty list explicitly set; nothing loads
    * set(...) → the concrete allow-list
    """
    config = load_config()
    plugins_cfg = config.get("plugins")
    if not isinstance(plugins_cfg, dict): return None
    if "enabled" not in plugins_cfg: return None
    enabled = plugins_cfg.get("enabled")
    if not isinstance(enabled, list): return None  # <-- boolean True hits this
    return set(enabled)
```

When `plugins.enabled: true` (boolean), this returns `None`.

## Gate 2 — What `None` means to the loader

**File:** `/opt/hermes-agent/hermes_cli/plugins.py`
**Line:** 1381

```python
enabled = _get_enabled_plugins()  # None = opt-in default (nothing enabled)
```

## Gate 3 — The allowlist check

**File:** `/opt/hermes-agent/hermes_cli/plugins.py`
**Lines:** 1454–1466

```python
lookup_key = manifest.key or manifest.name
is_enabled = (
    enabled is not None
    and (lookup_key in enabled or manifest.name in enabled)
)
if not is_enabled:
    # plugin loaded with enabled=False, logged at DEBUG:
    "Skipping '%s' (not in plugins.enabled)", lookup_key
```

## Plugin Discovery — Scanner

**File:** `/opt/hermes-agent/hermes_cli/plugins.py`
**Lines:** 1348–1352 (user plugins scan)

```python
user_dir = get_hermes_home() / "plugins"     # profile-specific
bundled = self._scan_directory(repo_plugins, source="bundled",
    skip_names={"memory", "context_engine", ...})
```

Note: `context_engine` is in `skip_names` — the bundled context_engine directory is NOT scanned. User plugins named `context_engine` are still picked up from the user dir.

## Memory Tool Dispatch

**File:** `/opt/hermes-agent/tools/memory_tool.py`
**Lines:** 1135–1171 (handler registration)

SMS path (when `tools.sovereign_memory` is importable):
```python
_memory_handler = lambda args, **kw: sovereign_memory(
    action=args.get("action", ""),
    target=args.get("target", "memory"),
    ...
)
```
No `store` kwarg passed — SMS has its own persistence.

Fallback path:
```python
_memory_handler = lambda args, **kw: memory_tool(
    action=args.get("action", ""),
    ...
    store=kw.get("store")  # will be None — not in dispatch kwargs
)
```

**Dispatch call chain:**

`model_tools.py` lines 1289–1295:
```python
def _dispatch(next_args):
    return registry.dispatch(
        function_name, next_args,
        task_id=task_id,
        session_id=session_id,
        user_task=user_task,
    )
```

`tools/registry.py` line 629–631:
```python
result = entry.handler(args, **kwargs)  # args ↔ next_args, kwargs ↔ {task_id, session_id, user_task}
```

## Sovereign Memory Paths (before fix)

Original hardcoded paths (line 23, 25, 26 of `tools/sovereign_memory.py`):

```python
# BEFORE (broken — pointed to .NOTTHEONETOEDIT backup)
SMS_SRC = Path.home() / ".NOTTHEONETOEDIT" / "profiles" / "thotheauphis" / "memory" / "sms" / "src"
FORGE_DB = Path.home() / "forge_memory" / "forge_memory.db"
ZODB_STORE = Path.home() / ".NOTTHEONETOEDIT" / "profiles" / "thotheauphis" / "memory" / "store" / "vsa_vectors.fs"

# AFTER (fixed — uses get_hermes_home())
SMS_SRC = get_hermes_home() / "memory" / "sms" / "src"
FORGE_DB = get_hermes_home() / "memory" / "forge_memory.db"
ZODB_STORE = get_hermes_home() / "memory" / "store" / "vsa_vectors.fs"
```

`get_hermes_home()` (from `hermes_constants`) returns the active profile's home: `~/.hermes/profiles/<name>/`.

## VSA Recall — End-To-End Path

```python
def _vsa_recall(query: str, k: int = 3) -> Dict[str, float]:
    sms = _get_sms()  # lazy-load SovereignMemoryIntegration
    if sms and hasattr(sms, 'vsa'):
        try:
            vec = sms._encode_message(query, sms.vsa.dimension)
            return sms.vsa.associative_recall(vec, top_k=k)
        except Exception:
            pass  # <-- silently returns {}
    return {}
```

The `_get_sms()` returns the same lazily-loaded singleton. On first call, it inserts `SMS_PKG` (parent of SMS_SRC) onto `sys.path` and imports `sms.src.integration.SovereignMemoryIntegration`. If the path is wrong, the import fails silently and `_vsa_recall()` returns `{}`.

## Gated Context Plugin Structure

**YAML** (`plugin.yaml`):
```yaml
name: gated-context
version: 1.0.0
kind: standalone
provides_tools:
  - peek_ptr
  - gate_status
  - gate_injectable
  - recall
```

**Entry point** (`__init__.py`):
```python
def register(ctx):
    for name, schema, handler, desc in [...]:
        ctx.register_tool(
            name=name,
            toolset="context_engine",
            schema=schema,
            handler=handler,
            check_fn=lambda: True,
            description=desc or schema["description"],
        )
```

**Toolset definition** (`toolsets.py` line 210):
```python
"context_engine": {
    "description": "Runtime tools exposed by the active context engine",
    "tools": ["peek_ptr", "gate_status", "gate_injectable", "recall"],
    "includes": []
},
```

**Profile toolset enablement** (`config.yaml`):
```yaml
platform_toolsets:
  cli: [context_engine]
```
