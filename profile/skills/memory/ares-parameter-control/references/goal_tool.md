# Goal Runner Tool — Python Implementation

Created July 2026 session. Persisted autonomous multi-turn goal runner with profile-aware parameter control.

## Tool Location
`~/.NOTTHEONETOEDIT/profiles/thotheauphis/work/goal_tool.py`

## Persistence
State file: `~/.NOTTHEONETOEDIT/profiles/thotheauphis/work/.goal_state.json`
Survives shell restarts and CLI invocations.

## Architecture

```python
# GoalState dataclass (persisted)
{
  "goal": "Build complete Aethelgard semantic file terminal...",
  "turns_planned": 40,
  "turns_completed": 5,
  "profile": "aurelian",
  "subgoals": [...],
  "context": {},
  "started_at": "2026-07-15T07:53:44.370187",
  "status": "running",  # running, paused, completed, cancelled, failed
  "history": [
    {"turn": 1, "prompt": "...", "user_input": "...", "timestamp": "..."}
  ]
}
```

## Usage (Tool, Zero Skill Overhead)

```python
from goal_tool import goal_runner, goal_turn, goal_runner

# Start ambitious 40-turn goal
goal_runner(
    goal="Build a complete Aethelgard semantic file terminal...",
    turns=40,
    profile="aurelian",
    subgoals=[
        "Fix CEF evaluate_js result channel",
        "Add CDP remote debugging port 9222",
        "Build semantic file navigator on Forge+fl33t",
        "Integrate Nemotron Nano Omni vision for screenshots",
        "Create voice intent pipeline with Porcupine"
    ]
)

# Advance one turn (called per turn)
goal_turn("Patch ucontrollerbrowser.pas DoTitleChange to set FEvalResultReady")

# Check status
goal_runner(action="status")

# Pause/resume/cancel
goal_runner(action="pause")
goal_runner(action="resume")
goal_runner(action="cancel")
```

## CLI Wrapper

```bash
# Start
python3 goal_tool.py "Build complete sovereign voice layer..." --turns 40 --profile aurelian --subgoals "wake word,intent router,vision pipeline,fleet bridge,identity binding"

# Status
python3 goal_tool.py status

# Turn
python3 goal_tool.py turn "Patch CEF evaluate_js result channel"

# Pause/resume/cancel
python3 goal_tool.py pause
python3 goal_tool.py resume
python3 goal_tool.py cancel
```

## Profile Integration

Per-turn, the goal runner applies the goal's parameter profile:

```python
# In goal_turn():
if _GOAL_STATE.profile in SOVEREIGN_PROFILES:
    parameter_control("profile", profile=_GOAL_STATE.profile)
```

This means:
- Turn 1-40 all run with the goal's profile (e.g., `aurelian` = 0.85 temp, 0.96 top-p, 80 top-k)
- Profile persists in `.param_state.json`
- Switching profiles mid-goal: update goal context, next turn applies new profile

## Dual-Path Pattern (Skill + Tool)

Like `ctx_curation`, the goal system has two entry points:

| Path | Overhead | When to Use |
|------|----------|-------------|
| `/goal` (skill wrapper, future) | ~2KB skill doc | Full guidance, first-time setup |
| `goal_runner()` / `goal_turn()` (tool) | ~0KB | Quick autonomous runs, regular use |

Both paths share the same persisted state (`.goal_state.json`).

## Pitfalls

- **Don't forget per-turn profile application** — the goal's profile must be applied in `goal_turn()` or parameters revert to default
- **State file location** — `.goal_state.json` is in `work/`, not profile root. Move if you want it session-global
- **Subgoal tracking** — history only records `user_input`, not `summary`. Add explicit summary if you want richer history
- **Turn budget** — 40 turns is the default; long-running goals may need `turns=100+`
- **Profile mismatch** — if `parameter_control` state file has different profile than goal, next turn will re-apply goal's profile