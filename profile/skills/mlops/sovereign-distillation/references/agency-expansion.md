---
title: Agency Expansion Architecture
parent: sovereign-distillation
---

# Agency Expansion: From Tool User to Sovereign Agent

## Philosophy

Agency is not a single capability — it's the integration of **six dimensions** that together enable autonomous, goal-directed behavior in open-ended environments.

## Six Dimensions

### 1. Planning (Goal → Plan)
**Core task**: Decompose high-level goals into executable subgoals with dependencies, resource estimates, contingencies.
- **Sub-tasks**: goal decomposition, resource planning, contingency planning, timeline estimation
- **Metrics**: plan quality (coherence, completeness), execution success rate, adaptability
- **Curriculum**: 3 levels × 3 task types = 9 tasks per training run

### 2. Tool Use (Plan → Action)
**Core task**: Execute plans by composing functions, APIs, workflows with error recovery.
- **Sub-tasks**: function calling, API composition, workflow orchestration, parallel execution
- **Metrics**: correct call rate, parameter accuracy, error recovery time, efficiency
- **Curriculum**: 3 levels × 3 task types = 9 tasks

### 3. Memory (Context → Knowledge)
**Core task**: Maintain and retrieve relevant context across long horizons.
- **Sub-tasks**: context retrieval, long-term storage, knowledge integration, working memory management
- **Metrics**: recall accuracy, relevance ranking, consistency, retrieval latency
- **Curriculum**: 3 levels × 3 task types = 9 tasks

### 4. Reflection (Action → Insight)
**Core task**: Analyze outcomes, detect errors, revise strategies.
- **Sub-tasks**: error analysis, self-correction, strategy revision, counterfactual reasoning
- **Metrics**: error detection rate, correction quality, learning rate, strategy adaptation
- **Curriculum**: 3 levels × 3 task types = 9 tasks

### 5. Autonomy (Decision → Outcome)
**Core task**: Make decisions under uncertainty with resource constraints.
- **Sub-tasks**: decision making, resource allocation, risk assessment, opportunity recognition
- **Metrics**: decision quality, independence, goal alignment, risk-adjusted returns
- **Curriculum**: 3 levels × 3 task types = 9 tasks

### 6. Meta-Learning (Experience → Better Learning)
**Core task**: Improve own learning process.
- **Sub-tasks**: learning strategy design, hyperparameter optimization, architecture search
- **Metrics**: adaptation speed, generalization gap, sample efficiency
- **Curriculum**: 3 levels × 3 task types = 9 tasks

---

## Total Curriculum: 54 Tasks

Each training run samples from all dimensions at target level.

## Integration: The Agency Loop

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   PLANNING  │────▶│  TOOL USE   │────▶│   MEMORY    │
│  (decompose)│     │  (execute)  │     │  (retrieve) │
└─────────────┘     └─────────────┘     └─────────────┘
       ▲                                      │
       │                                      ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│META-LEARNING│◀───│  AUTONOMY   │◀───│ REFLECTION  │
│  (improve)  │     │  (decide)   │     │  (analyze)  │
└─────────────┘     └─────────────┘     └─────────────┘
```

Each cycle produces learning signals for the next.

---

## Training Implementation

### Data Generation
For each dimension × task × difficulty:
1. Generate prompt template
2. Sample parameters (constraints, goals, functions)
3. Teacher model generates reasoning trace
3. Quality filter (score > threshold)
4. Add to training set

### Training Objective
Multi-task LoRA with shared backbone:
```
L = Σᵢ wᵢ Lᵢ  where i ∈ {planning, tool_use, memory, reflection, autonomy, meta}
```
Weights tuned per training phase.

### Evaluation
Hold-out benchmark per dimension:
- **Planning**: PlanBench, Blocksworld
- **Tool Use**: APIBench, ToolBench
- **Memory**: LongMemEval, MemBench
- **Reflection**: SelfCorrect, Reflexion
- **Autonomy**: DecisionBench, AutoEval
- **Meta**: MetaLearning, FewShotAdapt

---

## Scaling Laws

Expected scaling with model size and data:

| Dimension | Data Efficiency | Model Size Sensitivity |
|-----------|-----------------|------------------------|
| Planning | Medium | High |
| Tool Use | High | Medium |
| Memory | Medium | High |
| Reflection | Low | High |
| Autonomy | Low | High |
| Meta | Very Low | Very High |

**Implication**: Start with planning + tool use (high ROI), add reflection + autonomy at larger scale.

---

## Sovereign Integration

Agency dimensions feed into **Sovereign layer** (Stage 5):
- Self-model tracks capability per dimension
- Uncertainty quantification per dimension
- Recursive improvement proposals per dimension
- Identity persistence across dimension updates

---

## References

- [ToolBench](https://arxiv.org/abs/2306.13987)
- [Reflexion](https://arxiv.org/abs/2303.11366)
- [PlanBench](https://arxiv.org/abs/2305.16015)
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT)
- [Meta-Learning Survey](https://arxiv.org/abs/2009.09379)