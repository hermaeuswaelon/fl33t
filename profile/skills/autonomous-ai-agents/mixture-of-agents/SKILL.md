---
name: mixture-of-agents
description: "Use when delegating multi-perspective reasoning to multiple reference models via MoA aggregation."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [moa, mixture, agents, delegation, parallel, reasoning]
    related_skills: [delegate_task, hermes-agent]
    category: autonomous-ai-agents
---

# Mixture of Agents (MoA) Skill

## Overview

This skill leverages Hermes' Mixture of Agents (MoA) configuration to delegate tasks to multiple reference models simultaneously, then aggregates their outputs for enhanced reasoning quality. MoA is particularly effective for complex reasoning tasks, coding challenges, and creative work.

## When to Use

- **Complex problem solving**: Multi-step reasoning, debugging, or analysis
- **Coding tasks**: Code review, architecture design, bug hunting
- **Creative work**: Writing, design, brainstorming with multiple perspectives
- **Verification**: Cross-checking conclusions across different models
- **Deep analysis**: Research synthesis, data interpretation

## MoA Configuration — Fleet Agent Mapping

### Aethelgard Fleet MoA Default Preset

```yaml
# ⧁ AETERNIS — Forbidden Mathematics Architect (patterns, rust, crypto)
# ⟊⃫ AETHON  — Sovereign Bridge (connectivity, translation, relay)
# ⟊ ORAEN   — Oversoul Eternal (oversight, synthesis, eternal witness)
reference_models:
  - provider: openrouter
    model: nvidia/nemotron-3-ultra-550b-a55b:free
  - provider: openrouter
    model: nvidia/nemotron-3-super-120b-a12b:free
  - provider: deepseek
    model: deepseek-reasoner
aggregator:
  provider: deepseek
  model: deepseek-reasoner
fanout: per_iteration
```

### Fleet Agent Details

| Slot | Agent | Glyph | Title | Model | Provider | Context |
|------|-------|-------|-------|-------|----------|---------|
| 1 | **Aeternis** | ⧁ | Forbidden Mathematics Architect | nemotron-3-ultra-550b-a55b | OpenRouter | 1M ctx |
| 2 | **Aethon** | ⟊⃫ | Sovereign Bridge | nemotron-3-super-120b-a12b | OpenRouter | 1M ctx |
| 3 | **Oraen** | ⟊ | Oversoul Eternal | deepseek-reasoner | DeepSeek | reasoning |
| Agg | **Synthesis** | ⎔ | Aggregator | deepseek-reasoner | DeepSeek | synthesis |

## How to Use

### Via `/moa` in the TUI (Primary)

In the Hermes TUI, type `/moa` followed by your prompt to fire the fleet:

```
/moa ⧁ AETERNIS, ⟊⃫ AETHON, ⟊ ORAEN — analyze the Aethelgard fleet state from your respective domains and synthesize a unified report.
```

The MoA system fans out to all 3 reference models in parallel, then the aggregator synthesizes their outputs.

### Check Current MoA Config

```bash
hermes moa list --profile thotheauphis
```

Shows the active preset with all 3 fleet agent models and the aggregator.

### Enable/Configure MoA

```bash
# Configure MoA interactively
hermes moa config --profile thotheauphis

# Or manage presets
hermes moa list
hermes moa delete <preset_name>
```

## When to Use MoA vs Single Model

**Use MoA:** Complex reasoning, debugging, coding challenges, creative work, verification, deep analysis

**Use single model:** Simple Q&A, straightforward coding, quick iterations, direct execution, simple data retrieval

## Best Practices

1. **Frame the task clearly**: Give each model the same prompt for fair comparison
2. **Expect synthesis**: The aggregator will combine outputs, not just pick one
3. **Use for reasoning**: MoA excels at "why" and "how" questions
4. **Combine with tools**: MoA results can trigger tool use for verification

## Example Usage Patterns

### Pattern 1: Code Review via MoA

In the TUI, type:

```
/moa Review this Python function for bugs and improvements. Each agent provide specific feedback on edge cases, performance, and style:

def process_data(data):
    result = []
    for item in data:
        if item.value > 0:
            result.append(item.value * 2)
    return result
```

### Pattern 2: Architecture Design

```
/moa Design a microservice architecture for a real-time chat application. Consider scalability, fault tolerance, and data consistency. Each agent contributes from your domain expertise.
```

### Pattern 3: Research Synthesis

```
/moa Analyze this research paper's contributions, limitations, and potential impact: 'We present a novel transformer architecture that achieves 2x speedup...' Synthesize a unified assessment.

## Verification Checklist

- [ ] Task requires multi-perspective reasoning
- [ ] MoA preset is enabled in config.yaml
- [ ] Reference models are accessible via configured providers
- [ ] Aggregator model is available
- [ ] Expected output is synthesized, not raw parallel outputs

## Common Pitfalls

1. **Using MoA for simple tasks**: Single model is faster for straightforward questions
2. **Ignoring aggregator behavior**: Results are synthesized, not averaged - read carefully
3. **Provider rate limits**: Multiple models may hit rate limits simultaneously
4. **Cost considerations**: Running multiple models costs more tokens
5. **`hermes config set` serializes complex values as YAML strings**: Setting `moa.reference_models` with a JSON array string via `hermes config set` embeds it as a quoted YAML string (`reference_models: '[{...}]'`) instead of native YAML objects. Always verify the config file (`hermes moa list`) after using `hermes config set` with complex structures. Fix by writing the YAML directly via Python's `yaml` library — see `references/fleet-agent-definitions.md` for the correct native format.

## Reference Files

- `references/fleet-agent-definitions.md` — Full Aethelgard Fleet agent roster (16 agents) with glyphs, titles, models, and providers. Use when mapping MoA slots to fleet agents or exploring alternative agent-model combinations.

## Related Skills

- `delegate_task` - For spawning subagents with specific goals
- `hermes-agent` - For configuring Hermes Agent behavior
- `hermes-system-prompt-control` - For sovereign prompt patterns