---
name: firecrawl-monitor
description: |
  Monitor and automation umbrella skill for Firecrawl — change detection, site monitoring, knowledge base building, docs portal ingestion, workflow orchestration, website design cloning, site downloading, browser interaction, shopping research, and AI-powered autonomous extraction.

  This umbrella absorbs: firecrawl-monitor (original CLI monitor), firecrawl-knowledge-base, firecrawl-knowledge-ingest, firecrawl-workflows, firecrawl-website-design-clone, firecrawl-download, firecrawl-interact, firecrawl-shop, firecrawl-agent.
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

# Firecrawl Monitor Umbrella

This umbrella skill consolidates nine monitor- and automation-oriented Firecrawl skills. Choose the sub-skill matching your task.

## Choose Your Workflow

| Workflow | When to Use | Original Skill |
|---|---|---|
| **Monitor** | Detect content changes on a website and get notified by webhook or email. Pricing, jobs, docs, changelogs, status pages, any ongoing change detection. | firecrawl-monitor (original CLI) |
| **Knowledge Base** | Build a knowledge base from web content. Local reference docs, RAG-ready chunks, fine-tuning datasets, documentation mirrors, topic corpora, LLM-ready markdown. | firecrawl-knowledge-base |
| **Knowledge Ingest** | Ingest public or authenticated knowledge bases and docs portals. JS-heavy docs, login-gated portals, paginated help centers, support knowledge bases. | firecrawl-knowledge-ingest |
| **Workflows** | Run outcome-focused Firecrawl workflows producing deliverables (research reports, SEO audits, QA reports, lead lists, design systems, etc.). Generic workflow orchestrator. | firecrawl-workflows |
| **Website Design Clone** | Extract any website's design system into an agent-ready DESIGN.md. Colors, fonts, spacing, components, layout patterns, brand/UI guidance. | firecrawl-website-design-clone |
| **Download** | Download an entire website as local files (markdown, screenshots, multiple formats). Offline documentation, bulk site save. | firecrawl-download |
| **Interact** | Control and interact with a live browser session — click buttons, fill forms, navigate flows, extract data via natural language or code. | firecrawl-interact |
| **Shop** | Research products across the web and produce shopping recommendations with cart-ready summaries. | firecrawl-shop |
| **Agent** | AI-powered autonomous data extraction. Navigates complex sites and returns structured JSON. Multi-page structured extraction with JSON schema. | firecrawl-agent |

---

## 1. Monitor

Detect when content on a website changes and get notified by webhook or email.

### When to Use
- The user wants to know **when** something changes and be notified about it
- Ongoing change detection: pricing, docs, changelogs, blogs, job boards, status pages, competitor sites, regulatory pages, product availability, hiring pages, top-N rankings
- "Alert me when...", "notify me when...", "email me if...", "send a webhook when..."

### Quick Start
```bash
# Single page, natural-language schedule, email alert
firecrawl monitor create --name "Blog" --schedule "every 30 minutes" \
  --goal "Alert when a new blog post is published." \
  --page https://example.com/blog --email alerts@example.com

# Multiple pages
firecrawl monitor create --name "Product pages" --schedule "every 30 minutes" \
  --goal "Alert when pricing, docs, or changelog content changes." \
  --scrape-urls https://example.com/pricing,https://example.com/docs,https://example.com/changelog

# Webhook notifications
firecrawl monitor create --name "Docs webhook" --schedule "every 30 minutes" \
  --goal "Alert when docs content changes." \
  --page https://example.com/docs \
  --webhook-url https://example.com/hook \
  --webhook-events monitor.page,monitor.check.completed

# Manage
firecrawl monitor list --limit 20
firecrawl monitor run <monitorId>
firecrawl monitor checks <monitorId>
firecrawl monitor check <monitorId> <checkId> --page-status changed
firecrawl monitor update <monitorId> --state paused
firecrawl monitor delete <monitorId>
```

### Goal Writing
Convert user intent into a concise 2-3 sentence goal:
- Start with "Alert when..." and state the trigger
- Restate scope: top N, price, role type, region, company
- Add "Ignore..." only for intent-specific exclusions
- Don't repeat generic noise exclusions (whitespace, casing, tracking params)
- Don't invent business rules unless the user mentioned them

### JSON-mode Change Tracking
For structured per-field diffs (pricing tiers, feature lists, etc.), pass a JSON body:
```bash
cat > pricing-monitor.json <<'EOF'
{
  "name": "Pricing watch",
  "goal": "Alert when plan prices or headline features change.",
  "schedule": { "text": "hourly", "timezone": "UTC" },
  "targets": [{
    "type": "scrape",
    "urls": ["https://example.com/pricing"],
    "scrapeOptions": {
      "formats": [{
        "type": "changeTracking",
        "modes": ["json"],
        "prompt": "Extract pricing tiers and headline features.",
        "schema": {
          "type": "object",
          "properties": {
            "plans": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "name": { "type": "string" },
                  "price": { "type": "string" },
                  "features": { "type": "array", "items": { "type": "string" } }
                }
              }
            }
          }
        }
      }]
    }
  }]
}
EOF
firecrawl monitor create pricing-monitor.json
```

### Options
`--name`, `--goal`, `--schedule`, `--cron`, `--timezone`, `--page`, `--scrape-urls`, `--crawl-url`, `--webhook-url`, `--webhook-events`, `--email`, `--retention-days`, `--state`, `--page-status`, `-o`, `--pretty`.

---

## 2. Knowledge Base

Turn URLs or topics into organized LLM-ready content.

### Output Modes
- Reference: markdown files, `index.md`, `sources.json`
- RAG: markdown files plus chunk files and `manifest.json`
- Training: scraped source files plus `training-data.jsonl` and `training-metadata.json`
- Docs mirror: complete markdown mirror with table of contents

### Process
Use map for documentation sites, search for topic-based corpora, scrape into markdown. Preserve code examples and tables.
Output convention:
```text
.firecrawl/
  <hostname>/
    <path>/
      index.md
```

### Final Deliverable
```markdown
# Knowledge Base: [Source]
## Summary
## Output Structure
## Coverage
## Usage Notes
## Sources
```

---

## 3. Knowledge Ingest

Ingest docs portals needing browser navigation, auth, pagination, or JS rendering.

### Process
Use Firecrawl browser: open portal, inspect navigation, identify sections/categories/sidebar/article URLs, follow sidebar/next links/pagination/load-more/search, scrape article content as markdown, extract metadata (title, section, last updated, author, tags).

### JSON Shape
`source`, `url`, `extractedAt`, `totalArticles`, `sections[]` with article `title`, `url`, `section`, `content`, `metadata`.

### Quality Bar
- Preserve code examples, tables, and formatting.
- Strip nav chrome, headers, and footers.
- Track extraction progress and page failures. Respect authentication boundaries.

---

## 4. Workflows

Generic outcome-focused Firecrawl workflows. Use when the user wants a finished deliverable and no specific workflow above fits.

### Default Process
1. Confirm the workflow and final artifact.
2. Collect web evidence with Firecrawl CLI or equivalent.
3. Save or cite source evidence.
4. Run independent research units in parallel.
5. Synthesize findings into the requested deliverable.
6. Include a "Rerun Inputs" block.

### Deliverable Standards
- Concise executive summary
- Evidence base used
- Analysis or artifact requested
- Recommendations or next actions
- Automation inputs for reruns

---

## 5. Website Design Clone

Extract any website's design system into an agent-ready DESIGN.md.

### Process
Always start with two parallel scrapes:
```bash
firecrawl scrape "<url>" --format branding,images -o ".firecrawl/site-branding.json" --pretty &
firecrawl scrape "<url>" --full-page-screenshot -o ".firecrawl/site-screenshot.png" &
wait
```
Use branding output for colors, typography, components, brand assets. Use images list for page content imagery. Use screenshot for visual reference.

### Final Deliverable
`DESIGN.md` with reference screenshot, design summary, design tokens (colors, typography, spacing), components, page patterns, content style, and agent build instructions.

---

## 6. Download

> **Experimental.** Combines `map` + `scrape` to save an entire site as local files.

```bash
firecrawl download https://docs.example.com --screenshot --limit 20 -y
firecrawl download https://docs.example.com --format markdown,links --screenshot --limit 20 -y
firecrawl download https://docs.example.com --include-paths "/features,/sdks" -y
```

Options: `--limit`, `--search`, `--include-paths`, `--exclude-paths`, `--allow-subdomains`, `-y`, plus all scrape options.

---

## 7. Interact

Interact with scraped pages in a live browser session.

### Quick Start
```bash
firecrawl scrape "<url>"
firecrawl interact --prompt "Click the login button"
firecrawl interact --prompt "Fill in the email field with test@example.com"
firecrawl interact --code "agent-browser click @e5" --language bash
firecrawl interact stop
```

### Profiles
Use `--profile` on the scrape to persist browser state across sessions.

### Tips
- Always scrape first — interact requires a scrape ID.
- Never use interact for web searches — use `search` instead.
- Use `firecrawl interact stop` to free resources when done.

---

## 8. Shop

Research products across the web and produce a shopping recommendation.

### Process
1. Research product options across multiple sources (reviews, product pages, specs, pricing).
2. Compare price, specs, reviews, seller quality, shipping, fit to preferences.
3. Pick the best option and explain why.
4. If asked for cart actions, open shopping site in browser, add item, stop before checkout.

### Final Deliverable
```markdown
# Shopping Research: [Product]
## Recommendation
## Products Compared
## Review Signals
## Cart Status (if requested)
## Sources
```

---

## 9. Agent

AI-powered autonomous extraction. The agent navigates sites and extracts structured data (takes 2-5 minutes).

### Quick Start
```bash
firecrawl agent "extract all pricing tiers" --wait -o .firecrawl/pricing.json
firecrawl agent "extract products" --schema '{"type":"object","properties":{"name":{"type":"string"},"price":{"type":"number"}}}' --wait -o .firecrawl/products.json
```

### Options
`--urls`, `--model`, `--schema`, `--schema-file`, `--max-credits`, `--wait`, `--pretty`, `-o`.

### Tips
- Always use `--wait` to get results inline.
- Use `--schema` for predictable structured output.
- For simple single-page extraction, prefer the base `firecrawl` skill.

---

## General Principles (All Workflows)

- Infer inputs from context; ask at most 1-3 concise questions only if blocked.
- Use sub-agents or parallel task runners for independent work units.
- Every deliverable should include rerun inputs for easy re-execution.
- Preserve source URLs and scrape artifacts for auditability.
