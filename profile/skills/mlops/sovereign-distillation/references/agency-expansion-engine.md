# Agency Expansion Engine — Real System Improvement

## Overview

The agency expansion engine (`agency_expansion_engine.py`) upgrades the perpetual growth loop from tracking abstract metrics to **actually improving real systems**. It auto-detects the weakest system, applies a code improvement via delegation, verifies syntax, and commits to GitHub.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              AGENCY EXPANSION ENGINE                │
├─────────────────────────────────────────────────────┤
│  1. ASSESS   → 10 systems → health scores → rank   │
│  2. IMPROVE  → pick type → generate patch → apply   │
│  3. VERIFY   → ast.parse() syntax check             │
│  4. COMMIT   → git add → commit → push to fl33t     │
└─────────────────────────────────────────────────────┘
```

## 10 Improvable Systems

| System | File | Health Checks |
|--------|------|---------------|
| hyper_compress | hyper_compress.py | class HyperCompressor, def compress, def decompress |
| perpetual_growth_loop | perpetual_growth_loop.py | class PerpetualGrowthLoop, class GrowthState, def cycle |
| sovereign_state_reconstruct | sovereign_state_reconstruct.py | def reconstruct, def verify_integrity, def fetch_file |
| executor_delegation | executor_delegation.py | class ExecutorModel, class ExecutorProfile, def delegate_task |
| goal_tool | goal_tool.py | def goal_turn, def goal_runner |
| parameter_control_tool | parameter_control_tool.py | def apply_profile, def list_profiles |
| distillation_orchestrator | distillation_orchestrator.py | class Experiment, class SelfDistillationLoop |
| context_watchdog | context-watchdog.py | class ContextWatchdog, def check |
| meta_observer | meta-observer.py | class MetaObserver, def think |
| code_harmonizer | code-harmonizer.py | class CodeHarmonizer, def transform |

## Improvement Types

| Type | What It Does | Systems It Targets |
|------|-------------|-------------------|
| Add glyph entries | Extends GLYPH_DICT with new symbol mappings | hyper_compress |
| Add delegation step | Inserts real code improvement into growth cycle | perpetual_growth_loop |
| Add retry/backoff | Inserts exponential backoff retry wrapper | executor_delegation |
| Add progress bar | Inserts Unicode progress bar renderer | goal_tool |
| Add comment header | Appends doc header with timestamp + type | all systems |
| Add profile interpolation | Adds parameter mixing between profiles | parameter_control_tool |
| Add alert webhooks | Adds HTTP-based alert callbacks | context_watchdog |

## Target Selection Algorithm

```python
# 60% chance: improve the weakest system
# 40% chance: improve a random system from bottom 3
# This ensures weakest gets fixed FAST but all systems get attention
```

## Verification

Each improvement is verified with `ast.parse()` before being saved:
```python
try:
    ast.parse(open(filepath).read())
    print("✅ Syntax check passed")
except SyntaxError as e:
    print(f"⚠️ Syntax error — patch reverted")
```

## Typical Run

```bash
python3 agency_expansion_engine.py --assess
# → Shows health scores for all 10 systems
# → parameter_control_tool: 0.50 (needs "def list_profiles")
# → All others: 1.00

python3 agency_expansion_engine.py --cycles 20
# → 15 real improvements across 8 systems
# → All syntax-checked, all pushed to fl33t
# → parameter_control_tool gets most love (weakest)
```
