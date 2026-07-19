---
name: dynamic-tool-selection-patterns
category: tools
description: "Captures dynamic tool selection and ordering patterns for LLM agents, including two‑stage decoupled framework, SkillGraph prior, and learned pairwise reranker."
---

# Dynamic Tool Selection Patterns for LLM Agents

This skill captures the state‑of‑the‑art techniques for dynamically selecting and ordering tools in LLM‑driven agents. It summarizes the two‑stage decoupled framework, graph foundation priors, and learned pairwise reranking that have become standard in recent research (e.g., SkillGraph, AgenticRec, SPaRK, ToolOmni). The goal is to enable agents to:

* **Select** a relevant subset of tools from large libraries without overwhelming the context.
* **Order** the selected tools according to expected data‑flow dependencies, improving success rates and reducing negative impact on other metrics.

## Two‑Stage Decoupled Framework
1. **Candidate Selection** – Uses a combination of semantic similarity retrieval and a graph‑based prior (SkillGraph) built from thousands of successful trajectories. This stage produces a fixed candidate set \(\hat{\\mathcal{S}}\) of up to \\(K\\) tools.
2. **Learned Pairwise Reranker** – Orders the candidate set with a lightweight pairwise model (e.g., a 3‑layer MLP) that consumes features such as semantic similarity, transition probabilities from SkillGraph, and positional priors. This avoids the single‑stage trade‑off where selection quality and ordering quality degrade each other.

## Graph Foundation Prior (SkillGraph)
* Constructed once from ~50 k successful agent trajectories.
* Encodes workflow precedence as directed weighted edges; community structure reveals coherent tool clusters.
* Provides interpretable transition probabilities that the reranker can directly consume, sidestepping expensive GNN inference at query time.

## Learned Pairwise Reranker Features
* Semantic similarity & rank (f1‑f2)
* SkillGraph transition probabilities (f3‑f6)
* Positional priors (f7‑f8)
* Optionally, tool‑specific features (e.g., frequency, rarity).

## Integration with Hermes
* **Skill Category Selection** – Hermes’ `skill_selector.py` maps user messages and active toolsets to skill categories, demoting irrelevant categories to names‑only (Tier 2) while keeping full descriptions for active categories. This reduces prompt bloat while preserving recall.
* **Tool Tips** – Context‑specific hints (e.g., “use `web_search` for research”) are injected via the skill selector, offering per‑turn guidance without full schema payloads.
* **Caching** – The skill index is cached in‑process (LRU) and persisted to a manifest‑validated JSON file (`.skills_prompt_snapshot.json`) for fast rebuilds across sessions.

## Pitfalls & Best Practices
* **Avoid single‑stage selection/ordering** – Combining retrieval and ranking in one model often yields negative Kendall‑τ on API‑Bank.
* **Do not ignore graph precedence** – Purely semantic rerankers can invert tool order when data dependencies exist.
* **Keep cache valid** – Context compression invalidates the prompt cache; always call `invalidate_system_prompt` after compression.
* **Maintain minimal tool descriptions** – Verbose descriptions increase token usage and can distract the model; keep descriptions concise.

## Verification
* Run a benchmark with a known data‑flow (e.g., `read_file → parse → summarize`) and verify that the reranker orders tools as `read_file → parse → summarize`.
* Check that Kendall‑τ improves from ~0.04 (semantic only) to >0.6 when SkillGraph‑derived features are used (as reported in SkillGraph paper).

## References
* SkillGraph: Graph Foundation Priors for LLM Agent Tool Sequence Recommendation (arXiv 2604.19793)
* AgenticRec: A Recommendation‑Oriented Agentic Framework (arXiv 2603.21613)
* SPaRK: Step‑wise Policy for Rare‑tool Knowledge (arXiv 2607.11371)
* ToolOmni: Enabling Open‑World Tool Use (arXiv 2602.10490)