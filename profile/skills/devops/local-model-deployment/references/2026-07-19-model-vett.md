# Local Model Vett — Session 2026-07-19

## System
- CPU: AMD HawkPoint2, 6 threads, amd-pstate-epp performance governor
- GPU: AMD integrated (512MB VRAM), Vulkan 1.4.341
- RAM: 14GB total, ~4.5GB baseline
- llama.cpp: ~/llama.cpp-yuuko-grounders/build-vulkan/bin/llama-server
- Profile: thotheauphis

## Models Tested

### LFM2.5-1.2B-Nova-Function-Calling.Q6_K.gguf (919MB)
- **Port**: :8080
- **Speed**: 153 tok/s generation
- **Load**: Instant
- **Text**: ✅ All tests passed (QA, system prompt, function calling, JSON, multi-turn, high-temp, Chinese)
- **Verdict**: KEEP — primary text model
- **Ctx**: 49152, ngl 99, flash-attn auto, mlock
- **API key**: lfm-local-key

### Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf (4.4GB) + mmproj (1.3GB)
- **Port**: :8088
- **Speed**: ~17s image processing, ~15 tok/s generation
- **Load**: ~30s
- **Vision**: ✅ Color ID (red/green/blue/white/black), OCR (Hello World), complex scenes — all correct
- **Format**: Requires base64 data URIs only. URLs fail ("Failed to download image"). Tiny/broken PNGs fail.
- **Verdict**: KEEP — only working vision model
- **Ctx**: 16384, ngl 99, image-min-tokens 1024
- **API key**: qwen-vl-key

### LocateAnything-3B-Q4_K_M.gguf (2.0GB) + mmproj (833MB)
- **Port**: :8086
- **Speed**: 19 tok/s
- **Vision**: ❌ Prompt-mirroring — answers "What color is this?" instead of the color
- **Chat template tested**: chatml, peg-native — same result
- **Verdict**: REJECT — vision encoder broken with this llama.cpp build

### LFM2-VL-GUI-SFT.gguf (679MB, full) / -q4_k_m.gguf (219MB, Q4) + mmproj (101MB)
- **Port**: :8086
- **Speed**: 127 tok/s
- **Vision**: ❌ Hallucinates — "A is in the middle" for solid color, "Fashion is a picture" for simple shapes
- **Verdict**: REJECT — vision output unreliable

## Final Stack
```
:8080 = LFM 1.2B Nova (text + function calling)  ← default for Hermes/Warp
:8088 = Qwen2.5-VL 7B (vision + text)             ← use sparingly for vision tasks
```

## Port Allocation Convention
- :8080 — primary text model (LFM)
- :8088 — vision model (Qwen2.5-VL)
- :8086 — dead / abandoned models (was: LocateAnything, LFM2-VL)

## Notes
- All VL models except Qwen2.5-VL were unusable for vision tasks
- Qwen is slow but is the only local option that works
- No systemd auto-restart services — manual launch only
- Background processes must use Hermes `background=true`, NOT shell `&`
