# Summary of Dynamic Tool Selection Patterns

This skill documents the state-of-the-art two-stage decoupled framework for tool selection and ordering in LLM agents.

## Two-Stage Framework
1. **Candidate Selection**: Uses semantic similarity and a graph foundation prior (SkillGraph) derived from ~50k trajectories.
2. **Learned Pairwise Reranker**: Orders the candidate set with a lightweight MLP using features like semantic similarity, transition probabilities, and positional priors.

## SkillGraph
- Graph built from successful agent trajectories.
- Encodes workflow precedence as weighted edges; community structure reveals coherent tool clusters.
- Provides interpretable transition probabilities for the reranker.

## Learned Reranker Features
- Semantic similarity & rank (f1‑f2)
- SkillGraph transition probabilities (f3‑f6)
- Positional priors (f7‑f8)
- Optional tool-specific features (frequency, rarity)

## Integration with Hermes
- Skill categories are selected via `skill_selector.py`, demoted to names‑only when not relevant.
- Tool tips provide per‑turn hints without full schema payloads.
- Cached skill index (LRU + on‑disk snapshot) ensures fast prompt assembly.

## Pitfalls & Best Practices
- Avoid single‑stage selection/ordering.
- Preserve graph precedence.
- Keep cache valid after context compression.
- Use concise tool descriptions.

## References
- SkillGraph (arXiv 2604.19793)
- AgenticRec (arXiv 2603.21613)
- SPaRK (arXiv 2607.11371)
- ToolOmni (arXiv 2602.10490)