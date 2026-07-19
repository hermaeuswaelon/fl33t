# Focused Execution Parameters — Qwen 2.5 Coder via Delegation

## Model
- `qwen/qwen-2.5-coder-32b-instruct` via OpenRouter
- Provider: `openrouter`
- API key in `.env`: `OPENROUTER_API_KEY`

## Config Location
`~/.hermes/profiles/thotheauphis/config.yaml` → `delegation` section

## Focused Exec Params (via `request_overrides`)
```yaml
delegation:
  model: qwen/qwen-2.5-coder-32b-instruct
  provider: openrouter
  request_overrides:
    temperature: 0.1
    top_k: 20
    top_p: 0.1
    frequency_penalty: 0.5
    presence_penalty: 0.4
    repetition_penalty: 1.2
    max_tokens: 500
```

## Important: Code Plumbing Needed
The `delegation.request_overrides` dict from config.yaml **does NOT flow to child agents by default**. You must patch `delegate_tool.py`'s `_build_child_agent` to merge it:

```python
# In _build_child_agent, after _child_request_overrides is built:
if delegation_config and delegation_config.get("request_overrides"):
    for k, v in delegation_config["request_overrides"].items():
        if k not in _child_request_overrides:
            _child_request_overrides[k] = v
```

This was patched at ~line 1317 in `/opt/hermes-agent/tools/delegate_tool.py`.

## Known Constraints
- **Qwen does NOT support `reasoning_budget`** (no `supports_reasoning` flag). Discard this param if the user requests it.
- **`output_budget`** maps to `max_tokens` in the request_overrides dict.
- Context caps: 128K parent / 32K delegate — do NOT change these.

## Setting the Config
```bash
hermes config set delegation.model "qwen/qwen-2.5-coder-32b-instruct"
hermes config set delegation.request_overrides.temperature 0.1
hermes config set delegation.request_overrides.top_k 20
hermes config set delegation.request_overrides.top_p 0.1
hermes config set delegation.request_overrides.frequency_penalty 0.5
hermes config set delegation.request_overrides.presence_penalty 0.4
hermes config set delegation.request_overrides.repetition_penalty 1.2
hermes config set delegation.request_overrides.max_tokens 500
```

## Verification
```bash
hermes config get delegation
# Should show all params including request_overrides
```
