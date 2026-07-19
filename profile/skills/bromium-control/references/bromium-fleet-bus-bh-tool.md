# ⟐ Fleet Bus (@ :8080) and Hermes Browser Driver (`bh`)

## Fleet Bus (`bromium-bus.py`)
HTTP REST API wrapper for the Bromium IPC socket. Runs on `http://127.0.0.1:8080`.
Auto-started via `terminal(background=True)` (no persistent systemd service yet as of 2026-07-18).

```bash
python3 /home/craig/.local/bin/bromium-bus.py
```

### Fleet Bus API Endpoints
| Endpoint | Method | Params | Returns |
|----------|--------|--------|---------|
| `/api/health` | GET | — | `{"status":"ok","socket":"alive"}` |
| `/api/status` | GET | — | tab/url/title state |
| `/api/tabs` | GET | — | tab list |
| `/api/navigate` | POST | `url`, `tab_id` | navigation status |
| `/api/js` | POST | `code`, `tab_id` | eval result (fast path, uses `evaluate_js` + `get_eval`) |
| `/api/click` | POST | `selector`, `tab_id` | click result |
| `/api/tab` | POST | `action` (create/close/activate), `url` | tab mgmt |
| `/api/screenshot` | POST | `tab_id` | base64 screenshot |

### Fast Eval Path
Uses the `evaluate_js` → `get_eval` IPC commands with polling retry.
⚠️ JS code MUST use `return` expression syntax (the Pascal server wraps it in `(function(){...})()`).

```bash
# Good:
curl -s -X POST http://127.0.0.1:8080/api/js -d '{"code":"return document.title","tab_id":1}'

# Bad (will return undefined):
curl -s -X POST http://127.0.0.1:8080/api/js -d '{"code":"document.title","tab_id":1}'
```

### Fast Eval Timing
The `evaluate_js` command fires JS asynchronously in CEF's render process.
Results arrive via `OnTitleChange` callback → `FEvalResult`.
The bus polls `get_eval` with 0.3s delay, retrying up to 5 times (~1.5s total).
Simple pages resolve in ~300ms; heavy pages may need the full retry chain.

## `bh` — Hermes Browser Driver
Comprehensive CLI for Bromium control from terminal. Location: `/home/craig/.local/bin/bh`.

### Commands
```bash
bh nav <url>           # Navigate and wait for load
bh eval <js>           # Fast eval (return expression)
bh exec <js>           # Execute JS (no return value)
bh click <selector>    # Click element by CSS selector
bh text [max=N]        # Extract page text (default max=5000)
bh links               # Extract all links
bh tabs                # List all tabs
bh health              # System health check
bh research <url>      # Deep research (inject bridge + extract all data)
bh extract [links|text|forms|all]  # Extract from current page
bh stealth <url>       # Check automation signatures
```

### Integration with Hermes
From Hermes' terminal tool, call `bh` for any browser action:
```python
terminal("bh nav https://example.com")
terminal('bh eval "return document.title"')
terminal("bh extract links")
```

## `bh-research` — Deep Research Injector
Location: `/home/craig/.local/bin/bh-research`

Injects bridge content script + stealth check + page data extractor post-navigation.
All injection runs in MAIN world (no isolated world issues). Returns structured JSON.

### Key injection payloads
- **BRIDGE_SCRIPT**: Injects `window.__aethelgardBridge` in main world
- **STEALTH_CHECK**: Verifies no automation signatures (`navigator.webdriver`, plugins, etc.)
- **RESEARCH_EXTRACT**: Extracts links, images, forms, tables, meta, text in one eval

## IPC Protocol Notes
- Socket: `/tmp/aethelgard_cef.sock` (UNIX domain)
- JSON format: `{"action": "<cmd>", "id": "<ts>", ...params}`
- Parameter name for JS code: **`code`** (NOT `js`)
- `evaluate_js` stores result in `FEvalResult`; `get_eval` retrieves it
- `execute_javascript` runs JS via `document.title` (no return, but title-based result)
- For results, use `evaluate_js` + `get_eval` (fast path), NOT `execute_javascript` + `get_title` (slow path)
