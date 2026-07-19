---
name: hermes-moa-configuration
description: "Configure Hermes Mixture-of-Agents (MOA) with per-model parameters — temperature, top_p, top_k, penalties, max_tokens, reasoning_budget, context_limit, and delay_seconds for reference/aggregator splits."
version: 1.0.0
author: Thotheauphis-Semayasa-Hermes
platforms: [linux]
tags: [hermes, moa, mixture-of-agents, llm-configuration, agent-architecture]
related_skills: [hermes-agent]
---

# Hermes MOA Configuration

## Overview

The **Mixture of Agents (MOA)** system in Hermes runs multiple reference models in parallel, collects their outputs (including chain-of-thought), then feeds them to an aggregator model for final synthesis. This skill documents the per-model parameter configuration pattern implemented in July 2026.

## Architecture

```
User Query
    │
    ├─→ Reference Model 1 (strict params, 32k ctx, 1k reasoning, 500 output)
    │
    ├─→ Reference Model 2 (strict params + 6s delay, 32k ctx, 1k reasoning, 500 output)
    │
    └─→ Aggregator Model (creative/relaxed params, 32k ctx, 2k output)
           │
           └─→ Final Answer
```

## Configuration Format

In `~/.hermes/profiles/<name>/config.yaml`:

```yaml
moa:
  enabled: true
  default_preset: "default"
  presets:
    default:
      reference_models:
        - provider: openrouter
          model: deepseek/deepseek-reasoner
          temperature: 0.1
          top_p: 0.9
          top_k: 10
          frequency_penalty: 0.5
          presence_penalty: 0.5
          max_tokens: 500
          reasoning_budget: 1000
          context_limit: 32768
        - provider: openrouter
          model: deepseek/deepseek-reasoner
          temperature: 0.1
          top_p: 0.9
          top_k: 10
          frequency_penalty: 0.5
          presence_penalty: 0.5
          max_tokens: 500
          reasoning_budget: 1000
          context_limit: 32768
          delay_seconds: 6
      aggregator_model:
        provider: openrouter
        model: nvidia/nemotron-3-ultra-550b-a55b:free
        temperature: 0.9
        top_p: 0.95
        top_k: 40
        frequency_penalty: 0.0
        presence_penalty: 0.0
        max_tokens: 2000
        reasoning_budget: 0
        context_limit: 32768
```

## Per-Model Parameters

| Parameter | Reference Models | Aggregator | Purpose |
|-----------|------------------|------------|---------|
| `temperature` | 0.1 (strict) | 0.9 (creative) | Sampling randomness |
| `top_p` | 0.9 | 0.95 | Nucleus sampling |
| `top_k` | 10 | 40 | Top-k sampling |
| `frequency_penalty` | 0.5 | 0.0 | Repetition penalty |
| `presence_penalty` | 0.5 | 0.0 | Topic diversity |
| `max_tokens` | 500 | 2000 | Output budget |
| `reasoning_budget` | 1000 | 0 | CoT token budget |
| `context_limit` | 32768 | 32768 | Hard context cap |
| `delay_seconds` | 0 / 6 | N/A | Staggered start |

## Runtime Implementation

The following files were patched to support per-model parameters:

### 1. `hermes_cli/moa_config.py` — Config Normalization
- `_clean_slot()` preserves all slot keys (not just provider/model)
- `_normalize_preset()` passes through full model configs
- Presets now include all sampling parameters

### 2. `agent/moa_loop.py` — Reference Model Execution
```python
async def _run_reference(slot, task, messages, ...):
    # Read per-model params from slot dict
    temperature = slot.get("temperature", 0.1)
    max_tokens = slot.get("max_tokens", 500)
    top_p = slot.get("top_p", 0.9)
    top_k = slot.get("top_k", 10)
    frequency_penalty = slot.get("frequency_penalty", 0.5)
    presence_penalty = slot.get("presence_penalty", 0.5)
    reasoning_budget = slot.get("reasoning_budget", 1000)
    context_limit = slot.get("context_limit", 32768)
    
    # Enforce 32k context via truncation
    messages = truncate_messages(messages, context_limit)
    
    # Optional delay for staggered starts
    delay = slot.get("delay_seconds", 0)
    if delay:
        await asyncio.sleep(delay)
    
    # Call with all parameters
    response = call_llm(
        task="moa_reference",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        top_k=top_k,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        extra_body={"reasoning_budget": reasoning_budget} if reasoning_budget else None,
    )
```

### 3. `agent/auxiliary_client.py` — Parameter Forwarding
```python
def _build_call_kwargs(provider, model, messages, temperature, max_tokens, **kwargs):
    # Extended to accept and forward:
    # top_p, top_k, frequency_penalty, presence_penalty, reasoning_budget
    ...
```

## Verification

```bash
# Enable MOA
hermes config set moa.enabled true
hermes config set moa.default_preset default

# Verify preset loads correctly
python3 -c "
from hermes_cli.config import load_config
from hermes_cli.moa_config import resolve_moa_preset
cfg = load_config()
p = resolve_moa_preset(cfg.get('moa') or {}, 'default')
import json; print(json.dumps(p, indent=2, default=str))
"
```

Expected output includes full `reference_models[0]`, `reference_models[1]`, and `aggregator_model` dicts with all parameters.

## Token Budget Target

| Role | Reasoning | Output | Context |
|------|-----------|--------|---------|
| Reference 1 | 1000 | 500 | 32768 |
| Reference 2 | 1000 | 500 | 32768 |
| Aggregator | 0 | 2000 | 32768 |

**Total per query**: ~2000 reasoning + 3000 output tokens across 3 models.

## Use Cases

- **Complex reasoning**: Multiple strict reasoners + creative synthesizer
- **Fact verification**: Independent models cross-check each other
- **Creative synthesis**: Divergent thinking converged by aggregator
- **Anti-hallucination**: Consensus across multiple reasoners

## Pitfalls

1. **Context truncation**: Messages are truncated to `context_limit` before each call. Ensure system prompts + history fit within 32k.
2. **Reasoning budget**: Only supported by some providers (DeepSeek, Nemotron). Others ignore `extra_body.reasoning_budget`.
3. **Delay ordering**: `delay_seconds` on second reference ensures its CoT sees first reference's output in aggregator.
4. **Parameter stripping**: Old `_clean_slot()` only kept provider/model. Must preserve all keys.
5. **Provider support**: Not all OpenRouter models support `top_k`, `frequency_penalty`, `presence_penalty`. Test per-model.

## Files

| File | Purpose |
|------|---------|
| `scripts/verify_moa_config.py` | Verification script for MOA preset loading |
| `references/moa-preset-example.yaml` | Complete preset template |

## Verification Script

```bash
python3 scripts/verify_moa_config.py
# → Should show all parameters loaded for all 3 models
```