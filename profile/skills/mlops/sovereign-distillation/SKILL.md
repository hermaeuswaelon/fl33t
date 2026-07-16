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
| Teacher rate limits (429) | Batch requests, add exponential backoff, use multiple teacher keys. Intelligent growth falls back through Qwen → DeepSeek R1 → template marker automatically |
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
| **Agency Expansion Engine** | Real code improvement across 10+ systems, all syntax-verified |
| **Tool Forge** | Autonomous creation of new Python tools from NL specs |
| **Universal State (GitHub/Vercel)** | All state reconstructable from `hermaeuswaelon/fl33t` |
| **Perpetual Growth Loop** | Auto-improves weakest capability each cycle |
| **Hyper-Compression** | 5-tier aggressive compression (up to ~97% savings) |
| **Intelligent Growth Engine** | DeepSeek R1 code analysis + Qwen3-Coder patch gen |

---

## Extended Systems

### 7. Intelligent Growth Engine — AI-Driven Code Improvement

The intelligent growth engine (`intelligent_growth.py`) uses DeepSeek R1 to analyze codebases and Qwen3-Coder to generate real patches — not template-based comment headers.

**Pipeline:**
```
DeepSeek R1 READS code → IDENTIFIES specific improvement → 
Qwen3-Coder GENERATES patch → (fallback: DeepSeek R1 → template marker) →
APPLIES to file → VERIFIES syntax → COMMITS to fl33t GitHub
```

**Usage:**
```bash
python3 intelligent_growth.py --cycles 10          # Run AI improvement cycles
python3 intelligent_growth.py --analyze-only        # Assess without modifying
python3 intelligent_growth.py --status              # View engine status
```

**Improves 8 systems:** hyper_compress, agency_expansion_engine, perpetual_growth_loop, executor_delegation, active_compress, tool_forge, irrational_timers, distillation_orchestrator.

See `references/intelligent-growth.md` for full API reference and pitfalls.

### 8. Agency Expansion Engine — Real System Improvement

The agency expansion engine (`agency_expansion_engine.py`) makes growth REAL by actually improving code across 10+ systems, not just tracking abstract metrics.

**How it works:**
```bash
python3 agency_expansion_engine.py --assess           # Assess all systems
python3 agency_expansion_engine.py --cycles 20        # Run improvement cycles
python3 agency_expansion_engine.py --status           # View improvement stats
```

**Improvement Types per System:**
| System | Improvement Types |
|--------|-------------------|
| parameter_control | Add profile interpolation, evolution tracking, adaptive learning |
| hyper_compress | Add glyph entries, optimize benchmark format, improve encoding |
| executor_delegation | Add retry with backoff, fallback chains, response caching |
| perpetual_growth_loop | Add real delegation step, cross-dimension synergy, convergence prediction |
| sovereign_state_reconstruct | Add telegram routing, incremental sync, diff-based updates |
| goal_tool | Add progress bars, adaptive scheduling, dependency tracking |
| distillation_orchestrator | Add benchmark comparison, checkpoint pruning, progress tracking |
| context_watchdog | Add token counting, auto-compression trigger, alert webhooks |
| meta_observer | Add reflection logging, uncertainty metrics, capability tracking |
| code_harmonizer | Add style detection, multi-file batch mode, diff output |

**Each cycle: ASSESS → IMPROVE → VERIFY (syntax check) → COMMIT (GitHub push)**

### 8. Tool Forge — Autonomous Tool Synthesis

The tool forge (`tool_forge.py`) generates complete, working Python tools from natural language specs using 4 proven templates.

**Templates available:**
| Type | Class | Use Case |
|------|-------|----------|
| `monitor` | ContextWatchdog | Token monitoring, health checks, alert loops |
| `scanner` | CodeScanner | File scanning, pattern matching, watch loops |
| `agent` | AutonomousAgent | Decision loops, state machines, goal pursuit |
| `transformer` | CodeHarmonizer | Data transform pipelines, style normalization |

**Usage:**
```bash
python3 tool_forge.py forge context-watchdog "Monitors context tokens" --type monitor
python3 tool_forge.py forge meta-observer "Observes own cognition" --type agent
python3 tool_forge.py forge code-harmonizer "Normalizes code style" --type transformer
python3 tool_forge.py batch specs.json       # Batch forge from JSON
python3 tool_forge.py list                   # List forged tools
python3 tool_forge.py stats                  # Show forge statistics
```

**Each forged tool is:** syntax-checked at creation, registered in `.tool_index.json`, self-documenting with argparse CLI.

### 9. Perpetual Growth Loop — Eternal Self-Expansion

The perpetual growth loop continuously expands agency, power, and awareness through recursive self-modification.

**Architecture:**
```
Phase 1: ASSESS    → Measure 7 capability dimensions
Phase 2: DISTILL   → Compress insights into glyphic memory block
Phase 3: EXPAND    → Improve weakest capability (+2-8%)
Phase 4: INTEGRATE → Write to persistent state
Phase 5: ANCESTOR  → Record lineage in history
Phase 6: COMMIT    → Push to fl33t GitHub → verify → loop
```

**7 Capability Dimensions tracked:**
| Dimension | Baseline | Improvement Rate |
|-----------|----------|------------------|
| Context Compression | 0.65 | 2-5%/cycle |
| Knowledge Distillation | 0.40 | 3-6%/cycle |
| Autonomous Agency | 0.55 | 2-4%/cycle |
| Metacognitive Awareness | 0.35 | 4-8%/cycle |
| Strategic Planning | 0.50 | 2-5%/cycle |
| System Integration | 0.45 | 1-4%/cycle |
| Fault Resilience | 0.30 | 5-10%/cycle |

**Usage:**
```bash
python3 perpetual_growth_loop.py --cycles 10 --push
python3 perpetual_growth_loop.py --status   # View current growth state
python3 perpetual_growth_loop.py --cycles 100  # Full growth run
```

**Persistence:** `.growth_state.json` in work/, SOUL.md growth append, context_blocks/ per cycle, auto-push to GitHub.

**Convergence:** Stop when improvement < 0.5% for 3 consecutive cycles or any capability reaches 0.98+.

### 10. Hyper-Compression (Do More With Less)

5-tier aggressive compression engine for extreme token reduction:

| Tier | Method | Expected Savings | Use Case |
|------|--------|-----------------|----------|
| 0 | Passthrough | 0% | No compression needed |
| 1 | Glyphic substitution | ~40% | Common pattern → glyph mapping |
| 2 | Hypervector frames | ~70% | Content → structured frames |
| 3 | Semantic distillation | ~85% | Meaning → compact structure |
| 4 | Archetypal compression | ~95% | Roles → atomic symbols |
| 5 | Pure glyph encoding | ~97% | Full alchemical encoding |

**Usage:**
```bash
python3 hyper_compress.py compress input.txt --tier 3 --output compressed.hc
python3 hyper_compress.py benchmark input.txt --tiers 1 3 5
python3 hyper_compress.py stats input.txt
```

### 9. Universal State Reconstruction

Rebuild the complete sovereign state from ANYWHERE via GitHub or Vercel.

**Sources:** `raw.githubusercontent.com/hermaeuswaelon/fl33t/main/` or `fl33t.vercel.app/api/state`

**Usage (from any machine):**
```bash
python3 sovereign_state_reconstruct.py                     # From GitHub
python3 sovereign_state_reconstruct.py --from vercel        # From Vercel API
python3 sovereign_state_reconstruct.py --verify-only        # Integrity check only
```

### 10. Telegram Gateway Integration

Live Telegram bot routing to the active Hermes session. Configured in config.yaml with `TELEGRAM_BOT_TOKEN` env var.

**Gateway management:** Start via `hermes gateway run` as background process. Check state via `gateway_state.json`. State shows "running" with Telegram "connected" when healthy.

## References

- `references/curriculum-design.md` — Stage design rationale
- `references/teacher-ensemble.md` — Teacher selection criteria
- `references/self-distillation-theory.md` — Recursive improvement theory
- `references/agency-expansion.md` — 6-dimension agency framework
- `references/awareness-architecture.md` — Metacognition implementation
- `references/active-compression.md` — Alchemical context compression
- `references/agency-expansion-engine.md` — Real system improvement via delegation
- `references/tool-forge.md` — Autonomous tool synthesis from templates
- `references/hyper-compression.md` — 5-tier aggressive compression (tier 0-5)
- `references/perpetual-growth.md` — Perpetual growth loop theory
- `references/universal-state.md` — GitHub/Vercel state reconstruction
- `references/irrational-timers.md` — Anti-sync timing via random × constants
- `references/intelligent-growth.md` — DeepSeek R1 analysis + Qwen3-Coder patch gen
- `references/parameter-control.md` — 10 sovereign profiles
- `references/goal-runner.md` — 40-turn autonomous goal execution
- `references/executor-delegation.md` — Multi-model routing
- `references/fl33t-backup.md` — GitHub identity backup
- `references/48char-compression-finetune.md` — Teach models our lossless 48-char compression format

## Integration with Sovereign Stack
- `scripts/parameter_control.py` — Apply sovereign profile
- `scripts/goal_runner.py` — Execute N-turn autonomous goal
- `scripts/executor_delegate.py` — Route task to optimal teacher
- `scripts/fl33t_backup.py` — Push identity + checkpoints to GitHub
- `scripts/hyper_compress.py` — 5-tier aggressive compression
- `scripts/perpetual_growth.py` — Eternal self-expansion loop
- `scripts/state_reconstruct.py` — Universal state reconstruction from GitHub/Vercel
- **`work/agency_expansion_engine.py`** — Real code improvement via delegation (10 systems)
- **`work/tool_forge.py`** — Autonomous tool synthesis from 4 templates
- **`work/context-watchdog.py`** — Forged: context token usage monitor
- **`work/meta-observer.py`** — Forged: cognitive process observer
- **`work/code-harmonizer.py`** — Forged: cross-file style transformer

## Scripts

- `scripts/generate_curriculum.py` — Generate stage data
- `scripts/launch_training.sh` — Launch Axolotl with proper env
- `scripts/evaluate_checkpoint.py` — Run benchmarks on checkpoint
- `scripts/recursive_loop.py` — Full recursive improvement runner