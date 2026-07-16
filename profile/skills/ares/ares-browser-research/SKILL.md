---
name: ares-browser-research
description: "ARES Browser Research Suite — navigate Bromium (the CEF4Delphi browser) to any website, extract content via Unix socket IPC and injected JS, control 11 installed extensions, run deepresearch on chat.deepseek.com, and save findings. Overcomes AI-blocks by using a real Chromium process."
version: 2.0.0
author: Thotheauphis / ARES
platforms: [linux]
tags: [ares, browser, bromium, research, navigation, ipc, extensions, deepseek, deepresearch, web-scraping]
related_skills: [ares-dual-citizen-browser, ares-omni-azazel-suite, computer-use]
---

# 🌐 ARES Browser Research Suite — Bromium

## Overview

Drive **Bromium** (the renamed Dual Citizen CEF4Delphi browser) to any website via Unix socket IPC. Extract page content with injected JavaScript, control 11 installed research extensions, and run autonomous deepresearch on chat.deepseek.com. Bromium runs real Chromium 131 — AI-blocking sites see a real browser.

**Binary:** `/home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/bromium`
**Socket:** `/tmp/aethelgard_cef.sock`
**CDP:** Port 9224 (in baked config)
**Ext dir:** `.../dual-citizen-v2/extensions/`
**Profile:** `/tmp/bromium-profile/`

## Quick Start

### Launch Bromium
```bash
DISPLAY=:0 /home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/bromium \
  --socket /tmp/aethelgard_cef.sock \
  --user-data-dir=/tmp/bromium-profile
```

### Navigate & Interact (via `work/bromium_bridge.py`)
```bash
cd /home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/work
python3 bromium_bridge.py navigate https://example.com
python3 bromium_bridge.py title
python3 bromium_bridge.py text                    # page body text
python3 bromium_bridge.py js "document.title"     # arbitrary JS
```

### Browse Social / Research Sites
```bash
python3 bromium_bridge.py browse reddit
python3 bromium_bridge.py search reddit "sovereign AI"
python3 bromium_bridge.py search craigslist "freepascal developer"
python3 bromium_bridge.py browse linkedin
```
Each follows: `sock_send(navigate) → sleep → execute_js → get_title`.

## DeepResearch (chat.deepseek.com)

The bridge implements a complete autonomous research pipeline using the installed BetterDeepSeek extension:

```bash
python3 bromium_bridge.py deepresearch "your research question here"
```

**Pipeline:**
1. Navigate to `https://chat.deepseek.com`
2. Wait for page load (5s)
3. Inject the extension bridge content script into page context
4. Type the query into the textarea via `nativeSetter` + `Event('input')`
5. Click send button or dispatch Enter keydown
6. Poll for response (up to 60s across 5 DOM selectors: `[class*="message"]:last-child [class*="content"]`, `.ds-markdown`, `[class*="answer"]`, `[class*="response"]`, `[class*="final"]`)
7. Return extracted text (capped at 5000 chars)

The BetterDeepSeek extension (`aabiopennjmopfippagcalmkdjlepdhh`) handles response rendering. The bridge only submits the query and extracts the result.

## Installed Extensions (11 total)

Extensions are stored in the browser profile at `/tmp/bromium-profile/Default/Extensions/`:

| ID | Name | Version | Auto-runs on |
|----|------|---------|-------------|
| `aabiopennjmopfippagcalmkdjlepdhh` | **Better DeepSeek** | 0.1.10 | `chat.deepseek.com/*` |
| `ceacgaccjcomdbnoodjpllihjmeflfmg` | **Science Research Assistant** | 3.1.3 | — |
| `liihfcjialakefgidmaadhajjikbjjab` | **alphaXiv** | 2.4.0 | `arxiv.org/abs/*`, `*.google.com/*`, `duckduckgo.com/*`, `x.com/*` |
| `ofaokhiedipichpaobibbnahnkdoiiah` | **Instant Data Scraper** | 1.6.0 | `*://*/*` |
| `okngcalljddikhljpfhgmikklmmmdkkd` | **Agent OS** | 3.2.0 | — (popup-based) |
| `ihdobppgelceaoeojmhpmbnaljhhmhlc` | **Spoof Geolocation** | 0.3.1 | — |
| `hnmpcagpplmpfojmgmnngilcnanddlhb` | *(locale key)* | 4.2.8 | — |
| `bbfnidnhpngjjbmmlakaogggmdnnjbnm` | *(locale key)* | 0.6.2 | `<all_urls>` |
| `bfaoaaogfcgomkjfbmfepbiijmciinjl` | *(locale key)* | 0.11.27 | `<all_urls>` |
| `cgenfommofedogdmkmjdndijcilplkmg` | *(locale key)* | 1.6.16 | `<all_urls>`, `getvm.io` |
| `pmaonbjcobmgkemldgcedmpbmmncpbgi` | *(locale key)* | 1.3.5 | — |

## Extension Bridge & Control

Since Bromium has no extension toolbar UI, control extensions via **injected JS** that calls `chrome.runtime.sendMessage()`:

```bash
# List installed extensions
python3 bromium_bridge.py ext-list

# List via CDP (port 9224)
python3 bromium_bridge.py ext-list --cdp

# Send a message to an extension
python3 bromium_bridge.py ext <extension-id> --action query --data '{"text":"research this"}'
```

The bridge injects a content script into every page (`chrome.runtime.onMessage.addListener`) that opens a channel to `chrome.runtime`, so socket commands can invoke extension APIs.

### Extension Enablement History
- **Before:** `--disable-extensions` was hardcoded in `dual_citizen_v2.lpr` (line 36)
- **Fix 1:** Removed the line from Pascal source + added `GlobalCEFApp.EnableExtensions := True` and `ExtensionDir`
- **Fix 2:** Hex-patched the compiled binary: `sed -i 's/--disable-extensions/--enable-extensions /g' bromium`
- **Now:** 11 extensions installed in browser profile, all content-script extensions run automatically

## Socket Protocol Reference

Send JSON commands via Unix socket, one per connection:

```python
import socket, json
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(10)
s.connect("/tmp/aethelgard_cef.sock")
s.send(json.dumps({"action": "navigate", "url": "...", "tab_id": 1}).encode() + b'\n')
resp = s.recv(65536).decode()
```

### Supported Actions
| Action | Params | Returns |
|--------|--------|---------|
| `navigate` | `url`, `tab_id` | `{id, status, url}` |
| `get_title` | `tab_id` | `{id, title}` |
| `execute_javascript` | `code`, `tab_id` | `{id, status, bytes}` |
| `list_tabs` | — | `{id, tabs: [...]}` |
| `create_tab` | `url` | `{id, tab_id}` |
| `close_tab` | `tab_id` | `{id, status}` |
| `activate_tab` | `tab_id` | `{id, status}` |

**Note:** `evaluate_js` / `get_eval` is **broken in headless** — FEvalResultReady never fires. Workaround: use `execute_javascript` to set `document.title` then `get_title` to read it back (30-char limit).

## CDP (Chrome DevTools Protocol)

CDP is available on port **9224** (baked into the compiled binary via `--remote-debugging-port=9224`):

```bash
curl http://127.0.0.1:9224/json/list        # List all targets (tabs, extensions, service workers)
curl http://127.0.0.1:9224/json/version      # Browser version info
```

Use the `cdp_get_targets()` and `cdp_evaluate()` functions in `bromium_bridge.py` to talk to extension background pages.

**Troubleshooting:** If CDP is not responding, the flag may not have survived a binary rebuild or the software renderer may be blocking it. Check with `ss -tlnp | grep 9224`.

## Related Tools in `work/`

| Tool | File | Purpose |
|------|------|---------|
| **Bromium Bridge** | `work/bromium_bridge.py` | Unified CLI for drive + extension control + deepresearch + site browsing |
| **Pascal Lens** | `work/pascal_lens.py` | Convert `.pas`/`.lpr` → AI-readable pseudo-code; CEF4Delphi type reference; structural analysis |
| **Ctx Tight** | `work/ctx_tight.py` | Squeeze verbose text into broken English + shorthand + glyphs + equations |
| **TAC** | `work/tac.py` | Thotheauphis Auto-Curator — saves context encoded in Chinese for token efficiency |

### Pascal Lens Usage
```bash
# Analyze Pascal file structure
python3 pascal_lens.py dual_citizen_v2.lpr --analyze

# Full annotated conversion with CEF type reference
python3 pascal_lens.py ucontrollerbrowser.pas --full

# Batch-convert all Pascal files in a directory
python3 pascal_lens.py --dir /path/to/pas/ --analyze

# CEF4Delphi type reference sheet
python3 pascal_lens.py --explain-types
```
Key insight: FreePascal sources use `begin`/`end`, `:=`, `.pas`/`.lpr`, and CEF4Delphi-specific types (`TCefApplication`, `GlobalCEFApp`, `TControllerForm`, `Chromium1`). The lens converts these to familiar syntax and provides type definitions for all 45+ CEF API types.

## Browser State Management

- **Log:** `/tmp/dual_citizen_v2.log`
- **Profile:** `/tmp/bromium-profile/` (contains extensions, cookies, localStorage)
- **Refresh:** Kill with `pkill -9 bromium`, relaunch with `DISPLAY=:0 ./bromium ...`
- **Extensions persist** across restarts (stored in profile's `Default/Extensions/`)

## Pitfalls

- **`evaluate_js` is broken** for returning values in headless mode. Use `execute_javascript` + `get_title` workaround or `page_text()` extraction via `document.body.innerText`.
- **CDP port 9224** may not respond if software rasterizer blocks it. Check with `ss -tlnp`.
- **Extensions must be installed via the browser UI** (drag .crx into the window, or use chrome://extensions). Placing files in `extensions/` directory requires a CEF relaunch.
- **Extension popups** (toolbar button menus) have no UI in Bromium. Use `chrome.runtime.sendMessage()` via injected JS instead.
- **BetterDeepSeek** is the only fully-working research extension. alphaXiv handles arXiv. Instant Data Scraper handles `*://*/*`.
