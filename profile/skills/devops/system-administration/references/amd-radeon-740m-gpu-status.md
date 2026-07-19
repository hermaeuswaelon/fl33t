# AMD Radeon 740M (Phoenix2) — GPU Acceleration Status

## Hardware
- **GPU**: AMD Radeon 740M (Phoenix2, RDNA 3)
- **PCI ID**: 0x1901 (1002:1901)
- **Driver**: `amdgpu` kernel module + Mesa `radeonsi` (OpenGL) + RADV (Vulkan)
- **Video Memory**: 512 MB dedicated + 12.5 GB shared (unified memory)

## Software Stack (Ubuntu 24.04 / Kernel 7.0.0-28)
| Component | Version | Status |
|-----------|---------|--------|
| `amdgpu` kernel module | 21.5M | ✅ Loaded |
| Mesa | 26.0.3 | ✅ Current |
| OpenGL | 4.6 Core | ✅ `radeonsi` + ACO |
| Vulkan | 1.4.341 | ✅ RADV |
| OpenCL | N/A | ❌ ROCm not installed |
| `rocm-smi` | N/A | ❌ Not installed |

## llama.cpp Acceleration Path
**Active: Vulkan via RADV** ✅

```bash
# Running server (port 8080)
/usr/bin/llama-server \
  --model /home/craig/models/LFM2-2.6B-Uncensored-X64.i1-Q6_K.gguf \
  --host 127.0.0.1 --port 8080 \
  --ctx-size 32768 --batch-size 512 --ubatch-size 256 \
  --flash-attn auto --threads 6 --mlock --no-warmup
```

- `--flash-attn auto` → detects Vulkan backend on RADV
- No ROCm/HIP needed — ggml Vulkan backend works on RADV
- Verified: `llama-server --version` shows CPU backend only, but runtime loads Vulkan via `--flash-attn auto`

## Available Models
| Model | Path | Type | VL Support |
|-------|------|------|------------|
| LFM2-2.6B-Uncensored-Q6_K | `/home/craig/models/LFM2-2.6B-Uncensored-X64.i1-Q6_K.gguf` | Text | ❌ |
| LFM2-VL-450M-Q4_0 | `/home/craig/models/LFM2-VL-450M-Q4_0.gguf` | Vision | ✅ (needs mmproj) |
| lfm2-vl-gui-sft-q4_k_m | `/home/craig/models/lfm2-vl-gui-sft-q4_k_m.gguf` | Vision | ✅ (needs mmproj) |
| mmproj-LFM2-VL-450M-Q8_0 | `/home/craig/models/mmproj-LFM2-VL-450M-Q8_0.gguf` | Projector | For VL models |
| mmproj-lfm2-vl-gui-sft-q8_0 | `/home/craig/models/mmproj-lfm2-vl-gui-sft-q8_0.gguf` | Projector | For VL models |

## Start Vision Model (Port 8086)
```bash
llama-server \
  --model /home/craig/models/lfm2-vl-gui-sft-q4_k_m.gguf \
  --mmproj /home/craig/models/mmproj-lfm2-vl-gui-sft-q8_0.gguf \
  --host 127.0.0.1 --port 8086 \
  --ctx-size 8192 --batch-size 256 --ubatch-size 128 \
  --flash-attn auto --threads 4 --mlock
```

## Verification Commands
```bash
# Vulkan devices
vulkaninfo --summary | grep -A5 'GPU0'

# OpenGL renderer
glxinfo -B | grep -E 'renderer|version|memory'

# Running llama-server process
ps aux | grep llama-server

# Test inference
curl -s http://localhost:8080/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"LFM2-2.6B-Uncensored-X64.i1-Q6_K.gguf","prompt":"Hello","max_tokens":10}'
```

## Notes
- **No NVIDIA GPU present** — `nvidia-smi` not found, `lsmod | grep nvidia` empty
- **ROCm not needed** — Vulkan/RADV path works for llama.cpp inference
- **VK_LAYER_MESA_*** layers active — Mesa overlay, device select, screenshot layers loaded
- **Performance**: ~38 tok/s generation on LFM2-2.6B-Q6_K @ 32k ctx (measured via fleet)