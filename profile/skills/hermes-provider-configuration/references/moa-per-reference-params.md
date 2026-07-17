# MoA Per-Reference Parameters — Architecture Gap

## The Problem

The user's MoA preset configures per-reference parameters (reasoning_tokens, temperature, top_p, repetition penalty) but these are **not forwarded** to the reference model's API call.

**Desired config:**
- Ref 1 (deepseek-reasoner): `reasoning_tokens=1414`, `max_tokens=500`
- Ref 2 (Qwen3.5-9B): temperature, top_p, top_k, frequency_penalty, presence_penalty

## Root Cause

The call chain in `/opt/hermes-agent/agent/moa_loop.py`:

1. `aggregate_moa_context()` → `_run_references_parallel()` → `_run_reference(slot, ...)`
2. `_run_reference()` (line 220) receives the `slot` dict from the preset config
3. It calls `_slot_runtime(slot)` (line 126) which resolves `{provider, model, base_url, api_key, api_mode}` — and **only** those keys
4. It then calls `call_llm(task="moa_reference", ..., **runtime)` (line 273)

The `slot` dict may carry additional keys like `extra_body_additions` or `temperature`, but **`_run_reference()` never extracts them** from the slot. Only the resolved `runtime` dict is forwarded.

## Where the Fix Goes

**File:** `/opt/hermes-agent/agent/moa_loop.py`
**Lines:** 254-278 (`_run_reference` function)

The `slot` dict can carry arbitrary keys. The fix is to extract `extra_body_additions` (and any other per-reference overrides) from the slot and merge them into the call:

```python
# After line 254 (label = _slot_label(slot))
extra_body_additions = slot.get("extra_body_additions")
```

Then pass it to `call_llm`:

```python
response = call_llm(
    task="moa_reference",
    messages=messages,
    temperature=temperature,
    max_tokens=max_tokens,
    extra_body_additions=extra_body_additions,  # ← added
    **runtime,
)
```

The transport layer already supports `extra_body_additions` — it's merged in `chat_completions.py` lines 497 and 614.

## Config YAML Format (After Fix)

To use per-reference params, the preset in `config.yaml` would look like:

```yaml
moa:
  presets:
    default:
      reference_models:
        - provider: deepseek
          model: deepseek-reasoner
          extra_body_additions:
            reasoning_tokens: 1414
            max_tokens: 500
        - provider: togetherai
          model: Qwen/Qwen3.5-9B
          extra_body_additions:
            temperature: 0.7
            top_p: 0.95
            top_k: 40
            frequency_penalty: 0.3
            presence_penalty: 0.3
```

## Alternative (No Code Change)

Set per-reference parameters at the **provider level** instead of the reference level:
- For deepseek-reasoner: set `reasoning_tokens` as a provider-wide default (if your provider supports it)
- For TogetherAI/Qwen: set default temperature in the custom provider config

This applies the parameter to ALL calls through that provider, not just MoA references.

## Verification

After patching, test with:

```bash
# Verify the moa loop picks up extra_body_additions
python3 -c "
from agent.moa_loop import _run_reference
import inspect
src = inspect.getsource(_run_reference)
print('extra_body_additions' in src)
"
```
