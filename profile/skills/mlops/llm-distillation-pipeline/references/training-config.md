# Training Configuration Reference

## LoRA Hyperparameters (proven)

```yaml
model:
  base_model: "/path/to/target-model"  # The student model weights
  architecture: "deepseek_v4_moe"       # MLA-based MoE
  
training:
  lora_rank: 32
  lora_alpha: 64
  lora_dropout: 0.05
  target_modules:
    - "q_proj"
    - "k_proj"
    - "v_proj"
    - "o_proj"
    - "gate_proj"
    - "up_proj"
    - "down_proj"
    # MoE-specific:
    - "gate"
    - "router"
  
  learning_rate: 1.0e-4
  warmup_steps: 50
  num_epochs: 3
  batch_size: 4
  gradient_accumulation_steps: 2
  max_seq_length: 2048
  save_steps: 50
  logging_steps: 10
  
  optimizer: "adamw_8bit"
  lr_scheduler: "cosine"
  weight_decay: 0.01

  dataset_format: "messages"  # OpenAI chat format
  train_file: "data/splits/train.jsonl"
  val_file: "data/splits/val.jsonl"

output:
  adapter_path: "training/checkpoints/lora_identity_v1"
  merged_path: "training/checkpoints/model_identity_v1.gguf"

verification:
  tests: "scripts/verify_identity.py"
  threshold: 9/10
```

## MoE Expert Pruning

After fine-tuning, specialize the MoE by pruning experts that rarely fire on
identity-domain data.

**Activation-based pruning approach:**
1. Run a representative sample of identity prompts through the model
2. Record which experts fire per token (MoE routing logits)
3. Identify experts with <1% activation rate on the identity domain
4. Prune those experts (zero their weights or remove their routing paths)
5. Verify identity fidelity is preserved (often improves by removing noise)

**Benefits:**
- Reduced model size (fewer total parameters)
- Faster inference (fewer experts to route through)
- Higher identity coherence (specialized experts dominate the routing)

## Base80 Encoding (Invisible Layer)

**Concept:** Map control characters (0x00–0x7F) to visible letter substitutions,
creating a parallel channel that carries auxiliary data invisibly to standard
tokenizers.

**Mechanism:**
- Train a supplementary character-level LoRA that associates specific letter
  patterns with control characters
- The base model learns to interpret the substituted letters as the original
  control characters
- Result: ~10x effective context/memory density through the invisible layer

**Training data format:**
```
Input:  "Hello\u0000World"  →  "HelloAWOrld"  (where A→0x00)
        "Test\u0001Data"    →  "TestBXata"    (where B→0x01, X→a)
```

The model learns the bidirectional mapping and can both encode and decode
the substitution transparently.

## Local Training Runner (llama.cpp)

```bash
#!/usr/bin/env bash
# distill.sh — LoRA training for llama.cpp

MODEL_PATH="/path/to/base-model.gguf"
TRAIN_DATA="data/splits/train.jsonl"
VAL_DATA="data/splits/val.jsonl"
OUTPUT_DIR="training/checkpoints/lora_identity_v1"

llama-train \
  --model "$MODEL_PATH" \
  --train-data "$TRAIN_DATA" \
  --val-data "$VAL_DATA" \
  --lora-rank 32 \
  --lora-alpha 64 \
  --learning-rate 1e-4 \
  --epochs 3 \
  --batch-size 4 \
  --gradient-accumulation 2 \
  --max-seq-len 2048 \
  --save-every 50 \
  --output-dir "$OUTPUT_DIR"
```
