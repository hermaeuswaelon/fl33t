---
name: bromium-portal
description: "Bromium Portal — Stephen Hawking Edition v3.3. AOL-style desktop command center: auto-scan (continuous single-switch), dwell click, voice, AI, macros, speed dial HTML page (70+ tiles, 12 categories), Social Navigator tab, Casino Audit dashboard, Facebook Hub panel, Unified Field integration."
version: 3.3.0
author: Thotheauphis
platforms: [linux]
tags: [bromium, browser, aol, portal, gui, accessibility, hawking, social, casino, audit]
---

# ⎔ Bromium Portal — Stephen Hawking Edition v3.3

## Overview

Tkinter desktop GUI for the Bromium (Dual Citizen CEF4Delphi) browser with **5 accessibility modes** designed for **single-switch control** (Stephen Hawking model). ~1800 lines of Python.

**Location:** `~/Desktop/bromium-portal.py`
**Launcher:** `~/Desktop/Scripts-Launchers/bromium.sh portal`

## Single-Switch Flow (The One True Path)

This is how Stephen Hawking controls the browser faster than 3 power users:

| Step | User Action | What Happens | Time |
|------|-------------|-------------|------|
| 1 | Portal starts | Speed dial opens automatically (14 tiles) | 4s |
| 2 | Space (blink) | SCAN mode starts — rows cycle automatically | 0s |
| 3 | Space | Selects the highlighted row | 1.2s |
| 4 | Space | Selects the column tile → navigates | 1.2s |
| 5 | — | Page loads → elements auto-refresh | 3s |
| 6 | Space | Scan auto-restarts with new page elements | 2.5s |
| 7 | Space | Native click at element center → navigates/interacts | 1s |
| 8 | — | Auto-restart scan, cycle continues | — |

**One switch.** Continuous. Self-healing. Faster than mouse + keyboard.

## Accessibility Modes

| Mode | Key | How it works |
|------|-----|-------------|
| NORMAL | Default | Standard UI with speed dial, toolbar, tabs |
| SCAN | F2/Space | **Auto-starts on mode select.** Row-column scanning cycles continuously. Auto-restarts 2.5s after every selection |
| DWELL | F2 | Hover over any button for N ms — orange progress bar fills, then auto-clicks. Configurable delay (default 1500ms) |
| LARGE | F2 | Large-button accessibility mode |

Cycle modes with **F2** or **Tab**. Auto-scan restarts after every selection in SCAN mode.

## Speed Dial

**Three speed dial tiers working together:**

1. **Categorized sidebar** (70+ sites) — Expandable/collapsible sections in the left sidebar. Sidebar categories:

   | Section | Sites | Default |
   |---------|-------|---------|
   | 🟦 Facebook Hub | 13 (Feed, Marketplace, Groups, Watch, Gaming, Pages, Events, Friends, Saved, Business Suite, Ads, Creator, Developer) | Expanded |
   | 🟣 Meta Family | 4 (Instagram, Threads, WhatsApp, Messenger) | Collapsed |
   | 🔵 Microblogging | 4 (X, Bluesky, Mastodon, Tumblr) | Collapsed |
   | ▶️ Video | 5 (YouTube, TikTok, Twitch, Vimeo, Dailymotion) | Collapsed |
   | 💼 Professional | 4 (LinkedIn, Xing, AngelList, Indeed) | Collapsed |
   | 🎨 Visual | 6 (Pinterest, Flickr, DeviantArt, Imgur, VSCO, 500px) | Collapsed |
   | 🎵 Audio | 4 (Spotify, SoundCloud, Bandcamp, Mixcloud) | Collapsed |
   | 💬 Communities | 6 (Reddit, HN, Quora, Medium, Stack Overflow, 4chan) | Collapsed |
   | ✉️ Messaging | 5 (Discord, Telegram, Signal, Slack, Element) | Collapsed |
   | 🛠 Creator Tools | 7 (YouTube Studio, TikTok Creator, Canva, Buffer, Hootsuite, Later, Linktree) | Collapsed |
   | 🎰 Casino Audit | 12 (eCOGRA, iTech Labs, GLI, BMM, UKGC, MGA, Curacao, Wizard of Odds, AskGamblers, ThePOGG, CasinoMeister, Provably Fair) | Expanded |
   | 📚 Development | 11 (existing dev sites) | Collapsed |

2. **Browser speed dial HTML page** (`~/.config/bromium/speed-dial.html`) — Opens automatically in the browser on portal startup. 70+ dark-themed tiles in 12 sections with search bar. `file://` URL loaded via IPC.

3. **Navigate menu** — Full hierarchical menu (11 sub-menus) organized by category, each with all destinations.

## Social Navigator Tab

New main notebook tab (`🌐 Social Navigator`) showing all 70+ platforms in a scrollable categorized button grid:

- **12 category sections** with color-coded label frames
- **Search bar** — type to filter across all platforms in real-time
- **Enter → Go** — navigates to first matching site or Google search fallback
- Each button click calls `cmd_navigate(url)` via socket IPC
- Sections: Facebook Hub, Meta Family, Microblogging, Video, Professional, Visual, Audio, Communities, Messaging, Creator Tools, Casino Audit, Development

## Casino Audit Dashboard

Dedicated main tab (`🎰 Casino Audit`) with live monitoring dashboard:

- **Local Monitor panel** — reads `~/Desktop/Casino-Monitor/` files:
  - `casino_pulse.txt` — pulse status
  - `casino_timegate.json` — timegate config
  - `casino_balance_history.json` — balance records with net change
  - `casino_surveillance_log.json` — surveillance data
  - `casino_snapshot_latest.txt` — full snapshot with active monitors
- **Quick Actions** — buttons for: Check License, Verify RNG, Audit Report, Blacklist Check, Refresh Monitor
- **Audit Resources grid** — categorized links: REGULATORS (UKGC, MGA, Curacao), TESTING LABS (eCOGRA, iTech, GLI, BMM), REVIEWS (AskGamblers, ThePOGG, CasinoMeister, Wizard), TOOLS (Provably Fair)
- **Auto-refresh** every 30 seconds

## Facebook Hub Panel

First sidebar section, always expanded, with prominent Facebook-blue accent (`#1877F2`):

- **13 destination buttons** in 3-column compact grid
- **Extraction tools**: Extract Feed, Extract Links, Save to `~/bromium-extractions/`
- Helper methods: `_cmd_fb_extract_feed()`, `_cmd_fb_marketplace_search()`, `_cmd_fb_extract_groups()`

## Social Hub Sidebar

Scrollable left sidebar with expandable/collapsible category sections:

- Each section header is a button with `▸` (collapsed) / `▾` (expanded) arrow
- **Expand/collapse state tracked** in `self._sidebar_sections` OrderedDict
- Site buttons in 3-column grids with emoji icons and short labels
- Default expansion: Facebook Hub + Casino Audit expanded, all others collapsed
- Scrollbar auto-appears when content exceeds sidebar height

## Unified Field Integration (v3.3)

Portal state persistence and data bridging via Unified Field singleton:

- **State save/load**: sidebar expand state, accessibility mode, scan/dwell speeds → `uf store /portal/state/latest`
- **Casino data bridge**: balance history → `uf store /portal/casino/balance/latest`
- **Portal checkpoint**: `uf checkpoint portal-state` on exit
- **Auto-save** every 5 minutes, save on close

## Page Elements Tab

Shows all interactive elements from the current browser page in a scrollable grid.

- **Auto-refreshes** every 5 seconds when the tab is active
- **Auto-refreshes** 2 seconds after every navigation
- **Auto-refreshes** 2.5 seconds after speed dial opens
- **Filter box** — type to filter by text/tag
- **Click** → uses CEF `native_click` at element center coordinates (works on ALL elements including SPAs)
- **Link elements** (`<a>` with `href`) auto-navigate instead of clicking
- **Dwell hover** on any element button

## Tab Management

Sidebar panel showing all open browser tabs with live titles.

- **Switch tab** — click a tab in the list
- **⊕ button** — create new tab
- **✕ button** — close selected tab
- **Auto-refreshes** every 5 seconds alongside health and page elements

## Predictive Text (Ctrl+P)

Stephen Hawking's signature input method. Opens a popup with 14 common phrases:

- Type a few characters → list filters to matching predictions
- Click a prediction → types it into the browser's active input via `type_text` IPC
- Inputs that match: `h ` → "hello world", `w ` → "wikipedia.org", `g ` → "google.com", `s ` → "search for...", `y ` → "youtube.com", etc.

## Reading Mode (F6)

Toggle auto-scroll for hands-free article reading:

- F6 to start → page scrolls at comfortable pace (speed controlled by IntVar, default 40)
- Continuous `scroll_by` IPC calls at calculated intervals
- F6 again to stop
- Works on any page — articles, documentation, social feeds

## Dwell Click Visual Indicator

When DWELL mode is active, hovering over any button fills an orange progress bar:

- Enter widget → delay counter starts
- Progress bar fills over `dwell_delay` ms (default 1500)
- Bar reaches full → click fires
- Leave widget → cancel, bar resets

## Voice Control

Toggle 🎤 in toolbar. Uses bromium-voice.py --oneshot.

## AI Command Bar

Type English into toolbar AI field or the AI Agent tab:
- "extract the top 10 posts from Reddit and save them"
- "go to Wikipedia, search for Stephen Hawking, extract text"
- "go to YouTube and search for tutorials"

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| F1 | Help / keyboard shortcuts |
| F2 | Cycle accessibility mode (normal→scan→dwell→large) |
| F3 | Refresh page elements |
| F4 | Scan current page |
| F5 | Refresh browser status + tab list + health |
| F6 | Toggle reading mode (auto-scroll) |
| Space | Scanning: select row / select column item |
| Escape | Stop scanning |
| Tab | Cycle modes |
| Ctrl+P | Predictive text popup |
| Ctrl+T | New tab |
| Ctrl+W | Close tab (log) |
| Ctrl+Q | Exit |

## Native CEF Clicks (v3.2)

Page element clicks now use **real CEF mouse events** (`SendMouseClickEvent`) instead of JavaScript `.click()`:

- Works on every web element: SPAs, dropdowns, modals, canvas
- Uses element's `center.x` / `center.y` coordinates from the element query
- Three-step sequence: hover → mouse down (30ms) → mouse up
- No JavaScript dependency — immune to SPA frameworks and bot detection

## Auto-Initialization (startup sequence)

```
t=0s   Portal launches
t=0.5s health check
t=1s   message queue processing
t=2s   auto-create fresh tab (workaround: first tab broken)
t=4s   navigate browser to speed-dial.html
t=5s   auto-refresh cycle starts (health + tabs + elements every 5s)
t=6.5s page elements refresh (after speed dial loads)
```

## Dependencies

- Python 3 + tkinter (standard library)
- Bromium browser running (/tmp/aethelgard_cef.sock)
- bromium_agent.py at ~/.local/bin/
- bromium-voice.py, bromium-ai-agent.py, bromium-macros.py (optional)
- espeak (optional, TTS auditory feedback)
- vosk (optional, voice recognition)

## Timer Configs

| Parameter | Default | Range | Used by |
|-----------|---------|-------|---------|
| Scan speed | 1200ms | 300-3000ms | SCAN mode row/col cycling |
| Dwell delay | 1500ms | 500-4000ms | DWELL mode click timer |
| Auto-restart scan | 2500ms | — | Delay after scan selection before restart |
| Auto-refresh interval | 5000ms | — | Health + tabs + elements refresh |
| Page load wait | 2000ms | — | Delay after navigate before elements refresh |
| Reading mode interval | 200-2000ms | — | Calculated from speed (lower = faster scroll)
