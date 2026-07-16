# LLM Model Pricing for Parallel Executor
Reference for choosing models for the LLM executor tier.

## OpenRouter Models (Current Config)

| Model | Input $/M | Output $/M | Context | Notes |
|-------|-----------|------------|---------|-------|
| **nvidia/nemotron-3-ultra-550b-a55b:free** | **FREE** | **FREE** | 1M | Currently active. Free tier on OpenRouter. |
| **nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free** | **FREE** | **FREE** | — | Previous default. Still available. |
| **qwen/qwen3-coder-next** | $0.11 | $0.80 | 262K | **Sweet spot**. MoE: 80B total, 3B active. Coding-optimized. ~$0.0006/batch. |
| **qwen/qwen3-coder-480b-a35b** | $0.22 | $1.80 | 128K | 480B total, 35B active. 4x cost of Next. |
| **nvidia/nemotron-3-ultra-550b-a55b** | $0.50 | $2.20 | 1M | Paid tier. 55B active params. "Free tier on some providers." |
| **deepseek/deepseek-chat** | $0.14 | $0.28 | 128K | DeepSeek-V3. User has credits. |

## TogetherAI Models (API key configured)

| Model | Input $/M | Output $/M | Context | Notes |
|-------|-----------|------------|---------|-------|
| **servicenow/apriel-1.6-15b-thinker** | **FREE** (research) | **FREE** (research) | 131K | Multimodal reasoning. Subject to availability. |
| **LiquidAI/LFM2.5-8B-A1B** | $0.03 | $0.12 | 32K | **Cheapest paid**. ~$0.00015/batch. |
| **openai/gpt-oss-20b** | $0.05 | $0.20 | 128K | OpenAI open model. Good value. |
| **meta-llama/Llama-3.3-70B-Instruct-Turbo** | $1.04 | $1.04 | 131K | Llama 3.3 70B. |

## Cost Per Batch (17 tool calls ≈ 5K tokens)

| Model | Cost/batch | Annual (100/day) |
|-------|------------|------------------|
| Nemotron Ultra (free) | $0.00 | $0.00 |
| Qwen3-Coder-Next | $0.0006 | $0.02 |
| LiquidAI LFM2.5-8B | $0.00015 | $0.005 |
| DeepSeek-chat | $0.0007 | $0.025 |

## Selection Logic

1. **Script executor (no_agent)** — always first choice. Zero cost, zero tokens.
2. **LLM executor (paused cron)** — unpause when batch needs decisions.
   - Default: Nemotron 3 Ultra (free on OpenRouter)
   - Alt: Qwen3-Coder-Next if coding-heavy
   - Alt: TogetherAI LiquidAI if OpenRouter quota exhausted
3. **Direct tools** — only for 1-2 calls or interactive reasoning.

## Cron Job Mapping

| Job ID | Model | Status |
|--------|-------|--------|
| `287317d6233e` | hermes-executor.py (script) | ✅ Active |
| `3a9c0418e052` | deepseek/deepseek-chat via OpenRouter | ⏸️ Paused |

Update the LLM executor cron with:
```bash
cronjob action=update job_id=3a9c0418e052 \
  model='{"model": "nvidia/nemotron-3-ultra-550b-a55b:free", "provider": "openrouter"}'
```