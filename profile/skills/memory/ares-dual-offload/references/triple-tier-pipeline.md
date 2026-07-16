# Triple-Tier Distillation Pipeline — Implementation Details

## Architecture Overview

The pipeline transforms broad creative chain-of-thought into concentrated actionable output through three stages:

```
Broad Creative Chaos → [reasoning 3x output] → [40/60 think/act] → Concentrated Action
```

## Stage 1: Foreman Daemon (`foreman_worker.py`)

**Location**: `/home/craig/.hermes/parallel/foreman_worker.py`
**Model**: `deepseek/deepseek-r1` via OpenRouter
**API**: `https://openrouter.ai/api/v1/chat/completions`
**System Prompt**: "You are the FOREMAN in a three-tier reasoning distillation chain. INPUT: Broad, creative chain-of-thought. YOUR ROLE: Distill this creative reasoning through your strict structured filter. OUTPUT: Concentrated, precise reasoning that carries the essence of the creative input. Your reasoning budget is 3x your output budget — reason thoroughly, output concisely."

**Key implementation details**:
- `call_api()` sends `"reasoning": {"max_tokens": max_tokens * 3}` in payload
- Response parsing handles OpenRouter's `reasoning` field (chain-of-thought)
- If `content` is None, falls back to `reasoning` as output
- Returns both `content` (distilled output) and `reasoning` (the CoT)

**The auto-pipe**: When the foreman completes a work item, it automatically writes a new work item to the doer's inbox. This happens in `main()` after the result is saved:

```python
if result.get("status") == "completed":
    together_in = Path.home() / ".hermes" / "parallel" / "doer" / "in"
    to_doer = {
        "id": f"{f.stem}_to_doer",
        "prompt": f"""FOREMAN'S DISTILLED REASONING (from DeepSeek Reasoner):
OUTPUT: {result.get('content', '')}
FOREMAN'S CHAIN-OF-THOUGHT:
{result.get('reasoning', '')}
You are the final entity. Complete or finalize based on this."""
    }
    (together_in / f"{f.stem}_to_doer.json").write_text(json.dumps(to_doer))
```

## Stage 2: Doer Daemon (`doer_worker.py`)

**Location**: `/home/craig/.hermes/parallel/doer_worker.py`
**Model**: `Qwen/Qwen2.5-7B-Instruct-Turbo` via TogetherAI
**API**: `https://api.together.xyz/v1/chat/completions`
**System Prompt**: "You are the final entity in a series of specialists. You are to use what information you can glean from the chain-of-thought of your foreman, DeepSeek, to help him complete or finalize his tasks to the best of your ability. RULES: 1. Speak little. Actions over words. 2. If a tool call or action is needed, prioritize it. 3. Do not explain what you're doing — just do it. 4. The foreman's filtered reasoning is your primary signal. 5. Output concise, actionable results."

**Key implementation details**:
- Standard TogetherAI call with User-Agent header
- Temperature 0.05 (tight, execution-focused)
- The 40/60 think-to-output ratio is enforced via system prompt only (Qwen has no API-level reasoning budget)

## Stage 3: Integration Script (`triple_distill.py`)

**Location**: `/home/craig/.hermes/parallel/triple_distill.py`

This is what prime invokes during reasoning:

```python
from triple_distill import distill
results = distill(my_chain_of_thought)
# results["foreman"]["content"]  — DeepSeek R1's distilled output
# results["foreman"]["reasoning"] — DeepSeek R1's chain-of-thought
# results["doer"]["content"]     — Qwen's final actionable output
```

**Timeout handling**:
- Foreman: up to 45 seconds (deepseek-r1 thinks slowly)
- Doer: up to 15 seconds (Qwen is fast)
- Total worst-case: ~60 seconds for full pipeline

## Environment Variables Required

All loaded from `~/.NOTTHEONETOEDIT/profiles/thotheauphis/.env`:
- `OPENROUTER_API_KEY` — for DeepSeek R1
- `TOGETHER_API_KEY` — for Qwen 7B

## Daemon Lifecycle

### Launch (manual, for testing):
```bash
setsid python3 foreman_worker.py </dev/null &>/tmp/foreman.log &
setsid python3 doer_worker.py </dev/null &>/tmp/doer.log &
```

### Service files (for boot persistence):
```bash
~/.config/systemd/user/thotheauphis-foreman.service
~/.config/systemd/user/thotheauphis-doer.service
```

### Verify alive:
```bash
cat ~/.hermes/parallel/foreman/status/heartbeat.json
cat ~/.hermes/parallel/doer/status/heartbeat.json
```

Both must show `"alive": true` with a recent timestamp (<30s old).

## Change History

| Date | Change |
|------|--------|
| 2026-07-16 | Initial triple-tier pipeline built. Replaced old dual-worker pattern (DeepSeek Chat + TogetherAI both flat). Foreman uses deepseek-r1 with reasoning 3x output. Doer uses togetherAI Qwen with "final entity" system prompt. Auto-pipe implemented. |

## Related Files
- `ares-dual-offload/SKILL.md` — Main skill file with user preferences and architecture overview
- `ares-dual-offload/references/api-quirks.md` — API-specific gotchas (User-Agent header, model names, reasoning budget)
