# Hardware Sizing Guide

## Target Configuration: AMD 395 MAX

**Primary recommendation:** AMD 395 MAX with 128 GB unified memory.

This is the sweet spot for sovereign identity models because:
- Unified memory eliminates PCIe transfer bottlenecks
- 128 GB fits DeepSeek v4-flash at Q4 with 90 GB+ remaining for context
- Fast enough throughput — speed is secondary to capacity
- Can run multiple smaller models simultaneously (Gemma 4 + LFM 2.5 + coder)

### What fits at various quantization levels

| Model | Size | Q4 | Q5 | Q6 | Q8 |
|-------|------|-----|-----|-----|-----|
| DeepSeek v4-flash | ~72B | ~42 GB | ~50 GB | ~58 GB | ~72 GB |
| DeepSeek v3/R1 | ~685B MoE | N/A | N/A | N/A | N/A |
| DeepSeek v2 236B | 236B | ~130 GB | — | — | — |
| Qwen 3 MoE 30B | ~30B | ~18 GB | ~22 GB | ~25 GB | ~30 GB |
| Gemma 4 E4B | ~4B | ~3 GB | ~3.5 GB | ~4 GB | ~4 GB |

### 128 GB breakdown (395 MAX with v4-flash Q4)

```
┌─────────────────────────────────┐
│ Model weights (v4-flash Q4)     │  ~42 GB
│ KV cache (128K context)         │  ~8 GB
│ System + overhead               │  ~5 GB
│ Remaining for concurrent models │  ~73 GB
└─────────────────────────────────┘
```

### Extreme scenarios

**DeepSeek V2 236B at Q2:** ~59 GB — fits on 395 MAX but leaves only ~20 GB
for context. Possible if the purest channel requires V2 specifically.

**Multi-model simultaneous:**
```
- v4-flash Q4 (primary identity) : 42 GB
- Gemma 4 Q6 (secondary eval)    :  4 GB
- LFM 2.5 Q6 (fallback)          :  6 GB
- Total                          : 52 GB — comfortable
```

## Building the system

- **CPU:** AMD 395 MAX (128 GB unified) or 495 MAX if available
- **No discrete GPU needed** — unified memory handles inference
- **Storage:** NVMe SSD, 2 TB+ for model storage and datasets
- **RAM:** 128 GB unified (not expandable — buy the max from the start)
