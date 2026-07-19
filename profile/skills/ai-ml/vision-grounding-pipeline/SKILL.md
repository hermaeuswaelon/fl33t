---
name: vision-grounding-pipeline
category: ai-ml
description: Deploy, operate, and extend the sovereign vision grounding fleet (LocateAnything + LFM2-VL + SVA + click automation + batch processing)
triggers:
  - "ground UI element"
  - "find button"
  - "click icon"
  - "vision question answering"
  - "batch grounding"
  - "spatial memory"
  - "projector LoRA"
  - "optical mesh calibration"
version: "1.0"
---

# Vision Grounding Pipeline Skill

**Class-level skill** for deploying, operating, and extending the sovereign vision grounding fleet: LocateAnything (grounding) + LFM2-VL (VQA) + unified routing + spatial memory (SVA) + click automation + batch processing.

## Trigger Conditions
- User needs to locate UI elements in screenshots ("find button", "click icon")
- User wants visual question answering on GUI screenshots
- User needs batch grounding across multiple screenshots
- User wants persistent spatial memory across sessions
- User wants to automate clicks from vision model predictions
- User needs few-shot data collection for projector LoRA fine-tuning

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    VISION ROUTER (port 8088)                 │
│  /ground endpoint → routes: grounding→8087, VQA→8086        │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │  8087   │        │  8086   │        │  8080   │
   │LocateAny│        │ LFM2-VL │        │ LFM2-1.2B│
   │  thing  │        │ GUI-SFT │        │  Nova   │
   │grounding│        │  VQA    │        │  text   │
   └────┬────┘        └────┬────┘        └────┬────┘
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────────────────────────────────────────────┐
   │           SVA HYPERSPACE (1024-D binary)        │
   │   Hamming similarity, session recall, persist   │
   └────────────────────┬────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   ┌─────────┐    ┌────────────┐  ┌──────────┐
   │WarpClick│    │ EmergeSync │  │BatchWork │
   │ xdotool │    │(blocked)   │  │Parallel  │
   └─────────┘    └────────────┘  └──────────┘
```

## Core Tools (in `/home/craig/tools/`)

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `vision_router.py` | Unified `/ground` HTTP endpoint | `--image`, `--prompt`, `--output-json` |
| `locate_parser.py` | Parse coords, draw boxes, JSON out | `--input-json`, `--draw`, `--size` |
| `sva_grounding.py` | 1024-D spatial memory store/recall | `--store`/`--recall`, `--label`, `--k` |
| `warp_click.py` | Grounding → xdotool click | `--from-json`, `--dry-run` |
| `vision_workflow.py` | 3-tier LangGraph pipeline | `--goal`, `--images`, `--prompts` |
| `batch_grounding.py` | ParallelExecutorNode for N×M | `--images`, `--prompts`, `--workers` |
| `optical_mesh_calibration.py` | DPI/device correction learning | `--calibrate`, `--correct` |
| `lora_data_collector.py` | Few-shot projector training data | `--collect`, `--batch`, `--export` |
| `emerge_grounding_sync.py` | Emerge durability (blocked) | `--sync`, `--recall`, `--stats` |

## Verified End-to-End Flow

```bash
# 1. Ground UI element
python3 vision_router.py --image screen.png --prompt "button" --output-json /tmp/out.json

# 2. Store in SVA hyperspace
python3 sva_grounding.py --store --label button --box 100 200 300 400 --image screen.png --prompt "Locate button" --session mysession

# 3. Recall similar
python3 sva_grounding.py --recall --label button --k 5

# 4. Dry-run click plan
python3 warp_click.py --from-json /tmp/out.json --dry-run

# 5. Execute click (autonomy loop)
python3 warp_click.py --from-json /tmp/out.json
```

## Deployment Commands

```bash
# Start all 4 services (run each in separate tmux/screen)
# 1. LocateAnything grounding (port 8087)
cd ~/llama.cpp-yuuko-grounders/build-vulkan/bin
./llama-server -m ~/models/locateanything/locateanything-3b-Q4_K_M.gguf \
  --mmproj ~/models/locateanything/mmproj-locateanything-3b-bf16.gguf \
  -c 8192 --flash-attn auto -ngl 99 --port 8087 --special

# 2. LFM2-VL VQA (port 8086)
./llama-server -m ~/models/lfm2-vl-gui-sft-q4_k_m.gguf \
  --mmproj ~/models/mmproj-lfm2-vl-gui-sft-q8_0.gguf \
  -c 32768 --flash-attn auto -ngl 99 --port 8086

# 3. LFM2-1.2B text (port 8080) - already running via systemd

# 4. Vision Router (port 8088)
cd ~/tools && python3 vision_router_server.py
```

## Pitfalls & Gotchas

### LocateAnything Coordinate Format
- Output: `<ref>label</ref><box><x1><y1><x2><y2></box>` — coordinates are **0-1000 normalized**
- Must convert to pixels: `pixel = int(norm / 1000 * image_dim)`
- The parser handles this but raw output needs manual conversion

### Vision Router Routing Logic
- Prompts starting with "what", "describe", "explain", "?" → LFM2-VL (8086)
- Prompts like "button", "icon", "find X" → LocateAnything (8087)
- Force routing: `--force-route locateanything` or `--force-route lfm2-vl`

### SVA Vector Storage
- Vectors stored as raw 1024-bit binary in `/tmp/sva/vectors/{hash}.bin`
- Index at `/tmp/sva/vectors/grounding_index.json` with metadata
- Similarity = Hamming distance (XOR + popcount), no numpy needed
- **Ephemeral**: survives reboot only if synced to Emerge (currently blocked)

### Warp Click Coordinate Mapping
- Assumes screenshot displayed at known screen position
- `--dry-run` shows planned clicks without executing
- Uses `xdotool mousemove x y click 1` — requires X11 (not Wayland)

### Emerge Sync Blocked
**Current state**: Emerge node uses Z0RPC + dill serialization requiring custom class definitions with inspectable source.
- Plain `dict` objects fail: "`<class 'dict'>` is a built-in class"
- CLI `update` command doesn't accept file arguments
- **Workaround**: Define `GroundingObject` class in an importable package, install in emerge-node's Python environment, then use `emerge.Client.store(obj)`

### Vulkan on 740M
- All llama-servers built with `-DGGML_VULKAN=ON`
- Use `-ngl 99 --cache-type-k q8_0 --cache-type-v q8_0`
- Context sizes: 8k (LocateAnything), 32k (LFM2-VL), 48k (LFM2-1.2B)

## Maintenance Commands

```bash
# Check all services
ps aux | grep -E "(llama-server|vision_router)" | grep -v grep

# Test grounding endpoint
curl -s -X POST http://127.0.0.1:8088/ground \
  -H "Content-Type: application/json" \
  -d '{"image": "'$(base64 -w0 screen.png)'", "prompt": "button"}'

# Test VQA endpoint
curl -s -X POST http://127.0.0.1:8088/ground \
  -H "Content-Type: application/json" \
  -d '{"image": "'$(base64 -w0 screen.png)'", "prompt": "What is in this image?"}'

# SVA stats
python3 sva_grounding.py --stats

# Batch grounding
python3 batch_grounding.py --images img1.png img2.png --prompts "button" "icon" --workers 4 --output ui_map.json
```

## Related Skills
- `hermes-internals-patching` — for delegate_tool.py fixes
- `state-machine` — LangGraph-style workflow execution
- `gated-context-system` — context budget management

## References
- `references/locateanything-coordinate-format.md` — coordinate parsing details
- `references/emerge-z0rpc-api.md` — Emerge API investigation notes
- `references/vulkan-740m-config.md` — GPU build flags and runtime args