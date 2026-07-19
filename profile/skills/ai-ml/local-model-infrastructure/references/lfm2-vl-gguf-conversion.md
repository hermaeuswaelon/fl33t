# LFM2-VL GGUF Conversion Notes

## Architecture Detection Bug

The llama.cpp `convert_hf_to_gguf.py` converter has a bug in `get_model_architecture()`
that silently drops VL architecture names for models with nested `text_config`.

**Root cause** (`conversion/base.py:get_model_architecture`):
```python
# Line 2637 — overrides top-level arch with text_sub_arch
if model_type == ModelType.TEXT and text_config.get("architectures") is not None:
    arch = text_config["architectures"][0]
```

For LFM2-VL models, the config.json has:
- Top-level: `"architectures": ["Lfm2VlForConditionalGeneration"]`
- `text_config.architectures: ["Lfm2ForCausalLM"]`

The override replaces `Lfm2VlForConditionalGeneration` → `Lfm2ForCausalLM`,
which causes the converter to load only text backbone tensors (149 out of 352),
dropping all vision encoder + projector tensors.

## Fix

Add `Lfm2VlForConditionalGeneration` to the exception list at line 2633:
```python
if model_type == ModelType.TEXT and arch in (
    "StepVLForConditionalGeneration",
    "Sarashina2VisionForCausalLM",
    "Exaone4_5_ForConditionalGeneration",
    "Step3p7ForConditionalGeneration",
    "Lfm2VlForConditionalGeneration",      # <-- ADD THIS
):
    return arch
```

## Two-Class Pattern (following StepVL)

After the fix, a TEXT model class registered for `Lfm2VlForConditionalGeneration`
must exist. Follow the StepVL pattern:

1. **MMPROJ class** (existing `LFM2VLModel(MmprojModel)`):
   - Registered via `@ModelBase.register("Lfm2VlForConditionalGeneration")`
   - Handles vision encoder + projector for `--mmproj` conversion
   - Output: `mmproj-<name>.gguf`

2. **TEXT class** (needs creation):
   - `class LFM2VLTextModel(LFM2Model)` with `model_arch = gguf.MODEL_ARCH.LFM2`
   - Registered via `@ModelBase.register("Lfm2VlForConditionalGeneration")`
   - Must include `multi_modal_projector.*` tensors in its `filter_tensors`
   - Output: `<name>.gguf` (text backbone + projector)

## The fine-tune (`lfm2-vl-gui-sft`)

- Base: LiquidAI/LFM2-VL-450M
- Fine-tune: GUI SFT on realGUI-800K dataset
- Weights: 352 tensors, all FP32, 1.72 GB (full merged model)
- Vision: SigLIP2 (12 layers, 768 dim, patch=16)
- Projector: LayerNorm(3072) → Linear(3072→2560) → Linear(2560→1024)
- Text: LFM2 backbone with short-convolution layers

## Conversion strategy

Run conversion TWICE for a complete VL model:

```bash
# 1. Extract vision encoder + projector (mmproj)
PYTHONPATH=... python3 convert_hf_to_gguf.py \
    <model_dir> --mmproj --outtype f16

# 2. Extract text backbone + projector (text GGUF)
PYTHONPATH=... python3 convert_hf_to_gguf.py \
    <model_dir> --outtype f16
```

Serve together:
```bash
llama-server --model text.gguf --mmproj mmproj-text.gguf --port 8086
```

## Quantization

After conversion, quantize the text GGUF:
```bash
llama-quantize text.gguf text-Q4_K_M.gguf q4_k_m
```
