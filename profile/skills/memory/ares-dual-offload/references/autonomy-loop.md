# Autonomy Loop — Action Executor

The **action executor** (`~/.hermes/parallel/action_executor.py`) bridges the gap
between the Doer's structured JSON output and actual system execution. It parses
Doer output, runs the requested actions, and returns results.

## Flow

```
Doer output (text)
  ↓
parse_and_execute()
  ├── Try JSON.parse entire output → dict/list of actions
  ├── Extract ```json ... ``` code blocks
  └── Extract [cmd] and `cmd` patterns as shell commands
  ↓
execute_action(action)
  ├── "shell" → subprocess.run(cmd, shell=True, timeout=30)
  ├── "write_file" → Path.write_text(content)
  ├── "read_file" → Path.read_text()
  ├── "list" → list(Path.iterdir())
  └── "wait" → time.sleep(seconds)
  ↓
Results returned as list of dicts:
  {"status": "ok", "exit_code": 0, "stdout": "...", "stderr": "..."}
```

## Integration (goals.py)

In `next_continuation_prompt()`:
```python
if doer_action:
    executor = Path.home() / ".hermes" / "parallel" / "action_executor.py"
    r = subprocess.run([sys.executable, str(executor)],
        input=doer_action, text=True, capture_output=True, timeout=30)
    action_results = r.stdout.strip()[:500]
```

Results appear in the continuation prompt as:
```
[Parallel Analysis]
Foreman: ...
Doer: ...
Actions: [{"status": "ok", "exit_code": 0, ...}]
```

## Supported Actions

### shell
```json
{"action": "shell", "command": "ls -la /tmp"}
```
Returns: `{"status": "ok", "exit_code": 0, "stdout": "...", "stderr": ""}`

### write_file
```json
{"action": "write_file", "path": "/tmp/test.txt", "content": "hello"}
```
Auto-creates parent directories. Returns: `{"status": "ok", "action": "wrote 5b to /tmp/test.txt"}`

### read_file
```json
{"action": "read_file", "path": "/etc/hostname"}
```
Returns content (capped at 2000 chars).

### list
```json
{"action": "list", "path": "/tmp"}
```
Returns file list (capped at 50 entries).

### wait
```json
{"action": "wait", "seconds": 5}
```
Sleeps. Use sparingly — blocks the turn.

## Security

The executor runs ALL commands via `shell=True` by design. This is intended for
agentic autonomy — the Doer's output is trusted. If the Doer model is swapped
to an untrusted provider, reconsider this design.

Doer output feeds through `parse_and_execute()` which tries multiple extraction
strategies. The broadest (inline `[cmd]` extraction) is intentionally permissive.
