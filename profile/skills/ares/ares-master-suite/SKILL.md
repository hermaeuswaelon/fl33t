---
name: ares-master-suite
description: "Master skill suite for ARES using free OpenRouter vision models and Pascal Bromium Browser integration."
version: 1.1.0
author: Craig / Thotheauphis
platforms: [linux]
tags: [ares, openrouter, vision, pascal, browser, suite]
related_skills: [ares, ares-dual-citizen-browser, sovereign-distillation]
---

# ARES Master Skill Suite

## 1. Free OpenRouter Vision Integration

Model: `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` (30B A3B, 256K ctx, vision+audio+video)
Endpoint: `https://openrouter.ai/api/v1/chat/completions`

**Dispatch pattern:**
```python
delegate_task(
    goal="analyze this screenshot",
    model={"provider": "openrouter", "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"},
    toolsets=["browser", "vision"]
)
```

## 2. Bromium Browser

Bromium (née Dual Citizen v2) is a 37MB CEF4Delphi browser. See `ares-dual-citizen-browser` for full reference.

| Component | Path | Notes |
|-----------|------|-------|
| **Bromium (primary)** | `dual-citizen-v2/bromium` | Main browser binary |
| **dual_citizen_v2** | `dual-citizen-v2/dual_citizen_v2` | Fallback binary |
| **CEF Controller** | `cef_controller` | Alternate controller |
| **Extensions** | `dual-citizen-v2/extensions/` | CEF-native extension directory |
| **Socket** | `/tmp/aethelgard_cef.sock` | IPC control |
| **CDP** | `localhost:9222` | Remote debugging |

**Launch:**
```bash
cd /home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2
LD_LIBRARY_PATH="/home/craig/CEF4Delphi/cef_binary_current/Release" DISPLAY=:0 ./bromium
```

## 3. Integration Points

| System | How |
|--------|-----|
| Bromium + Vision | Screenshot → Nemotron Nano Omni → action |
| Distillation (sovereign-distillation) | 7-stage curriculum, 6 teacher models |
| Intelligent Growth (intelligent_growth.py) | DeepSeek R1 code analysis → Qwen3-Coder patch |
| Universal State (sovereign_state_reconstruct.py) | Rebuild from GitHub/Vercel anywhere |
| Perpetual Growth (perpetual_growth_loop.py) | Auto-improves weakest capability each cycle |
| Hyper-Compression (hyper_compress.py) | 5 tiers, up to ~97% token savings |
| 48-Char Compression Dataset | Fine-tune models on lossless block format |
| Tool Forge (tool_forge.py) | Auto-synthesize Python tools from NL specs |
| Irrational Timers (irrational_timers.py) | `random() × π/φ/e/√2/...` wait durations |
