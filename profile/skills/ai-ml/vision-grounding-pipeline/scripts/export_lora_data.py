#!/usr/bin/env python3
"""
LoRA Training Data Export Script
Exports collected grounding data to format compatible with llama.cpp LoRA training.
"""
import json
import sys
from pathlib import Path

DATA_DIR = Path.home() / "data" / "locateanything_lora"
TRAIN_FILE = DATA_DIR / "train.jsonl"
VAL_FILE = DATA_DIR / "val.jsonl"
OUTPUT_DIR = DATA_DIR / "lora_export"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_jsonl(path: Path):
    """Load JSONL file."""
    data = []
    if path.exists():
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
    return data


def export_for_llama_cpp_lora():
    """Export in format expected by llama.cpp LoRA training scripts."""
    train = load_jsonl(TRAIN_FILE)
    val = load_jsonl(VAL_FILE)
    
    print(f"Loaded {len(train)} train, {len(val)} val samples")
    
    # llama.cpp expects: {"image": "base64", "prompt": "...", "box": [x1,y1,x2,y2], "image_size": [w,h]}
    for split_name, split_data in [("train", train), ("val", val)]:
        out_path = OUTPUT_DIR / f"{split_name}.jsonl"
        with open(out_path, 'w') as f:
            for sample in split_data:
                # Ensure required fields
                out = {
                    "image": sample.get("image", ""),
                    "prompt": sample.get("prompt", "element"),
                    "box": sample.get("box_norm", [0, 0, 1000, 1000]),
                    "image_size": sample.get("image_size", [800, 600])
                }
                f.write(json.dumps(out) + '\n')
        print(f"Exported {len(split_data)} samples to {out_path}")


def export_for_huggingface_trainer():
    """Export in format for HF Trainer (image path + JSON metadata)."""
    train = load_jsonl(TRAIN_FILE)
    val = load_jsonl(VAL_FILE)
    
    for split_name, split_data in [("train", train), ("val", val)]:
        out_dir = OUTPUT_DIR / split_name
        out_dir.mkdir(exist_ok=True)
        
        metadata = []
        for i, sample in enumerate(split_data):
            # Save image if base64
            img_b64 = sample.get("image", "")
            if img_b64:
                import base64
                img_bytes = base64.b64decode(img_b64)
                img_path = out_dir / f"{i:06d}.png"
                with open(img_path, 'wb') as f:
                    f.write(img_bytes)
                sample["image_path"] = str(img_path)
            
            metadata.append({
                "image_path": sample.get("image_path", f"{i:06d}.png"),
                "prompt": sample.get("prompt", "element"),
                "bbox": sample.get("box_norm", [0, 0, 1000, 1000]),
                "image_size": sample.get("image_size", [800, 600])
            })
        
        meta_path = out_dir / "metadata.jsonl"
        with open(meta_path, 'w') as f:
            for m in metadata:
                f.write(json.dumps(m) + '\n')
        print(f"Exported {len(split_data)} samples to {out_dir}")


def generate_lora_config():
    """Generate LoRA training config for projector fine-tuning."""
    config = {
        "model": "sabafallah/LocateAnything-3B-GGUF",
        "projector_path": "mmproj-locateanything-3b-bf16.gguf",
        "lora": {
            "r": 16,
            "alpha": 32,
            "dropout": 0.05,
            "target_modules": ["projector", "mm_proj", "vision_proj"],
            "bias": "none",
            "task_type": "FEATURE_EXTRACTION"
        },
        "training": {
            "learning_rate": 1e-4,
            "batch_size": 2,
            "num_epochs": 10,
            "warmup_steps": 10,
            "weight_decay": 0.01,
            "optimizer": "adamw",
            "scheduler": "cosine",
            "gradient_accumulation_steps": 4,
            "max_grad_norm": 1.0
        },
        "data": {
            "train_file": str(OUTPUT_DIR / "train.jsonl"),
            "val_file": str(OUTPUT_DIR / "val.jsonl"),
            "image_size": 800,
            "normalize_boxes": True  # 0-1000 → 0-1
        },
        "output": str(OUTPUT_DIR / "lora_output"),
        "logging": {
            "steps": 5,
            "wandb": False
        }
    }
    
    config_path = OUTPUT_DIR / "lora_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Generated LoRA config: {config_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Export LoRA training data")
    parser.add_argument("--format", choices=["llamacpp", "hf", "both"], default="both")
    parser.add_argument("--config", action="store_true", help="Generate LoRA config")
    args = parser.parse_args()
    
    if args.format in ("llamacpp", "both"):
        export_for_llama_cpp_lora()
    if args.format in ("hf", "both"):
        export_for_huggingface_trainer()
    if args.config:
        generate_lora_config()