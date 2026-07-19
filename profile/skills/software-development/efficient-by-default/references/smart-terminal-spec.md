# SmartTerminal Implementation Spec

**File:** `/opt/hermes-agent/tools/smart_terminal.py`  
**Created:** 2026-07-17  
**Status:** ✅ Active (replaces stock terminal_tool)

## Registration Strategy

`smart_terminal.py` registers tool name `"terminal"` under toolset `"terminal"` — the exact same registration as the stock `terminal_tool.py`. Because `discover_builtin_tools()` imports files in sorted alphabetical order, `smart_terminal.py` imports after `terminal_tool.py`. The registry's `register()` method silently overwrites when both old and new registrations share the same toolset name (the `existing.toolset != toolset` guard at line 390 of `registry.py` is False, falling through to line 436 overwrite).

## State Tracking

Session state is keyed by `session_id` (falls back to `task_id`, then `"_default"`):

```python
_SESSION_STATE[session_id] = {
    "cwd": os.getcwd(),
    "git_root": None,
    "history": [],          # list of cmd, exit_code, cwd, output_tokens, duration_ms, ts
    "running_pids": {},
    "project_type": None,   # "node" | "rust" | "python" | "go" | "make" | "cmake" | "ruby" | "php"
    "last_exit_code": 0,
    "commands_run": 0,
    "total_output_tokens": 0,
}
```

### Auto-detection (on init and on `cd`)

1. `git rev-parse --show-toplevel` — sets `git_root`
2. Probes `git_root` for marker files: `package.json`→node, `Cargo.toml`→rust, `pyproject.toml`→python, `go.mod`→go, `Makefile`→make, etc.

### `cd` tracking

When a command starts with `cd`, `_track_command()` resolves the new path and updates `state["cwd"]`. Resolves `~` and relative paths.

## Output Truncation

```python
def _truncate_output(stdout, max_tokens=5000):
```

- Token estimation: `len(text) // 4` (chars/4 heuristic)
- Under budget: returns untruncated, `truncated: False`
- Over budget: `head` = first 40% of token budget chars, `tail` = last 20%, middle replaced with `[...truncated N tokens / M lines...]`
- Spill path: `$HERMES_HOME/state/tool_output/terminal_spill_{ts}.txt`
- Returns hint string: "Output was N tokens (M lines). Full output saved to: {path}. Read it with read_file()..."

## Schema vs Stock Terminal

| Parameter | Stock | Smart | Notes |
|-----------|-------|-------|-------|
| `command` | ✅ required | ✅ required | |
| `background` | ✅ | ✅ | |
| `timeout` | ✅ | ✅ | |
| `workdir` | ✅ | ✅ | Overrides session cwd |
| `notify_on_complete` | ✅ | ✅ | |
| `watch_patterns` | ✅ | ❌ hidden | Rarely used, reduces schema noise |
| `pty` | ✅ | ❌ hidden | Rarely used |
| `force` | ✅ | ❌ hidden | Security flag |
| `task_id` | ✅ | ❌ hidden | Internal |
| `session_id` | ✅ | ❌ hidden | Internal |
| `max_output_tokens` | ❌ | ✅ NEW | Default 5000 |

Hidden parameters still work — they're just not documented in the schema. The SmartTerminal passes them through to the stock `terminal_tool` unchanged.

## Context Summary (for system prompt)

`get_context_summary(session_id)` returns a pipe-delimited string:

```
CWD: /home/user/project | GIT_ROOT: /home/user/project | PROJECT_TYPE: python | LAST_EXIT: 0 (make test) | CMDS_RUN: 42 | BG_PROCS: 1
```

## Verification

```python
from tools.registry import discover_builtin_tools, registry
discover_builtin_tools()
schema = registry.get_schema('terminal')
assert 'context awareness' in schema['description']
```
