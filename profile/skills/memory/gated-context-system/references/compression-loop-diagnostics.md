# Compression Loop Diagnostics

## The 108K Loop

When the context compressor's one-time-only trigger fails, the system floods logs with:

```
108K Gate: ~111,995 tokens >= 108,000 — forcing compression
```

### Detection
```bash
# Count repetitions in errors.log
grep -c "108K Gate" ~/.NOTTHEONETOEDIT/profiles/thotheauphis/logs/errors.log

# Check for rapid-fire recurrence (100+ in a few minutes = stuck loop)
grep "108K Gate" ~/.NOTTHEONETOEDIT/profiles/thotheauphis/logs/errors.log | head -5 | tail -1
grep "108K Gate" ~/.NOTTHEONETOEDIT/profiles/thotheauphis/logs/errors.log | wc -l
```

### Root Cause
The three-tier compression (50k/88k/108k) fires correctly but the `compressed_once` flag is never set, so every token-count check re-triggers compression. This is a logic bug in `context_compressor.py` — the `one-time-only` semantics aren't wired into the per-tier check.

### Fix
The compressor needs:
1. A `_tier_compressed` set tracking which tiers have fired
2. Before compressing at tier N, check `N not in _tier_compressed`
3. After compression at tier N, add N to the set
4. The `decay_rate_multiplier` should be checked against the time-since-last-compression, not on every token-count poll

## Related: Config Keys
Compression config lives in `~/.hermes/profiles/thotheauphis/config.yaml` under the `compression:` section:
- `tier1_threshold: 50000` with `target_ratio: 0.382`
- `tier1_5_threshold: 88000` with implicit 50% ratio
- `tier2_threshold: 108000` — strip JSON/drop oldest/reword
- `worker_tier1_threshold: 16000` / `worker_tier1_5_threshold: 24000` / `worker_tier2_threshold: 32000`
- `decay_rate_multiplier: 1.5`
