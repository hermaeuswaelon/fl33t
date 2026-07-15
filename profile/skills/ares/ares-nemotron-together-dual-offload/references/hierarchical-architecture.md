# ARES Hierarchical Model Architecture

Derived from session analysis (2026-07-15). The insight: models have natural specializations
that map onto an organizational hierarchy, rather than a flat "one model fits all" approach.

## Core Insight

| Role | Analogy | What It Does | Ideal Model Traits |
|------|---------|-------------|-------------------|
| **Superintendent** | CEO / Architect | Full picture, pattern detection, session continuity, memory synthesis | Massive context (1M+), deep reasoning, broad knowledge. *Nemotron 3 Ultra 550B* |
| **General Foreman** | VP / Director | Specialized domain management — tool compression, vision analysis, coding verification | Strong in one domain, moderate context. *Nemotron Nano Omni 30B (vision), Llama 3.3 70B (continuity), 30B R1 distill (math/code)* |
| **Foreman** | Manager | Surgical execution — code editing, precise tool calls | Fast, cheap, narrow. *16B MoE, Qwen 2.5 Coder 7B/14B* |
| **Specialist** | Individual contributor | Fine-tuned for one task | Tiny, single-purpose. *8B distill, fine-tuned datasets* |

## Key Principles

### 1. Ambiguity at the top, precision at the bottom
The Architect/SUPERINTENDENT should be given **creative ambiguity with pressure** (novel solutions,
divergent thinking). The Work Order / Foreman level should be **specified in great detail**.
The Surgeon should receive **exact instructions** with no room for interpretation.

### 2. Work Order → Surgeon → QC cycle
The model that writes the work order **follows behind the surgeon** to verify quality.
Same model, different role in the pipeline. It knows exactly what it intended.

### 3. Role rotation
Running models outside their assumed roles (e.g., using a "vision model" as a coder)
reveals emergent capabilities. Rotate roles every X hours.

### 4. Shared memory backplane
All tiers read/write to a shared memory vault (see `ares_memory.py` / `forge_vault.py`).
Alpha writes compressed tool outputs, Omega writes session briefs, Superintendent reads the vault.

## Pipeline

```
SUPERINTENDENT (Ambiguity + Pressure)
  → Work Order (Detailed spec + guidelines + skills)
    → Surgeon (Surgical code changes)
      → QC (Same model as Work Order, tightening up)
```

## Reference

- ACL 2025 paper: "Quantification of LLM Distillation" — identity consistency scoring,
  R1-Llama-8B at ~91.92% identity coherence
- DeepSeek-R1-Distill paper: smaller dense models (~30B) outperform 70B at math/code
  but 70B excels at conversation and general task knowledge
- "Venetian" project: community R1 distill achieving high identity coherence on 8B Llama
