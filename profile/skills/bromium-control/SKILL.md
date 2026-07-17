---
name: bromium-control
description: "Control the Bromium Dual-Citizen Browser via Unix socket IPC — navigate, evaluate JS, bridge extensions, read page titles, manage tabs, accessibility scanning."
version: 3.2.0
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
- 🎤 Voice toggle → `bromium-voice.py --oneshot` listener
- 🤖 AI command bar → English instruction → browser automation
- ⚡ Macro quick-buttons → one-tap complex workflows
- 🔊 TTS auditory feedback (espeak)
- Live health monitoring (5s refresh)

## Fast Eval Pattern (get_eval polling)

**Replace 2-second fixed sleeps with sub-100ms polling.** The key architectural change:

1. **Pascal: `ExecuteJS` resets `FEvalResultReady := False`** before executing JS (line 393 of `ucontrollerbrowser.pas`). This makes `get_eval` IPC return immediately after `DoTitleChange` stores the result.
2. **Python: poll `get_eval` in 50ms intervals** instead of sleeping 1.5-2s for `get_title`.

```python
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

- **First tab (tab 1) often won't load pages** — The Bromium browser's initial tab frequently stays on `about:blank` after a `navigate` call. **Always create a new tab** with `create_tab` IPC (or `--create-tab`), then navigate on the new tab. The new tab's ID will be ≥ 2. This is a CEF initialization ordering issue — the first tab's browser context isn't fully ready for navigation at startup.

  ```python
  # ✅ Correct: create tab first, then navigate
  result = sock_cmd("create_tab")
  new_tab_id = result.get("tab_id", 2)
  sock_cmd("navigate", url="https://example.com", tab_id=new_tab_id)

  # ❌ Wrong: navigating tab 1 will likely stay on about:blank
  sock_cmd("navigate", url="https://example.com", tab_id=1)
  ```

- **`get_eval` vs `get_title`** — After `execute_javascript`, `get_eval` returns immediately (via `FEvalResult`). `get_title` reads the page's current title which may have changed since the JS ran. **Prefer `get_eval` for JS results.** Only use `get_title` when you need the page's actual title (not a JS-set one).

- **`list_extensions` uses different escaping** — Unlike other IPCs, `list_extensions` wraps its response in `\\\"` (double-escaped quotes). Always use the safe parsing pattern above, not a naive `json.loads()`.

- **Auto-inject JS must avoid modern JS features** — Pascal string concatenation in `DoLoadEnd` can't handle backticks, `=>`, or `?.`. Keep auto-injected JS to ES5 idioms: `function()`, `indexOf()`, `Array.from()`. Test after every Pascal rebuild.

- **Page nav destroys JS context** — Navigating to a new page destroys all injected JS. The DoLoadEnd auto-injection re-injects it, but there's a brief window (~100ms) between navigation and DoLoadEnd where `__bromiumScan` is unavailable. If you call `get_elements` during this window, use the direct `querySelectorAll` JS (which doesn't depend on the scan API).

- **`about:blank` = not loaded** — Poll title in a loop after navigate. Never use fixed `sleep()`.

- **Rebuild required after Pascal changes** — `fpc` compile (1.5s), restart browser. Always check `cef_controller` is the same binary: `cp bromium cef_controller`.

- **`EncodeJSON` vs manual escaping** — Pascal's `EncodeJSON` handles most cases. For complex inline JS, prefer `ExecuteJS` with well-tested JS strings rather than Pascal string concatenation.
