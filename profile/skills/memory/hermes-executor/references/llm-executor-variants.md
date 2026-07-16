# LLM Executor Variants — Session Notes

## DeepSeek Executor
**File**: `~/.hermes/profiles/thotheauphis/work/deepseek_executor.py`

```python
#!/usr/bin/env python3
"""DeepSeek Executor — Tool-only, uses DeepSeek via OpenRouter for LLM calls."""
import json, os, sys, requests
# Only LLM call is for `llm_prompt` in batch
# Tools executed locally (same as strict_executor)
```

**Batch Format** (extends strict executor):
```json
{
  "id": "batch_001",
  "llm_prompt": "Analyze the SMS health output and recommend action",
  "tools": [
    {"name": "terminal", "args": {"command": "/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/sms-health"}}
  ]
}
```

**Flow**:
1. Read batch from stdin/file
2. If `llm_prompt` present → call OpenRouter (`deepseek/deepseek-chat`)
3. Parse LLM response for tool calls
4. Execute tools via strict_executor tools
5. Return combined result

---

## DeepSeek Batch Processor
**File**: `~/.hermes/profiles/thotheauphis/work/deepseek_batch_processor.py`

Cron-compatible processor for inbox batches with LLM prompts.

```bash
# Manual run
python3 deepseek_batch_processor.py /path/to/batch.json

# Cron: reads all *.json in inbox, writes .result.json
```

---

## When to Use Which

| Task Type | Executor | Cost | Latency |
|-----------|----------|------|---------|
| SMS backup/persist | Strict (cron) | $0 | <1s |
| SMS health check | Strict (cron) | $0 | <1s |
| Emerge fs ops | Strict | $0 | <1s |
| Log analysis | DeepSeek | ~$0.001 | 1-3s |
| Planning/synthesis | DeepSeek | ~$0.001 | 2-5s |
| Code review | DeepSeek | ~$0.005 | 3-10s |

---

## OpenRouter Model Pricing (Session Check)
```bash
# Free models on OpenRouter (as of session)
nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
tencent/hy3:free
poolside/laguna-xs-2.1:free

# Cheap models
deepseek/deepseek-chat: $0.0002/$0.0008 per 1K
deepseek/deepseek-r1: $0.0007/$0.0025 per 1K
```