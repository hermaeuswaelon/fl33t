---
name: bromium-control
description: "Control the Bromium Dual-Citizen Browser via Unix socket IPC — navigate, evaluate JS, bridge extensions, read page titles, manage tabs, accessibility scanning."
version: 3.2.2
author: Thotheauphis
platforms: [linux]
tags: [bromium, browser, ipc, extensions, aethelgard, accessibility]
custom_commands:
  - command: /bromium health
    description: "Check Bromium browser health — socket, PID, extensions, tabs"
  - command: /bromium navigate <url> [--tab N]
    description: "Navigate tab N to URL"
  - command: /bromium eval <js> [--tab N]
    description: "Execute JavaScript on tab N and return result via get_eval"
  - command: /bromium native-click <x> <y> [--tab N]
    description: "Send real CEF mouse click at pixel coordinates (works on ALL elements)"
  - command: /bromium tabs
    description: "List all open tabs with titles"
  - command: /bromium activate-tab <N>
    description: "Switch to tab N"
  - command: /bromium close-tab <N>
    description: "Close tab N"
  - command: /bromium scroll <amount> [--tab N]
    description: "Scroll page by N pixels"
  - command: /bromium page-text [--max N] [--tab N]
    description: "Extract visible page text content"
  - command: /bromium elements [--tab N]
    description: "Get interactive elements with bounding boxes"
  - command: /bromium type <text> [--tab N]
    description: "Type text into focused element"
  - command: /bromium zoom <level> [--tab N]
    description: "Set page zoom level"
  - command: /bromium extensions
    description: "List all loaded extensions"
---

# 🧩 Bromium Browser Control — Stephen Hawking Edition v3.0

## Overview

Control the **Dual-Citizen Aethelgard Browser** (Bromium) — a CEF4Delphi-based Chromium 131 browser with **20 loaded extensions** — via Unix socket IPC.

**Socket:** `/tmp/aethelgard_cef.sock`
**Binary:** `~/projects/aethelgard/fleet/pascal/dual-citizen-v2/bromium`
**Watchdog:** Systemd `dual-citizen-watchdog.service` (auto-recovery ~5-8s)
**Agent CLI:** `~/.local/bin/bromium_agent.py`

## Accessibility-First Architecture

The Bromium Suite is built for **single-switch accessibility** (Stephen Hawking model):

| Mode | What it does | How it works |
|------|-------------|-------------|
| **SCAN** | Row-column scanning | Space to select row, Space to pick item |
| **DWELL** | Gaze-based clicking | Hover for N ms = click |
| **VOICE** | Speech-to-text control | "go to reddit", "search for X" |
| **AI** | Natural language | "extract top posts and save them" |
| **MACROS** | One-tap workflows | "research-mode" opens 3 tabs |

## Suite Components

| Component | Path | Purpose |
|-----------|------|---------|
| **Bromium Portal** | `~/Desktop/bromium-portal.py` | Tkinter GUI with all accessibility modes |
| **Agent CLI** | `~/.local/bin/bromium_agent.py` | Unix socket IPC for all commands |
| **Voice Commander** | `~/.local/bin/bromium-voice.py` | Speech-to-text browser control |
| **AI Agent** | `~/.local/bin/bromium-ai-agent.py` | Natural language → browser actions |
| **Macro Runner** | `~/.local/bin/bromium-macros.py` | One-click multi-step workflows |
| **Pascal Browser** | `dual-citizen-v2/bromium` | CEF4Delphi Chromium 131 binary |
| **Unified Launcher** | `~/Desktop/Scripts-Launchers/bromium.sh` | Launch any component |
| **Scan API Extension** | `extensions/assistive-scanning/` | Chrome extension: `window.__bromiumScan` |

## Quick Reference — booomium_agent.py

```bash
# Health check
python3 ~/.local/bin/bromium_agent.py

# Navigate + wait for page load
python3 ~/.local/bin/bromium_agent.py --navigate https://example.com --tab 1
sleep 3
python3 ~/.local/bin/bromium_agent.py --title --tab 1

# Execute JavaScript (result via title channel)
python3 ~/.local/bin/bromium_agent.py --eval 'document.title=JSON.stringify({url:location.href})' --tab 1
sleep 1.5
python3 ~/.local/bin/bromium_agent.py --title --tab 1

# ★ NEW: Inject assistive scan API into current page
python3 ~/.local/bin/bromium_agent.py --inject-scan --tab 1
sleep 2
python3 ~/.local/bin/bromium_agent.py --title --tab 1

# ★ NEW: Get all interactive elements with bounding boxes
python3 ~/.local/bin/bromium_agent.py --get-elements --tab 1
sleep 2
python3 ~/.local/bin/bromium_agent.py --title --tab 1

# ★ NEW: Click element by scan index
python3 ~/.local/bin/bromium_agent.py --click-element 0 --tab 1
sleep 2

# ★ NEW: Scroll page
python3 ~/.local/bin/bromium_agent.py --scroll 400 --tab 1

# ★ NEW: Extract visible page text
python3 ~/.local/bin/bromium_agent.py --page-text --max 50000 --tab 1
sleep 2
python3 ~/.local/bin/bromium_agent.py --title --tab 1

# ★ NEW: Type text (into focused element)
python3 ~/.local/bin/bromium_agent.py --type-text "Hello world" --tab 1

# ★ NEW: Set zoom level
python3 ~/.local/bin/bromium_agent.py --set-zoom 1.5 --tab 1
```

## Unified Launcher

```bash
# Launch Portal GUI
~/Desktop/Scripts-Launchers/bromium.sh portal

# Voice command mode
~/Desktop/Scripts-Launchers/bromium.sh voice

# AI agent interactive
~/Desktop/Scripts-Launchers/bromium.sh ai

# Run one AI instruction
~/Desktop/Scripts-Launchers/bromium.sh ai-cmd "extract all links from current page"

# List macros
~/Desktop/Scripts-Launchers/bromium.sh macros

# Full health check
~/Desktop/Scripts-Launchers/bromium.sh health

# Rebuild browser binary
~/Desktop/Scripts-Launchers/bromium.sh build

# Restart browser (with new binary)
~/Desktop/Scripts-Launchers/bromium.sh restart

# Stop browser completely
~/Desktop/Scripts-Launchers/bromium.sh stop
```

## Extensions (20 loaded — July 2026)

### Aethelgard Fleet Extensions

| Extension | Directory | Bridge Object | Purpose |
|-----------|-----------|---------------|---------|
| ⟐ Aethelgard Bridge | `aethelgard-bridge/` | `window.__aethelgardBridge` | Sovereign agent ↔ extension IPC |
| ⎔ DOM Scraper | `dom-scraper/` | `window.__domScraper` | Data extraction from pages |
| ⧉ Page Automation | `page-automation/` | `window.__pageAutomation` | Click, form fill, automation |
| ⧉ Session Manager | `session-manager/` | — | Tab orchestration |
| Network Proxy | `network-proxy/` | — | Proxy configuration |
| **⎔ Assistive Scanning** | `assistive-scanning/` | `window.__bromiumScan` | Accessibility: element scanning |

### Chrome Web Store Extensions (14)

uBlock Origin, JSON Viewer, Wappalyzer, Web Developer, MarkDownload, EditThisCookie, GoFullPage, WhatFont, User-Agent Switcher, Clear Cache, SingleFile, Research Notes, Better DeepSeek, Chromium Automation

## Pascal IPC Commands — Full Reference

### Standard Commands
| Command | Params | Description |
|---------|--------|-------------|
| `navigate` | `url`, `tab_id` | Navigate tab to URL |
| `execute_javascript` | `code`, `tab_id` | Execute JS, result via title channel |
| `create_tab` | — | Create new browser tab |
| `close_tab` | `tab_id` | Close a tab |
| `activate_tab` | `tab_id` | Switch to a tab |
| `list_tabs` | — | List all open tabs |
| `list_extensions` | — | List loaded extensions |
| `get_title` | `tab_id` | Get page title |
| `get_url` | `tab_id` | Get current URL |
| `evaluate_js` | `code`, `tab_id` | Full eval with result storage |
| `get_eval` | — | Get stored eval result |
| `click` | `selector`, `tab_id` | Click element by CSS selector |
| `form_fill` | `fields`, `tab_id` | Fill multiple form fields |
| `get_form_fields` | `tab_id` | Get all form field definitions |
| `go_back` / `go_forward` | `tab_id` | History navigation |
| `extension_bridge` | `code`, `tab_id` | Bridge IPC via extension |
| `install_crx` | `url` or `path` | Install CRX extension |
| `set_proxy` / `get_proxy` | — | Proxy configuration |
| `spoof` | `profile`, `tab_id` | Apply spoofing profile |
| `clear_cache` | — | Clear browser cache |

### ★ New Accessibility Commands

| Command | Params | Description |
|---------|--------|-------------|
| `native_click` | `x`, `y`, `tab_id` | **CEF native mouse click at coordinat... (v3.2)** |
| `inject_scan_api` | `tab_id` | Inject `window.__bromiumScan` (auto-injected via DoLoadEnd) |
| `get_elements` | `tab_id` | Get interactive elements with bounds |
| `click_element` | `index`, `tab_id` | JS click by scan index (legacy; prefer `native_click`) |
| `scroll_by` | `amount`, `tab_id` | Scroll page by pixels |
| `get_page_text` | `max_length`, `tab_id` | Extract visible page text |
| `type_text` | `text`, `tab_id` | Type into focused element |
| `set_zoom` | `level`, `tab_id` | Set page zoom level (float) |

### window.__bromiumScan API

Injected via `inject_scan_api` or via DoLoadEnd auto-injection. Compact JavaScript API for assistive scanning:

```javascript
window.__bromiumScan = {
  getElements()    // → [{id, tag, text, bounds, center}, ...] sorted visually
  getPageText(max) // → string — visible text content
}
```

## Native CEF Click (`native_click` IPC)

**Added v3.2.** Sends real mouse events via CEF's `SendMouseClickEvent` at pixel coordinates. Works on **every** web element — SPAs, modals, dropdowns, canvas — because it bypasses JavaScript entirely.

### Pascal Implementation

```pascal
// HandleCommand, ucontrollerbrowser.pas, ~line 1100
var
  mouseEvent: TCefMouseEvent;
begin
  mouseEvent.x := nx;     // from IPC params
  mouseEvent.y := ny;
  mouseEvent.modifiers := 0;
  browserHost := FTabs[i].ChromiumWindow.ChromiumBrowser.Browser.Host;
  browserHost.SendMouseMoveEvent(@mouseEvent, False);  // hover first
  Sleep(10);
  browserHost.SendMouseClickEvent(@mouseEvent, MBT_LEFT, False, 1);  // down
  Sleep(30);
  browserHost.SendMouseClickEvent(@mouseEvent, MBT_LEFT, True, 1);   // up
end;
```

### CEF4Delphi API (critical — record-based, not coordinate-based)

| CEF4Delphi Method | Parameters | Notes |
|---|---|---|
| `SendMouseMoveEvent` | `const event: PCefMouseEvent; mouseLeave: Boolean` | Pointer to record, NOT x,y ints |
| `SendMouseClickEvent` | `const event: PCefMouseEvent; mouseButtonType: TCefMouseButtonType; mouseUp: Boolean; clickCount: Integer` | MBT_LEFT=0 |
| `PCefMouseEvent` | `^TCefMouseEvent` | Pass with `@` operator |
| `TCefMouseEvent` | `x: Integer; y: Integer; modifiers: TCefEventFlags` | Stack record, not class |

### Pitfalls

- **DO NOT pass x,y as separate args** — takes `PCefMouseEvent`. Error: `Wrong number of parameters`.
- **Declare `mouseEvent` in procedure `var` section** — Pascal forbids `var` inside `begin...end`.
- **Use `MBT_LEFT` not `0`** — `TCefMouseButtonType` is an enum. `0` gives `Incompatible type: Got ShortInt`.
- **`SendMouseMoveEvent` must come first** — CSS `:hover`-dependent UIs need mouseenter before accepting clicks.
- **30ms sleep** between down/up — zero-delay clicks get filtered by anti-bot heuristics.

### Python usage

```python
def _native_click(self, x, y):
    return sock_cmd("native_click", x=x, y=y, tab_id=self.current_tab)

# Using center coordinates from element query:
cx = element.get("center", {}).get("x", 0)
cy = element.get("center", {}).get("y", 0)
if cx and cy:
    _native_click(cx, cy)
```

## Tab Management IPC

`list_tabs` returns titles (added v3.2):

```json
{"tabs": [
  {"tab_id": 1, "profile": "", "data_dir": "...", "title": "about:blank"},
  {"tab_id": 2, "title": "Example Domain"}
]}
```

Commands: `list_tabs`, `activate_tab`, `close_tab`, `create_tab`.

## Voice Commander — `bromium-voice.py`

```bash
bromium-voice.py --listen        # Interactive voice command loop
bromium-voice.py --oneshot        # One command, then exit
bromium-voice.py --say "go to reddit"  # Direct command (no STT)
```

### Voice Commands
| Say | Action |
|-----|--------|
| "go to reddit" | Navigate to known site |
| "search for quantum computing" | Google search |
| "scroll down/up" | Scroll page |
| "click 3" | Click element 3 from scan |
| "back / forward / reload" | History / refresh |
| "new tab / close tab / tabs" | Tab management |
| "extract page" | Get page text content |
| "type hello world" | Type into input |
| "ai do something complex" | AI agent delegation |
| "macro research-mode" | Run a named macro |
| "status / help" | Browser health / help |

## AI Agent — `bromium-ai-agent.py`

Takes natural language instructions and decomposes them into sequential browser actions:

```bash
bromium-ai-agent.py --cmd "extract the top 10 posts from Reddit"
bromium-ai-agent.py --cmd "go to Wikipedia, search for Stephen Hawking, extract text"
bromium-ai-agent.py --cmd "open YouTube and search for free pascal tutorial"
bromium-ai-agent.py --interactive  # REPL mode
```

## Macro System — `bromium-macros.py`

```bash
bromium-macros.py --list                     # List available macros
bromium-macros.py --run research-mode        # Execute a macro
bromium-macros.py --add my-macro             # Create new macro
bromium-macros.py --export                   # Export all macros as JSON
```

### Built-in Macros
| Macro | Steps | Description |
|-------|-------|-------------|
| `research-mode` | 9 | Opens Wikipedia, Scholar, ArXiv in 3 tabs |
| `reddit-scrape` | 4 | Extracts top posts from Reddit front page |
| `daily-briefing` | 7 | Opens HN, BBC, Lobsters |
| `page-save` | 2 | MarkDownload preparation |
| `extract-links` | 2 | Extract all links to JSON |
| `extract-full-page` | 2 | Full page text extraction |
| `deepseek-chat` | 3 | Navigate to DeepSeek |
| `clear-all` | 2 | Clear cache + reset |
| `browser-status` | 1 | Health report |

## Portal GUI — `bromium-portal.py`

```bash
python3 ~/Desktop/bromium-portal.py
```

Five modes accessible from toolbar or F2/Tab keyboard shortcuts:
1. **NORMAL** — Standard UI with speed dial + toolbar
2. **SCAN** — Row-column scanning (Space to select row, Space to pick item)
3. **DWELL** — Gaze/hover dwell-click (configurable 1500ms delay)
4. **LARGE** — Large-button accessibility mode

Additional features:
- 🎤 Voice toggle → text input dialog → `bromium-voice.py --say` (not mic-based; see Pitfalls)
- 🤖 AI command bar → English instruction → browser automation
- ⚡ Macro quick-buttons → one-tap complex workflows
- 🔊 TTS auditory feedback (espeak → WAV → aplay through ALSA devices)
- Live health monitoring (5s refresh)

### Portal v4 — Glassmorphism + AOL Oldschool Redesign (July 2026)

The v4 portal (`bromium-portal-v4.py`) implements a sovereign "system of the future" aesthetic:

| Layer | Style | Contrast |
|-------|-------|----------|
| Background | Dark radial gradient (#0a0e17 → #05080e) | — |
| Panels | Glassmorphism: rgba(20,28,44,0.85) + blur(12px) + 1px border | WCAG AA on dark |
| Text | #e8edf5 on panels, #8ab4f8 on headers | 7.2:1 minimum |
| Accents | #00d4aa (teal), #ff6b6b (coral), #ffd93d (amber) | Color-blind safe |
| Borders | 1px solid rgba(255,255,255,0.08) | Subtle separation |

**UI Components:**
- **AOL-style Menu Bar** (File, Edit, View, Go, Tools, Window, Help) — native tk.Menu themed
- **Toolbar** — Connect/Disconnect, New Tab, Reload, Home, Back/Forward, Voice, TTS, AI, Predictive Text
- **Tab Bar** — Drag-reorder, close buttons, favicon placeholder, title truncation
- **Sidebar** — Minilists (irrational timers), Scrapers, Cayce Readings, Logs, Settings
- **Content Area** — CEF embed placeholder + Welcome screen with quick actions
- **Status Bar** — Live CPU/Memory (psutil, 5s), Connection status, Latency, Action queue

**Quick Actions on Welcome Screen:**
- 🔗 Connect Browser (starts Bromium CEF)
- 🤖 AI Agent Mode (MOA: 2 strict refs + 1 creative aggregator)
- 🔴 Reddit Worker (PRAW automation with irrational timers)
- 📘 Facebook Worker (Bromium tab automation)
- 🕷️ Scraping Pipeline (anti-bot countermeasures)
- 🔮 Cayce Readings Finder (semantic search)
- ⚙️ Settings

**Integration Points:**
- Reddit Worker: `--add-user`, `--send-message`, `--post`, `--scrape-subreddit`, `--start-worker`
- MOA Agent Mode: Uses Hermes MOA preset `default` (configured in `~/.hermes/profiles/thotheauphis/config.yaml`)
- Bromium IPC: All browser actions via `/tmp/aethelgard_cef.sock`

### Pitfalls

- **Voice button uses `--say` not `--listen`** — no microphone/Whisper dependency. Opens a text dialog, then calls `bromium-voice.py --say "text"`.
- **TTS uses espeak + ALSA** — tries `hw:1,0` (analog) → `hw:0,3` (HDMI) → default. No PulseAudio/PipeWire dependency.
- **Portal close button** — uses `WM_DELETE_WINDOW` protocol calling `root.quit()` + `sys.exit(0)`. Ctrl+Q routes through same handler.
- **Browser must stay dead** — stop `dual-citizen-watchdog.service` or it respawns CEF in ~5-8s.
- **Glassmorphism on X11** — `tkinter` has no native backdrop blur. Uses solid rgba background + border. For true blur, need compositor (picom) + custom frame.
- **Drag-reorder tabs** — implemented via `<Button-1>`/`<B1-Motion>`/`<ButtonRelease-1>` on tab buttons. Track index, swap in `self.tabs` list, rebuild bar.

## Reddit Worker Integration (New — July 2026)

The Bromium Portal v4 integrates a **PRAW-based Reddit automation worker** with irrational timers for human-like behavior:

### Worker Module
**Path:** `/home/craig/.local/bin/reddit-worker.py`

### Capabilities
| Feature | Description |
|---------|-------------|
| **Messaging** | Send PMs to users with human-like delays (30-120s between messages) |
| **Posting** | Submit posts to subreddits (text, link, or crosspost) |
| **Commenting** | Comment on submissions and reply to comments |
| **Voting** | Upvote/downvote submissions and comments |
| **Scraping** | Subreddit posts (hot/new/top/rising), user activity, search, post comments |
| **Minilists** | SQLite-backed priority queues with cooldown tracking per target |
| **Background Worker** | Autonomous processing of minilist items with configurable actions |

### Irrational Timer Profiles
The Reddit worker uses the **Advanced Human-Like Timer** (see `mathematical-timers/scripts/irrational_timer_advanced.py`):

| Action Type | Log-Normal (μ, σ) | Description |
|-------------|-------------------|-------------|
| `message` | 1.8, 0.4 | Sending PMs — slow, careful |
| `comment` | 1.2, 0.3 | Public comments — moderate |
| `reply` | 1.0, 0.3 | Replies — slightly faster |
| `post` | 2.5, 0.5 | Creating posts — slowest |
| `upvote` | 0.5, 0.2 | Quick reactions |
| `scrape` | 0.8, 0.2 | Reading — fast |
| `global` | 2.0, 0.5 | Between actions |

**Plus:** Pareto bursts (5% chance, α=1.5, scale=2.0) + Circadian rhythm (peak 14:00, trough 04:00)

### Portal Integration

**Sidebar Minilists Panel** shows Reddit targets with:
- Target type (user/subreddit/post)
- Priority (0-100, higher = more urgent)
- Cooldown remaining
- Actions/hour rate limit
- Last action timestamp

**Quick Actions (Welcome Screen):**
- 🔴 Reddit Worker → launches `reddit-worker.py` CLI or starts background worker
- Configure OAuth credentials via `--add-account`

### CLI Quick Reference

```bash
# Add account (OAuth)
python3 reddit-worker.py --add-account --username USER --client-id ID --client-secret SECRET --refresh-token TOKEN

# Add targets to minilist
python3 reddit-worker.py --add-user "target_user" --list-name "outreach" --priority 50
python3 reddit-worker.py --add-subreddit "target_sub" --list-name "monitor" --priority 30

# List targets
python3 reddit-worker.py --list-targets --list-name "outreach"

# One-off actions
python3 reddit-worker.py --send-message "user" "Subject" "Body"
python3 reddit-worker.py --post "subreddit" "Title" "Body"
python3 reddit-worker.py --comment "post_id" "Comment text"
python3 reddit-worker.py --scrape-subreddit "subreddit" "hot"
python3 reddit-worker.py --scrape-user "username"

# Background worker
python3 reddit-worker.py --start-worker
python3 reddit-worker.py --stop-worker
python3 reddit-worker.py --worker-status
```

### Database
**Path:** `~/.local/share/bromium/reddit_worker.db`

Tables: `accounts`, `minilist`, `action_log`

### Configuration
**Path:** `~/.config/bromium/reddit_config.json`

```json
{
  "global_cooldown": 2.0,
  "max_concurrent_actions": 1,
  "default_minilist": "default"
}
```
def fast_eval(code, tab_id=1, max_polls=40):
    """Execute JS and poll get_eval at 50ms until result ready. Typical: 50-150ms."""
    sock_cmd("execute_javascript", code=code, tab_id=tab_id)
    for _ in range(max_polls):
        r = sock_cmd("get_eval", tab_id=tab_id)
        if r.get("status") == "ok":
            raw = r.get("result", "")
            if raw:
                try: return json.loads(raw)  # result is JSON embedded in JSON
                except: return raw  # plain string result
        time.sleep(0.05)
    return None  # timeout after ~2s
```

**Why it works:** `ExecuteJS` calls `browser.MainFrame.ExecuteJavaScript(code)` which sets `document.title`. CEF fires `DoTitleChange` which stores the title in `FTabs[i].LastTitle` AND sets `FEvalResult := title; FEvalResultReady := True`. The `get_eval` IPC checks `FEvalResultReady` and returns the stored result immediately — no round-trip to the renderer process needed.

**Benchmark:** The raw `ExecuteJS` + `get_eval` cycle takes ~50-100ms (two socket round-trips). The old `execute_javascript` + `time.sleep(2)` + `get_title` cycle took ~3500ms.

**Important:** `get_eval` returns the result as a JSON-embedded string. The `result` field in the response contains the JavaScript value stringified. Parse it with `json.loads()` after extracting from the outer JSON:
```python
# Raw response from get_eval IPC:
# {"id":"1","status":"ok","result":"{\"a\":1,\"b\":\"test\"}"}
# `result` value is: {"a":1,"b":"test"}
# After json.loads(result): {'a': 1, 'b': 'test'}
```

## Direct JS Element Querying (reliable alternative to scan API)

The scan API's `getElements()` method can have Pascal string escaping issues in auto-injected code. **Prefer direct `querySelectorAll` + `Array.from().map()`** JS in `execute_javascript`:

```python
code = '''
document.title=JSON.stringify(
(function(){
  var e=document.querySelectorAll("a[href],button,input:not([type=hidden]),select,textarea");
  return Array.from(e).map(function(n,i){
    var b=n.getBoundingClientRect();
    if(b.width<4||b.height<4)return null;
    var t=n.textContent.trim().substring(0,80)||n.placeholder||n.title||n.getAttribute("aria-label")||"";
    return{id:i,tag:n.tagName.toLowerCase(),text:t,
      href:n.href||"",
      bounds:{top:b.top|0,left:b.left|0,width:b.width|0,height:b.height|0},
      center:{x:(b.left+b.width/2)|0,y:(b.top+b.height/2)|0}}
  }).filter(function(e){return e!==null})
})()
)'''
result = fast_eval(code, tab_id=tab)
# result is a list of element dicts
```

**Advantages over scan API:**
- No Pascal string escaping issues (JS is passed as a single argument, not concatenated)
- Works independently of DoLoadEnd auto-injection
- Same speed (~50ms for example.com with 1 element)
- No `WeakSet` or other ES6 feature dependencies

## Auto-Injection in DoLoadEnd

`ucontrollerbrowser.pas` line ~1300: Every page load injects `window.__bromiumScan` via `browser.MainFrame.ExecuteJavaScript(...)`. This means:

- No manual `inject_scan_api` IPC needed after navigation
- Scan API is available immediately when `DoLoadEnd` fires
- Only injects on non-Chrome-Web-Store pages (those get their own CWS hook)

**Implementation detail:** The JS code is built with Pascal string concatenation. To avoid escaping issues, keep the JS as simple as possible — no template literals, no arrow functions, no `?.` optional chaining. Prefer `Array.from()` over spread operator. Prefer `indexOf()` over `.includes()`.

## IPC JSON Parsing: Two Escaping Patterns

Pascal IPC responses use **two different escaping conventions** that must be handled separately:

| Pattern | Used by | Example |
|---------|---------|---------|
| `\"` (single backslash) | Most IPCs (get_title, scroll_by, set_zoom, get_eval) | `{"status":"ok","title":"hello"}` |
| `\\\"` (double backslash) | list_extensions, any IPC using `Format('\\\"...\\\"', ...)` | `{\\"id\\":\\"1\\",\\"extensions\\":[...]}` |

**Safe parsing pattern (use in any Python IPC client):**

```python
def parse_ipc_response(raw_text):
    # Try raw first (most IPCs use standard JSON)
    try: return json.loads(raw_text)
    except:
        # Fallback: unescape Pascal \\\" → " and find first JSON object
        t = raw_text.replace('\\"', '"')
        for i, ch in enumerate(t):
            if ch in ('{', '['):
                try: return json.loads(t[i:])
                except: continue
    return {"error": "parse_failed", "raw": raw_text[:200]}
```

## Reference Files

| File | What it contains |
|------|-----------------|
| `~/.local/bin/bromium_agent.py` | Updated agent CLI with all 19+ IPC commands |
| `~/.local/bin/bromium-voice.py` | Speech-to-text command listener |
| `~/.local/bin/bromium-ai-agent.py` | Natural language → browser action pipeline |
| `~/.local/bin/bromium-macros.py` | Macro runner + storage (`~/.config/bromium/macros.json`) |
| `~/Desktop/bromium-portal.py` | Stephen Hawking Edition Tkinter GUI |
| `~/Desktop/Scripts-Launchers/bromium.sh` | Unified launcher for all components |
| `~/Desktop/bromium-portal.desktop` | Desktop entry for portal |
| `ucontrollerbrowser.pas` | Pascal source: all IPC handlers + accessibility commands |
| `extensions/assistive-scanning/manifest.json` | Chrome extension for `window.__bromiumScan` |
| `extensions/assistive-scanning/content.js` | Full scan API JS (auto-injects on page load) |
| `references/portal-session3-features.md` | Page Elements tab, predictive text, dwell indicator, new shortcuts |
| `references/fast-eval-pattern.md` | execute_javascript + get_eval polling, JSON parsing nuances |
| `references/redteam-suite.md` | Bromium Red Team Suite — CEF-level recon, credential sweep, network interceptor, native clicks |
| `references/portal-wiring-session.md` | TTS, voice, close button, watchdog wiring from v3.2.1 session |
| `/tmp/aethelgard_cef.sock` | IPC socket |
| `~/bromium-extractions/` | Saved page extractions (JSON) |

## IPC Protocol Notes

### JSON Parsing: The `.replace('\\\\"', '"')` Trap

The socket returns standard JSON from most commands (`get_title`, `navigate`, `get_eval`) but
`list_extensions` uses Pascal `Format('\\"…\\"', …)` producing double-escaped quotes.
A naive Python `resp.replace('\\\\"', '"')` **destroys valid JSON** that contains escaped inner
quotes in string values (e.g. tab titles with embedded JSON).

**Robust parsing pattern:**

```python
text = resp.decode("utf-8", errors="replace")
stripped = text.strip()
if stripped:
    try: return json.loads(stripped)
    except json.JSONDecodeError: pass
for i, ch in enumerate(text):
    if ch in ("{", "["):
        try: return json.loads(text[i:])
        except json.JSONDecodeError: continue
return {"status": "error", "error": "no valid json", "raw": text[:300]}
```

### JS Evaluation: `__bromium_rt` Private Variable Pattern

**Problem:** Writing every JS result to `document.title` causes a **title channel collision**
— `get_page_text()`, `dom_sniff()`, and `js_eval` all overwrite it, so sequential calls
lose each other's results.

**Solution:** Store results in `window.__bromium_rt` (a private JS variable), then read it
back with a second minimal `execute_javascript` call:

```python
wrapper = (
    f"(function(){{"
    f"try{{window.__bromium_rt=JSON.stringify((function(){{{code}}})())}}"
    f"catch(e){{window.__bromium_rt=JSON.stringify({{error:''+e.message}})}}"
    f"}})()"
)
_sock("execute_javascript", code=wrapper, tab_id=tab)
time.sleep(1.0)
reader = "document.title=window.__bromium_rt||JSON.stringify({error:'not set'})"
_sock("execute_javascript", code=reader, tab_id=tab)
time.sleep(0.5)
r = _sock("get_title", tab_id=tab)
```

| Pattern | When | Why |
|---------|------|-----|
| `__bromium_rt` two-call | Data retrieval (DOM dump, storage, metrics) | Avoids title collision |
| Direct `document.title` | Raw page text extraction | Only when nothing else writes to title |

### DOM Enumeration: try/catch Per Element

`querySelectorAll('*')` iterates all nodes. Wrap each iteration in `try/catch` because
`getComputedStyle()` throws on detached nodes and `getBoundingClientRect()` can fail on
virtual/offscreen elements. Without this, a single problematic node silently aborts the
entire enumeration returning 0 elements:

```javascript
for(i=0;i<els.length;i++){
  try{
    n=els[i];b=n.getBoundingClientRect();cs=window.getComputedStyle(n);
    out.push({id:i, tag:n.tagName.toLowerCase(), ...})
  }catch(e){}
}
```

### Red Team Suite Reference

A CEF-level reconnaissance suite (`bromium_redteam.py`) now ships under this umbrella.
See `references/redteam-suite.md` for modules, CLI commands, and architecture.

## Pitfalls

### Portal Tkinter — Widget Creation Order

**`_sb_mode` accessed before created.** `_build_accessibility_toolbar()` calls `_update_mode_buttons()`, which does `self._sb_mode.configure(...)`. But `_sb_mode` is created in `_build_status_bar()`, which runs LATER in `__init__`. Fix: move `self._update_mode_buttons()` from the toolbar builder to `__init__` after `_build_status_bar()`.

```python
# __init__ — correct ordering
self._build_menu_bar()
self._build_accessibility_toolbar()
self._build_main_layout()
self._build_status_bar()
self._update_mode_buttons()  # moved here: needs _sb_mode from status bar
```

**grid/pack geometry manager mixing.** `_refresh_macro_grid()` called `btn.grid(row, col, ...)` inside `self._macro_grid` — a frame packed into `self.macro_frame`. Tkinter raises: `TclError: cannot use geometry manager grid inside ...frame which already has slaves managed by pack`. Fix: convert to all-pack layout using per-row sub-frames:

```python
row_frame = None
for i, name in enumerate(macros):
    if i % 3 == 0:
        row_frame = tk.Frame(self._macro_grid, bg=DARK_BG)
        row_frame.pack(pady=2)
    btn = tk.Button(row_frame, text=name.upper(), ...)
    btn.pack(side=tk.LEFT, padx=4)
```

**Rule:** Never mix `pack` and `grid` for siblings sharing the same parent. Pick one geometry manager per parent frame — pack for linear flows, grid for tables.

### Portal TTS & Voice
- **TTS espeak → ALSA pipeline.** Portal's `speak_async()` generates a WAV via espeak then plays via `aplay` through ALSA (`hw:1,0` analog → `hw:0,3` HDMI → `default`). All exceptions caught silently. To test: `espeak "test" -w /tmp/t.wav && aplay -D hw:1,0 /tmp/t.wav`. Uses `tempfile.mktemp(suffix=".wav")` — ensure `import tempfile` in portal imports.
- **Voice button is text-dialog, not mic.** `_start_voice_listener` pops `tk.simpledialog.askstring()` → `bromium-voice.py --say`. Not `--oneshot` (mic) because `openai-whisper` is too heavy (~2GB with torch) for mid-session install. To add mic: `pip install openai-whisper` and revert `_start_voice_listener` to `--oneshot` path.
- **`bromium-voice.py --oneshot` needs whisper.** Falls back to `speech_recognition` (Google API, needs pulseaudio + internet).

### Portal Close & Browser Restart
- **X button does nothing without protocol handler.** Tkinter's `WM_DELETE_WINDOW` protocol must be set: `self.root.protocol("WM_DELETE_WINDOW", self._on_close)`. The handler must call `self.root.quit()` + `sys.exit(0)` — `root.quit()` alone stops the mainloop but doesn't exit the process.
- **Watchdog restarts killed browser.** `dual-citizen-watchdog.service` auto-restarts the bromium binary within ~5-8s. To kill the browser permanently: `systemctl --user stop dual-citizen-watchdog.service` first, then kill the bromium/cef_controller PIDs. Clean up the socket: `rm -f /tmp/aethelgard_cef.sock`.

### Portal Performance Monitor
- **Live CPU/MEM meter added to status bar.** `_build_status_bar()` creates `self._sb_perf` label, right-aligned before health indicator. `_update_perf()` polls `psutil.virtual_memory()` + `psutil.cpu_percent(interval=0)` every 5s via `self.root.after(5000, ...)`. Requires `psutil` package (7.1.0 installed).
- **Hermes CLI cost/timestamps.** Enable performance output in terminal: `hermes config set show_cost true && hermes config set timestamps true`.

### Tab Management
- **First tab (tab 1) often won't load pages** — CEF init ordering issue. Always create a new tab first, then navigate on the new tab (ID ≥ 2).

  ```python
  result = sock_cmd("create_tab")
  new_tab_id = result.get("tab_id", 2)
  sock_cmd("navigate", url="https://example.com", tab_id=new_tab_id)
  ```

- **`get_eval` vs `get_title`** — `get_eval` returns immediately (via `FEvalResult`). `get_title` reads page's actual title. Prefer `get_eval` for JS results.

### JSON & JS
- **`list_extensions` uses double-escaped quotes** (`\\\\\\\"`). Use safe parsing pattern above, not naive `json.loads()`.
- **Auto-inject JS must avoid ES6+** — Pascal string concat can't handle backticks, `=>`, `?.`. Keep to ES5: `function()`, `indexOf()`, `Array.from()`. Test after Pascal rebuild.
- **Page nav destroys JS context.** DoLoadEnd re-injects, but ~100ms window where `__bromiumScan` unavailable. Use direct `querySelectorAll` JS during that window.
- **`about:blank` = not loaded** — Poll title in loop. Never fixed `sleep()`.

### Build & Deploy
- **Rebuild required after Pascal changes** — `fpc` compile (1.5s), restart browser. Ensure `cef_controller` same binary: `cp bromium cef_controller`.
- **`EncodeJSON` vs manual escaping** — Pascal's `EncodeJSON` handles most cases. For complex inline JS, prefer `ExecuteJS` with well-tested strings over Pascal concatenation.
