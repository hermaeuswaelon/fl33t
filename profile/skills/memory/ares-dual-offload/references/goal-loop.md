# /goal Loop — Autonomous Goal Pursuit (50 turns)

The goal loop is a **self-contained autonomous reasoning cycle** that uses the triple-tier distillation pipeline to pursue a goal across N turns (default 50).

## How It Works

Each turn:
1. Captures system state (RAM, disk, load, timestamp)
2. Builds a prompt from cumulative context + current state + goal
3. Feeds through: Foreman (deepseek-r1, 3x reasoning) → Doer (qwen3-coder-flash)
4. Saves both outputs as checkpoint JSON
5. Appends result to cumulative context for next iteration

## Directory Layout

```
~/.hermes/goals/
└── goal_<unix_timestamp>/
    ├── manifest.json       — Goal, config, turns, timestamps
    ├── turn_001.json       — Foreman + Doer + system state
    └── turn_002.json       ...
```

## Usage

```bash
parallel goal "Build the persistence layer"     # 50 turns default
parallel goal "Optimize fleet" 20                # Custom turns
parallel goals                                   # List sessions
parallel goal-show goal_1784225526               # View manifest
```

## Key Design

- **Persistence**: Every turn saves independently. Survives crashes/reboots.
- **No feedback loops**: Foreman → Doer only. Never backward.
- **Cumulative context**: Each turn builds on all previous turns.
- **Config snapshotted**: Full config saved in manifest for reproducibility.
- **Timeouts**: Foreman 90s (deepseek-r1 is slow), Doer 30s.

## Implementation

Script: `~/.hermes/parallel/goal_loop.py`
