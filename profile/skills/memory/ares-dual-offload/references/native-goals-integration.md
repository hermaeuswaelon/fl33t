# Native Hermes Agent Integration — Lilareyon Aethelgard

## File Modified
`/opt/hermes-agent/hermes_cli/goals.py`

## Changes Made

### 1. DEFAULT_MAX_TURNS = 50 (line 47)
```python
DEFAULT_MAX_TURNS = 50  # was 20
```

### 2. _ensure_parallel_workers() method (added after line 1139)
```python
def _ensure_parallel_workers(self) -> None:
    """Ensure foreman + doer daemons are running. Part of the Hermes agent."""
    try:
        import subprocess
        import os
        from pathlib import Path
        
        workers = [
            ("foreman", "foreman_worker.py"),
            ("doer", "doer_worker.py"),
        ]
        para_dir = Path.home() / ".hermes" / "parallel"
        env_file = Path.home() / ".NOTTHEONETOEDIT" / "profiles" / "thotheauphis" / ".env"
        
        env = {}
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
        
        for name, script in workers:
            r = subprocess.run(["pgrep", "-f", script], capture_output=True, text=True)
            if not r.stdout.strip():
                worker_py = para_dir / script
                if worker_py.exists():
                    subprocess.Popen(
                        ["setsid", "python3", str(worker_py)],
                        stdout=open(f"/tmp/{name}.log", "a"),
                        stderr=subprocess.STDOUT,
                        env={**env, **{k: v for k, v in os.environ.items()}},
                        stdin=subprocess.DEVNULL,
                    )
    except Exception:
        pass  # Non-blocking
```

### 3. Call from set() (line ~1199)
```python
self._state = state
save_goal(self.session_id, state)
self._ensure_parallel_workers()  # <-- added
return state
```

### 4. next_continuation_prompt() augmented (around line 1557)
- Wraps the existing prompt generation logic
- Before building the continuation prompt, feeds the goal to Foreman + Doer via file IPC (in/out directories at `~/.hermes/parallel/foreman/`)
- Appends `[Parallel Analysis]` block with Foreman's analysis + Doer's action to the continuation prompt
- All worker calls are in a try/except block — non-blocking

## Verification
```bash
cd /opt/hermes-agent
python3 -m pytest tests/tui_gateway/test_goal_command.py -v
# 15/15 tests pass
```

## Reapplication
If a Hermes update overwrites these changes, reapply with:
```bash
patch -p1 < /home/craig/.hermes/parallel/references/hermes-goals-integration.patch
```
(Generate the patch with `git diff hermes_cli/goals.py > ~/.hermes/parallel/references/hermes-goals-integration.patch` while changes are fresh.)
