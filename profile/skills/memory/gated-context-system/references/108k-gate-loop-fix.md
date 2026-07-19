# 108K Gate Infinite Loop Fix (2026-07-18)

## Problem

Two cooperating infinite loops in context compression:

1. **`should_compress()`** — no once-only tracking → fired every time `should_compress` was polled (hundreds of times per session)
2. **108K Gate override** in `conversation_loop.py` bypassed `should_compress()` entirely via `_gate_override` boolean, which only had a per-turn limit (`compression_attempts < 3`) that reset each turn

Result: 489× "108K Gate: ~111,995 tokens >= 108,000 — forcing compression" in errors.log

## Fix (two files, four changes)

### context_compressor.py

1. Added three session-level flags in `__init__`:
```python
self._has_fired_tier1 = False
self._has_fired_tier1_5 = False
self._has_fired_tier2 = False
```

2. Modified `should_compress()` — each tier checks + sets its flag:
```python
if tokens >= self.tier2_threshold_tokens:
    if self._has_fired_tier2:
        return False  # Once-only
    self._compression_tier = 2
    if not self._automatic_compression_blocked():
        self._has_fired_tier2 = True
        return True
    return False
```
(Repeated for tier1_5 and tier1)

### conversation_loop.py

3. Gate check now uses `_gate_has_fired` flag on the compressor:
```python
_gate_raw = gate_should_stop(request_pressure_tokens)
_gate_override = _gate_raw and not getattr(
    _compressor, '_gate_has_fired', False
)
```

4. After `_compress_context()` succeeds:
```python
_compressor._gate_has_fired = True
```

## Testing

All 151 existing tests in `test_context_compressor.py` pass.
All 16 related test files pass (cross_session_guard, session_end, summary_continuity, temporal_anchoring).
Both modified files compile cleanly.

## Key Insight

The `_gate_override` short-circuit in the `if _gate_override or (...should_compress...)` condition means the compressor's own once-only logic was completely invisible to the gate path. Two separate fixes were needed — one in each subsystem.
