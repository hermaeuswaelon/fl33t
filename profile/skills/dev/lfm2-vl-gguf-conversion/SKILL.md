---
name: "lfm2-vl-gguf-conversion"
title: "LFM2-VL GGUF Conversion"
description: "Convert LFM2-VL fine-tune safetensors to dual GGUF (text + mmproj) for llama-server"
---

# LFM2-VL GGUF Conversion

Convert fine-tuned LFM2-VL safetensors (vision language model) to dual GGUF format for llama-server deployment.

## Architecture

LFM2-VL = SigLIP2 vision encoder (12/24 layers, 768 dim) + projector (layer_norm→linear_1→linear_2) + LFM2 text backbone (16 layers, 1024 dim, shortconv)

Full safetensors: 352 tensors (~1.7 GB FP32) = 203 vision+projector + 149 text. GGUF conversion produces two files:
- **Text GGUF**: 149 text tensors only (F16 → quantize to Q4_K_M)
- **Mmproj GGUF**: 203 vision+projector tensors only (Q8_0)

llama-server uses: `--model text-gguf --mmproj mmproj-gguf`

## Conversion

### 1. Text GGUF (text backbone only)
```bash
# Convert all tensors → converter routes to LFM2Model (TEXT mode),
# silently drops vision/projector tensors
python3.13 convert_hf_to_gguf.py /path/to/model-dir --outtype f16

# Quantize
llama-quantize /path/to/model-f16.gguf /path/to/model-q4_k_m.gguf Q4_K_M
```

### 2. Mmproj GGUF (vision encoder + projector)
```bash
# --mmproj flag routes to LFM2VLModel(MmprojModel)
# Lfm2VlForConditionalGeneration → registered in MMPROJ_MODEL_MAP → module "lfm2"
python3.13 convert_hf_to_gguf.py /path/to/model-dir --mmproj --outtype q8_0
```

### 3. Deploy
```bash
llama-server \
  --model /path/to/model-q4_k_m.gguf \
  --mmproj /path/to/mmproj-model-q8_0.gguf \
  --host 127.0.0.1 --port 8086 --api-key vl-local-key \
  --ctx-size 8192 --batch-size 256 --ubatch-size 128 \
  --flash-attn auto --threads 6 --mlock
```

## Tensor Naming

Fine-tune safetensors uses `model.vision_tower.vision_model.*` and `model.multi_modal_projector.*` prefixes. LFM2VLModel.filter_tensors strips the `model.` prefix before MMPROJ tensor mapping:

- `multi_modal_projector.linear_{bid}` → `mm.{bid}` (V_MMPROJ)
- `multi_modal_projector.layer_norm` → `mm.input_norm` (V_MM_INP_NORM)
- `vision_tower.vision_model.*` → `v.*` (V_ENC_*)

## Pitfalls

- **DO NOT** use `--type` flag — it's `--outtype` in convert_hf_to_gguf.py
- **Default python3 is 3.14** which lacks gguf/safetensors. Use `/usr/bin/python3.13` for conversion
- **Quantize syntax**: `llama-quantize input.gguf output.gguf TYPE` (output BEFORE type)
- **Old mmproj incompatible** if projector dimensions differ — always regenerate mmproj from fine-tune
- **`get_model_architecture()` bug**: For TEXT mode, `text_config.architectures` overrides top-level VL arch. This is intentional — the text-only conversion should use LFM2Model. The --mmproj path is NOT affected (model_type != TEXT check)
