# yuuko-grounders llama.cpp Build Notes

## Why This Build Works

The `yuuko-grounders/build-vulkan` build is the **only** local llama.cpp build that includes:
1. **Vulkan backend** (`libggml-vulkan.so.0.13.1` - 58MB)
2. **Server implementation library** (`libllama-server-impl.so`)
3. **Linked llama-server binary** that actually loads both

Other builds tested:
- `/usr/local/bin/llama-server-vulkan` — 17KB stub, missing `libllama-server-impl.so`
- Official Debian `llama-server` — CPU only, no Vulkan backend
- Custom builds without `-DGGML_VULKAN=ON` — no Vulkan support

## Build Configuration (Reference)

```bash
# From llama.cpp-yuuko-grounders repo
cmake -B build-vulkan \
  -DGGML_VULKAN=ON \
  -DGGML_NATIVE=OFF \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_SERVER=ON \
  -DLLAMA_CURL=ON
cmake --build build-vulkan --config Release -j$(nproc)
```

## Critical Artifacts

| Artifact | Path | Size | Purpose |
|----------|------|------|---------|
| llama-server | `build-vulkan/bin/llama-server` | ~18MB | Main binary |
| libllama-server-impl.so | `build-vulkan/bin/libllama-server-impl.so` | ~12MB | Server logic (HTTP, slots, etc.) |
| libggml-vulkan.so.0.13.1 | `build-vulkan/bin/libggml-vulkan.so.0.13.1` | ~58MB | Vulkan compute backend |
| libggml-base.so.0 | `build-vulkan/bin/libggml-base.so.0` | ~ | Core GGML |
| libggml-cpu.so.0 | `build-vulkan/bin/libggml-cpu.so.0` | ~ | CPU fallback |

## Deployment Pattern

**DO NOT** copy binaries to `/usr/local/bin` — they lose library references.

**DO** run directly from build directory with `LD_LIBRARY_PATH`:
```bash
LD_LIBRARY_PATH=/home/craig/llama.cpp-yuuko-grounders/build-vulkan/bin \
  /home/craig/llama.cpp-yuuko-grounders/build-vulkan/bin/llama-server ...
```

Or in systemd:
```ini
Environment=LD_LIBRARY_PATH=/home/craig/llama.cpp-yuuko-grounders/build-vulkan/bin
ExecStart=/home/craig/llama.cpp-yuuko-grounders/build-vulkan/bin/llama-server ...
```

## Version Info

```
build_info: b8681-Debian  (from journalctl)
```
This corresponds to llama.cpp commit `b8681` (post-b4000, pre-b5000 era) with Vulkan patches from yuuko-grounders fork.

## Known Quirks

1. **MLOCK warning**: `warning: failed to mlock 57MB buffer` — harmless, model still loads; add `LimitMEMLOCK=infinity` to service
2. **Context fit warning**: `n_ctx_seq (8192) < n_ctx_train (128000)` — model trained on 128k, running at 8k; expected for VL model
3. **Speculative decoding warnings**: `no implementations specified for speculative decoding` — harmless, feature not configured
4. **SWA/cache warnings**: `forcing full prompt re-processing due to lack of cache data` — Sliding Window Attention behavior with recurrent models (LFM2), expected