---
name: local-model-serving
title: Local Model Serving (llama.cpp)
category: dev
description: Build, configure, and optimize llama.cpp server instances with Vulkan GPU offload, context sizing, and systemd management.
trigger: User asks to run a local GGUF model, optimize inference speed, set context limits, build llama.cpp, or create a model service.
---

# Local Model Serving — llama.cpp

Building and optimizing llama-server instances for local model inference, with focus on AMD APU (Radeon 740M/780M) Vulkan offload.

## Building with Vulkan Support

The Debian-packaged `llama-server` lacks Vulkan backend. Build from source:

```bash
# Dependencies
sudo apt-get install -y glslc spirv-headers glslang-dev libshaderc-dev libvulkan-dev

# Configure with Vulkan
cd /path/to/llama.cpp
cmake -B build -DGGML_VULKAN=ON -DGGML_CUDA=OFF -DLLAMA_SERVER=ON -DCMAKE_BUILD_TYPE=Release

# Build just the server
cmake --build build --target llama-server -j$(nproc)

# Install alongside system package
sudo cp build/bin/llama-server /usr/local/bin/llama-server-vulkan
```

### Verify GPU Detection

```bash
/usr/local/bin/llama-server-vulkan --list-devices
# Expected: Vulkan0: AMD Radeon 740M/780M Graphics (RADV)
```

## Optimization Flags (AMD APU)

| Flag | Purpose | Always? |
|------|---------|---------|
| `-ngl 99` | Offload all layers to GPU | ✅ |
| `--cache-type-k q8_0 --cache-type-v q8_0` | KV cache quant | ✅ |
| `--flash-attn auto` | Flash attention | ✅ |
| `-t N` | Threads = physical cores (6c/12t → -t 6) | ✅ |

### Expected Speed Gains (CPU → GPU)

| Model | CPU t/s | GPU t/s | Uplift |
|-------|---------|---------|--------|
| ≤300M (VL) | 7-8 | 100-110 | 14× |
| 1.2B (Q6_K) | 30-32 | 37-40 | +22% |

## Context Size Guidelines

| Model Role | Recommended Ctx | Rationale |
|------------|----------------|-----------|
| Planner (1-2B) | 49152 (48k) | Multi-turn with scan histories |
| Vision (≤300M) | 8192 (8k) | Image + short instruction |
| Chat | Model's trained length | Don't exceed without RoPE scaling |

**KV Cache Memory:** 1.2B @ 48k + q8_0 KV ≈ 3.2GB total. VL 219M @ 8k ≈ 500MB.

## systemd Service Template

```ini
[Service]
ExecStart=/usr/local/bin/llama-server-vulkan \
    --model /path/to/model.gguf \
    --host 127.0.0.1 --port 8080 \
    --api-key my-key \
    --ctx-size 49152 \
    -ngl 99 \
    --cache-type-k q8_0 --cache-type-v q8_0 \
    --batch-size 512 --ubatch-size 256 \
    --flash-attn auto \
    --threads 6 --mlock --no-warmup
Restart=on-failure
RestartSec=5
Nice=5
```

## BIOS Tuning (One-Time)

For Radeon 740M/780M APUs: UMA Frame Buffer Size in BIOS controls VRAM carveout. Default 2-4GB. Bump to 8GB+ for larger model offload. Look for "UMA Frame Buffer Size" or "Variable Graphics Memory (VGM)".

## Pitfalls

- **glslc not found**: Install `glslc` package (standalone, not shaderc)
- **SPIRV-Headers cmake error**: Install `spirv-headers` AND `libshaderc-dev`
- **No Vulkan devices**: Missing `mesa-vulkan-drivers` or binary built without `-DGGML_VULKAN=ON`
- **SMT threads hurt**: On 6c/12t, use `-t 6` (physical), not `-t 12`
- **Two models same GPU**: For concurrent use, consider single server with `--parallel` + `--cont-batching`
