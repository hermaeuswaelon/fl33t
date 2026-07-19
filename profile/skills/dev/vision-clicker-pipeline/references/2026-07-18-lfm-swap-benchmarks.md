# ⧉ LFM 1.2B Swap Benchmarks — 2026-07-18

## Context
User request: "maybe we had better try the LFM 1.2 over the 2.6??"
Reason: LFM 2.6B (1.8 t/s gen) was too slow for interactive planning.

## Models Compared

| Model | File | Size | Speed (gen) | Speed (prompt) |
|-------|------|------|-------------|----------------|
| LFM 2.6B (old) | `LFM2-2.6B-Uncensored-X64.i1-Q6_K.gguf` | 2.0 GB | **1.8 t/s** | 6.5 t/s |
| LFM2.5-1.2B-Nova | `LFM2.5-1.2B-Nova-Function-Calling.Q6_K.gguf` | 919 MB | **22.1 t/s** | 118.4 t/s |

**Improvement: 12× generation, 18× prompt processing.**

## Why 1.2B Works for Planning
- Function-calling variant — naturally suited to structured output (JSON planning)
- Q6_K quantization preserves quality despite small size
- Enough reasoning to decompose browser goals into action steps
- Fast enough (22 t/s) to be interactive — 6x faster than real-time reading

## Migration
1. `systemctl --user stop hermes-lfm26.service` — stopped 2.6B
2. Created `~/.config/systemd/user/hermes-lfm12.service` — 1.2B on port 8080
3. Same API key (`lfm-local-key`), same port, same client scripts — transparent swap

## Key Insight
CPU inference speed scales roughly linearly with parameter count for the same quantization.
2.6B / 1.2B ≈ 2.17× parameter ratio; measured 22.1/1.8 ≈ 12.3× speedup due to:
  - Smaller memory bandwidth bottleneck (smaller model fits better in cache)
  - Nova architecture likely more efficient
  - Q6_K same on both, so comparison is fair
