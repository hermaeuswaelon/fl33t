---
name: mixture-of-agents
category: core
version: 1.0
description: >
  Configuring and troubleshooting Hermes Mixture-of-Agents (MoA) delegation
  — reference model setup, OpenRouter provider wiring, parallel worker config,
  context budgets, and role assignments for three-tier pipelines.
---

# Mixture of Agents (MoA)

Hermes uses a **three-tier MoA pipeline** with conditional routing:

```
  [Architect]    deepseek-reasoner — creative, relaxed params
       ↓ conditional: budget < 30% → compress, else →
  [Foreman]      secondary model — structured distillation
       ↓ conditional: budget < 30% → compress, else →
  [Doer]         action executor — tool calls, execution
```

## Config Structure (`moa.presets` in config.yaml)

```yaml
moa:
  default_preset: default
  presets:
    default:
      enabled: true
      fanout: per_iteration      # how often to fan out
      reference_max_tokens: 1500
      aggregator:
        model: deepseek-reasoner
        provider: deepseek
        context_limit: 32000
        max_tokens: 8000
        role: creative_aggregator
        temperature: 1.2
      reference_models:
        - model: deepseek-reasoner
          provider: deepseek
          context_limit: 32000
          role: strict_executor
          max_tokens: 1500
          temperature: 0.1
        - model: qwen/qwen-2.5-coder-32b-instruct
          provider: openrouter
          context_limit: 32000
          role: strict_executor
          max_tokens: 4096
          temperature: 0.1
```

## Setting Up a Parallel Worker via OpenRouter

1. **Add API key to `.env`:**
   ```bash
   echo 'OPENROUTER_API_KEY=sk-or-v1-...' >> ~/.hermes/profiles/<profile>/.env
   ```

2. **Edit `reference_models` in config.yaml** — find the `moa.presets.default.reference_models` list and add or replace an entry:
   ```yaml
   - model: qwen/qwen-2.5-coder-32b-instruct
     provider: openrouter
     context_limit: 32000
     max_tokens: 4096
     role: strict_executor
     temperature: 0.1
   ```

3. **Key parameters:**
   - `role`: `strict_executor` (tool-focused), `strict_follower` (follows aggregator), `creative_aggregator` (synthesis)
   - `context_limit: 32000` — matches worker budget cap
   - `max_tokens` — max output per reference call (4096 for coding output)
   - `delay_seconds: 6` — stagger to avoid rate limits (optional)

## Common OpenRouter Models for Workers

| Model | ID | Good For |
|-------|-----|----------|
| Qwen 2.5 Coder 32B | `qwen/qwen-2.5-coder-32b-instruct` | Code generation, tool calls |
| Qwen 2.5 Coder 7B | `qwen/qwen-2.5-coder-7b-instruct` | Fast, cheap code tasks |
| Nemotron 3 Ultra (free) | `nvidia/nemotron-3-ultra-550b-a55b:free` | Reasoning on free tier |
| DeepSeek V4 Flash | `deepseek/deepseek-v4-flash` | Fast execution (via DeepSeek) |

## Pitfalls

- `hermes config set` cannot write lists. Edit `config.yaml` directly via terminal/yaml.
- The profile's `.env` path is `~/.hermes/profiles/<profile>/.env` — not the default profile.
- Workers with 32K context need separate compression thresholds (16K/24K/32K) in the `compression` section — the main window's 108K gate doesn't apply.
- OpenRouter free-tier models (`:free` suffix) have strict rate limits (16 req/min for Nvidia).
- Model names on OpenRouter use forward-slash format: `provider/model-name`.
