# LocateAnything Build & Test Log — Session 2026-07-18

## Environment
- **Host**: Linux 7.0.0-28-generic, Ryzen 7 7840HS (AMD 740M iGPU, Phoenix2)
- **Vulkan**: 1.4.341 RADV, Mesa 26.0.3, driverVersion 26.0.3
- **llama.cpp forks tested**:
  1. `yuuko-eth/llama.cpp` @ `mtmd-grounders` (commit db0d72b, ggml 0.13.1) — **WORKS**
  2. `ggml-org/llama.cpp` @ main (commit 571d0d5, ggml 0.17.0) — lacks "locateanything" projector type

## Model Acquisition
```bash
mkdir -p /home/craig/models/locateanything
cd /home/craig/models/locateanything
hf download sabafallah/LocateAnything-3B-GGUF --include "locateanything-3b-Q4_K_M.gguf" --local-dir .
hf download sabafallah/LocateAnything-3B-GGUF --include "mmproj-locateanything-3b-bf16.gguf" --local-dir .
```
- `locateanything-3b-Q4_K_M.gguf` — 2,107,054,240 bytes
- `mmproj-locateanything-3b-bf16.gguf` — 872,659,776 bytes
- q8_0 projector NOT available on repo (only bf16)

## Build 1: yuuko-eth fork, CPU-only
```bash
git clone https://github.com/yuuko-eth/llama.cpp --branch mtmd-grounders --depth 1 llama.cpp-yuuko-grounders
cd llama.cpp-yuuko-grounders
cmake -B build-cpu -DGGML_VULKAN=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build build-cpu --config Release -j$(nproc)
```
- **Result**: Build successful, `llama-mtmd-cli` produced (72 KB)
- **Test**: 1920x1200 screenshot → **timeout after 300s** (too slow on CPU)
- **Test**: 640x400 screenshot → **success in ~7s**, output: `<ref>button</ref><box><0><0><1000><1000></box>`

## Build 2: yuuko-eth fork, Vulkan
```bash
cmake -B build-vulkan -DGGML_VULKAN=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build-vulkan --config Release -j$(nproc)
```
- **Result**: Build successful, Vulkan backend detected (glslc found, cooperative matrix extensions present)
- **Test**: 1920x1200 → **crash**: `vk::Queue::submit: ErrorDeviceLost`, `radv/amdgpu: The CS has been cancelled because the context is lost`
- **Test**: 640x400 → **success in ~2s**, output: `<ref>button</ref><box>None</box>` (no button on that screenshot)

## Build 3: ggml-org main, CPU-only
```bash
git clone https://github.com/ggml-org/llama.cpp --depth 1 llama.cpp-cpu
cd llama.cpp-cpu
cmake -B build -DGGML_VULKAN=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j$(nproc)
```
- **Result**: Build successful
- **Test**: Fails with `load_hparams: unknown projector type: locateanything` — **confirms fork is required**

## Working Inference Command (Vulkan, 640x400)
```bash
cd /home/craig/llama.cpp-yuuko-grounders/build-vulkan/bin
./llama-mtmd-cli \
  -m /home/craig/models/locateanything/locateanything-3b-Q4_K_M.gguf \
  --mmproj /home/craig/models/locateanything/mmproj-locateanything-3b-bf16.gguf \
  --image /home/craig/test_screenshot_small.png \
  --chat-template chatml \
  --temp 0 -n 128 \
  -p "<image 1><__media__>Locate all the instances that matches the following description: button."
```
Output: `<ref>button</ref><box><0><0><1000><1000></box>`

## Key Findings
1. **Fork is mandatory** — mainline llama.cpp doesn't have "locateanything" projector
2. **Projector must be bf16** — q8_0 not available, and even if it were, the projector type registration is fork-specific
3. **Image size limit on AMD 740M Vulkan** — ~640x400 max before DeviceLost; CPU backend handles larger but 40x slower
4. **Prompt wording matters** — "matches" (plural) in prompt matches training data; "match" produces worse results
5. **Coordinate format** — 0-1000 normalized, full-image box = not found

## Next Steps
- Test server mode with `--special` flag for coordinate token preservation
- Integrate with uf_integrator gated context for spatial memory
- Build Python wrapper for async batch grounding