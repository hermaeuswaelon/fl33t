# Current Fleet Configuration

Built 2026-07-18 on Phoenix APU (Ryzen 5, Radeon 740M). Both models rebuilt with `-DGGML_VULKAN=ON`.

## Running Services

### LFM2.5-1.2B-Nova (Planner) — Port 8080
- **Service:** hermes-lfm12.service (systemd user)
- **Model:** LFM2.5-1.2B-Nova-Function-Calling.Q6_K.gguf (919 MB)
- **Ctx:** 49152 (48k)
- **Speed:** 38.1 t/s gen, 108 t/s prompt
- **Flags:** `-ngl 99 --cache-type-k q8_0 --cache-type-v q8_0 --flash-attn auto -t 6 --mlock`
- **Key:** lfm-local-key

### lfm2-vl-gui-sft (Vision) — Port 8086
- **Service:** hermes-vl.service (systemd user)
- **Model:** lfm2-vl-gui-sft-q4_k_m.gguf (219 MB) + mmproj-lfm2-vl-gui-sft-q8_0.gguf (101 MB)
- **Ctx:** 8192 (8k)
- **Speed:** 105.2 t/s gen, 164 t/s prompt
- **Flags:** `-ngl 99 --cache-type-k q8_0 --cache-type-v q8_0 --flash-attn auto -t 6 --mlock`
- **Key:** vl-local-key

### Deprecated / Stopped
- LFM2-2.6B-Uncensored (old planner): stopped. Was 1.8 t/s on CPU. Replaced by 1.2B at 38 t/s.

## Vulkan Details
- **Device:** AMD Radeon 740M Graphics (RADV PHOENIX2)
- **VRAM:** 8155 MiB total, ~5861 MiB free with both models loaded
- **Driver:** mesa-vulkan-drivers 26.0.3
- **ICD:** /usr/share/vulkan/icd.d/radeon_icd.json
- **Version:** Vulkan 1.4.341
- **llama-server:** Built from source, installed at /usr/local/bin/llama-server-vulkan

## Model Files
All in /home/craig/models/:
- LFM2.5-1.2B-Nova-Function-Calling.Q6_K.gguf (919 MB)
- lfm2-vl-gui-sft-q4_k_m.gguf (219 MB)
- mmproj-lfm2-vl-gui-sft-q8_0.gguf (101 MB)
- LFM2-2.6B-Uncensored-X64.i1-Q6_K.gguf (2.0 GB, stopped)

## Service Files
- ~/.config/systemd/user/hermes-lfm12.service
- ~/.config/systemd/user/hermes-vl.service
