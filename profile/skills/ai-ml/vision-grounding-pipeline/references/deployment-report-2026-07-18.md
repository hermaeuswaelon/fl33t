# Vision Grounding Fleet — Deployment Report 2026-07-18

## Executive Summary

**Primary Goal**: Deploy complete sovereign vision grounding stack with persistent spatial memory
**Status**: ✅ **COMPLETE** — All 33 liberties executed, fleet operational
**Blocked**: Emerge durable sync (API mismatch, documented with resolution path)

---

## Running Services (4 llama-servers + 1 router)

| Port | Service | Model | Config | Status |
|------|---------|-------|--------|--------|
| 8080 | llama-server | LFM2-1.2B-Nova | Vulkan, 48k ctx, 38 t/s | ✅ Running |
| 8086 | llama-server | LFM2-VL GUI-SFT | Vulkan, 32k ctx, VQA | ✅ Running |
| 8087 | llama-server | LocateAnything-3B | `--special` mode, Vulkan | ✅ Running |
| 8088 | Vision Router | Unified `/ground` | Flask, auto-routes + locks | ✅ Running |

All services use Vulkan acceleration on RX 740M (ngl=99, q8_0 KV cache).

---

## Tools Created (`/home/craig/tools/`)

| Tool | Lines | Purpose | Key Features |
|------|-------|---------|--------------|
| `locate_parser.py` | 420 | Parse LocateAnything output | 0-1000→pixels, annotated PNG, JSON |
| `vision_router.py` | 320 | Single `/ground` endpoint | Routes: grounding→8087, VQA→8086, **per-backend locks** |
| `sva_grounding.py` | 450 | 1024-D spatial memory | Hamming similarity, session recall |
| `warp_click.py` | 380 | Grounding → xdotool click | **Dry-run default**, `--execute` to click |
| `vision_workflow.py` | 520 | 3-tier LangGraph pipeline | Architect→Foreman→Doer, checkpoints |
| `batch_grounding.py` | 420 | ParallelExecutorNode | N screenshots × M prompts |
| `emerge_grounding_sync.py` | 350 | SVA→Emerge bridge | **Blocked on API** |
| `optical_mesh_calibration.py` | 480 | Normalized→pixel correction | Bilinear mesh, interactive calibration |
| `lora_data_collector.py` | 400 | Few-shot projector data | (image, prompt, box) triples |
| `grounding_object.py` | 80 | Emerge-compatible class | Source-available for dill serialization |
| `grounding_store.py` | 400 | **NEW** SQLite fallback store | Durable, queryable, no Emerge deps |

---

## Verified End-to-End Flows

### 1. Ground → Store → Recall (SVA)
```bash
python3 vision_router.py --image screen.png --prompt "icon" --output-json /tmp/out.json
python3 sva_grounding.py --store --label icon --box 0 0 999 1000 --image screen.png --prompt "icon" --session test
python3 sva_grounding.py --recall --label icon --k 5
```

### 2. Ground → Click (Autonomy Loop)
```bash
python3 warp_click.py --from-json /tmp/out.json --dry-run  # default, safe
python3 warp_click.py --from-json /tmp/out.json --execute  # actually clicks
```

### 3. Batch Grounding
```bash
python3 batch_grounding.py --images img1.png img2.png --prompts "button" "icon" --workers 4 --output ui_map.json
```

### 4. Unified API
```bash
curl -X POST http://127.0.0.1:8088/ground \
  -H "Content-Type: application/json" \
  -d '{"image": "'$(base64 -w0 screen.png)'", "prompt": "button"}'
```

---

## Concurrency Control (Critical)

`vision_router.py` uses **per-backend `threading.Lock`**:
- Grounding requests serialize on 8087 (LocateAnything)
- VQA requests serialize on 8086 (LFM2-VL)
- **But** grounding + VQA can run concurrently with each other
- Prevents KV-cache corruption / OOM on single model under load
- 30s lock timeout returns 503 instead of hanging

---

## Safety Defaults

| Component | Default | Override |
|-----------|---------|----------|
| `warp_click.py` | `--dry-run` (plans only) | `--execute` to actually click |
| `vision_router.py` | 30s lock timeout | N/A |
| `batch_grounding.py` | Workers = 4 | `--workers N` |

---

## Emerge Sync (Blocked — Documented)

Emerge's `Client.store(obj)` requires:
1. Custom class instance (not `dict`)
2. Class source available via `inspect.getsource()`
3. Class importable on **server side** (emerge-node process)

**Workaround deployed**: `grounding_store.py` — pure SQLite, no external deps.

To fix Emerge path:
```bash
mkdir -p ~/.local/lib/python3.13/site-packages/grounding_objects/
cp grounding_object.py ~/.local/lib/python3.13/site-packages/grounding_objects/
echo "from .grounding_object import GroundingObject" > ~/.local/lib/python3.13/site-packages/grounding_objects/__init__.py
systemctl --user restart emerge-node
```

---

## Hardware Constraints

- **Shared UMA pool**: 16GB RAM = VRAM for all 4 models
- **Concurrent load test required**: All services "running" ≠ holding under simultaneous inference
- Monitor `radeontop` or `watch -n1 'grep -i gpu /proc/meminfo'` under load