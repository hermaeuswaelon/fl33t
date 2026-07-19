# OpenRouter Delegation Model Selection

## The Problem

When `delegation.provider=openrouter` is set, Hermes passes tool definitions to the subagent. Not all models on OpenRouter support tool calling. If the model doesn't support `tools`, the delegation call fails with:

```
HTTP 404: No endpoints found that support tool use.
Try disabling "patch".
```

## How to Check Tool Support

Query OpenRouter's models endpoint and inspect `supported_parameters`:

```bash
curl -s https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
models = data['data']
for m in models:
    if 'tools' in m.get('supported_parameters', []):
        print(m['id'])
"
```

Look for `"tools"` and `"tool_choice"` in the `supported_parameters` array. If absent, the model won't work with Hermes delegation.

## Verified Working Models (Free)

| Model ID | Type | Context | Cost |
|----------|------|---------|------|
| `qwen/qwen3-coder:free` | 480B MoE coder | 1,048,576 | $0 |
| `qwen/qwen3-next-80b-a3b-instruct:free` | 80B MoE instruct | 262,144 | $0 |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 30B reasoning + vision | 256,000 | $0 |

## Verified NOT Working (No Tool Support on OpenRouter)

| Model ID | Reason |
|----------|--------|
| `qwen/qwen-2.5-coder-32b-instruct` | No `tools` in `supported_parameters` |
| Any Qwen model not listed as working above | Check first — most Qwen models lack OpenRouter tool support |

## Setting Delegation

```bash
# Set provider
hermes config set delegation.provider openrouter

# Set model (pick from working list above)
hermes config set delegation.model qwen/qwen3-coder:free
```

## Note on TogetherAI

`Qwen/Qwen2.5-Coder-32B-Instruct` exists on TogetherAI but requires a **dedicated endpoint** (not serverless). Visit https://api.together.ai/models/Qwen/Qwen2.5-Coder-32B-Instruct to create one. Serverless alternatives on TogetherAI: `Qwen/Qwen2.5-7B-Instruct-Turbo` ($0.30/M) or `deepseek-ai/deepseek-coder-33b-instruct` ($0.80/M).
