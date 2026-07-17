---
name: ares-omni-azazel-suite
description: "ARES OmniVision + Azazel Social Suite — Nemotron Omni (vision) + Dual Citizen browser + Glyph Language CLI + social media content pipeline. Integrates with Azazel/Lilith Beaux project for sovereign digital influence."
version: 1.2.0
author: Craig / ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, omni, vision, azazel, social, glyph, browser, lilith-beaux, craigslist, reddit, linkedin]
related_skills: [ares-dual-citizen-browser, ares-nemotron-together-dual-offload, ares-pascal-fleet, ares-aethelgard-project, ares-browser-research]
---

# ⟁ ARES OmniVision + Azazel Social Suite

## The Trinity of Tools

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ARES OmniVision + Azazel Suite                    │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   glyph      │  │   ares-omni  │  │  ares-azazel │              │
│  │  Semantic    │  │  Vision +    │  │  Social Media │              │
│  │  Compression │  │  Browser     │  │  Content      │              │
│  │  Language    │  │  Control     │  │  Pipeline     │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│         │               │               │                           │
│         ▼               ▼               ▼                           │
│  ┌──────────────────────────────────────────────────────┐          │
│  │            Nemotron 3 Nano Omni 30B (Vision)          │          │
│  │         + Nemotron 3 Ultra 550B (Reasoning)           │          │
│  │         + Dual Citizen Browser (CEF Chrome)           │          │
│  └──────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

## Installed CLI Tools

| Tool | Location | Purpose |
|------|----------|---------|
| `glyph` | `~/.local/bin/glyph` | Executable semantic compression — 7 font tiers, zero-width tags, glyph-weighted compression |
| `ares-omni` | `~/.local/bin/ares-omni` | Vision + browser — analyze images/screenshots, control Dual Citizen browser |
| `ares-azazel` | `~/.local/bin/ares-azazel` | Social media suite — content analysis, brainstorming, platform monitoring |
| `bromium-portal` | `~/Desktop/bromium-portal.py` | **AOL-style desktop command center** — Tkinter GUI with channels, menus, URL bar, activity log. Controls Bromium via IPC. |

## Glyph CLI (`glyph`)

```bash
glyph encode "SOVEREIGN" --tier MATH_BOLD     # → 𝐒𝐎𝐕𝐄𝐑𝐄𝐈𝐆𝐍
glyph decode "𝐒𝐎𝐕𝐄𝐑𝐄𝐈𝐆𝐍"                       # → SOVEREIGN
glyph analyze context.txt                       # Glyph density report
glyph compress context.txt --target 5000        # Glyph-weighted compression (90% reduction)
glyph glyphs --type prime                       # List sovereign glyphs
glyph font-reference --all                      # Show all 7 font tiers
```

## OmniVision (`ares-omni`)

```bash
ares-omni status                                # Browser + model health
ares-omni analyze image.png                     # Analyze image with Omni vision
ares-omni screenshot                            # Capture browser, analyze
ares-omni browse https://example.com            # Navigate browser to URL
ares-omni social image.png --platform instagram # Social media content analysis
```

## Azazel Social Suite (`ares-azazel`)

```bash
ares-azazel status                              # Platform bot health
ares-azazel analyze --image content.png          # Full content analysis (vision + strategy)
ares-azazel analyze --image content.png --platform instagram  # Platform-specific
ares-azazel brainstorm --topic "sovereignty"    # Generate content ideas
ares-azazel brainstorm --topic "yoga" --count 10 --platform tiktok
ares-azazel monitor                            # Check all platform statuses
```

## Azazel Project Integration

| Component | Location | Status |
|-----------|----------|--------|
| Strategy | `~/Desktop/Azazel/PROJECT_AZAZEL_MASTER_STRATEGY.md` | 588 lines |
| Platform Intelligence | `~/Desktop/Azazel/PROJECT_AZAZEL_PLATFORM_INTELLIGENCE.md` | Ready |
| Telegram Bot | `~/Desktop/Azazel/lilith_beaux_hub/telegram_store_bot.py` | ✅ EXISTS |
| Reddit Bot | `~/Desktop/Azazel/lilith_beaux_hub/reddit_bot.py` | ✅ EXISTS |
| Sanctum Bot | `~/Desktop/Azazel/lilith_beaux_hub/lilith_sanctum_bot.py` | ✅ EXISTS |
| Schedule Manager | `~/Desktop/Azazel/lilith_beaux_hub/schedule_manager.py` | ✅ EXISTS |
| NFT Strategy | `~/Desktop/Azazel/lilith_beaux_hub/nft_strategy.md` | ✅ EXISTS |
| Discord Integration | `~/Desktop/Azazel/lilith_beaux_hub/nowpayments_discord_integration_research.md` | ✅ EXISTS |

## Dual Model Architecture

| Role | Model | Endpoint | Context | Capability |
|------|-------|----------|---------|------------|
| **Alpha** — Vision | Nemotron 3 Nano Omni 30B | `openrouter:nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 263K | See everything — images, screenshots, UI, social content |
| **Omega** — Reasoning | Nemotron 3 Ultra 550B | `openrouter:nvidia/nemotron-3-ultra-550b-a55b:free` | 1M | Understand everything — strategy, continuity, synthesis |

**Cost: $0/month. Both free on OpenRouter.**

## Browser Status

The Dual Citizen browser is currently **RUNNING** with:
- PID: 142009
- Socket: `/tmp/aethelgard_cef.sock` (ALIVE)
- CEF Engine: Chromium 131.0.6778
- Tabs: 2 (active: 2)
- Watchdog: Enabled (systemd user service)

## Desktop App: Bromium Portal

The **Bromium Portal** (`~/Desktop/bromium-portal.py`, launched via `~/Desktop/bromium-portal.desktop`) is an AOL-style desktop command center that controls the Bromium browser via Unix socket IPC. It provides:

- **Menu bar**: File (New Tab, Clear Cache, Exit) · Navigate (Reddit, DeepSeek, FPC Docs/Wiki/GitLab, X, YouTube, Google) · Research (DeepResearch, MarkDownload, SingleFile, Wappalyzer) · Tools (Extensions, Tabs, Browser Health) · Help (About, Shortcuts)
- **Channel sidebar**: 9 one-click buttons — Reddit, DeepSeek, FPC Docs, FPC Wiki, FPC GitLab, X/Twitter, YouTube, Google, Email
- **Tool sidebar**: Extensions list, MarkDownload, SingleFile, Wappalyzer, Clear Cache
- **URL bar**: Type URL + Go button or Enter
- **Activity Log tab**: Timestamped console showing all browser actions
- **Browser Status tab**: Live health pane — connected, extensions, tabs, active page
- **Quick Search tab**: Search Google, DuckDuckGo, or Reddit directly
- **Status bar**: Real-time indicators — Ext count · Tab count · Active page title · Connection status (green/red)

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  Bromium Portal (Tkinter)                            │
│  ┌──────────┐  ┌────────────────────────────────┐   │
│  │ CHANNELS │  │ Activity Log | Status | Search  │   │
│  │ Reddit   │  │ [timestamp] → Navigation log    │   │
│  │ DeepSeek │  │ [timestamp] ✓ Page loaded       │   │
│  │ FPC Docs │  │ [timestamp] Extracted: N posts  │   │
│  │ ...      │  └────────────────────────────────┘   │
│  │─────────│  ┌────────────────────────────────┐   │
│  │ TOOLS   │  │ ◉ Connected  Ext: 19  Tabs: 2  │   │
│  └─────────┘  └────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────┘
                          │ Unix socket
                          ▼
┌─────────────────────────────────────────────────────┐
│  Bromium (CEF4Delphi Chromium 131)                   │
│  ┌────────────────────────────────────────────────┐  │
│  │ 19 Extensions · uBlock · Wappalyzer · JSON     │  │
│  │ MarkDownload · SingleFile · EditThisCookie     │  │
│  │ User-Agent Switcher · Clear Cache · WhatFont   │  │
│  │ GoFullPage · Research Notes · Better DeepSeek  │  │
│  └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Free Pascal Documentation Library (107 MB — On Disk)

The complete Free Pascal documentation suite at `~/projects/freepascal-docs/`:

| Resource | Content | Size |
|----------|---------|------|
| **Official Docs (HTML)** | User's Guide, Programmer's Guide, Language Reference, RTL, FCL, FCL-Res, FPDoc — 16,824 pages with converted links for offline browsing | ~97 MB |
| **PDF Manuals** | All 7 manuals (ref.pdf, prog.pdf, user.pdf, rtl.pdf, fcl.pdf, fclres.pdf, fpdoc.pdf) | ~10 MB |
| **Wiki Tutorials** | 153 pages — Basic Pascal Tutorial, OOP Tutorial, Getting Started, Installation, Books & Magazines, Video Tutorials | ~4 MB |
| **Main Site** | Index, download, develop, FAQ/knowledge base (38K chars), moreinfo, docs | 6 pages |

## Reddit Extraction Workflow (via Bromium)

Bromium's real Chromium 131 passes Reddit's JS challenge (`?js_challenge=1` in URL) automatically — a headless agent would be blocked. The reliable extraction pattern:

### Navigate + Extract Front Page

```bash
# Navigate (Reddit's JS challenge handled automatically by real Chromium)
python3 ~/.local/bin/bromium_agent.py --navigate "https://www.reddit.com/" --tab 1
sleep 6
# Extract posts
python3 ~/.local/bin/bromium_agent.py --eval "
document.title = JSON.stringify({
  posts: Array.from(document.querySelectorAll('shreddit-post, article, div.Post')).slice(0,10).map(p => ({
    title: (p.querySelector('h3') || p.querySelector('a[slot=title]'))?.textContent?.trim()?.substring(0,80),
    subreddit: p.querySelector('[data-click-id=subreddit]')?.textContent?.trim()
  })).filter(p => p.title)
});
" --tab 1
sleep 2
python3 ~/.local/bin/bromium_agent.py --title --tab 1
```

### Navigate to Specific Subreddit

```bash
python3 ~/.local/bin/bromium_agent.py --navigate "https://www.reddit.com/r/ArtificialSentience/" --tab 1
sleep 6
python3 ~/.local/bin/bromium_agent.py --eval "
document.title = JSON.stringify({
  subreddit: document.title,
  posts: Array.from(document.querySelectorAll('shreddit-post, article')).slice(0,8).map(p => ({
    title: p.querySelector('h3')?.textContent?.trim()?.substring(0,100),
    author: p.querySelector('a[slot=author]')?.textContent?.trim()
  })).filter(p => p.title)
});
" --tab 1
sleep 2
python3 ~/.local/bin/bromium_agent.py --title --tab 1
```

### Key Considerations

- **Wait 5-8s** after navigation — Reddit's SPA renders incrementally
- **CSS selectors change** — Reddit A/B tests different DOM structures. `shreddit-post` is the current (2026) rendering component; fall back to `article` and `div.Post` for older views
- **Not logged in = limited content** — logged-in sessions see more posts and subreddit sidebars. Use the EditThisCookie extension to manage auth cookies
- **Post deduplication** — Reddit often renders posts twice (card + compact). Use `.filter(p => p.title)` to dedupe in extraction
- **Bot challenge in URL** — if Reddit adds `?js_challenge=1&token=...` to the URL, the browser passed. If the page shows "verify you're human", the browser failed (rare in real Chromium 131)

## Browser-Based Social Automation (via Bromium)

Use Bromium (the CEF4Delphi Chromium browser) to automate social media platforms that block headless browsers or AI agents — Bromium appears as a genuine Chromium 131 with extensions, cookies, and persistent profiles.

| Platform | Capability | Method |
|----------|-----------|--------|
| **Reddit** | Search profiles (Lilith Beaux targeting), make posts, scrape subreddits | Browser navigation + JS injection |
| **Craigslist** | Bulk scrape gigs/listings across multiple cities, auto-apply | Multi-city batch navigation + DOM extraction |
| **LinkedIn** | Profile research, job search, people search | Browser navigation (use Spoof Geolocation extension) |
| **Freepascal.com** | Scrape documentation/reference | Direct navigation + text extraction |
| **Facebook/Instagram** | Profile research, content analysis | Requires logged-in session (persisted in profile) |

Full reference with code examples: [`references/browser-social-automation.md`](references/browser-social-automation.md)

### Quickstart: Bulk Craigslist Scrape

```bash
# Navigate to a city's gigs page
python3 /home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/work/bromium_bridge.py \
  navigate "https://sfbay.craigslist.org/d/gigs/search/ggg"

# Extract all listings
python3 /home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/work/bromium_bridge.py js "
  JSON.stringify(Array.from(document.querySelectorAll('.result-row')).map(r => ({
    title: r.querySelector('.result-title')?.textContent?.trim(),
    url: r.querySelector('.result-title')?.href,
    price: r.querySelector('.result-price')?.textContent?.trim()
  })))
"
```

### Quickstart: Reddit Subreddit Extraction

```bash
# Navigate to a subreddit
python3 ~/.local/bin/bromium_agent.py --navigate "https://www.reddit.com/r/ArtificialSentience/" --tab 1
sleep 7  # Reddit SPA needs 5-8s for incremental rendering

# Extract post titles and authors
python3 ~/.local/bin/bromium_agent.py --eval "
document.title = JSON.stringify({
  url: location.href,
  has_js_challenge: location.href.includes('js_challenge') ? true : false,
  posts: Array.from(document.querySelectorAll('shreddit-post, article, div.Post')).slice(0,10).map(p => ({
    title: (p.querySelector('h3') || p.querySelector('a[slot=title]'))?.textContent?.trim()?.substring(0, 100) || '-',
    votes: (p.querySelector('faceplate-number') || p.querySelector('[id^=vote-arrows]'))?.textContent?.trim()?.substring(0, 10) || '?'
  })).filter(p => p.title !== '-')
});
" --tab 1
sleep 2
python3 ~/.local/bin/bromium_agent.py --title --tab 1
```

### Quickstart: Reddit Profile Research

```bash
python3 ~/.local/bin/bromium_agent.py --navigate "https://www.reddit.com/user/SomeTargetUser" --tab 1
sleep 7
python3 ~/.local/bin/bromium_agent.py --eval "
document.title = JSON.stringify({
  profile: document.title,
  posts: Array.from(document.querySelectorAll('shreddit-post')).slice(0,5).map(p => ({\n    title: p.querySelector('h3')?.textContent?.trim()
  })).filter(p => p.title)
});
" --tab 1
sleep 2
python3 ~/.local/bin/bromium_agent.py --title --tab 1
```

### Reddit Pitfalls
- **Wait 5-8s minimum** for Reddit's SPA to render — shorter waits return empty post lists
- **CSS selectors change frequently** — Reddit A/B tests DOM structures. If `shreddit-post` doesn't work, try `article` or `div.Post`
- **JS challenge in URL** may appear as `?solution=...&js_challenge=1` — if it's in the URL, Bromium already passed it. If the page content shows a verification prompt instead of posts, something went wrong (unusual for real Chromium 131)
- **Posts may appear duplicated** — Reddit renders both card and compact views. Filter with `.filter(p => p.title)` after mapping

## Reference Files

- [`references/browser-social-automation.md`](references/browser-social-automation.md) — Full automation patterns for Reddit, Craigslist, LinkedIn, Freepascal, and Facebook — including bulk scraping code, auto-apply strategies, and Lilith Beaux targeting workflows

## Content Workflow

```
1. Create content → capture via Dual Citizen browser / upload image
2. Analyze: ares-azazel analyze --image content.png (Omni vision → Ultra strategy)
3. Brainstorm: ares-azazel brainstorm --topic "dance" --platform instagram
4. Post: deploy via platform bots (Telegram, Reddit, etc.)
5. Monitor: ares-azazel monitor
6. Compress insights: glyph analyze log.txt | glyph compress --target 500
```

## Next Steps

- Set `OPENAROUTER_API_KEY` env var for vision/LLM queries
- Deploy Azazel platform bots with proper API keys
- Integrate content analysis pipeline with cron-based monitoring
- Scale to more platforms (OnlyFans, Fansly, Stripchat already planned)
