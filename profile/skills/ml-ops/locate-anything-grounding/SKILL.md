---
name: locate-anything-grounding
version: "1.0"
category: ml-ops
tags: [locateanything, ui-grounding, multimodal, llama.cpp, vulkan, amd-740m]
description: |
  Build, test, and deploy LocateAnything 3B UI grounding model for coordinate extraction from screenshots.
  Uses yuuko-eth/llama.cpp mtmd-grounders fork for custom projector support.
---

# LocateAnything UI Grounding Model Skill

## Overview
LocateAnything is a 3B parameter multimodal model for UI element grounding — given a screenshot and natural language description, it returns bounding boxes in the format `<ref>label</ref><box><x1><y1><x2><y2></box>` with coordinates normalized 0-1000.

## Model Files
- **Weights**: `locateanything-3b-Q4_K_M.gguf` (~2.1 GB)
- **Projector**: `mmproj-locateanything-3b-bf16.gguf` (~872 MB, bf16 required — q8_0 fails)
- **Source**: `sabafallah/LocateAnything-3B-GGUF` on Hugging Face

## Required Fork
**yuuko-eth/llama.cpp branch `mtmd-grounders`** — standard llama.cpp lacks the "locateanything" projector type. This fork adds:
- Custom projector type registration in `llava.cpp`
- Coordinate token preservation via `--special` flag (or equivalent)
- Grounding-specific chat template handling

## Build Commands
```bash
# CPU-only build (stable, no device-lost errors)
git clone https://github.com/yuuko-eth/llama.cpp --branch mtmd-grounders --depth 1 llama.cpp-locateanything
cd llama.cpp-locateanything
cmake -B build -DGGML_VULKAN=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j$(nproc)

# Vulkan build (faster but unstable on AMD 740M with large images)
cmake -B build-vulkan -DGGML_VULKAN=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build-vulkan --config Release -j$(nproc)
```

## Inference CLI (mtmd-cli)
```bash
./llama-mtmd-cli \
  -m /path/to/locateanything-3b-Q4_K_M.gguf \
  --mmproj /path/to/mmproj-locateanything-3b-bf16.gguf \
  --image /path/to/screenshot.png \
  --chat-template chatml \
  --temp 0 -n 128 \
  -p "<image 1><__media__>Locate all the instances that matches the following description: submit button."
```

## Critical Parameters
- **Image size**: Must be ≤640x400 on AMD 740M Vulkan to avoid `ErrorDeviceLost` (VK context loss). CPU backend handles larger images but slower.
- **Projector**: Must use bf16 (`mmproj-locateanything-3b-bf16.gguf`), not q8_0 — q8_0 fails with "unknown projector type: locateanything"
- **Prompt format**: `<image 1><__media__>Locate all the instances that matches the following description: <query>.` (note "matches" not "match")
- **Temperature**: 0 (deterministic grounding)
- **Output parsing**: Coordinates are 0-1000 normalized. Convert to pixels: `pixel = coord / 1000 * image_dimension`

## Output Format
```
<ref>submit button</ref><box><123><456><789><1011></box>
```
- `<ref>`: detected label
- `<box>`: x1, y1, x2, y2 in 0-1000 space
- `<box>None</box>` or `<box><0><0><1000><1000></box>` = not found / full image

## AMD 740M / RADV Specific Workarounds
| Issue | Cause | Fix |
|-------|-------|-----|
| `vk::Queue::submit: ErrorDeviceLost` | VRAM/context loss on large image encode | Resize image to ≤640x400 before inference |
| `radv/amdgpu: CS cancelled context lost` | Same as above | Use CPU backend (`-DGGML_VULKAN=OFF` build) |
| Slow CPU inference | No GPU acceleration | Acceptable for grounding (~7s on Ryzen 7 7840HS) |

## Server Mode (Experimental)
The fork supports server mode but requires `--special` flag to preserve coordinate tokens. Not yet tested in this session.

## Integration with Unified Field (uf_integrator)
- Gate tool outputs via `gate_injectable()` → pointer refs
- Recall via `recall(query, k=3)` for spatial memory
- Checkpoint before/after grounding calls via `uf checkpoint`

## References
- `references/locate-anything-build-log.md` — full build + test transcript
- `references/amd-740m-vulkan-workarounds.md` — device-lost error analysis