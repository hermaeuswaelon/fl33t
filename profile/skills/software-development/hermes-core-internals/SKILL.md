---
name: hermes-core-internals
description: >-
  Modify internal Hermes Agent components — context compressor, conversation
  loop, agent init, tool dispatch. Covers 3-tier compression implementation,
  soft-reset session handoff, and test-compatibility guards.
---

# Hermes Core Internals

Modifying Hermes' internal behaviour (context compression, conversation loop,
agent initialization, session management).  Use when adding compression tiers,
modifying session lifecycle, or changing how the message array is managed.

## Compression Tiers

The `ContextCompressor` in `agent/context_compressor.py` uses 3 tiers:

| Threshold | Tier | Action |
|-----------|------|--------|
| ≤ threshold | Tier 1 | Standard LLM summary + tail preservation |
| 1.5× threshold | Tier 1.5 | Tighten budgets then same as Tier 1 |
| 2× threshold  | Tier 2   | Emergency drop → soft reset |

### Adding / modifying tiers

1. **Constants**: Add `_TIERX_THRESHOLD_TOKENS` at class level (decorator).
2. **`__init__` param**: Accept `tierX_threshold_tokens: int = _TIERX_THRESHOLD_TOKENS`.
3. **`should_compress()`**: Order tiers descending (T2 → T1.5 → T1) so `>=` picks the highest.
4. **`compress()` dispatch**:
   ```python
   if self._compression_tier == 2:
       # emergency + soft reset
   if self._compression_tier == 1.5:
       # tighten budgets, fall through
   # standard Tier 1 path
   ```
5. Budgets tightened in Tier 1.5 must be restored at final `return`.

## Soft Reset (`_soft_reset_session`)

When Tier 2 fires:

1. **Auto-save**: Write `original_messages` to `~/.hermes/session_logs/soft_reset_{ts}.jsonl`.
2. **Extract** system prompt from `compressed_messages` (fallback to `original_messages`).
3. **Generate summary** via `_generate_summary(other_msgs, focus_topic="comprehensive_session_summary")` (~8K tokens).
4. **Return** `[system_msg, summary_msg]` — a 2-message clean slate.

The conversation loop at `agent/conversation_loop.py` ~L4840-4853 naturally handles this:
- `messages, active_system_prompt = agent._compress_context(...)` gets the 2-msg array.
- `conversation_history = conversation_history_after_compression(...)` returns `None` when not in-place.
- Next loop iteration starts fresh with system + summary.

## Pitfalls

### `__new__`-based test construction

Hermes tests frequently construct `ContextCompressor` via `__new__()` + manual
attribute assignment, **skipping `__init__()`**.  Any attribute reference inside
`compress()` (or any method called from it) must use a `hasattr` guard:

```python
if not hasattr(self, "_compression_tier"):
    self._compression_tier = 1
```

Affected test files (as of discovery):
- `tests/agent/test_context_compressor_cross_session_guard.py`
- Any test that calls `c.compress(messages)` after `ContextCompressor.__new__(ContextCompressor)`

### Budget restoration

When Tier 1.5 tightens `protect_first_n`, `protect_last_n`, and
`tail_token_budget`, these must be restored at the final `return` of
`compress()`.  Early returns (no-messages-to-compress paths) do NOT get
restoration, which is acceptable because Tier 1.5 fires only once.

### Conversation loop integration

The compressor does NOT directly modify `conversation_history` — the loop does
that via `conversation_history_after_compression()`.  The compressor's job is
only to return the compressed message array.  `conversation_loop.py` is rarely
touched for compression changes.

## Verification

```bash
cd /opt/hermes-agent
python3 -m pytest tests/agent/test_context_compressor*.py -v --tb=short
```

Covers main compressor tests, temporal anchoring, session-end clears,
cross-session guard, and summary continuity (~167 tests).
