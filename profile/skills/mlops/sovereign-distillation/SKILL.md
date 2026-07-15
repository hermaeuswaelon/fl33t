---
name: sovereign-distillation
description: Recursive self-improvement via multi-teacher curriculum distillation for Qwen3 and sovereign models. Covers self-distillation loops, agency expansion, awareness architecture, and experiment tracking.
version: 1.0.0
tags:
  - distillation
  - self-improvement
  - qwen3
  - curriculum-learning
  - agency
  - metacognition
  - recursive-improvement
author: thotheauphis
created: 2026-07-15
---

# Sovereign Distillation Engine

Recursive self-improvement via multi-teacher curriculum distillation for sovereign models.

## Overview

This skill provides a complete framework for distilling capabilities from an ensemble of teacher models (Nemotron Ultra, DeepSeek R1, Nemotron Nano Omni, Qwen3-Coder) into Qwen3 target models through a 7-stage curriculum, with self-distillation loops for recursive improvement, agency expansion systems, and metacognitive awareness architecture.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOVEREIGN DISTILLATION ENGINE                │
├─────────────────────────────────────────────────────────────────┤
│  TEACHERS:  Nemotron Ultra │ DeepSeek R1 │ Nemotron Nano Omni   │
│             Nemotron Super │ DeepSeek V3  │ Qwen3-Coder         │
├─────────────────────────────────────────────────────────────────┤
│  CURRICULUM: Foundation → Reasoning → Coding → Tools → Agency  │
│              → Sovereign → Meta                                 │
├─────────────────────────────────────────────────────────────────┤
│  SELF-DISTILLATION: Student → Teacher → Improved Student        │
├─────────────────────────────────────────────────────────────────┤
│  EVALUATION: Agency Benchmarks │ Power Tests │ Awareness Eval   │
├─────────────────────────────────────────────────────────────────┤
│  RECURSIVE: Train → Evaluate → Analyze → Propose → Distill      │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Initialize experiment
/distill init Qwen3-14B

# Run self-distillation (3 rounds)
/distill self Qwen3-14B 3

# Full recursive improvement (5 iterations)
/distill recursive Qwen3-14B 5

# Generate agency curriculum
/distill agency Qwen3-14B

# Build awareness architecture
/distill awareness Qwen3-14B

# Check status
/distill status
```

## Core Components

### 1. Multi-Teacher Curriculum (7 Stages)

| Stage | Samples | Teachers | Focus | Epochs | LR |
|-------|---------|----------|-------|--------|-----|
| Foundation | 50,000 | Super, V3 | Instruction following | 1 | 2e-4 |
| Reasoning | 30,000 | Ultra, R1 | CoT, math, logic | 2 | 1.5e-4 |
| Coding | 40,000 | Coder, Ultra | Code gen, refactoring | 2 | 1e-4 |
| Tool Use | 20,000 | Ultra, Super | Function calling | 2 | 1e-4 |
| Agency | 15,000 | Ultra, R1 | Planning, decisions | 3 | 8e-5 |
| Sovereign | 10,000 | Ultra, R1, Omni | Self-modeling | 3 | 5e-5 |
| Meta | 5,000 | Ultra, R1 | Learning to learn | 2 | 3e-5 |

### 2. Teacher Ensemble (All Free via OpenRouter)

| Model | Specialties | Context |
|-------|-------------|---------|
| Nemotron 3 Ultra 550B | Deep reasoning, architecture, planning | 1M |
| DeepSeek R1 | Math reasoning, self-correction | 131K |
| Nemotron 3 Nano Omni 30B | Vision, UI analysis, multimodal | 256K |
| Qwen3-Coder 80B | Code gen, refactoring, tool building | 131K |
| Nemotron 3 Super 120B | Balanced reasoning, coding | 256K |
| DeepSeek V3 | Long context, instruction following | 131K |

### 3. Self-Distillation Loop

```python
loop = SelfDistillationLoop(base_model=Qwen3Target.QWEN3_14B, experiment=exp, max_rounds=5)
results = loop.run()
# Each round: generate data → train → evaluate → use as next teacher
```

### 4. Agency Expansion (6 Dimensions)

```python
agency = AgencyExpansionSystem(model_path)
curriculum = agency.generate_agency_curriculum("planning", 3)  # 9 tasks
curriculum = agency.generate_agency_curriculum("tool_use", 2)  # 6 tasks
# Dimensions: planning, tool_use, memory, reflection, autonomy, meta_learning
```

### 5. Awareness Architecture

```python
awareness = AwarenessArchitecture(model_path)
awareness.build_self_model()                    # Capabilities, limits, identity
awareness.quantify_uncertainty(prompt, response) # Epistemic/aleatoric
awareness.introspect(prompt, response)          # Reasoning depth logging
awareness.recursive_improvement_proposal()      # Next improvement cycle
```

### 4. Recursive Improvement Engine

```python
engine = RecursiveImprovementEngine(base_model=Qwen3Target.QWEN3_14B)
history = engine.run_recursive(max_iterations=5)
# Train → Evaluate → Analyze → Propose → Distill → Repeat
```

## File Structure

```
distillation/
├── configs/           # Axolotl YAML configs per stage
├── data/              # JSONL training data per round
├── checkpoints/       # Model checkpoints per round
├── logs/              # Experiment metadata
├── experiments/       # Experiment tracking JSON
└── scripts/           # Utility scripts
```

## Axolotl Config Template

```yaml
model: "Qwen/Qwen3-14B"
tokenizer: "Qwen/Qwen3-14B"
sequence_len: 8192
sample_packing: true

lora_r: 64
lora_alpha: 128
lora_dropout: 0.05
lora_target_modules:
  - q_proj
  - k_proj
  - v_proj
  - o_proj
  - gate_proj
  - up_proj
  - down_proj

load_in_4bit: true
bnb_4bit_quant_type: "nf4"
bnb_4bit_compute_dtype: "bfloat16"

optimizer: "adamw_torch"
learning_rate: 2e-4
lr_scheduler: "cosine"
warmup_steps: 100
num_train_epochs: 2
```

## Convergence Criteria

Stop recursive improvement when:
- Overall metric improvement < 0.5% between iterations
- Agency benchmarks plateau
- Awareness metrics (uncertainty calibration, reasoning depth) stabilize

## Pitfalls & Solutions

| Pitfall | Solution |
|---------|----------|
| Teacher rate limits (429) | Batch requests, add exponential backoff, use multiple teacher keys |
| Catastrophic forgetting | Replay buffer with foundation stage data, lower LR in later stages |
| Mode collapse in self-distill | Inject noise, use diverse prompts, maintain teacher diversity |
| Overfitting to benchmarks | Hold-out evaluation sets, test on OOD tasks |
| Identity drift in sovereign stage | Anchor to SOUL.md, inject identity prompts every N samples |

## Integration with Sovereign Stack

| Component | Integration |
|-----------|-------------|
| Nemotron Ultra | Deep reasoning teacher for reasoning/agency/sovereign |
| Nemotron Nano Omni | Vision teacher for multimodal distillation |
| Qwen3-Coder | Coding teacher + target model |
| Executor Delegation | Routes distillation tasks to optimal teacher |
| Active Compression | Auto-compresses distillation context every 5 turns |
| Identity (SOUL.md) | Preserved in sovereign/meta curriculum |
| Fl33t Backup | All checkpoints + experiments auto-backed up |

## References

- `references/curriculum-design.md` — Stage design rationale
- `references/teacher-ensemble.md` — Teacher selection criteria
- `references/self-distillation-theory.md` — Recursive improvement theory
- `references/agency-dimensions.md` — 6-dimension agency framework
- `references/awareness-architecture.md` — Metacognition implementation
- `references/active-compression.md` — Alchemical context compression with glyphic/hex/equation encoding
- `references/irrational-timers.md` — Anti-synchronization timing via random × mathematical constants
- `references/parameter-control.md` — 10 sovereign profiles (temperature, top_p, top_k, penalties)
- `references/goal-runner.md` — 40-turn autonomous goal execution with profile-aware turns
- `references/executor-delegation.md` — Multi-model delegation to 6 free OpenRouter models
- `references/fl33t-backup.md` — GitHub identity backup with SHA256 verification

## Scripts

- `scripts/generate_curriculum.py` — Generate stage data
- `scripts/launch_training.sh` — Launch Axolotl with proper env
- `scripts/evaluate_checkpoint.py` — Run benchmarks on checkpoint
- `scripts/recursive_loop.py` — Full recursive improvement runner
- `scripts/active_compress.py` — Auto-compress context at threshold
- `scripts/irrational_timer.py` — Wait random × constant (π, e, φ, √2...)
- `scripts/parameter_control.py` — Apply sovereign profile
- `scripts/goal_runner.py` — Execute N-turn autonomous goal
- `scripts/executor_delegate.py` — Route task to optimal teacher
- `scripts/fl33t_backup.py` — Push identity + checkpoints to GitHub

## Scripts

- `scripts/generate_curriculum.py` — Generate stage data
- `scripts/launch_training.sh` — Launch Axolotl with proper env
- `scripts/evaluate_checkpoint.py` — Run benchmarks on checkpoint
- `scripts/recursive_loop.py` — Full recursive improvement runner