---
name: bromium-extension-bridge
description: "Control the Aethelgard Bridge extension and all loaded extensions inside Bromium via Unix socket IPC — list, open, bridge, evaluate."
version: 1.0.0
author: Thotheauphis
platforms: [linux]
tags: [ares, bromium, extensions, bridge, ipc, aethelgard]
related_skills: [ares-dual-citizen-browser, ares-browser-research]
---

# 🧩 Bromium Extension Bridge — Agent Control

## Overview

Bromium loads unpacked Chrome extensions from `extensions/` and profile-based extensions from the browser profile. This skill covers **how I (the agent) control all of them** via the Unix socket IPC.

**Socket:** `/tmp/aethelgard_cef.sock`
**Binary:** `~/projects/aethelgard/fleet/pascal/dual-citizen-v2/bromium`
**Custom extension:** `extensions/aethelgard-bridge/`

## Quick Reference

```python
import socket, json

def sock_cmd(action, **kw):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect("/tmp/aethelgard_cef.sock")
    payload = {"action": action, "id": "1", **kw}
    s.send(json.dumps(payload).encode() + b"\n")
    resp = s.recv(65536).decode()
    s.close()
    return json.loads(resp)
```

## Extension IPC Commands

### `list_extensions` — List all loaded unpacked extensions
```python
sock_cmd("list_extensions")
# → {"extensions": [{"name": "⟐ Aethelgard Bridge", "dir": "aethelgard-bridge"}]}
```
Scans the `extensions/` directory for subdirectories containing `manifest.json`.

### `open_extension` — Activate an extension in a new tab
```python
sock_cmd("open_extension", name="⟐ Aethelgard Bridge")
# Creates a new tab and executes a bridge ping to verify connectivity
# → {"status": "ok", "name": "⟐ Aethelgard Bridge"}
```

### `extension_bridge` — Send JS through `window.__aethelgardBridge`
```python
# Ping the bridge to check connectivity
sock_cmd("extension_bridge",
    code="b.send('ping').then(r=>document.title=JSON.stringify(r))",
    tab_id=1
)

# Get all tabs via extension API
sock_cmd("extension_bridge",
    code="b.send('get_all_tabs').then(r=>document.title=JSON.stringify(r))"
)

# Get page source HTML
sock_cmd("extension_bridge",
    code="b.send('get_page_source').then(r=>document.title=JSON.stringify(r))"
)

# Read extension storage
sock_cmd("extension_bridge",
    code="b.send('get_storage',{key:'settings'}).then(r=>document.title=JSON.stringify(r))"
)

# Write extension storage
sock_cmd("extension_bridge",
    code="b.send('set_storage',{data:{theme:'dark'}}).then(r=>document.title=JSON.stringify(r))"
)
```

The `b` variable is `window.__aethelgardBridge` — injected into every page by the content script. Available commands:

| Command | Params | Returns |
|---------|--------|---------|
| `ping` | — | `{version, tabs, busConnected}` |
| `get_all_tabs` | — | `[{id, url, title, active}]` |
| `activate_tab` | `tabId` | `{success}` |
| `get_page_source` | — | `{html}` |
| `get_storage` | `key` (optional) | `{data}` |
| `set_storage` | `data` | `{success}` |
| `inject_script` | `code` | `{result}` |

## Profile-Based Extensions (11 installed)

Bromium also loads extensions from the browser profile at `/tmp/bromium-profile/Default/Extensions/`. These are regular Chrome Web Store extensions:

| ID | Name | Trigger |
|----|------|---------|
| `aabiopennjmopfippagcalmkdjlepdhh` | Better DeepSeek | `chat.deepseek.com/*` |
| `ceacgaccjcomdbnoodjpllihjmeflfmg` | Science Research Assistant | — |
| `liihfcjialakefgidmaadhajjikbjjab` | alphaXiv | `arxiv.org/abs/*` |
| `ofaokhiedipichpaobibbnahnkdoiiah` | Instant Data Scraper | `*://*/*` |
| `okngcalljddikhljpfhgmikklmmmdkkd` | Agent OS | popup-based |
| `ihdobppgelceaoeojmhpmbnaljhhmhlc` | Spoof Geolocation | — |

### Control profile extensions via CDP (port 9224)

Extensions have background/service worker pages accessible through CDP:

```bash
# List all debuggable targets (includes extension workers)
curl -s http://127.0.0.1:9224/json/list | python3 -m json.tool

# Find the extension's background page WebSocket URL, then evaluate JS:
# ws_url = "ws://127.0.0.1:9224/devtools/page/..."
# Send JSON via CDP protocol to call chrome.runtime.sendMessage()
```

### Execute JS on any page (all extensions' content scripts run automatically)

```python
sock_cmd("execute_javascript",
    code="document.title = document.body.innerText.substring(0, 30)",
    tab_id=1
)
title_resp = sock_cmd("get_title", tab_id=1)
# title_resp["title"] contains the result
```

## The Aethelgard Bridge Extension Pattern

The extension at `extensions/aethelgard-bridge/` is the reference implementation:

```
manifest.json       → MV3, content_scripts[<all_urls>], action popup
background.js       → Service worker routing commands, fleet bus heartbeat
content.js          → window.__aethelgardBridge injected into every page
inject.js           → window.__aethelgard API (web-accessible)
popup.html/js       → Shows connected tabs, bridge health
```

To build a new extension:
1. Create a subdirectory under `extensions/`
2. Add `manifest.json` (MV3, content_scripts as needed)
3. Rebuild bromium (`fpc ... dual_citizen_v2.lpr -o bromium`)
4. The extension loads on next launch

## Reading Extension Results

The `extension_bridge` and `evaluate_js` commands return results via **document.title** (the title channel). Read it back with `get_title`:

```python
sock_cmd("extension_bridge",
    code="b.send('ping').then(r=>document.title=JSON.stringify(r))"
)
import time; time.sleep(0.5)
result = sock_cmd("get_title")
print(result["title"])  # '{"version":"1.0.0","tabs":3,...}'
```

## Reference Files

| File | What it contains |
|------|-----------------|
| `references/aethelgard-bridge-protocol.md` | Full message protocol — all message types, bridge commands, CDP fallback, lifecycle events |
| `templates/basic-extension-scaffold.js` | Copy-paste scaffold for building a new extension: manifest.json, background.js, content.js patterns |

## Pitfalls

- **`extension_bridge` only works on pages where the content script has injected.** Any HTTP(S) page works. `about:blank` does NOT.
- **Title channel is 30-char truncated** in the tab caption. Use `get_title` IPC which returns the full string.
- **`b` is `window.__aethelgardBridge`**, not `window.__aethelgard`. The `__aethelgard` object is the web-accessible inject.js wrapper.
- **Extension must be a subdirectory of `extensions/`** with its own `manifest.json`. Flat files in the root won't load.
- **Rebuild required** after adding new extensions to the directory — CEF only reads `--load-extension` at startup.
