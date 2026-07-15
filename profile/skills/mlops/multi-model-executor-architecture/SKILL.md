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
  presets:
    default:
      reference_models:
        - provider: openrouter
          model: nvidia/nemotron-3-ultra-550b-a55b:free
        - provider: openrouter
          model: nvidia/nemotron-3-nano-30b-a3b:free
      aggregator:
        provider: deepseek
        model: deepseek-reasoner
      fanout: per_iteration
  max_tokens: 4096
  fanout: per_iteration
  enabled: true
```

### Available Free OpenRouter Executors

| Model | Slug | Active Params | Context | Best For |
|-------|------|---------------|---------|----------|
| Nemotron 3 Ultra | `nvidia/nemotron-3-ultra-550b-a55b:free` | 55B | 1M tokens | Deep reasoning, long context |
| Nemotron 3 Nano | `nvidia/nemotron-3-nano-30b-a3b:free` | 3B | 256K | Fast tool calls, quick code |
| Nemotron 3 Super | `nvidia/nemotron-3-super-120b-a12b:free` | 12B | 256K | Balanced speed/reasoning |

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

- **Free tier limits:** OpenRouter free models have rate limits and log prompts/outputs — don't send secrets.
- **MOA token cost:** Each turn costs (N_references × output_tokens) + aggregation. Prefer single-model delegation for quick turns.
- **Model availability:** Free models come and go. Check `openrouter.ai` for current free lineup.
- **Context window:** Ensure aggregator context >= executor context to avoid truncation.