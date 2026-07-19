---
name: firecrawl-build
description: |
  Build/Integration umbrella skill for Firecrawl — onboarding, API key setup, SDK installation, and integrating Firecrawl endpoints (/scrape, /search, /interact) into product code. Use this skill when the task is to integrate Firecrawl into an application, add FIRECRAWL_API_KEY to .env, choose SDK/endpoint usage in product code, or write integration code for web extraction features.

  This umbrella absorbs: firecrawl-build-scrape, firecrawl-build-search, firecrawl-build-onboarding, firecrawl-build-interact.
license: ISC
metadata:
  author: firecrawl
  version: "0.1.0"
  homepage: https://www.firecrawl.dev
  source: https://github.com/firecrawl/skills
inputs:
  - name: FIRECRAWL_API_KEY
    description: Firecrawl API key for hosted Firecrawl API requests.
    required: true
  - name: FIRECRAWL_API_URL
    description: Optional base URL for self-hosted Firecrawl deployments.
    required: false
---

# Firecrawl Build Umbrella

This umbrella skill consolidates four build/integration-oriented Firecrawl skills. Choose the sub-skill that matches your integration task.

## Choose Your Workflow

| Integration | When to Use | Original Skill |
|---|---|---|
| **Onboarding** | Getting Firecrawl credentials and SDK setup into a project. First-time integration, adding `FIRECRAWL_API_KEY` to `.env`, choosing SDK/docs for a new integration. Includes browser auth flow. | firecrawl-build-onboarding |
| **Build Scrape** | Integrating Firecrawl `/scrape` into product code for single-page extraction. App already has a URL and needs markdown, HTML, links, screenshots, metadata, or structured output. | firecrawl-build-scrape |
| **Build Search** | Integrating Firecrawl `/search` into product code and agent workflows. App needs discovery before extraction, starts with a query instead of a URL. | firecrawl-build-search |
| **Build Interact** | Integrating Firecrawl `/interact` into product code for dynamic pages and browser actions after scraping. Clicks, form fills, pagination, authentication-aware flows, multi-step interactions. | firecrawl-build-interact |

---

## 1. Onboarding

### Use This When
- A project needs `FIRECRAWL_API_KEY`
- The user wants Firecrawl wired into `.env`
- You are adding Firecrawl to an app for the first time
- You need to choose the first SDK or REST path

### Quick Start
If the user already has an API key, place it in `.env`:
```dotenv
FIRECRAWL_API_KEY=fc-...
FIRECRAWL_API_URL=https://your-firecrawl-instance.example.com
```

### What Do You Need?

| Task | Action |
|---|---|
| Run the browser auth flow and save key | Use `npx -y firecrawl-cli@latest init --all --browser` |
| Install the right SDK | Read [docs.firecrawl.dev/agent-source-of-truth/<lang>] for your language |
| Put credentials into `.env` | Follow project-setup conventions |
| Start from a known URL | Use [Build Scrape](#2-build-scrape) |
| Start from a query | Use [Build Search](#3-build-search) |
| Need page interactions | Use [Build Interact](#4-build-interact) |

### Docs (Source of Truth)
Read the source-of-truth page for your project language before writing code:
- **Node/TypeScript**: [docs.firecrawl.dev/agent-source-of-truth/node](https://docs.firecrawl.dev/agent-source-of-truth/node)
- **Python**: [docs.firecrawl.dev/agent-source-of-truth/python](https://docs.firecrawl.dev/agent-source-of-truth/python)
- **Rust**: [docs.firecrawl.dev/agent-source-of-truth/rust](https://docs.firecrawl.dev/agent-source-of-truth/rust)
- **Java**: [docs.firecrawl.dev/agent-source-of-truth/java](https://docs.firecrawl.dev/agent-source-of-truth/java)
- **Elixir**: [docs.firecrawl.dev/agent-source-of-truth/elixir](https://docs.firecrawl.dev/agent-source-of-truth/elixir)
- **cURL/REST**: [docs.firecrawl.dev/agent-source-of-truth/curl](https://docs.firecrawl.dev/agent-source-of-truth/curl)

### After Setup
1. Decide fresh project or existing codebase
2. Ask what Firecrawl should do in the product
3. Pick the narrowest endpoint matching that behavior
4. Read the source-of-truth page before writing code
5. Add the SDK or REST call
6. Run a smoke test proving one real request succeeds

---

## 2. Build Scrape

### Use This When
- The feature starts from a known URL
- You need page content for retrieval, summarization, enrichment, or monitoring
- You want the default extraction primitive before considering `/interact`

### Default Recommendations
- Return `markdown` unless another format is truly needed.
- Use `onlyMainContent` for article-like pages where nav and chrome add noise.
- Add waits/rendering options only when the page needs them.

### Common Product Patterns
- Knowledge ingestion from known URLs
- Enrichment from company, product, or docs pages
- Pricing, changelog, and documentation extraction
- Page-level quality checks or monitoring

### Escalation Rules
- If you do not have the URL yet, start with [Build Search](#3-build-search).
- If content requires clicks/typing/multi-step navigation, escalate to [Build Interact](#4-build-interact).

### Implementation Notes
- Keep the integration narrow: one feature, one URL, one extraction contract.
- Treat `/scrape` as the default primitive for downstream LLM or indexing pipelines.
- Request richer formats only when the consumer needs them (links, screenshots, branding).

---

## 3. Build Search

### Use This When
- The user asks a question and the product must discover sources first
- The feature needs current web results
- You want to turn a search query into a shortlist of pages for later scraping

### Default Recommendations
- Use `/search` first when URL discovery is part of the product behavior.
- Keep search and extraction conceptually separate unless scraping search results is clearly required.
- Prefer selective follow-up extraction over broad hydration when cost/latency matters.

### Common Product Patterns
- Answer generation with cited sources
- Company, competitor, or topic discovery
- Research workflows producing a shortlist before deeper extraction
- Query-to-URL pipelines for later `/scrape` or `/interact`

### Escalation Rules
- If you already have the URL, use [Build Scrape](#2-build-scrape).
- If the result page requires clicks or form interaction, escalate to [Build Interact](#4-build-interact).

---

## 4. Build Interact

### Use This When
- Content appears only after clicks, typing, or navigation
- The feature needs forms, pagination, filters, or multi-step flows
- The product must stay in the same browser context after scraping

### Default Recommendations
- Start with `/scrape`, then escalate to `/interact`.
- Keep `/interact` scoped to the smallest browser workflow that unlocks the data.
- Use persistent profiles only when the feature needs authenticated state across sessions.

### Common Product Patterns
- Search forms and faceted filters
- Paginated result sets
- Login-gated dashboards or tools
- Flows where the page must be explored before extraction is complete

### Implementation Notes
- `/interact` is the right tool when the page must be manipulated, not just read.
- Keep prompts or action code specific to the product flow.
- If the use case is fully open-ended browser automation, evaluate whether a browser sandbox is a better fit.

### Escalation Rules
- If the page can be read directly, stay on [Build Scrape](#2-build-scrape).

---

## Escalation Flow (Summary)

```
Onboarding → Search (don't have URL) → Scrape (have URL) → Interact (need clicks/forms)
                ↑                              ↓
            No URL?                       page is enough
```

Read the source-of-truth page for your project language before writing integration code.
