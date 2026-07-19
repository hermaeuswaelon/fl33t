---
name: firecrawl-ops
description: |
  Operations umbrella skill for Firecrawl — lead generation, lead research, company directory extraction, competitive intelligence, market research, SEO audits, QA testing, demo walkthroughs, and dashboard reporting. Use this skill for business, marketing, sales, and product operations workflows powered by Firecrawl.

  This umbrella absorbs: firecrawl-lead-gen, firecrawl-lead-research, firecrawl-company-directories, firecrawl-competitive-intel, firecrawl-market-research, firecrawl-seo-audit, firecrawl-qa, firecrawl-demo-walkthrough, firecrawl-dashboard-reporting.
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

# Firecrawl Ops Umbrella

This umbrella skill consolidates nine operations-oriented Firecrawl workflows. Choose the sub-skill that matches your task.

## Choose Your Workflow

| Workflow | When to Use | Original Skill |
|---|---|---|
| **Lead Gen** | Generate structured lead lists from prospect databases and web directories. Find prospects by role, company type, industry, stage, location, or technologies. CRM-ready JSON/CSV export. | firecrawl-lead-gen |
| **Lead Research** | Produce pre-meeting lead intelligence briefs. Company research, person research, recent news, talking points, pain points, outreach preparation. | firecrawl-lead-research |
| **Company Directories** | Extract structured company lists from directories (YC, Crunchbase, Product Hunt, G2, startup directories, custom databases). | firecrawl-company-directories |
| **Competitive Intel** | Monitor competitor pricing, features, changelogs, dashboards, and product changes over time. | firecrawl-competitive-intel |
| **Market Research** | Extract market, financial, earnings, industry, and company metrics. Industry trends, public company data, financial comparisons, earnings research. | firecrawl-market-research |
| **SEO Audit** | Audit a website's SEO: metadata, headings, sitemap/structure, keyword opportunities, competitor SERP comparison, prioritized recommendations. | firecrawl-seo-audit |
| **QA Testing** | QA test a live website: exploratory QA, form testing, navigation/link checks, responsive checks, performance observations, bug reports, pre-launch review. | firecrawl-qa |
| **Demo Walkthrough** | Walk through a product's key flows. Signup, onboarding, pricing, docs, dashboard, product demo prep, UX teardown, first-run experience analysis. | firecrawl-demo-walkthrough |
| **Dashboard Reporting** | Pull metrics from analytics dashboards and internal web tools. Cross-platform metric summaries, authenticated analytics extraction, date-range reports. | firecrawl-dashboard-reporting |

---

## 1. Lead Gen

Extract legitimately accessible prospect lists.

### Process
- Use Firecrawl browser for databases requiring filters, search forms, pagination, or login.
- Use search/scrape for public sources.
- Apply filters: role, company size, industry, geography, funding stage, technologies.
- Extract visible fields: name, title, company, company URL, location, email/phone/LinkedIn only when visible/allowed, industry, company size, funding stage, notes, profile URL.

### Final Deliverable
```markdown
# Lead List: [Target]
## Summary
[Source, filters, count, caveats]
## Leads
[Table or link to JSON/CSV]
## Data Gaps
[Masked, unavailable, or paywalled fields]
```

### Quality Bar
- Only extract publicly visible or legitimately accessible data.
- Note masked, unavailable, or paywalled fields.
- Deduplicate leads. Do not bypass CAPTCHAs or access controls.

---

## 2. Lead Research

Create a concise, actionable pre-meeting brief.

### Process
Gather via search and scrape: company website, about, product, pricing, careers, team, customer pages; recent news, funding, launches, hiring, partnerships, press; public person profiles, talks, posts, interviews; relevant industry context and business challenges.

### Final Deliverable
```markdown
# Lead Brief: [Company]
## Company Overview
## Recent Activity
## Key People
## Talking Points
[5-7 specific conversation starters]
## Likely Pain Points
[Evidence-backed hypotheses]
## Outreach Angle
## Sources
```

---

## 3. Company Directories

Turn startup or company directories into structured lists.

### Process
Use Firecrawl browser when the directory needs filters, pagination, infinite scroll, or profile clicks. Use scrape/map when listings are public and static.
Extract fields: name, description, industry/category, stage/founded/location/team size/funding when visible, tags, directory profile URL, company website URL.

### JSON Shape
Use `source`, `filters`, `extractedAt`, `totalResults`, `companies[]` with standard fields.

---

## 4. Competitive Intel

Monitor competitors over time.

### Process
For each competitor: scrape pricing pages, annual/monthly toggles, feature tables; feature pages; changelogs, blogs, release notes, docs updates; authenticated dashboards only when the user has legitimate access.

### Final Deliverable
```markdown
# Competitive Intel: [Competitors]
## Alerts
## Per-Competitor Breakdown
## Cross-Competitor Comparison
## Suggested Follow-Ups
## Sources
```

---

## 5. Market Research

Sourced market and financial research.

### Process
Use search and scrape for market reports, news, investor relations, SEC filings, company pages. Use browser where charts, tabs, period selectors, or financial portals require interaction.
Common sources: company investor relations, SEC filings, financial portals, earnings releases, industry reports, news.

### Quality Bar
- Cross-reference key numbers when possible.
- Note conflicting data across sources.
- Include period and unit for every metric.
- Do not provide financial advice.

---

## 6. SEO Audit

Turn a website into a specific, prioritized SEO audit.

### Process
1. Map the site to understand URL structure.
2. Scrape key pages: homepage, product/service pages, pricing, docs, blog, about, landing pages.
3. Extract title tags, meta descriptions, headings, internal links, content structure, canonical signals, image alt text.
4. Search target keywords; scrape top ranking pages for comparison.

### Final Deliverable
```markdown
# SEO Audit: [Site]
## Executive Summary
## Site Structure
## On-Page SEO
## Keyword Opportunities
## Competitor/SERP Comparison
## Prioritized Recommendations
## Sources
```

---

## 7. QA Testing

Test a live site and return a unified QA report.

### Process
Use Firecrawl map to discover pages. Use Firecrawl browser for interactions, forms, navigation, responsive/manual checks. Use scrape for page content and link extraction.
Parallel testing: Navigation and Links, Forms and Interactions, Content and Visual, Error States.

### Final Deliverable
```markdown
# QA Report: [Site]
## Summary
Health score, pages tested, issues found (critical/major/minor)
## Critical Issues
## Major Issues
## Minor Issues
## Positive Observations
## Pages Tested
```

---

## 8. Demo Walkthrough

Document a product experience step by step.

### Process
Use Firecrawl browser to navigate key flows. Snapshot at each step, scrape pages when useful. Do not submit real credentials, purchases, or irreversible actions unless instructed and authorized.
Parallel walkers: Homepage and Marketing, Signup and Onboarding, Pricing and Plans, Docs and Developer Experience, Dashboard and Core Product.

### Final Deliverable
```markdown
# Product Walkthrough: [Product]
## Product Overview
## Flow Walkthroughs
## Key Findings
## Recommendations
## Pages Visited
```

---

## 9. Dashboard Reporting

Extract visible metrics from dashboards the user can legitimately access.

### Process
Use Firecrawl browser for authenticated dashboards: open each dashboard, set/verify date range, extract visible KPI cards/tables/labels, click tabs/expand sections/scroll tables. If login has expired, ask user to re-authenticate.

### JSON Shape
Use `reportedAt`, `dateRange`, `dashboards[]`, `metrics[]`, `tables[]`, `exports[]`, `summary`.

---

## General Principles (All Workflows)

- For each workflow, infer inputs from context; ask at most 1-3 concise questions only if blocked.
- Use sub-agents or parallel task runners for independent work units.
- Every deliverable should include a "Rerun Inputs" block with workflow name and parameters for easy re-execution.
- Preserve source URLs and scrape artifacts for auditability.
