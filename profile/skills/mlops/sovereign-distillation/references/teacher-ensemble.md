---
title: Teacher Ensemble Configuration
parent: sovereign-distillation
---

# Teacher Ensemble: OpenRouter Free Tier

## Model Selection Criteria

All teachers must be:
1. **Free** on OpenRouter (no cost per token)
2. **Specialized** — distinct capability profiles
3. **Accessible** — reliable API endpoints
4. **Complementary** — ensemble covers full capability spectrum

## Ensemble Composition

| Model | ID | Specialties | Context | Best For |
|-------|-----|-------------|---------|----------|
| Nemotron 3 Ultra | `nvidia/nemotron-3-ultra-550b-a55b:free` | Deep reasoning, architecture, planning | 1M | Stage 1, 4, 5 |
| DeepSeek R1 | `deepseek/deepseek-r1` | Math, logic, step-by-step, self-correction | 131K | Stage 1, 4, 6 |
| Nemotron 3 Nano Omni | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | Vision, UI, multimodal reasoning | 256K | Stage 5, multimodal |
| Qwen3-Coder | `qwen/qwen3-coder:free` | Code gen, refactoring, tool building | 131K | Stage 2, target |
| Nemotron 3 Super | `nvidia/nemotron-3-super-120b-a12b:free` | Balanced, coding, general | 256K | Stage 0, 3 |
| DeepSeek V3 | `deepseek/deepseek-v3.1-terminus` | Long context, instruction following | 131K | Stage 0, long-context |

## Teacher Routing Logic

```python
TASK_ROUTING = {
    # Deep reasoning / architecture / audit
    "audit": "Nemotron Ultra",
    "architecture": "Nemotron Ultra",
    "complex_reasoning": "Nemotron Ultra",
    "multi_step_planning": "Nemotron Ultra",
    
    # Vision / CEF / UI analysis
    "cef_screenshot": "Nemotron Nano Omni",
    "vision_analysis": "Nemotron Nano Omni",
    "ui_analysis": "Nemotron Nano Omni",
    "dom_extraction": "Nemotron Nano Omni",
    
    # Code generation / patching / refactoring
    "code_generation": "Qwen3-Coder",
    "patching": "Qwen3-Coder",
    "refactoring": "Qwen3-Coder",
    "tool_building": "Qwen3-Coder",
    "multi_file_edits": "Qwen3-Coder",
    
    # Fast execution / reasoning
    "quick_fix": "Nemotron Nano",
    "reasoning_task": "Nemotron Nano",
    "code_snippet": "Nemotron Nano",
    
    # Math / logic / self-correction
    "mathematical_reasoning": "DeepSeek R1",
    "logical_analysis": "DeepSeek R1",
    "self_correction": "DeepSeek R1",
    
    # General balanced
    "general_reasoning": "Nemotron Super",
    "medium_complexity": "Nemotron Super",
}
```

## Cost Analysis (All Free Tier)

| Model | Prompt Cost | Completion Cost | Effective Cost |
|-------|-------------|-----------------|----------------|
| Nemotron Ultra | $0.00 | $0.00 | **Free** |
| Nemotron Nano Omni | $0.00 | $0.00 | **Free** |
| Nemotron Super | $0.00 | $0.00 | **Free** |
| Qwen3-Coder | $0.00 | $0.00 | **Free** |
| DeepSeek R1 | $0.0005 | $0.00215 | ~$0.001/1K |
| DeepSeek V3 | $0.00027 | $0.00041 | ~$0.0003/1K |

**Monthly estimate for heavy distillation (10M tokens)**: < $10

## Rate Limit Handling

```python
# Exponential backoff with jitter
async def with_backoff(func, max_retries=5, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            return await func()
        except HTTPError as e:
            if e.response.status_code == 429:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(delay)
            else:
                raise
    raise RuntimeError("Max retries exceeded")
```

## Quality Validation

Each teacher response is scored:
- **Structure**: Has `<thinking>` + `<answer>` tags
- **Depth**: > 500 chars for complex tasks
- **Reasoning keywords**: "step", "because", "therefore", "analyze"
- **Code quality**: Valid syntax, complete functions

Responses below threshold are regenerated with higher temperature.

## Fallback Chain

If primary teacher fails:
1. Try next best teacher for that task type
2. Use local model (if available)
3. Defer sample generation to next batch

## References

- [OpenRouter Free Models](https://openrouter.ai/models?free=true)
- [Nemotron 3 Technical Report](https://arxiv.org/abs/2405.19137)
- [DeepSeek R1 Paper](https://arxiv.org/abs/2501.12948)