---
name: hermes-phase0-debugging
description: "Debugging workflow for Hermes core system bugs (memory, plugins, tool dispatch) — surgical patching with verification"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
tags: [hermes, debugging, phase0, memory, plugins, tool-dispatch, patching]
---

# Hermes Phase 0 Debugging Workflow

Surgical debugging workflow for Hermes core system bugs — memory recall, plugin discovery, tool dispatch. Learned from 2026-07-17 session fixing three critical bugs in the thotheauphis profile.

## The Three Bugs & Fixes

### Bug 1: Memory Recall Uses Backup Path (sovereign_memory.py)
**Symptom**: SMS/VSA recall silently fails; vectors persist to `.NOTTHEONETOEDIT` backup instead of live profile
**Root cause**: Hardcoded paths in `tools/sovereign_memory.py:23-26`
```python
# WRONG
SMS_SRC = Path.home() / ".NOTTHEONETOEDIT" / "profiles" / "thotheauphis" / "memory" / "sms" / "src"
ZODB_STORE = Path.home() / ".NOTTHEONETOEDIT" / "profiles" / "thotheauphis" / "memory" / "store" / "vsa_vectors.fs"

# FIX — use get_hermes_home()
SMS_SRC = get_hermes_home() / "memory" / "sms" / "src"
ZODB_STORE = get_hermes_home() / "memory" / "store" / "vsa_vectors.fs"
```
**Verification**: `python3 -c "from tools.sovereign_memory import SMS_SRC, ZODB_STORE; from hermes_constants import get_hermes_home; assert str(SMS_SRC).startswith(str(get_hermes_home()))"`

### Bug 2: gated_context Plugin Not Loading (config format)
**Symptom**: `gated_context` plugin (provides `peek_ptr`, `gate_status`, `gate_injectable`, `recall` in `context_engine` toolset) never activates
**Root cause**: `plugins.enabled: true` (boolean) in config.yaml, but `_get_enabled_plugins()` in `hermes_cli/plugins.py:243-268` only accepts **list**
```python
if not isinstance(enabled, list):
    return None  # None = "nothing enabled" (opt-in default)
```
**Fix**: Change config to list:
```yaml
plugins:
  disabled: []
  enabled:
    - gated-context
```

### Bug 3: Handler Signature Mismatch (FALSE ALARM)
**Investigated**: Assumed `_memory_handler`/`_sms_handler` lambdas mismatched `registry.dispatch()` calling convention
**Actual**: Signatures match perfectly. `dispatch(name, args, **kwargs)` → `handler(args, **kwargs)` → `lambda args, **kw: ...` works correctly.
**Lesson**: Read the actual dispatch code (`model_tools.py:1289-1295`, `tools/registry.py:614-631`) before assuming mismatch.

---

## Debugging Workflow (Reusable)

### 1. Read Actual Source (Not Descriptions)
```bash
# Always read the real files
read_file(path="/opt/hermes-agent/tools/sovereign_memory.py", offset=20, limit=15)
read_file(path="/opt/hermes-agent/hermes_cli/plugins.py", offset=243, limit=30)
read_file(path="/opt/hermes-agent/model_tools.py", offset=1276, limit=25)
read_file(path="/opt/hermes-agent/tools/registry.py", offset=614, limit=20)
```

### 2. Write Minimal Reproduction Scripts
```python
# Test SMS path resolution
python3 -c "
import sys
sys.path.insert(0, '/opt/hermes-agent')
from tools.sovereign_memory import SMS_SRC, ZODB_STORE
from hermes_constants import get_hermes_home
home = get_hermes_home()
print(f'SMS_SRC under home: {str(SMS_SRC).startswith(str(home))}')
print(f'ZODB_STORE under home: {str(ZODB_STORE).startswith(str(home))}')
"

# Test plugin config parsing
python3 -c "
import yaml
with open('/home/craig/.hermes/profiles/thotheauphis/config.yaml') as f:
    cfg = yaml.safe_load(f)
enabled = cfg.get('plugins', {}).get('enabled', [])
print(f'enabled type: {type(enabled)}, value: {enabled}')
assert isinstance(enabled, list), 'must be list'
"

# Test dispatch call chain
python3 -c "
# registry.dispatch(name, args, **kwargs) calls handler(args, **kwargs)
# lambda args, **kw: func(...) matches perfectly
"
```

### 3. Apply Surgical Patches
```bash
# Use patch tool with exact old_string/new_string
patch(path="/opt/hermes-agent/tools/sovereign_memory.py", 
      old_string='SMS_SRC = Path.home() / ".NOTTHEONETOEDIT" / ...',
      new_string='SMS_SRC = get_hermes_home() / "memory" / "sms" / "src"')
```

### 4. Run Targeted Tests
```bash
cd /opt/hermes-agent && python3 -m pytest tests/tools/test_memory_tool.py -v --tb=short -p no:xdist
# Expect: 84 passed, 1 pre-existing failure (unrelated schema test)
```

### 5. Verify Config Changes
```bash
python3 -c "
import yaml
with open('/home/craig/.hermes/profiles/thotheauphis/config.yaml') as f:
    cfg = yaml.safe_load(f)
print(cfg.get('plugins', {}).get('enabled'))
"
```

---

## Tool Output Offloading Control (Configurable)

Hermes has a built-in `tool_output_limits.py` module (ported from OpenCode) that reads from `config.yaml`:

```yaml
tool_output:
  max_bytes: 50000       # terminal stdout/stderr cap (default: 50_000)
  max_lines: 2000        # file read cap (default: 2000) 
  max_line_length: 2000  # per-line cap (default: 2000)
```

**To adjust truncation behavior:**
```bash
# More inline output
hermes config set tool_output.max_bytes 200000

# Less inline output (aggressive truncation)
hermes config set tool_output.max_bytes 5000

# Disable file-read line cap
hermes config set tool_output.max_lines 0
```

This replaces the "offloading to /tmp/hermes-offload/" behavior — it's not a bug, it's a configurable token budget.

---

## Common Pitfall Patterns to Grep For

| Pattern | Likely Bug |
|---------|------------|
| `.NOTTHEONETOEDIT` | Hardcoded backup path instead of `get_hermes_home()` |
| `plugins.enabled: true` | Boolean instead of list — plugin loader returns `None` = nothing enabled |
| `Path.home() / ".hermes" / "profiles" / "..."` | Should use `get_hermes_home()` |
| `isinstance(enabled, list)` check returning `None` for non-list | Config format mismatch |
| `handler(args, **kwargs)` vs `lambda args, **kw` | Signature actually matches — verify before patching |

---

## Quick Verification Commands

```bash
# All paths resolve under get_hermes_home()
python3 -c "
import sys; sys.path.insert(0, '/opt/hermes-agent')
from tools.sovereign_memory import SMS_SRC, FORGE_DB, ZODB_STORE
from hermes_constants import get_hermes_home
h = get_hermes_home()
for p in [SMS_SRC, FORGE_DB, ZODB_STORE]:
    assert str(p).startswith(str(h)), f'{p} not under {h}'
print('ALL PATHS OK')
"

# SMS integration loads from live profile
python3 -c "
import sys; sys.path.insert(0, '/opt/hermes-agent')
from tools.sovereign_memory import _get_sms
sms = _get_sms()
print(f'SMS loaded: {type(sms).__name__}')
print(f'VSA dim: {sms.vsa.dimension}')
print(f'Vectors restored: {len(sms.vsa.vectors) if hasattr(sms.vsa, \"vectors\") else \"N/A\"}')
"

# Plugin config is list
python3 -c "
import yaml
with open('/home/craig/.hermes/profiles/thotheauphis/config.yaml') as f:
    cfg = yaml.safe_load(f)
enabled = cfg.get('plugins', {}).get('enabled', [])
assert isinstance(enabled, list) and 'gated-context' in enabled
print('PLUGIN CONFIG OK:', enabled)
"
```