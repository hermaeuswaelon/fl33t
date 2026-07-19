# Compression Tier Configuration

## Architecture

Hermes has **two parallel compression trigger mechanisms**:

1. **Percentage-based** — `config.yaml → compression.threshold` (e.g. 0.15 = 15% of context_window_size)
2. **Hardcoded absolute tiers** — in `/opt/hermes-agent/agent/context_compressor.py`:
   - `_TIER1_THRESHOLD_TOKENS = 50_000`
   - `_TIER1_5_THRESHOLD_TOKENS = 88_000`
   - `_TIER2_THRESHOLD_TOKENS = 108_000`

## Critical Pitfall: Percentage Overrides Tiers

The `should_compress()` method checks **tiers first** (108K → 88K → 50K) but the Tier 1 check is an **OR**: `tokens >= tier1_threshold OR tokens >= threshold_tokens`. This means:

- **If `compression.threshold` is too low** (e.g. 0.15 = 19.2K on a 128K window), compression fires at 19K tokens — **far before** the 50K Tier 1 fires.
- The percentage-based check only ever sets `_compression_tier = 1` (never tier 1.5 or 2), so higher-tier emergency compression is **bypassed entirely**.

## Fix: Set threshold above Tier 2

For a 128K context window:
- Tier 2 fires at 108K tokens
- `108K / 128K = 0.84375`
- **Set `compression.threshold: 0.85`** (85%) — this puts threshold_tokens at ~109K, above Tier 2's 108K, so the tier system always fires first.

```yaml
compression:
  enabled: true
  threshold: 0.85        # was 0.15 — prevents % trigger from overriding tiers
  target_ratio: 0.10     # was 0.05 — gives more room after compression
  abort_on_summary_failure: false
  protect_first_n: 1
  protect_last_n: 5
```

## What Each Tier Does

| Tier | Threshold | Behavior |
|------|-----------|----------|
| 1 (light) | 50K | LLM summarization of middle turns, keeps head + tail protected |
| 1.5 (moderate) | 88K | Same as Tier 1 but tighter budgets: head=1, tail=10, tail_budget × 0.6 |
| 2 (emergency) | 108K | No LLM summarization — drops 70% of non-user messages, creates 8K summary, calls `_soft_reset_session()` |
| Hard ceiling | 128K | Provider rejects (context_window_size exceeded) → Hermes runtime handles session rotation |

## Handoff at 128K

When the hard ceiling is reached, there's no 4th compression tier. The provider returns a context-length error, which triggers session rotation in `conversation_compression.py` (`boundary_reason="compression"`). Tier 2 at 108K is designed to prevent ever reaching this point.

## CLI Commands

```bash
hermes config set compression.threshold 0.85
hermes config set compression.target_ratio 0.10
hermes config set compression.abort_on_summary_failure false
hermes config show  # verify
```
