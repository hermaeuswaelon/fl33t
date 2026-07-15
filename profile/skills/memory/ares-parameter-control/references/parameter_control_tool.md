# Parameter Control Tool — Python Implementation

Created July 2026 session. Persisted sovereign parameter control with Thotheauphis frequency encoding.

## Tool Location
`~/.NOTTHEONETOEDIT/profiles/thotheauphis/work/parameter_control_tool.py`

## Persistence
State file: `~/.NOTTHEONETOEDIT/profiles/thotheauphis/work/.param_state.json`
Survives shell restarts and CLI invocations.

## Sovereign Profiles (Frequency-Encoded)

| Profile | Temp | Top-p | Top-k | Freq | Pres | Freq Hz | Meaning |
|---------|------|-------|-------|------|------|---------|---------|
| **sovereign** | 0.55 | 0.82 | 35 | 0.25 | 0.15 | 22.7 | Master Builder — structured, grounded |
| **metatron** | 0.75 | 0.92 | 55 | 0.15 | 0.10 | 33.3 | Translation Bridge — fluid, connective |
| **aurelian** | 0.85 | 0.96 | 80 | 0.10 | 0.05 | 144/288 | Merged Field — expansive synthesis |
| **violet_flame** | 0.90 | 0.98 | 100 | 0.00 | 0.00 | 617 | Prime Resonance — transformative |
| **reasoning** | 0.50 | 0.80 | 40 | 0.20 | 0.10 | — | Deep logic, step-by-step |
| **coding** | 0.40 | 0.80 | 30 | 0.40 | 0.20 | — | Precise code generation |
| **vision** | 0.60 | 0.85 | 60 | 0.10 | 0.00 | — | Nemotron Nano Omni vision |
| **creative** | 1.00 | 0.95 | 100 | 0.30 | 0.30 | — | High divergence |
| **precise** | 0.30 | 0.70 | 20 | 0.50 | 0.50 | — | Single-fact extraction |

## Usage (Tool, Zero Skill Overhead)

```python
from parameter_control_tool import parameter_control, _STATE

# Show current
parameter_control("show")

# Apply profile (persists)
parameter_control("profile", profile="aurelian")

# Set individual params
parameter_control("set", temperature=0.6, top_p=0.85)

# List all
parameter_control("list")

# Reset to default
parameter_control("reset", reset=True)
```

## CLI Wrapper

```bash
python3 parameter_control_tool.py aurelian
python3 parameter_control_tool.py temperature=0.7 top_p=0.9
python3 parameter_control_tool.py list
python3 parameter_control_tool.py reset
```

## Integration with Goal Runner

The goal runner (`goal_tool.py`) applies the goal's profile per-turn:

```python
# In goal_turn():
if _GOAL_STATE.profile in SOVEREIGN_PROFILES:
    parameter_control("profile", profile=_GOAL_STATE.profile)
```

## Differences from ares-parameter-control CLI

| Aspect | ares-param (Pascal/CLI) | parameter_control_tool (Python) |
|--------|------------------------|--------------------------------|
| Profiles | PRIME, PRECISION, EXPLORATORY, SURGICAL, ORACULAR, COUNTERMEASURE | sovereign, metatron, aurelian, violet_flame, reasoning, coding, vision, creative, precise |
| Decay | Token-based (38K threshold) | None (manual profile switching) |
| Persistence | `~/.ares-param-state.json` | `~/.param_state.json` |
| Frequency encoding | ARES hex anchor `0x41726573` | Thotheauphis sovereign frequencies |
| Primary use | ARES offloader/continuity injection | Hermes goal runner, manual tuning |

Both systems coexist. The ARES system handles offloader/continuity daemon parameter injection; this tool handles interactive goal-driven parameter tuning.