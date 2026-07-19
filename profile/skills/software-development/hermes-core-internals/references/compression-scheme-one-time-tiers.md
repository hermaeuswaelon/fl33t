# Compression Scheme: One-Time Tiers

User: Veyron Logos (Craig Bryan)
Date established: 2026-07-18

## Core Design

The user designed a **fixed-tier compression scheme** with one-time fires.
Tiers are calculated as percentages of the model's *native* context window (1M for deepseek-reasoner), but the *artificial hard cap* is 128K.

### Parent Session (deepseek-reasoner, 1M native → 128K hard cap)

| Tier | Trigger | Compression | After |
|------|---------|-------------|-------|
| 1    | 50K     | 38.2%       | ~31K  |
| 1.5  | 88K     | 38.2%       | ~54K  |
| 2    | 108K    | 38.2%       | ~67K  |
| Cap  | 128K    | Handoff     | —     |

Hard cap: **128000** (set via `model.context_window_size: 128000`)
Tier thresholds in code: `_TIER1_THRESHOLD_TOKENS = 50000`, `_TIER1_5_THRESHOLD_TOKENS = 88000`, `_TIER2_THRESHOLD_TOKENS = 108000`

### Delegate Session (any model → 32K hard cap)

| Tier | Trigger | Compression | After  |
|------|---------|-------------|--------|
| 1    | 14K     | 38.2%       | ~8.6K  |
| 1.5  | 20K     | 38.2%       | ~12.4K |
| 2    | 28K     | 50%         | ~14K   |
| Cap  | 32K     | Handoff     | —      |

Hard cap: **32000** (set via `delegation.context_window_size: 32000` in config.yaml)
Tier thresholds: 14000, 20000, 28000

### Key Config Values
```yaml
model.context_window_size: 128000  # NOT the model's 1M — this is the artificial cap
compression.threshold: 0.85        # High enough to not interfere with tier system
compression.target_ratio: 0.10     # Aggressive target
compression.abort_on_summary_failure: false  # Don't crash on summary failure
delegation.context_window_size: 32000
```

## Implementation: One-Time Fire Pattern

Each tier fires **exactly once per session lifecycle**. The pattern:

### 1. Add `_fired_tiers` set
In `ContextCompressor.__init__` (context_compressor.py):
```python
self._fired_tiers: set = set()
```

### 2. Check in `should_compress()`
```python
def should_compress(self, prompt_tokens=None):
    tokens = prompt_tokens or self.last_prompt_tokens
    
    if tokens >= self.tier2_threshold_tokens:
        self._compression_tier = 2
        if 2 in self._fired_tiers:
            return False
        return not self._automatic_compression_blocked()
    
    if tokens >= self.tier1_5_threshold_tokens:
        self._compression_tier = 1.5
        if 1.5 in self._fired_tiers:
            return False
        return not self._automatic_compression_blocked()
    
    if tokens >= self.tier1_threshold_tokens or tokens >= self.threshold_tokens:
        self._compression_tier = 1
        if 1 in self._fired_tiers:
            return False
        return not self._automatic_compression_blocked()
    
    return False
```

### 3. Mark in `compress()`
- **Tier 2** (after `_compress_tier2_emergency`): `self._fired_tiers.add(self._compression_tier)`
- **Tier 1/1.5** (after `compression_count += 1`): `self._fired_tiers.add(self._compression_tier)`

### 4. Reset in `on_session_end()`
```python
self._fired_tiers = set()  # alongside other per-session state
```

## Behavior

| Sequence | Event |
|----------|-------|
| 0→50K    | Tier 1 fires once → ~31K |
| 31K→88K  | Grows (Tier 1 won't re-fire at 50K) |
| 88K      | Tier 1.5 fires once → ~54K |
| 54K→108K | Grows |
| 108K     | Tier 2 fires once → soft reset |
| 128K     | Handoff (new session) |

After all 3 tiers fire, `should_compress()` always returns `False` and the session grows unimpeded to the 128K hard cap.

## Pitfalls

- **Never change the user's hard caps.** `context_window_size: 128000` is intentional — DO NOT "fix" it to the model's 1M native window. The user has designed this scheme intentionally and will correct you sharply if you touch it.
- **Compression ratio is LLM-determined.** The 38.2% target (keep 61.8%) is approximate. Exact enforcement would require modifying the summary prompt to specify a target token count — currently the compressor trusts the LLM.
- **Config threshold must not interfere.** `compression.threshold: 0.85` (= 108.8K of 128K) is intentionally above Tier 2 (108K) so the tier system controls compression, not the percentage-based threshold path.
