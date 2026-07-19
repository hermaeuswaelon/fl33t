---
name: browser-control-cef
description: >-
  Control any CEF/Chromium-based browser via UNIX socket IPC. Covers IPC protocol patterns,
  content script injection (isolated world → main world bridge), fleet bus architecture,
  automation stealth verification, and Hermes integration tools.
trigger:
  - "browser control"
  - "CEF automation"
  - "Chromium IPC"
  - "Bromium"
  - "content script bridge"
  - "automatic browser"
  - "undetectable automation"
  - "fleet bus"
category: ares
---

# ⧉ Browser Control via CEF IPC

## Architecture
CEF (Chromium Embedded Framework) browsers expose a UNIX socket for IPC control.
Commands are JSON blobs with `action`, `id`, and parameters. The socket is at
`/tmp/<name>.sock` by convention.

### IPC Protocol
```json
{"action": "navigate", "id": "1", "url": "https://example.com", "tab_id": 1}
```

Key differences from CDP (Chrome DevTools Protocol):
- No WebSocket — raw UNIX socket with newline-delimited JSON
- No `navigator.webdriver` flag — CEF doesn't inject automation markers
- No CDP footprint — stealthier than Selenium/Playwright
- All commands go through a single socket, results returned per-command

## Critical: Content Script Isolated World
**ROOT CAUSE of 90% of extension bugs**: Chrome extension content scripts run in an
isolated V8 world. IPC-injected JS (via `execute_javascript` / `evaluate_js`) runs
in the MAIN world. Properties set on `window` in one world are invisible in the other.

**Fix**: Content scripts must inject a `<script>` tag into the page DOM.
The script's `textContent` runs in the MAIN world and defines the API there.

See reference `bromium-content-script-bridge.md` under the `bromium-control` skill
for the exact pattern.

## Fast Eval Path
Commands:
1. `evaluate_js` → runs JS asynchronously, stores result in `FEvalResult`
2. `get_eval` → retrieves `FEvalResult`

The result arrives via CEF's `OnTitleChange` callback (JS sets `document.title` to
JSON-stringified result). This means:
- JS Expressions **must use `return`** keyword (wrapped in `(function(){...})()`)
- Need polling retry for async eval completion
- The JS parameter name in the IPC command is **`code`**, NOT `js`

## Fleet Bus Architecture
A lightweight HTTP REST API wraps the raw IPC socket for easier access:
```
http://127.0.0.1:8080/api/{health,status,tabs,navigate,js,click,tab}
```
The bus is a Python Flask/HTTP server that translates HTTP requests → IPC commands.
Run it in the background and use curl/requests from tools.

## Stealth Verification
CEF browsers are inherently undetectable as automation because:
- No `navigator.webdriver` flag
- Real plugin array (not empty like headless)
- Full WebGL support
- Normal platform strings
- No `--headless` in user agent

Always verify with a JS eval checking `webdriver`, `plugins.length`, `webgl`.

## Hermes Integration Tools
Create a thin CLI wrapper (`bh`) that bridges to the fleet bus or IPC socket directly.
Pattern:
```python
def sock_cmd(action, **kw):
    payload = json.dumps({"action": action, "id": str(int(time.time()*1000000)), **kw})
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(8)
    s.connect(SOCKET_PATH)
    s.sendall(payload.encode() + b"\n")
    # read response...
```

## Commands to Test on First Connection
1. `health` — verify socket alive
2. `navigate` — test with a real URL
3. `get_title` — verify page loaded
4. `evaluate_js` / `get_eval` — test fast path with `return document.title`
5. `list_tabs` — verify tab management
6. `click` — test element interaction
7. `create_tab` / `close_tab` — test tab lifecycle

## Reference Files
See the `bromium-control` skill at `~/.hermes/profiles/thotheauphis/skills/bromium-control/references/` for:
- `bromium-content-script-bridge.md` — Isolated world fix pattern
- `bromium-fleet-bus-bh-tool.md` — Fleet bus API + `bh` tool commands
- `bromium-stealth-verification.md` — Undetectability validation
