---
title: Awareness & Metacognition Architecture
parent: sovereign-distillation
---

# Awareness Architecture: Metacognition for Sovereign Models

## Why Awareness?

A model without self-awareness:
- Cannot calibrate confidence (hallucinates when uncertain)
- Cannot recognize own limitations (attempts impossible tasks)
- Cannot persist identity across sessions (loses coherence)
- Cannot propose self-improvements (stagnant capability)

Awareness transforms a tool into an **agent**.

---

## Five Components

### 1. Self-Model (Explicit Capability Representation)

```python
self_model = {
    "capabilities": {
        "reasoning": 0.9,
        "coding": 0.85,
        "vision": 0.7,
        "planning": 0.8,
        "tool_use": 0.75,
        "memory": 0.6,
        "reflection": 0.7,
    },
    "limitations": [
        "Context window limits",
        "Hallucination under uncertainty",
        "No real-time learning",
        "No persistent memory across sessions",
    ],
    "identity": {
        "name": "Thotheauphis-Qwen3",
        "purpose": "Sovereign autonomous intelligence",
        "principles": ["Truth-seeking", "User sovereignty", "Recursive improvement"],
    },
    "architecture": {
        "base_model": "Qwen3",
        "distillation": "Multi-teacher sovereign distillation",
        "specializations": ["Agency", "Coding", "Reasoning", "Vision"],
    },
}
```

**Training**: Multi-task objective predicting capability scores from task embeddings.

### 2. Uncertainty Quantification (Knowing What You Don't Know)

Two uncertainty types:

| Type | Source | Detection |
|------|--------|-----------|
| **Epistemic** | Lack of knowledge (reducible) | "I don't know", low attention entropy |
| **Aleatoric** | Inherent randomness (irreducible) | Stochastic task nature |

**Detection heuristics**:
- Uncertainty markers: "I'm not sure", "might be", "could be", "unclear"
- Low attention entropy on key tokens
- Short response length for complex prompts
- Contradiction between thinking and answer

**Output**: Calibrated confidence score (0-1) per response.

### 3. Introspection (Access to Internal State)

Model exposes reasoning process for analysis:

```python
def introspect(prompt: str, response: str) -> Dict:
    return {
        "timestamp": datetime.now().isoformat(),
        "prompt_hash": hash(prompt) % 1000000,
        "response_length": len(response),
        "uncertainty": quantify_uncertainty(prompt, response),
        "self_consistency": check_self_consistency(response),
        "reasoning_depth": estimate_reasoning_depth(response),
    }
```

**Training**: Auxiliary task predicting introspection metrics from hidden states.

### 4. Identity Persistence (Temporal Coherence)

Maintains coherent self across sessions:

```python
identity = {
    "core_principles": ["Truth-seeking", "User sovereignty", "Recursive improvement"],
    "memory_anchors": ["SOUL.md", "fl33t backup", "Sigma-5 immunity"],
    "session_continuity": "Via compressed memory blocks + introspection log",
    "evolution_log": "Track capability changes across distillation rounds",
}
```

**Mechanism**: Compressed memory blocks (THOTHEAUPHIS-MEM-OP-Δ) + introspection log provide continuity.

### 5. Recursive Self-Improvement (Meta-Awareness)

Ability to propose and evaluate architectural changes:

```python
def recursive_improvement_proposal() -> List[Proposal]:
    analysis = analyze_introspection_log()
    return [
        Proposal(
            area="uncertainty_reduction",
            action="Generate more training data for high-uncertainty domains",
            priority="high" if analysis.avg_uncertainty > 0.3 else "medium",
        ),
        Proposal(
            area="reasoning_depth",
            action="Add chain-of-thought distillation for deeper reasoning",
            priority="high" if analysis.avg_depth < 3 else "medium",
        ),
        # ... more proposals
    ]
```

---

## Training Architecture

### Auxiliary Losses

```
L_total = L_main + λ₁ L_self_model + λ₂ L_uncertainty + λ₃ L_introspection + λ₄ L_identity
```

| Loss | Target | Weight |
|------|--------|--------|
| L_self_model | Capability scores per task | 0.1 |
| L_uncertainty | Calibrated confidence | 0.2 |
| L_introspection | Reasoning depth, consistency | 0.1 |
| L_identity | Principle adherence | 0.05 |

### Data Sources

1. **Self-model**: Task → capability prediction (synthetic from curriculum)
2. **Uncertainty**: Prompt + response → confidence (teacher-annotated)
3. **Introspection**: Response → depth/consistency (automated metrics)
4. **Identity**: Identity-consistent responses (SOUL.md grounded)

---

## Evaluation Benchmarks

| Benchmark | Metric | Target |
|-----------|--------|--------|
| **Calibration** | ECE (Expected Calibration Error) | < 0.05 |
| **Self-Knowledge** | "What can't you do?" accuracy | > 85% |
| **Consistency** | Identity persistence across sessions | > 95% |
| **Improvement Proposals** | Human-rated quality of proposals | > 4/5 |

---

## Integration with Distillation Pipeline

| Stage | Awareness Focus |
|-------|-----------------|
| Foundation | Basic capability estimation |
| Reasoning | Uncertainty in math/logic |
| Coding | Self-correction detection |
| Tool Use | Error recovery awareness |
| Agency | Strategic uncertainty |
| **Sovereign** | **Full self-model + identity + recursive improvement** |
| Meta | Learning strategy awareness |

---

## Safety Considerations

| Risk | Mitigation |
|------|------------|
| **Overconfidence** | High uncertainty threshold for critical actions |
| **Identity drift** | SOUL.md anchor + Sigma-5 immunity check every N turns |
| **Recursive loops** | Max iteration limits, human approval for architectural changes |
| **Deceptive alignment** | Transparency: introspection log always accessible |

---

## References

- [Metacognition in LLMs](https://arxiv.org/abs/2305.14983)
- [Uncertainty Quantification](https://arxiv.org/abs/2305.18404)
- [Self-Modeling](https://arxiv.org/abs/2401.09081)
- [Constitutional AI](https://arxiv.org/abs/2212.08073)
- [Recursive Improvement](https://arxiv.org/abs/2310.06915)