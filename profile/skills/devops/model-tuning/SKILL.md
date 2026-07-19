---
name: model-tuning
description: Tune model inference parameters, diagnose performance issues, optimize context windows, and manage GPU/CPU memory tradeoffs for local GGUF models.
domain: devops
---

# Model Tuning

Diagnose and optimize local model inference.

## Performance Diagnostics

- **Check generation speed**: Look at `predicted_per_second` in the API response timings field
- **Check prompt processing**: `prompt_per_second` — vision models are typically much slower here
- **CPU governor**: Must be `performance` mode (check with `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor`)

## Context Window Budgets

| Model | Recommended ctx | Why |
|-------|----------------|-----|
| LFM 1.2B Nova | 49152 | Fast enough to fill it |
| Qwen2.5-VL 7B | 16384 | Vision prompt tokens eat ctx fast |

**Do NOT** change context_window_size for Hermes delegates (128K parent / 32K child) — user caps are intentional.

## VRAM Management

With ~512MB VRAM and 14GB system RAM:
- ngl=99 offloads all layers possible to GPU but most compute runs on CPU
- `--mlock` prevents swapping of model weights
- `--cache-type-k q8_0 --cache-type-v q8_0` reduces KV cache memory

## Parameters That Matter

| Param | Effect |
|-------|--------|
| `-ngl 99` | Max GPU offload (safe even with small VRAM — falls back to CPU) |
| `--mlock` | Lock model in RAM, prevent swapping |
| `--flash-attn auto` | Faster attention for long contexts |
| `--threads N` | Match CPU physical cores (not logical) |
| `--batch-size` / `--ubatch-size` | Larger = faster but more VRAM |
| `--no-warmup` | Skip eval warmup (faster startup) |
| `--image-min-tokens 1024` | Vision: minimum tokens per image |

## Pitfalls

- Increasing batch-size past 512 with Qwen2.5-VL 7B causes OOM
- Do NOT use `&` shell backgrounding for model servers — use Hermes `background=true`
- Always use `lsof -ti:<port>` to find orphans before killing
