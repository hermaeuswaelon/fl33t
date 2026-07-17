# Free-Tier Pipeline Test Results — 2026-07-16

## Models Tested

| Tier | Model | Cost | Provider | Status |
|------|-------|------|----------|--------|
| Foreman | `nvidia/nemotron-3-ultra-550b-a55b:free` | $0.00 | OpenRouter | ✅ Works reliably |
| Doer | `nvidia/nemotron-3-ultra-550b-a55b:free` | $0.00 | OpenRouter | ✅ Works (initially tried Qwen free → 429) |
| Doer (failed) | `qwen/qwen3-coder:free` | $0.00 | OpenRouter | ❌ HTTP 429 Too Many Requests |

## Verified Output

### Test 1: System health check
```
Architect: deepseek-reasoner → "Check disk usage, memory, daemon health"
Foreman (Nemotron 550B FREE) → Structured reasoning with command templates
                                (507 tokens, $0 cost)
Doer (Nemotron 550B FREE)   → {"action":"shell","command":"df -h"}
                                {"action":"shell","command":"free -h"}
                                (81 chars, pure JSON actions)
```

### Test 2: File listing
```
Architect: deepseek-reasoner → "List 3 files in home directory"
Foreman (Nemotron 550B FREE) → Structured reasoning (456 tokens)
Doer (Nemotron 550B FREE)   → {"action":"shell","command":"ls -la ~"}
```

## Key Findings

1. **Nemotron free tier is reliable** — did not hit 429 during testing. Qwen free tier 429s.
2. **Doer outputs executable JSON** — structured as `{"action":"shell","command":"..."}`.
   Can be directly fed to `doer_action_bridge.py` for real execution.
3. **Foreman processes in 20-45s** on free tier. Pipeline timeout set to 90s.
4. **Doer processes in 10-30s** after receiving foreman output.
5. **Both models produce 0-cost completions** — no token charges on OpenRouter free tier.

## Recommended Default Config

```json
{
  "foreman": {
    "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
    "provider": "openrouter",
    "reasoning_budget_multiplier": 3,
    "max_tokens": 1000,
    "temperature": 0.1
  },
  "doer": {
    "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
    "provider": "openrouter",
    "max_tokens": 800,
    "temperature": 0.3
  }
}
```

## Fallback Options (if Nemotron free is unavailable)

| Model | Cost | Reliability | Notes |
|-------|------|-------------|-------|
| `qwen/qwen3-coder-flash` | ~$0.001/M | High | Fast coder, paid |
| `qwen/qwen3.5-9b` | $0.0001/M | High | Ultra cheap |
| `deepseek/deepseek-chat` | ~$0.001/M | High | Generic chat |
| `deepseek/deepseek-r1` | ~$0.002/M | High | Has reasoning budget control |
