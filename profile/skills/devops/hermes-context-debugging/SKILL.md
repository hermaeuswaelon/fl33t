---
name: hermes-context-debugging
version: 1.0.0
description: "Diagnose and repair Hermes context compression issues: infinite compression loops, 108K Gate storms, ineffective compression, plugin registration noise."
trigger: |
  - User reports "108K Gate" spam in errors.log (>10 repeats per turn)
  - Context compression fires every turn without reducing tokens
  - "🧊 108K Gate:" message appears repeatedly in TUI status
  - Gateway logs show "forcing compression" every LLM call
  - Look for these signals: compression_attempts >3 per session, gate_override=True every turn, offload_system.py warnings in errors.log
author: Lilareyon Aethelgard
tags: [hermes, compression, debugging, context-gate, 108k]
---

# Hermes Context Debugging

Diagnosis and repair of infinite context compression loops in Hermes Agent.

## Architecture: Two Compression Paths

Hermes has **two independent** systems that trigger compression. **Both** must be fixed when looping:

### Path 1: `context_compressor.py` — `should_compress()`
Three-tier system (50K/88K/108K). Called by `conversation_loop.py` in the normal compression path.

**Once-only per-tier flags** prevent re-entry within a session:
- `_has_fired_tier1`, `_has_fired_tier1_5`, `_has_fired_tier2`
- Set to `True` when a tier fires, never reset
- Added in `__init__` + checked at top of each tier block in `should_compress()`

### Path 2: `conversation_loop.py` — 108K Context Gate (`_gate_override`)
**This bypasses `should_compress()` entirely.** The gate fires when `request_pressure_tokens >= 108000` and short-circuits the condition to `True`. Only `compression_attempts < 3` provides per-turn limiting, which resets each turn.

**Fix:** Add `_compressor._gate_has_fired` flag:
1. In the gate condition, check `not getattr(_compressor, '_gate_has_fired', False)` before enabling override
2. Set `_compressor._gate_has_fired = True` after `_compress_context()` returns

## Root Cause: Incompressible Prompt Floor

The system prompt (skills index ~10KB) + tool schemas (~26KB) + memory + user context totals 50-70K incompressible tokens. When this floor alone exceeds 108K, every compression pass fails to drop below threshold → infinite loop.

**Fix is always session-level once-only flags**, not per-turn limits.

## Diagnostic Commands

```bash
# Count gate firings in logs
grep "108K Gate" ~/.hermes/profiles/*/logs/errors.log | wc -l

# Check if gate fired this session
grep "108K Gate" ~/.hermes/profiles/*/logs/agent.log | tail -20

# Verify once-only flags are active
grep "_has_fired_tier" /opt/hermes-agent/agent/context_compressor.py | head -10
grep "_gate_has_fired" /opt/hermes-agent/agent/conversation_loop.py

# Run compression tests
cd /opt/hermes-agent && python3 -m pytest tests/agent/test_context_compressor*.py -v
```

## Fix Checklist

- [ ] Add once-only tier flags to `context_compressor.py` (`__init__` + `should_compress`)
- [ ] Add `_gate_has_fired` flag to `conversation_loop.py` (read in gate check, set after compress)
- [ ] Disable noisy plugins if gateway registration fails (see Plugins section)
- [ ] Verify with `python3 -m py_compile` on both files
- [ ] Run test suite: `python3 -m pytest tests/agent/test_context_compressor*.py -x`
- [ ] Deploy: needs agent restart or new `run_conversation` cycle

## Plugin Registration Noise

When a plugin requires env vars that are missing or credentials are invalid, it re-registers on every gateway restart, flooding logs.

**Fix:** Add to `plugins.disabled` in profile config.yaml using **path-derived keys**:
```yaml
plugins:
  disabled:
    - image_gen/xai       # path-derived key (category/name)
    - video_gen/xai       # NOT just "xai" (which would match both)
```

The plugin loader checks both `manifest.name` and the path-derived `lookup_key`. Use path keys for precision when names collide.

## Verifying Fixes

All 167+ tests in `tests/agent/test_context_compressor*.py` must pass:
```bash
python3 -m pytest tests/agent/test_context_compressor.py tests/agent/test_context_compressor_cross_session_guard.py tests/agent/test_context_compressor_session_end_clears_state.py tests/agent/test_context_compressor_summary_continuity.py tests/agent/test_context_compressor_temporal_anchoring.py -v
```

## Pitfalls

- NEVER change `context_window_size` — user caps (128K parent / 32K delegate) are intentional
- The gate override path is easily missed because it bypasses `should_compress()` — always check both paths
- `_automatic_compression_blocked()` handles cooldown + anti-thrashing but does NOT prevent infinite loops when the prompt floor exceeds the threshold
- Testing gates requires runtime — no unit tests for `_gate_override` path exist as of Jul 2026
- `yaml.dump` may reorder keys in config.yaml — prefer `hermes config set` for single keys, Python for list values

## Related

- `gated-context-system` skill — context budget configuration
- `hermes-agent` skill — general Hermes setup and tool configuration
