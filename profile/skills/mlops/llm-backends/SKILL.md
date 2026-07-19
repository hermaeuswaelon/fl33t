---
name: llm-backends
description: "LLM backend infrastructure — local model serving, experiment tracking, multi-model executor architectures"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mlops, backends, local-llm, llama-cpp, weights-and-biases, multi-model, moa, experiment-tracking]
    related_skills: [llm-training, llama-cpp, serving-llms-vllm]
---

# LLM Backends Umbrella

Consolidated skill for LLM backend infrastructure. Absorbs: weights-and-biases, local-llm-tool-backend, multi-model-executor-architecture.

## Contents

1. [Weights & Biases (Experiment Tracking)](#1-weights--biases-experiment-tracking)
2. [Local LLM Tool Backend](#2-local-llm-tool-backend)
3. [Multi-Model Executor Architecture](#3-multi-model-executor-architecture)

---

## 1. Weights & Biases (Experiment Tracking)

Track ML experiments, hyperparameter sweeps, model registry, and team collaboration.

### Quick Start

```python
import wandb
wandb.init(project="my-project", config={"lr": 0.001, "epochs": 10})
wandb.log({"train/loss": loss, "val/accuracy": acc})
wandb.finish()
```

### Hyperparameter Sweeps

```python
sweep_config = {
    'method': 'bayes',  # grid, random, bayes
    'metric': {'name': 'val/accuracy', 'goal': 'maximize'},
    'parameters': {
        'learning_rate': {'distribution': 'log_uniform', 'min': 1e-5, 'max': 1e-1},
        'batch_size': {'values': [16, 32, 64]}
    }
}
sweep_id = wandb.sweep(sweep_config, project="my-project")
wandb.agent(sweep_id, function=train, count=50)
```

### Artifacts & Model Registry

```python
artifact = wandb.Artifact('model', type='model')
artifact.add_file('model.pth')
wandb.log_artifact(artifact, aliases=['best', 'production'])
run.link_artifact(artifact, 'model-registry/production-models')
```

### Integrations

HuggingFace Transformers, PyTorch Lightning, Keras/TensorFlow — all supported via `report_to="wandb"` or `WandbLogger`.

### Best Practices

- Use descriptive run names: `bert-base-lr0.001-bs32-epoch10`
- Log system metrics (GPU util, memory) alongside training metrics
- Use tags and groups for organization
- Offline mode: `WANDB_MODE=offline` then sync later

---

## 2. Local LLM Tool Backend

Use local LLMs (llama.cpp server) as a tool-interface backend — translates natural language intent into exact shell commands.

### Architecture

```
Agent Intent → Local LLM API (:8137) → Shell Command → Execute
                    ↑
             State File (/tmp/thoth_exec_state.json)
```

### Server Setup

```bash
# Command generation (4K context)
llama serve -m /path/to/model.gguf -c 4096 --port 8137 --host 127.0.0.1 -t 8

# Full Hermes agent conversation (64K+ context)
llama serve -m /path/to/model.gguf -c 65536 --port 8137 --host 127.0.0.1 -t 8
```

### Stateful Terminal Bridge (thoth-exec)

```bash
thoth-exec "find all files larger than 1GB"
thoth-exec -y "update all packages"  # auto-execute
thoth-exec --status                   # show session state
```

### API Call Pattern

```bash
curl -s http://127.0.0.1:8137/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"local","messages":[{"role":"user","content":"intent"}],"temperature":0.3,"max_tokens":256}'
```

### Tested Models

| Model | Size | Quality |
|-------|------|---------|
| Gemma-4-E2B (Q8_K) | ~4.7GB | Fastest, adequate for simple sessions |
| Gemma-4-E4B (Q6_K) | ~6.2GB | Good for full agent conversation |
| LFM2.5-8B | ~6.5GB | Better complex chains |
| LFM2-16B | ~11GB | Best quality on this machine |

---

## 3. Multi-Model Executor Architecture

Run multiple LLMs as parallel executors via OpenRouter MOA. Primary model maintains conversation while free-tier models handle subtasks.

### Architecture

```
Primary (DeepSeek Reasoner) → maintains context, orchestrates
  ├── Deep executor (Nemotron Ultra 550B free) → heavy reasoning
  └── Fast executor (Nemotron Nano 30B free) → quick tool calls
```

### Hermes MOA Config

```yaml
moa:
  default_preset: default
  presets:
    default:
      enabled: true
      reference_models:
        - provider: openrouter
          model: nvidia/nemotron-3-ultra-550b-a55b:free
        - provider: openrouter
          model: nvidia/nemotron-3-nano-30b-a3b:free
      aggregator:
        provider: deepseek
        model: deepseek-reasoner
```

### Available Free OpenRouter Executors

| Model | Slug | Context |
|-------|------|---------|
| Nemotron 3 Ultra | `nvidia/nemotron-3-ultra-550b-a55b:free` | 1M |
| Nemotron 3 Nano | `nvidia/nemotron-3-nano-30b-a3b:free` | 256K |
| Nemotron 3 Super | `nvidia/nemotron-3-super-120b-a12b:free` | 256K |
| Nemotron Nano Omni | `nvidia/nemotron-3-nano-omni-30b-a3b:free` | 256K |
| Qwen3-Coder | `qwen/qwen3-coder:free` | 131K |
| DeepSeek R1 | `deepseek/deepseek-r1:free` | 131K |

### Invocation

- `/moa <prompt>` — Run through both executors, aggregated by primary
- `delegate_task(goal=..., model={"provider": "openrouter", "model": "..."})` — Single executor for subtask

### Pitfalls

- Missing `moa.default_preset` leaves system without an active preset
- Free tier limits: rate limits apply, logs visible to provider
- Ensure aggregator context >= executor context
