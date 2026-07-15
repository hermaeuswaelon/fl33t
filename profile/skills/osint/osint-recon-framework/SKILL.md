---
name: osint-recon-framework
description: OSINT reconnaissance framework with Firecrawl, subdomain tools, certificate transparency, and public records
version: 1.0.0
author: Ares
platforms: [linux]
tags: [osint, reconnaissance, firecrawl, subdomain, certificate-transparency, public-records]
---

# OSINT Reconnaissance Framework

## Available Tools

### Firecrawl (Web Extraction & Search)
| Skill | Purpose |
|-------|---------|
| `firecrawl-search` | Web search with full page content extraction |
| `firecrawl-scrape` | Extract clean markdown from any URL |
| `firecrawl-crawl` | Bulk extract entire website |
| `firecrawl-map` | Discover all URLs on a domain |
| `firecrawl-deep-research` | Intensive analytical report with citations |
| `firecrawl-monitor` | Detect content changes on pages |

### Subdomain & DNS (from pentesting skills)
- `pentest-subdomain-enum` — subfinder, dnsx, amass workflows

### Certificate Transparency
```bash
# crt.sh via curl
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sort -u

# certspotter
curl -s "https://api.certspotter.com/v1/issuances?domain=target.com&include_subdomains=true&expand=details" | jq -r '.[].dns_names[]' | sort -u
```

### Public Records & Intelligence
| Source | Method |
|--------|--------|
| SEC EDGAR | `firecrawl-search` for company filings |
| GitHub | `firecrawl-search` + GitHub API for code/secrets |
| LinkedIn | `firecrawl-search` for employee enumeration |
| Shodan/Censys | API-based (requires keys) |
| WHOIS | `whois target.com` or `firecrawl-scrape` whois sites |

## Common OSINT Workflows

### 1. Target Surface Mapping
```bash
# 1. Subdomain enum
subfinder -d target.com -all -silent > subs.txt

# 2. Resolve + HTTP probe
cat subs.txt | dnsx -silent -a -resp | httpx -silent -title -tech-detect > live.txt

# 3. Crawl for endpoints
cat live.txt | cut -d' ' -f1 | katana -d 2 -jc -silent > endpoints.txt
```

### 2. Certificate Transparency History
```bash
# All historical certs
curl -s "https://crt.sh/?q=%25.target.com&output=json" | \
  jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u > ct_subs.txt
```

### 3. Technology Fingerprinting
```bash
# From httpx output
cat live.txt | httpx -silent -tech-detect -json > tech.json

# Extract specific tech
jq -r 'select(.tech[] | contains("WordPress")) | .url' tech.json
```

### 4. Content Discovery (Firecrawl)
```bash
# Map entire site structure
firecrawl-map --url https://target.com

# Deep research on company
firecrawl-deep-research --query "Target Company security posture vulnerabilities"
```

### 5. Employee/Infrastructure Enumeration
```bash
# LinkedIn employees (via Firecrawl search)
firecrawl-search --query "site:linkedin.com \"Target Company\" employee"

# GitHub repositories
firecrawl-search --query "org:targetcompany filename:.env OR filename:config"
```

## Pro Tips
- **Firecrawl** excels at JS-heavy sites, auth flows, and structured extraction
- Chain: `subfinder` → `httpx` → `katana` → `nuclei` for full attack surface
- Use `firecrawl-monitor` on changelogs, careers pages, GitHub releases
- Certificate transparency reveals historical subdomains no longer in DNS
- GitHub code search (via Firecrawl) finds exposed secrets, internal hosts