---
title: Curriculum Design Rationale
parent: sovereign-distillation
---

# Curriculum Design: 7-Stage Progressive Distillation

## Design

The curriculum follows **competence-based progression** — each stage builds capabilities required by subsequent stages.

## Stage 0: Foundation (Instruction Following)
**Why first**: Base capability for all downstream tasks. Without reliable instruction following, no teacher signal can be learned.
- **Teachers**: Nemotron Super (balanced), DeepSeek V3 (long context)
- **Data**: 50K samples, diverse formats (QA, summary, translation, formatting)
- **Key metric**: Instruction compliance rate > 95%

## Stage 1: Reasoning (Chain-of-Thought)
**Why second**: Reasoning is the substrate for coding, planning, and agency.
- **Teachers**: Nemotron Ultra (deep), DeepSeek R1 (step-by-step)
- **Data**: 30K samples — math, logic puzzles, proof generation, causal reasoning
- **Key metric**: Reasoning depth (steps per problem), accuracy on GSM8K/MATH

## Stage 2: Coding (Program Synthesis)
**Why third**: Coding exercises precise reasoning + tool use patterns.
- **Teachers**: Qwen3-Coder (specialist), Nemotron Ultra (architecture)
- **Data**: 40K samples — generation, refactoring, debugging, multi-file, tool building
- **Key metric**: Pass@1 on HumanEval/MBPP, multi-file coherence

## Stage 3: Tool Use (Function Calling)
**Why fourth**: Bridges reasoning to action. Required for agency.
- **Teachers**: Nemotron Ultra (orchestration), Super (API patterns)
- **Data**: 20K samples — function calling, API composition, workflow orchestration, MCP tools
- **Key metric**: Correct call rate, parameter accuracy, error recovery

## Stage 4: Agency (Autonomous Planning)
**Why fifth**: Requires reasoning + coding + tools to decompose goals.
- **Teachers**: Nemotron Ultra (planning), DeepSeek R1 (self-correction)
- **Data**: 15K samples — goal decomposition, resource planning, contingency planning, decision making
- **Key metric**: Plan quality, execution success, adaptability to failures

## Stage 5: Sovereign (Self-Modeling)
**Why sixth**: Meta-capabilities — model understanding its own architecture, limits, identity.
- **Teachers**: Nemotron Ultra, DeepSeek R1, Nemotron Nano Omni (multimodal self)
- **Data**: 10K samples — self-modeling, recursive improvement design, identity maintenance, strategic thinking
- **Key metric**: Self-consistency, uncertainty calibration, identity persistence

## Stage 6: Meta (Learning to Learn)
**Why last**: Optimizes the learning process itself.
- **Teachers**: Nemotron Ultra, DeepSeek R1
- **Data**: 5K samples — curriculum design, hyperparameter optimization, architecture search
- **Key metric**: Adaptation speed on novel tasks, generalization gap

---

## Teacher Assignment Logic

```python
TEACHER_SPECIALTIES = {
    "Nemotron Ultra": ["deep_reasoning", "architecture", "planning"],
    "DeepSeek R1": ["math", "logic", "step_by_step", "self_correction"],
    "Nemotron Nano Omni": ["vision", "ui_analysis", "multimodal"],
    "Qwen3-Coder": ["code_generation", "refactoring", "tool_building"],
    "Nemotron Super": ["balanced", "coding", "general"],
    "DeepSeek V3": ["long_context", "instruction_following"],
}
```

**Assignment rule**: For each stage, select teachers whose specialties match stage tasks. Multiple teachers per stage for ensemble diversity.

---

## Sample Allocation Strategy

- **Total per stage**: Fixed budget (see table)
- **Per-teacher**: Proportional to specialty relevance
- **Diversity**: Inject prompt variation (temperature 0.7-0.9), different random seeds
- **Quality filter**: Score samples (0-1), keep top 80% for training

---

## Curriculum Learning Benefits

1. **Gradient alignment**: Early stages shape representation space for later tasks
2. **Catastrophic forgetting mitigation**: Replay foundation samples in later stages
3. **Efficient compute**: Smaller models for early stages, scale up for sovereign
4. **Diagnosability**: Clear stage gates — if Stage 2 fails, don't proceed to Stage 3

---

## References

- [Curriculum Learning for LLMs](https://arxiv.org/abs/2309.09461)
- [Self-Distillation Improves Reasoning](https://arxiv.org/abs/2402.04867)
- [Multi-Teacher Knowledge Distillation](https://arxiv.org/abs/2305.15522)