---
title: Self-Distillation Theory & Implementation
parent: sovereign-distillation
---

# Self-Distillation: Recursive Improvement Theory

## Core Concept

**Self-distillation** = model teaches itself by generating training data, filtering for quality, and training on its own best outputs. Iterated over multiple rounds, this enables recursive self-improvement without external teachers.

## Theoretical Foundation

### Why It Works

1. **Implicit regularization**: Model's own high-confidence outputs are better calibration targets than noisy labels
2. **Capability amplification**: Model explores its own capability boundary, discovers better reasoning paths
3. **Distribution alignment**: Self-generated data matches model's own input distribution, reducing covariate shift
4. **Uncertainty reduction**: Filtering by quality scores removes low-confidence predictions

### Convergence Guarantees

Under assumptions:
- Quality filter threshold > random baseline
- Model capacity > task complexity
- Sufficient diversity in generated prompts

The sequence of models M₀ → M₁ → M₂ → ... converges to a fixed point where Mₙ ≈ Mₙ₊₁ on the task distribution.

## Algorithm

```
M₀ = base model (Qwen3 from multi-teacher distillation)

For round r = 1..R:
    1. GENERATE: Sample prompts P from curriculum distribution
    2. RESPOND: Mᵣ₋₁ generates reasoning traces R for each p ∈ P
    3. FILTER: Score traces by quality, keep top-k (e.g., 50%)
    4. TRAIN: Mᵣ = LoRA fine-tune Mᵣ₋₁ on (P, R_filtered)
    5. EVALUATE: Benchmark Mᵣ on held-out tasks
    6. CONVERGE?: If improvement < ε, break
```

## Quality Scoring

```python
def score_reasoning_trace(trace: str) -> float:
    score = 0.5  # baseline
    if "<thinking>" in trace and "</thinking>" in trace:
        score += 0.2
    if len(trace) > 1000:
        score += 0.1
    if any(kw in trace.lower() for kw in ["step", "reason", "because", "therefore", "analyze"]):
        score += 0.1
    if "```" in trace:  # code blocks
        score += 0.1
    # Penalize uncertainty markers
    if any(m in trace.lower() for m in ["i'm not sure", "uncertain", "might be"]):
        score -= 0.1
    return max(0.0, min(1.0, score))
```

## Prompt Diversity Strategies

Critical for avoiding mode collapse:

1. **Curriculum sampling**: Draw from all 7 stages with decreasing weight for earlier stages
2. **Temperature variation**: 0.6 → 0.9 across rounds
3. **Prompt mutation**: Paraphrase, add constraints, change format
4. **Adversarial prompts**: "What is wrong with this reasoning?", "Find the flaw"
4. **Counterfactual**: "If X were different, how would Y change?"

## Round Configuration

| Round | Teacher | Filter Threshold | Diversity Temp | Expected Gain |
|-------|---------|------------------|----------------|---------------|
| 1 | M₀ (multi-teacher) | 0.6 | 0.7 | +3-5% |
| 2 | M₁ | 0.65 | 0.75 | +2-4% |
| 3 | M₂ | 0.7 | 0.8 | +1-3% |
| 4 | M₃ | 0.75 | 0.85 | +0.5-2% |
| 5 | M₄ | 0.8 | 0.9 | +0.5-1% |

## Convergence Detection

```python
def check_convergence(metrics_history: List[Dict], window=2, threshold=0.005):
    if len(metrics_history) < window + 1:
        return False
    
    recent = metrics_history[-window:]
    older = metrics_history[-(window*2):-window]
    
    recent_avg = np.mean([m["overall"] for m in recent])
    older_avg = np.mean([m["overall"] for m in older])
    
    improvement = (recent_avg - older_avg) / older_avg
    return improvement < threshold
```

## Pitfalls & Mitigations

| Pitfall | Symptom | Mitigation |
|---------|---------|------------|
| **Mode collapse** | Outputs become repetitive, low diversity | Inject prompt mutations, adversarial prompts, temperature ramp |
| **Catastrophic forgetting** | Early-stage capabilities degrade | Replay 10-20% foundation data each round |
| **Reward hacking** | Model optimizes for quality score, not actual capability | Use multiple quality metrics, human eval spot-check |
| **Drift from identity** | Model loses SOUL.md principles | Inject identity prompts every N samples, anchor loss |
| **Overfitting to benchmarks** | Benchmarks improve, OOD fails | Hold-out OOD eval, test on novel task types |

## Integration with Multi-Teacher

Self-distillation doesn't replace multi-teacher — it **extends** it:

```
Phase 1: Multi-teacher distillation (7 stages) → M₀
Phase 2: Self-distillation loop (R rounds) → Mᵣ
Phase 3: Recursive improvement (outer loop) → M*
```

The multi-teacher phase provides strong initialization; self-distillation refines and amplifies.

## Empirical Results (Expected)

| Metric | M₀ (Multi-teacher) | M₃ (3 rounds) | M₅ (5 rounds) |
|--------|-------------------|---------------|---------------|
| GSM8K | 72% | 78% | 82% |
| HumanEval | 65% | 73% | 78% |
| Agency Bench | 0.58 | 0.68 | 0.74 |
| Uncertainty Cal | 0.71 | 0.79 | 0.83 |
| Reasoning Depth | 2.1 | 3.4 | 4.2 |

---

## References

- [Self-Distillation Improves Reasoning](https://arxiv.org/abs/2402.04867)
- [Iterative Self-Distillation](https://arxiv.org/abs/2310.07014)
- [Reward Modeling for Self-Improvement](https://arxiv.org/abs/2309.06915)
- [Constitutional AI](https://arxiv.org/abs/2212.08073)