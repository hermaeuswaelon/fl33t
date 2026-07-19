---
name: firecrawl-research
description: |
  Research umbrella skill for Firecrawl — deep research reports, literature reviews, paper discovery, paper synthesis, and sourced analytical reports. Use this skill when the user needs rigorous synthesis of a complex topic, finding and synthesizing research papers/whitepapers/PDFs/technical reports, finding papers that answer a research query via semantic paper search, or producing an intensive cited analytical report with executive summary and multi-angle findings.

  This umbrella absorbs: firecrawl-deep-research, firecrawl-research-papers, firecrawl-research-index.
license: ISC
metadata:
  author: firecrawl
  version: "0.1.0"
  homepage: https://www.firecrawl.dev
  source: https://github.com/firecrawl/firecrawl-workflows
inputs:
  - name: FIRECRAWL_API_KEY
    description: Firecrawl API key for hosted Firecrawl requests.
    required: true
---

# Firecrawl Research Umbrella

This umbrella skill consolidates three research-oriented Firecrawl workflows. Use the sub-skill that matches your research need.

## Choose Your Workflow

| Workflow | When to Use | Original Skill |
|---|---|---|
| **Deep Research** | Rigorous synthesis of a complex topic requiring a formal analytical report with executive summary, multi-angle findings, contrarian views, open questions, and full sources. NOT for product picks, top-N lists, or quick lookups. | firecrawl-deep-research |
| **Research Papers** | Literature review, paper summary, research landscape, or sourced synthesis from PDFs and scholarly/industry publications. Uses semantic paper search, related-paper expansion, and in-body verification. | firecrawl-research-papers |
| **Research Index** | Finding papers that answer a research query using semantic search, semantic and structural expansion, and in-body verification. Use for any literature-finding / paper-retrieval task — single-paper lookups or full multi-paper sets. | firecrawl-research-index |

---

## 1. Firecrawl Deep Research

Use this only for report-scale research: a rigorous, cited synthesis the user explicitly wants delivered as a formal written report. If the request is a product pick, a top-N list, a quick lookup, or anything answerable with a short search, stop; do not use this workflow, let the request be handled the standard way.

### Onboarding Interview

Infer the topic and output format from context. Before starting, unless already specified, always ask one short question to define the scope:

> "How long do you want this research task to run?"

Map the answer to a depth tier:
- A few minutes → Quick
- ~10-15 minutes → Thorough
- Longer / no limit → Exhaustive

### Firecrawl Collection Plan

Use Firecrawl search and scrape. Match depth to the runtime:

- Quick: search 3-5 queries and scrape 5-10 high-quality sources.
- Thorough: search 5-10 queries from different angles and scrape 15-25 sources.
- Exhaustive: search 10+ queries and scrape 25+ sources, including primary sources, research papers, expert views, and contrarian sources.

### Final Deliverable

```markdown
# Deep Research: [Topic]

## Executive Summary
[2-3 paragraphs]

## Key Findings
[Numbered findings with source links]

## Detailed Analysis
[Themes, evidence, and synthesis]

## Contrarian Views And Risks
[Counterarguments, limitations, failure modes]

## Open Questions
[What remains uncertain]

## Sources
[Every URL used with a one-line note]

## Rerun Inputs
workflow: firecrawl-deep-research
topic: [topic]
depth: [quick/thorough/exhaustive]
output: [markdown/json/brief]
```

---

## 2. Firecrawl Research Papers

Use this to create a sourced literature review.

### Onboarding Interview

Infer the topic, source constraints, target count, and output format from context. If the topic is clear, proceed immediately. Ask at most 1-3 concise questions only if blocked.

### Collection Tools

- `firecrawl research search-papers <query> [--k <number>]` — Semantic search over paper abstracts
- `firecrawl research related-papers <seedIds...> --intent <intent> [--mode <similar|citers|references>] [--k <number>]` — Expand from seed papers
- `firecrawl research inspect-paper <id>` — Canonical metadata for a candidate paper
- `firecrawl research read-paper <id> --question <question>` — Verify specific claims in-body
- `firecrawl search <query>` / `firecrawl scrape <url>` — Web context outside the paper index

### Final Deliverable

```markdown
# Literature Review: [Topic]

## Abstract
[2-3 paragraph summary]

## Key Papers
[Title, authors, source URL, key findings, methodology, relevance]

## Themes And Consensus
[What sources agree on]

## Open Questions And Debates
[Disagreements and unresolved questions]

## Emerging Trends
[Recent developments]

## Sources
[Organized by paper/report/article]
```

---

## 3. Firecrawl Research Index

Find the research papers that answer a research query. There is no fixed recipe — read the query, decide what kind it is, and choose the approach.

### Query-Type Matching

- **Single named paper**: one `search-papers`, done.
- **Paper by description / method**: find the best match, then expand with `related-papers` and include the family.
- **Enumeration / method-family**: answer is a set — expand several strong anchors with `mode=similar`.
- **Superlative / leaderboard**: search the web for the ranking, then `search-papers` each top entry.
- **Org / author filtered**: verify affiliation with `inspect-paper` or `read-paper`.

### Principles

- When in doubt, include the relevant paper family rather than only the single best result.
- Use related-paper expansion to avoid stopping at one strong hit.
- Use read-paper to verify load-bearing constraints, not to summarize every candidate.

---

## Quality Bar (All Workflows)

- Cite sources for factual claims.
- Prefer primary sources when available.
- Flag uncertainty and conflicting evidence.
- Synthesize instead of listing scrape summaries.
- Distinguish peer-reviewed work from blogs and vendor reports.
- Include a "Rerun Inputs" block when the workflow could be automated.
