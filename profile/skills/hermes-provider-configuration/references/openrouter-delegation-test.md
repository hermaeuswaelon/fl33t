# OpenRouter Delegation Model Selection

## Quick reference for finding working delegate models on OpenRouter

### Tool support check
OpenRouter models declare tool/function-calling support via the `supported_parameters` field in their API response. Check a model with:

```python
curl -s https://openrouter.ai/api/v1/models | python3 -c "
import json, sys
data = json.load(sys.stdin)['data']
for m in data:
    if 'MODEL_NAME' in m['id']:
        print('tools' in m.get('supported_parameters', []))
"
```

### Reasoning effort bleed
The Hermes `reasoning_effort` parameter (set at `model.reasoning_effort` in config.yaml) leaks into delegation API calls. Models that don't support this param (all Qwen, most non-DeepSeek models) will return HTTP 400:

```
reasoning.effort: Invalid option: expected one of "max"|"xhigh"|"high"|"medium"|"low"|"minimal"|"none"
```

Fix: set `delegation.reasoning_effort: none` in config.yaml. This suppresses the param for delegated calls only.

### Free models with tool support (OpenRouter, July 2026)

| Model | Context | Vision | Upstream | Notes |
|-------|---------|--------|----------|-------|
| `qwen/qwen3-coder:free` | 1M | No | Venice | 480B MoE, rate-limited |
| `qwen/qwen3-next-80b-a3b-instruct:free` | 262k | No | Venice | 80B MoE, rate-limited |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 256k | Yes | NVIDIA | Vision: text+image+audio+video→text. **Recommended** |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 256k | No | NVIDIA | Text-only variant |

### Upstream provider rate limiting
Qwen models on OpenRouter route through Venice. Under load they return HTTP 429. The Nemotron models route through NVIDIA directly and are more reliable. Keep the Venician Qwen models as a secondary option.

### delegation config.yaml snippet
```yaml
delegation:
  provider: openrouter
  model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
  reasoning_effort: none
```
