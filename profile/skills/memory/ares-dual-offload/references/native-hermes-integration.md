# Native Hermes Integration — Parallel Workers in `/goal`

## What was modified

**File:** `/opt/hermes-agent/hermes_cli/goals.py`

### 1. DEFAULT_MAX_TURNS = 50 (was 20)

Line 47 changed. Every `/goal` in the TUI now runs 50 turns by default.

### 2. `_ensure_parallel_workers()` — lifecycle management

New method on GoalManager. Called from `set()` whenever a goal is activated:

```python
def _ensure_parallel_workers(self) -> None:
    """Ensure foreman + doer daemons are running."""
    # Checks pgrep for each worker
    # If not running, launches via setsid + subprocess.Popen
    # Loads API keys from .env file
    # Non-blocking — goal works without workers
```

**Auto-start chain:** `/goal set` → `set()` → `_ensure_parallel_workers()` → workers launch if dead.

### 3. next_continuation_prompt() — parallel worker injection

After the judge evaluates a goal turn, when generating the continuation prompt:

1. Feeds the goal text to the Foreman (deepseek-r1) inbox
2. Waits up to 60s for Foreman to produce analysis
3. Feeds Foreman's output to the Doer (qwen3-coder) inbox
4. Waits up to 30s for Doer to produce action recommendation
5. Appends both as a `[Parallel Analysis]` block to the continuation prompt

```python
def next_continuation_prompt(self) -> Optional[str]:
    # Parallel worker analysis (try/except pass — non-blocking)
    foreman_analysis = ""
    doer_action = ""
    try:
        # Write to foreman/in/, read from foreman/out/
        # Write to doer/in/, read from doer/out/
    except Exception:
        pass  # Goal continues without workers if they're down
    
    # Build base continuation prompt (unchanged)
    # Append [Parallel Analysis] block if worker data available
    return base  # or base + analysis_block
```

### 3. Design principles

- **Non-blocking**: if workers error or timeout, the goal continues with just the standard continuation prompt
- **File-based IPC**: foreman + doer workers read/write JSON to `~/.hermes/parallel/foreman/in|out/` and `~/.hermes/parallel/doer/in|out/`
- **No new dependencies**: uses Path.home(), json, time, urllib.request — all stdlib
- **Environment**: keys loaded from `~/.NOTTHEONETOEDIT/profiles/thotheauphis/.env`

## Why this matters

The user's directive: **"modify the actual Hermes agent, not build side projects."** The parallel workers are now part of the agent, not an external add-on. `/goal` in the TUI is the only interface needed.

## What to do on next session

If the skill is loaded, verify the modification is still in place:
```bash
grep "DEFAULT_MAX_TURNS = 50" /opt/hermes-agent/hermes_cli/goals.py
grep "foreman_in = Path.home()" /opt/hermes-agent/hermes_cli/goals.py
```

If Hermes was updated/reinstalled, re-apply the patch to goals.py.
