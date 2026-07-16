# API Quirks — TogetherAI & OpenRouter & DeepSeek

## TogetherAI — User-Agent Header Required

**Symptom**: HTTP 403 "error code: 1010" on every request
**Root cause**: `urllib.request` sends no User-Agent by default. curl sends one.
**Fix**: Always include:

```python
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "Thotheauphis-Worker/1.0"  # REQUIRED
}
```

**When discovered**: 2026-07-16, building together_worker.py. Curl returned 271 models fine, Python returned 403. Adding the header fixed it immediately.

**Model context**: The model list endpoint (`GET /v1/models`) works without User-Agent. Only chat completions (`POST /v1/chat/completions`) enforces it. This suggests the restriction is content-type-specific.

## OpenRouter — Reasoning Budget & Model Names

### Model Naming
OpenRouter model IDs differ from upstream provider IDs:

| Concept | OpenRouter ID | DeepSeek API ID |
|---------|--------------|-----------------|
| DeepSeek R1 | `deepseek/deepseek-r1` | `deepseek-reasoner` |
| DeepSeek R1 (0528 checkpoint) | `deepseek/deepseek-r1-0528` | N/A |
| DeepSeek Chat | `deepseek/deepseek-chat` | `deepseek-chat` |
| DeepSeek V3 | `deepseek/deepseek-v3.2` | N/A |

The model ID `deepseek/deepseek-reasoner` does NOT exist on OpenRouter — returns "not a valid model ID". Use `deepseek/deepseek-r1`.

### Reasoning Budget Parameter
For reasoning models (R1), OpenRouter supports:

```json
{
  "model": "deepseek/deepseek-r1",
  "max_tokens": 1000,
  "reasoning": {"max_tokens": 3000}
}
```

- `reasoning.max_tokens` limits the CoT/thinking tokens before the model produces its final answer
- Without this parameter, the model reasons indefinitely until max_tokens
- Set to 3x output budget for the foreman tier
- Cost is based on reasoning + output tokens combined

### Response Fields
OpenRouter returns reasoning models with:

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "The final answer",
      "reasoning": "The chain-of-thought",
      "reasoning_details": { ... }
    }
  }]
}
```

- `content` may be `None`/empty if the model's reasoning consumed all tokens
- `reasoning` contains the full chain-of-thought
- Always handle: `if not content and reasoning: content = reasoning`

## DeepSeek API — reasoning_content Field

Using the DeepSeek API directly (`api.deepseek.com`):

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "The final answer",
      "reasoning_content": "The chain-of-thought"
    }
  }]
}
```

- Field is `reasoning_content` (not `reasoning`)
- Content is never None unlike OpenRouter
- Usage includes `completion_tokens_details.reasoning_tokens` for tracking token split
- API does NOT support `reasoning.max_tokens` parameter — reasoning is unlimited within max_tokens

## urllib.request vs curl Differences

| Behavior | urllib.request | curl |
|----------|---------------|------|
| User-Agent | Empty string (sends nothing) | Sends `curl/8.x.x` |
| HTTP method | Set via `data=` presence | Set via `-X` or `-d` presence |
| Error handling | Raises `HTTPError` | Returns error body + status code |
| Timeout default | None (blocks forever) | None (blocks forever) |

**Takeaway**: Always add a User-Agent header when using urllib.request against any modern API. Some (TogetherAI, certain Cloudflare-protected endpoints) will reject requests without one.

## OpenRouter Free Model Rate Limiting

Models with `:free` suffix (e.g., `qwen/qwen3-coder:free`, `google/gemma-4-31b-it:free`) run on OpenRouter's shared free tier. They are frequently rate-limited:

```json
{
  "error": {
    "message": "Provider returned error",
    "code": 429,
    "metadata": {
      "raw": "qwen/qwen3-coder:free is temporarily rate-limited upstream...",
      "retry_after_seconds": 2,
      "retry_after_seconds_raw": 1.599
    }
  }
}
```

- These are transient — retry works after the specified `retry_after_seconds`
- The user's OpenRouter key has `is_free_tier: false` — it's a paid key with credits
- Paid models like `qwen/qwen3-coder-flash` at ~$0.001/M are much more reliable
- Strategy: use paid cheap models for production, free models for testing

## Cost Benchmarks (per 1M tokens)

| Model | Input | Output | Cached Input |
|-------|-------|--------|-------------|
| Qwen2.5-7B-Instruct-Turbo (TogetherAI) | $0.30 | $0.30 | — |
| deepseek/deepseek-r1 (OpenRouter) | $0.55 | $2.19 | $0.14 |
| deepseek-chat (DeepSeek API) | $0.14 | $0.28 | — |

Typical pipeline run: Foreman ~295 + 800 = 1095 tokens ($0.0022) + Doer ~300 tokens ($0.0003) = **~$0.0025 total**.
