---
name: llama-cpp-service-deployment
category: devops
description: Class-level skill for deploying and troubleshooting llama.cpp inference servers via systemd with GPU acceleration (Vulkan/ROCm/CUDA). Covers service file management, library path resolution, port conflict debugging, health verification, and GPU backend validation.
triggers:
  - Deploying llama-server as systemd user service
  - Debugging exit code 127 (missing shared libraries)
  - Resolving port conflicts on inference endpoints
  - Verifying GPU acceleration (Vulkan/ROCm/CUDA) in llama.cpp logs
  - Switching between llama.cpp builds (official, yuuko-grounders, custom)
  - Configuring KV cache quantization and flash attention
version: 1.0.0
tags:
  - llama.cpp
  - systemd
  - vulkan
  - amd-gpu
  - inference-serving
  - gpu-acceleration
---

# llama.cpp Service Deployment & Troubleshooting

## Overview
This skill covers the end-to-end workflow for running llama.cpp `llama-server` as a systemd user service with GPU acceleration. It captures the repeatable patterns for service file authoring, library dependency resolution, health checking, and GPU backend verification.

## Core Workflow

### 1. Diagnose Failed Service
```bash
# Check service status and recent logs
systemctl --user status <service-name> --no-pager
journalctl --user -u <service-name> --no-pager -n 50

# Exit code 127 = missing binary or shared library
# Check binary dependencies
ldd /path/to/llama-server

# Find required libraries
find / -name "libllama-server-impl.so" 2>/dev/null
find / -name "libggml-vulkan.so*" 2>/dev/null
```

### 2. Select Correct llama.cpp Build
**Key insight**: Not all llama.cpp builds include Vulkan backend. The `yuuko-grounders/build-vulkan` build is verified to include:
- `libggml-vulkan.so.0.13.1` (Vulkan backend for AMD/Intel)
- `libllama-server-impl.so` (server implementation library)
- `llama-server` binary linked against above

```bash
# Verify build has Vulkan
ls -la /path/to/build-vulkan/bin/libggml-vulkan.so*
ldd /path/to/build-vulkan/bin/llama-server | grep vulkan
```

### 3. Patch Service File
**Template** (see `templates/llama-server-vulkan.service`):
```ini
[Service]
Environment=LD_LIBRARY_PATH=/path/to/build-vulkan/bin
ExecStart=/path/to/build-vulkan/bin/llama-server \
    --model /path/to/model.gguf \
    --host 127.0.0.1 --port PORT \
    --api-key KEY \
    --ctx-size CTX \
    -ngl 99 \
    --cache-type-k q8_0 --cache-type-v q8_0 \
    --batch-size BATCH --ubatch-size UBATCH \
    --flash-attn auto \
    --threads N --mlock --no-warmup
```

**Critical fields**:
- `Environment=LD_LIBRARY_PATH` — points to build directory containing `libggml-vulkan.so*` and `libllama-server-impl.so`
- `ExecStart` — uses the SAME build directory's `llama-server` binary
- `-ngl 99` — offload all layers to GPU
- `LimitMEMLOCK=infinity` + `--mlock` — lock model in RAM (requires `ulimit -l unlimited` or systemd `LimitMEMLOCK`)

### 4. Resolve Port Conflicts
```bash
# Find process on port
lsof -ti:PORT
ss -ltnp | grep :PORT

# Kill if stray process (not managed by systemd)
kill -9 PID

# Then restart service
systemctl --user restart <service-name>
```

### 5. Verify GPU Acceleration
```bash
# Check journal for Vulkan device detection
journalctl --user -u <service-name> --no-pager | grep -i vulkan

# Expected output:
# ggml_vk_init: found 1 Vulkan devices
# Vulkan0 : AMD Radeon 740M Graphics (RADV PHOENIX2) (12800 MiB, 11827 MiB free)

# Health check
curl -s http://localhost:PORT/health -H "Authorization: Bearer KEY"
# {"status":"ok"}

# Generation test
curl -s -X POST http://localhost:PORT/completion \
  -H "Authorization: Bearer KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test","n_predict":10,"temperature":0}'
```

### 6. AMD GPU Specifics (RADV/Mesa)
- **No ROCm required** — Vulkan via Mesa RADV driver works for AMD 700M/600M series
- **Hardware**: HawkPoint2 [1002:1901] = Radeon 740M (Phoenix2)
- **Vulkan ICD**: `/usr/share/vulkan/icd.d/radeon_icd.x86_64.json` (provided by `mesa-vulkan-drivers`)
- **Verify**: `vulkaninfo | grep -i "device name"`

## Common Pitfalls & Fixes

| Symptom | Root Cause | Fix |
|---------|------------|-----|
| Exit code 127 | Binary linked to libs only in build dir | Set `LD_LIBRARY_PATH` in service `Environment=` |
| "couldn't bind HTTP server socket" | Port held by another llama-server | `lsof -ti:PORT && kill -9` then restart |
| "no devices with dedicated memory found" | llama.cpp can't detect GPU VRAM | Harmless warning; `-ngl 99` still works with Vulkan |
| MLOCK warning | RLIMIT_MEMLOCK soft limit too low | Add `LimitMEMLOCK=infinity` to `[Service]` |
| Vulkan not found | Wrong build (no vulkan backend) | Use `yuuko-grounders/build-vulkan` or build with `-DGGML_VULKAN=ON` |

## Service Templates

See `templates/` directory for ready-to-use service files:
- `llama-server-vulkan.service` — Base template for Vulkan-enabled llama-server
- `hermes-lfm12.service` — LFM 1.2B Nova function-calling model (port 8080, ctx 49152)
- `hermes-vl.service` — LFM2-VL vision model (port 8086, ctx 8192, mmproj)

## Verification Checklist

After deployment, verify all:
- [ ] `systemctl --user status <service>` shows `active (running)`
- [ ] `journalctl -u <service> | grep -i vulkan` shows device detection
- [ ] `curl /health` returns `{"status":"ok"}`
- [ ] Generation request returns tokens at expected speed (>20 tok/s for 1B models)
- [ ] `n_slots` = 4 (default) for concurrent request handling
- [ ] KV cache using `q8_0` (check logs for `cache_type_k = q8_0`)

## Integration with Hermes Unified Field

These services register as fleet daemons accessible via:
- `hermes-lfm12` → port 8080 (Architect/Foreman tier)
- `hermes-vl` → port 8086 (Vision/Doer tier)
- Both exposed to `uf_integrator.py` via `aethelgard-model-service` skill

## References
- `references/amd-vulkan-gpu-detection.md` — GPU hardware detection commands
- `references/yuuko-grounders-build-notes.md` — Why this specific build works
- `references/port-conflict-resolution.md` — Stray process handling patterns