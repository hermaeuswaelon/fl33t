---
name: hermes-compression-fix
description: Fix and troubleshoot compression mechanism in Hermes Agent conversations.
---

# Hermes Compression Fix

## When to Use
When compression in Hermes Agent conversations is not working as designed — multi-tier thresholds firing incorrectly, context not compressing, or default compression behavior needs adjustment.

## Key Files

| File | Purpose |
|------|---------|
| `/opt/hermes-agent/agent/context_compressor.py` | Core compression logic: thresholds, triggers, ratios |
| `/opt/hermes-agent/agent/system_prompt.py` | System prompt assembly, calls context_compressor |
| `/opt/hermes-agent/agent/prompt_builder.py` | Prompt assembly, passes context info to compressor |
| `~/.hermes/profiles/*/config.yaml` | Per-profile config, may override compression |

## Fix Pattern

1. **Check current thresholds** in `context_compressor.py`:
   - `_TIER1_THRESHOLD_TOKENS`, `_TIER1_5_THRESHOLD_TOKENS`, `_TIER2_THRESHOLD_TOKENS`
   - Verify they match desired behavior (single threshold vs multi-tier)

2. **Check compression triggers**: `should_compress()` logic + ratio targets

3. **Verify defaults**: `hermes config` CLI for conversation-level settings

4. **Test**: Force a compression event, check compressor output

## Default Single-64K Threshold (simplified)
```
_TIER1_THRESHOLD_TOKENS = 64000
_TIER1_5_THRESHOLD_TOKENS = 999999  # disabled
_TIER2_THRESHOLD_TOKENS = 999999    # disabled
_TIER1_COMPRESSED_RATIO = 0.382     # compress to 38.2%
```

## Pitfalls
- Update both `_TIER*_THRESHOLD_TOKENS` and `COMPRESSION_TIERS` dict when changing thresholds
- Changes to `context_compressor.py` take effect on next session start
- `context_window_size` in config.yaml may override model native context length
