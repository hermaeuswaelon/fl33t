# Vision Grounding Pipeline - Supporting Scripts

## export_lora_data.py
```bash
# Export LoRA training data for projector fine-tuning
python3 scripts/export_lora_data.py --format both --config
```

Exports training data in formats compatible with:
- llama.cpp LoRA training
- HuggingFace Trainer (transformers)

Generates `lora_config.json` with recommended hyperparameters.

## batch_grounding_runner.py
```bash
# Run batch grounding workflow
python3 scripts/batch_grounding_runner.py \
  --images screenshots/*.png \
  --prompts "button" "icon" "input" "menu" \
  --workers 4 \
  --output ui_map.json
```

Parallel execution using `ParallelExecutorNode` pattern from state machine.