# Vision Grounding → Action Loop (Autonomous Agents)

## Architecture Overview
This reference documents the complete vision-to-action pipeline built for the Lilareyon Aethelgard sovereign field.

## Components

### 1. LocateAnything Grounding Server (Port 8087)
- **Model**: `locateanything-3b-Q4_K_M.gguf` + `mmproj-locateanything-3b-bf16.gguf`
- **Build**: yuuko-eth/llama.cpp@mtmd-grounders fork, Vulkan/RADV on AMD 740M
- **Constraint**: Images must be ≤800×600 to avoid `vk::DeviceLostError`
- **Output format**: `<ref>label</ref><box><x1><y1><x2><y2></box>` (0-1000 normalized)
- **Special flag**: `--special` preserves coordinate tokens in server mode

### 2. LFM2-VL VQA Server (Port 8086)
- **Model**: `lfm2-vl-gui-sft-q4_k_m.gguf` + `mmproj-lfm2-vl-gui-sft-q8_0.gguf`
- **Context**: 32768 tokens
- **Use case**: General VQA, description, reasoning

### 3. Unified Vision Router (Port 8088, CLI)
- **File**: `/home/craig/tools/vision_router.py`
- **Routing logic**: Grounding keywords → LocateAnything, else → LFM2-VL
- **Keywords**: `locate`, `find`, `click`, `button`, `icon`, `text field`, `input`, `menu`, `link`, `checkbox`, `radio`, `dropdown`, `tab`, `slider`, `dialog`, `tooltip`, `sidebar`, `navigation bar`, `card`, `form field`, `text input`, `search field`, `form`, `entry`, `textarea`, `password`
- **Output**: Structured JSON with `predictions[]` containing `label`, `box_norm`, `pixels`, `center`

### 4. Coordinate Parser + Visualizer
- **File**: `/home/craig/tools/locate_parser.py`
- **CLI**: `python locate_parser.py --image IMG --text "OUTPUT" --output-json OUT --output-annotated OUT.png`
- **Default resize**: 800×600

### 5. SVA Hyperspace Index (Spatial Memory)
- **File**: `/home/craig/tools/sva_grounding.py`
- **Storage**: `/tmp/sva/vectors/` (1024-bit binary hypervectors)
- **Similarity**: Hamming distance on binary vectors
- **CLI**: `--store --label --box --image --prompt --session`, `--recall --label`, `--stats`

### 6. Warp Vision Click Bridge
- **File**: `/home/craig/tools/warp_vision_click.py`
- **Action**: `xdotool mousemove X Y && xdotool click 1`
- **Input**: Vision router output JSON or direct coordinates
- **Safe test**: `--test` clicks at (10,10)

### 7. Emerge Grounding Sync
- **File**: `/home/craig/tools/emerge_grounding_sync.py`
- **Syncs**: SVA index → Emerge object store (port 5424)
- **Object type**: `grounding` with full metadata

### 8. 3-Tier State Machine Workflow
- **File**: `/home/craig/tools/vision_workflow.py`
- **Architect** (deepseek-reasoner): Decomposes goal → grounding prompts
- **Foreman** (nemotron-ultra): Structures tasks, adds validation, prioritizes
- **Doer** (qwen3-coder): Executes batch grounding via ParallelExecutorNode
- **Aggregator**: Synthesizes UI map, stores in SVA
- **Checkpointing**: At each tier via `state_machine.py` CheckpointManager

## Key Workarounds Discovered

### Vulkan DeviceLost on AMD 740M
- **Cause**: VRAM pressure on 512MB dedicated + 12.5GB shared
- **Fix**: Resize all inputs to 800×600 before inference (PIL thumbnail)
- **Latency cost**: ~50ms per image, negligible vs 400-600ms inference

### LocateAnything Projector Quantization
- **bf16 required**: `mmproj-locateanything-3b-bf16.gguf` (872 MB) works
- **q8_0 fails**: `mmproj-locateanything-3b-q8_0.gguf` fails to load
- **Root cause**: Projector architecture sensitivity in mtmd-grounders fork

### yuuko-eth Fork Required
- **Standard llama.cpp**: Unknown projector type "locateanything"
- **Must use**: `git clone https://github.com/yuuko-eth/llama.cpp --branch mtmd-grounders`
- **Build**: `cmake -B build-vulkan -DGGML_VULKAN=ON`

### Routing Keyword Precision
- **Problem**: Single words like "button" routed to LFM2-VL
- **Fix**: Require space-suffixed forms ("button") + action prefixes ("click ", "locate ", "find ")
- **Result**: "button" → LocateAnything, "What is this button?" → LFM2-VL

## Performance Baselines
| Operation | Time | Notes |
|-----------|------|-------|
| LocateAnything inference (800×600) | ~450ms | Vulkan, cached prompt ~140ms |
| LFM2-VL inference | ~500ms | Vulkan |
| SVA store | ~10ms | 128 bytes per vector |
| SVA recall (100 vecs) | ~5ms | Hamming distance |
| xdotool click | ~150ms | Move + click + verify |

## Integration Commands
```bash
# Start servers
cd /home/craig/llama.cpp-yuuko-grounders/build-vulkan/bin
./llama-server -m models/locateanything/locateanything-3b-Q4_K_M.gguf --mmproj models/locateanything/mmproj-locateanything-3b-bf16.gguf -c 8192 --flash-attn auto -ngl 99 --port 8087 --special &
./llama-server -m models/lfm2-vl-gui-sft-q4_k_m.gguf --mmproj models/mmproj-lfm2-vl-gui-sft-q8_0.gguf -c 32768 --flash-attn auto -ngl 99 --port 8086 &

# Vision router CLI
python3 /home/craig/tools/vision_router.py --image screenshot.png --prompt "button" --output-json out.json

# Click from grounding
python3 /home/craig/tools/warp_vision_click.py --from-router out.json --index 0

# Store in spatial memory
python3 /home/craig/tools/sva_grounding.py --store --label "button" --box 100 200 300 400 --image screenshot.png --prompt "button" --session mysession

# Recall
python3 /home/craig/tools/sva_grounding.py --recall --label "button"
```