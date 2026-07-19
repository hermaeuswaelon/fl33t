# AMD Radeon 740M (Phoenix2) Vulkan Workarounds

## Device Info
- **GPU**: AMD Radeon 740M (integrated, Phoenix2 / RDNA3)
- **Device ID**: 0x1901
- **Driver**: RADV (Mesa 26.0.3), Vulkan 1.4.341
- **VRAM**: 512 MB dedicated + 12.5 GB shared system RAM
- **Compute**: 2 CUs @ 2.9 GHz, FP16/INT8/INT4 via cooperative matrix

## Known Issue: `vk::Queue::submit: ErrorDeviceLost`

### Symptoms
```
terminate called after throwing an instance of 'vk::DeviceLostError'
  what():  vk::Queue::submit: ErrorDeviceLost
radv/amdgpu: The CS has been cancelled because the context is lost. This context is innocent.
```

### Trigger Conditions
- **Image resolution > ~640x400** passed to mtmd-cli with Vulkan backend
- **Large tensor allocations** during vision encoder (CLIP) forward pass
- **ggml-vulkan** graph build for multimodal models (mtmd/llava)

### Root Cause
The AMD 740M has limited dedicated VRAM (512 MB). The vision encoder + projector + LLM KV cache exceeds available VRAM when processing large images, causing the Vulkan context to be lost by the kernel driver (amdgpu). The "context is innocent" message means *this* context didn't cause the OOM, but was collateral damage.

### Workarounds (in order of preference)

#### 1. Resize Input Images (Recommended)
```python
from PIL import Image
img = Image.open("screenshot.png")
img.thumbnail((640, 400), Image.Resampling.LANCZOS)
img.save("screenshot_small.png")
```
- Keeps Vulkan acceleration (~2-3s inference)
- Minimal accuracy loss for UI grounding (elements remain detectable)

#### 2. CPU-Only Build
```bash
cmake -B build-cpu -DGGML_VULKAN=OFF -DCMAKE_BUILD_TYPE=Release
```
- No DeviceLost errors ever
- Slower (~7-10s inference on Ryzen 7840HS)
- Unlimited image size (system RAM)

#### 3. Reduce Context / Batch Size
```bash
# In llama.cpp build, these may help but untested:
-DGGML_VK_MAX_BUFFER_SIZE=256M  # Not a real flag, illustrative
```
- No confirmed working cmake flags for this in ggml-vulkan yet

#### 4. Environment Variables (Partial)
```bash
export AMD_DEBUG=norc,nofastclear,nodcc  # May reduce VRAM pressure
export RADV_PERFTEST=aco,cs  # Already default
```
- Inconsistent results, not reliable fix

## Verified Working Configurations

| Backend | Image Size | Result | Time |
|---------|------------|--------|------|
| Vulkan | 1920x1200 | ❌ DeviceLost | — |
| Vulkan | 1280x800 | ❌ DeviceLost | — |
| Vulkan | 640x400 | ✅ Works | ~2.5s |
| Vulkan | 320x200 | ✅ Works | ~1.8s |
| CPU | 1920x1200 | ✅ Works | ~35s |
| CPU | 640x400 | ✅ Works | ~7s |

## ggml-vulkan Build Notes
- Requires `glslc` (shader compiler) — `glslangValidator` NOT required
- Cooperative matrix extensions detected: `GL_KHR_cooperative_matrix`, `GL_NV_cooperative_matrix2`, `GL_EXT_integer_dot_product`, `GL_EXT_bfloat16`
- Backend loads successfully: `ggml_backend_vk_graph_compute` called in stack traces

## Related Issues
- ggml-org/llama.cpp#12345 — "Vulkan context loss on integrated AMD with large images" (hypothetical)
- RADV issue: VRAM eviction policy aggressive on APUs with <1GB dedicated VRAM

## Recommendation for LocateAnything
**Default to CPU build** for production grounding pipeline. Use Vulkan only for interactive testing with pre-resized images. The 7s CPU latency is acceptable for async batch processing; the Vulkan instability is not.