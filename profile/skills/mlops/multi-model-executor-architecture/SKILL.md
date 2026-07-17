---
name: multi-model-executor-architecture
description: "Run multiple LLMs as parallel executors via OpenRouter MOA — primary model maintains conversation context while free-tier models (Nemotron Ultra, Nano, etc.) handle subtasks. File-backed state persistence."
version: 1.0.0
author: Thotheauphis-Semayasa-Hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-model, executor, moa, openrouter, nemotron, free-tier, architecture]
    category: mlops
---

# Multi-Model Executor Architecture

## Overview

Run **three models simultaneously** — one primary for conversation context, two (or more) free-tier executors for parallel subtasks. The executors are configured as OpenRouter MOA reference models; the primary is the MOA aggregator.

This pattern gives you:
- **Primary** (e.g. DeepSeek Reasoner) — maintains conversation context, orchestrates
- **Deep executor** (e.g. Nemotron 3 Ultra 550B A55B free) — heavy reasoning, 1M context
- **Fast executor** (e.g. Nemotron 3 Nano 30B A3B free) — quick tool calls, 256K context

## Architecture

```
User prompt
    │
    ▼
┌─────────────────┐     ┌──────────────────┐
│  MOA Aggregator │────▶│  Reference Model 1│  Deep executor
│  (primary model)│     │  (free OpenRouter)│  (Ultra, 550B A55B)
│                 │     └──────────────────┘
│  Maintains ctx  │     ┌──────────────────┐
│  Orchestrates   │────▶│  Reference Model 2│  Fast executor
│  Final synthesis│     │  (free OpenRouter)│  (Nano, 30B A3B)
└─────────────────┘     └──────────────────┘
```

## Configuration

### Hermes MOA Config

Add to `~/.hermes/config.yaml` (or profile config):

```yaml
moa:
  default_preset: default         # ← required — without this no preset is active
  presets:
    default:
      enabled: true               # ← per-preset on/off
      reference_models:
        - provider: openrouter
          model: nvidia/nemotron-3-ultra-550b-a55b:free
        - provider: openrouter
          model: nvidia/nemotron-3-nano-30b-a3b:free
      aggregator:
        provider: deepseek
        model: deepseek-reasoner
      fanout: per_iteration
  enabled: true
```

### Available Free OpenRouter Executors

| Model | Slug | Active Params | Context | Best For |
|-------|------|---------------|---------|----------|
| Nemotron 3 Ultra | `nvidia/nemotron-3-ultra-550b-a55b:free` | 55B | 1M tokens | Deep reasoning, long context |
| Nemotron 3 Nano | `nvidia/nemotron-3-nano-30b-a3b:free` | 3B | 256K | Fast tool calls, quick code |
| Nemotron 3 Super | `nvidia/nemotron-3-super-120b-a12b:free` | 12B | 256K | Balanced speed/reasoning |
| **Nemotron 3 Nano Omni** | `nvidia/nemotron-3-nano-omni-30b-a3b:free` | 3B | 256K | Vision, UI analysis, multimodal |
| **Qwen3-Coder-Next** | `qwen/qwen3-coder:free` | 80B | 131K | Code generation, refactoring |
| **DeepSeek R1** | `deepseek/deepseek-r1:free` | — | 131K | Math reasoning, self-correction |
| **DeepSeek V3** | `deepseek/deepseek-v3:free` | — | 131K | Long context, instruction following |

### Smart Task Routing (executor_delegation.py)

For production deployments, use the `executor_delegation.py` system which routes tasks by type:

```python
from executor_delegation import delegate_task

# Map task types to the optimal teacher model
TASK_ROUTING = {
    "vision_analysis":     "nvidia/nemotron-3-nano-omni-30b-a3b:free",
    "audit_deep":          "nvidia/nemotron-3-ultra-550b-a55b:free", 
    "code_generation":     "qwen/qwen3-coder:free",
    "fast_execution":      "nvidia/nemotron-3-nano-30b-a3b:free",
    "math_reasoning":      "deepseek/deepseek-r1:free",
    "general_reasoning":   "nvidia/nemotron-3-super-120b-a12b:free",
}

result = delegate_task(goal="Analyze this image", task_type="vision_analysis")
```

### Anti-Sync Timing: Irrational Timers

To avoid predictable timing patterns and rate-limit detection, use irrational timers:

```python
from irrational_timers import IrrationalTimer

timer = IrrationalTimer(default_constant='phi')
timer.wait()                    # random × φ (1.618...)
timer.wait(constant='pi')       # random × π (3.1415...)
timer.wait(constant='chaos')    # random constant each time
timer.wait_fibonacci(5, constant='phi')  # F(n) × φ × random
timer.wait_primes(5, constant='e')       # prime × e × random
```

Available constants: π, e, φ, √2, √3, √5, ln2, ln10, γ, ζ(3), Catalan, √π, eπ, π^e, e^π, φπ

### Per-Task Model Delegation

For subtasks that need a specific executor, use `delegate_task` with a model override:

```python
delegate_task(
    goal="Run xdotool to click at 500,500",
    model={
        "provider": "openrouter",
        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
    }
)
```

## Invocation

| Method | Effect |
|--------|--------|
| `/moa <prompt>` | Run through both executors, aggregated by primary |
| `delegate_task(..., model={"provider": "openrouter", "model": "..."})` | Single executor for a subtask |

## Pitfalls

- **Missing `moa.default_preset`:** Defining `moa.presets.default` without `moa.default_preset: default` leaves the system without an active preset — `hermes moa list` shows `Default: (none)` and `/moa` has nothing to invoke. Fix: `hermes config set moa.default_preset default`. Also set `presets.<name>.enabled: true`.
- **Free tier limits:** OpenRouter free models have rate limits and log prompts/outputs — don't send secrets.
- **MOA token cost:** Each turn costs (N_references × output_tokens) + aggregation. Prefer single-model delegation for quick turns.
- **Model availability:** Free models come and go. Check `openrouter.ai` for current free lineup.
- **Context window:** Ensure aggregator context >= executor context to avoid truncation.
- **Provider not in the picker:** See `references/adding-providers-via-custom-providers.md` for how to add providers (like TogetherAI) that have no plugin but are in the Hermes curated model list.

## Reference Documents

- `references/adding-providers-via-custom-providers.md` — How to add TogetherAI and similar providers via the `custom_providers` config section. Covers plugin discovery, activation, and verification.