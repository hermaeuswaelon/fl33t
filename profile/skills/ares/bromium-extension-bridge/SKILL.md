---
name: bromium-extension-bridge
description: "Control Bromium (Dual-Citizen Aethelgard Browser) via Unix socket IPC — navigate, evaluate JS, bridge extensions, read page titles, manage tabs, rebuild, watchdog operations."
version: 3.0.0
author: Thotheauphis
platforms: [linux]
tags: [ares, bromium, extensions, bridge, ipc, aethelgard, build, watchdog]
related_skills: [ares-dual-citizen-browser, ares-browser-research]
---

# 🧩 Bromium Extension Bridge — Agent Control

## Overview

Bromium loads unpacked Chrome extensions from `extensions/` and profile-based extensions from the browser profile. This skill covers **how I (the agent) control all of them** via the Unix socket IPC.

**Socket:** `/tmp/aethelgard_cef.sock`
**Binary:** `~/projects/aethelgard/fleet/pascal/dual-citizen-v2/bromium`
**Watchdog:** systemd `dual-citizen-watchdog.service` (auto-recovery ~5-8s after kill -9)
**Agent CLI:** `~/.local/bin/bromium_agent.py` — **preferred over raw socket**
**Custom extension:** `extensions/aethelgard-bridge/`

## Quick Reference — Agent CLI (preferred)

```bash
# Health check (extensions + tabs + title)
python3 ~/.local/bin/bromium_agent.py

# Navigate tab 1; wait 4-8s for page load, then read title
python3 ~/.local/bin/bromium_agent.py --navigate https://httpbin.org/html --tab 1
sleep 5
python3 ~/.local/bin/bromium_agent.py --title --tab 1

# Execute JS — result is stored in document.title, read with get_title
python3 ~/.local/bin/bromium_agent.py --eval "document.title = JSON.stringify({url: location.href})" --tab 1
sleep 1.5
python3 ~/.local/bin/bromium_agent.py --title --tab 1

# List extensions and tabs
python3 ~/.local/bin/bromium_agent.py --list-extensions
python3 ~/.local/bin/bromium_agent.py --list-tabs

# Bridge ping (only after content script injected — see Pitfalls)
python3 ~/.local/bin/bromium_agent.py --bridge "b.send('ping').then(r=>document.title=JSON.stringify(r))" --tab 1
sleep 2
python3 ~/.local/bin/bromium_agent.py --title --tab 1

# Raw socket IPC (use agent CLI unless you need custom commands)
python3 -c "
import socket, json
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(10)
s.connect('/tmp/aethelgard_cef.sock')
s.send(json.dumps({'action':'list_extensions','id':'1'}).encode()+b'\n')
resp = s.recv(65536).decode()
s.close()
print(json.loads(resp))
"

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
### `extension_bridge` — Send JS through `window.__aethelgardBridge` (async IIFE wrapper)

```python
# Ping the bridge to check connectivity
sock_cmd("extension_bridge",
    code="b.send('ping').then(r=>document.title=JSON.stringify(r))",
    tab_id=1
)
# Wait 2-3s for async callback, then:
result = sock_cmd("get_title", tab_id=1)
print(result["title"])

# Get all tabs via extension API
sock_cmd("extension_bridge",
    code="b.send('get_all_tabs').then(r=>document.title=JSON.stringify(r))"
)
```

**CEF requires async IIFE** for Promise-based `.then()` callbacks. The Pascal handler wraps `b.send(...)` in `(async()=>{...})()`. Without this, the `.then()` never fires because CEF's V8 isolates the execution context before the microtask queue drains.

The `b` variable is `window.__aethelgardBridge`. Available commands:| Command | Params | Returns |

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

### Execute JS on any page

```python
sock_cmd("execute_javascript",
    code="document.title = document.body.innerText.substring(0, 30)",
    tab_id=1
)
sleep(1.5)
title_resp = sock_cmd("get_title", tab_id=1)
# title_resp["title"] contains the result
```

⚠️ **CEF MV3 limitation: content scripts do NOT auto-inject.** Unlike standard Chrome, CEF's MV3 support does not run `content_scripts` declared in `manifest.json` on page navigation. All bridge objects (`window.__aethelgardBridge`, `window.__domScraper`, `window.__pageAutomation`) report `undefined` on real pages like `httpbin.org`, even though extensions load and `list_extensions` confirms them.

**Workarounds (in priority order):**
1. **Use `execute_javascript` (synchronous)** — bypasses the bridge entirely. Set `document.title` directly in raw JS and read with `get_title`. This is the most reliable path and works on any page.
2. **Manual injection** — after navigation, inject the content.js source via `execute_javascript`, then use `extension_bridge` normally.
3. **CDP injection** — connect to `http://127.0.0.1:9224` and call `Page.addScriptToEvaluateOnNewDocument` to inject scripts before every page load.
4. **Convert to MV2** — CEF natively supports MV2 content script auto-injection.

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

The `extension_bridge` and `evaluate_js` commands return results via **document.title** (the title channel). Read it back with `get_title` (which now accepts a `tab_id` parameter and returns the **full** stored title, not the 30-char UI-caption truncation):

```python
sock_cmd("extension_bridge",
    code="b.send('ping').then(r=>document.title=JSON.stringify(r))"
)
sleep(3)  # allow async callback to fire
result = sock_cmd("get_title", tab_id=1)
print(result["title"])  # '{"version":"1.0.0","tabs":3,...}'
```

## Title IPC (patched)

The `get_title` IPC handler was patched to fix two issues:
1. **Now accepts `tab_id` parameter** — reads `FTabs[idx].LastTitle` instead of only the active tab's UI-caption
2. **Returns full title** — not the 30-character CEF tab-bar truncation. `DoTitleChange` stores the complete title in `FTabs[i].LastTitle` before the caption is truncated

The `GetActiveTitle` fallback also checks `FTabs[idx].LastTitle` when the page-control caption is empty or exactly 30 chars (indicating it was truncated).

## Title Channel JSON Unescaping — Critical Pattern

The Pascal IPC response has Pascal-escaped quotes (`\"`) inside JSON string values. When reading title channel results (after `execute_javascript` sets `document.title`), the JSON may contain nested JSON in the `title` field. **Always try parsing the raw response first; only unescape on failure.**

```python
# CORRECT — try raw first, fallback to unescape:
def parse_ipc_response(raw_text):
    def _try(s):
        try: return json.loads(s)
        except: return None
    parsed = _try(raw_text)
    if parsed is None:
        # Pascal sends \" for internal quotes — strip them and retry
        cleaned = raw_text.replace('\\\\"', '"')
        for i, ch in enumerate(cleaned):
            if ch in ('{', '['):
                try: return json.loads(cleaned[i:])
                except: continue
    return parsed if parsed is not None else {"error": "parse failed", "raw": raw_text[:200]}
```

**Why:** The title value itself may be JSON (e.g. `"title":"{\\"status\\":\\"injected\\"}"`). Blind `replace('\\\\"', '"')` destroys the outer JSON structure by unescaping the inner quotes, producing `"title":"{"status":"injected"}"` which is invalid JSON.

## Pascal ExecuteJS: Direct Page Context, No Script Tag Needed

`ExecuteJS()` in CEF4Delphi runs JavaScript in the page's V8 context directly — NOT in an isolated sandbox. This means:
- `ExecuteJS('window.__bromiumScan = {...}; document.title = "OK";')` defines `__bromiumScan` on the **real** page window
- No need to create `<script>` elements or inject via content scripts
- **Never build complex JS as Pascal string literals for `<script>.textContent` injection** — Pascal's `''` (double-single-quote) escaping for single quotes inside strings is error-prone. Use `ExecuteJS` directly with the JS code as a plain string.

**What works (proven pattern):**
```pascal
// CORRECT: define the API directly in page context
jsCode := '(function(){ window.__bromiumScan = {getElements:function(){...}}; document.title=JSON.stringify({status:"injected"}); })()';
ExecuteJS(jsCode, tabId);
```

**What breaks (do not do):**
```pascal
// WRONG: Pascal single-quote hell + script element injection
jsCode := 'var s=document.createElement("script"); s.textContent=''complexJS()''; document.body.appendChild(s);';
// The '' inside Pascal strings produces single quotes in the JS,
// but nested quotes in the JS content are nearly impossible to get right.
```

## Page Navigation Destroys All JS Context

Every navigation event destroys the JavaScript execution context:
- `window.__bromiumScan` is gone after any page load
- `window.__aethelgardBridge` is gone (even with MV3 content_scripts declared)
- Any injected DOM modifications are gone

**Rule:** After every `navigate` IPC command, re-inject any custom JS APIs via `execute_javascript` or `inject_scan_api`. Poll for `document.title` to confirm the page loaded before injecting.

## Reference Files

| File | What it contains |
|------|-----------------|
| `references/aethelgard-bridge-protocol.md` | Full message protocol — all message types, bridge commands, CDP fallback, lifecycle events |
| `references/chrome-webstore-install-fix.md` | Full pipeline for Chrome Web Store "Add to Chrome" bypass: JS injection, title-signal detection, curl download, CRX3 unpack. CRX3 binary format reference. |
| `templates/basic-extension-scaffold.js` | Copy-paste scaffold for building a new extension: manifest.json, background.js, content.js patterns |
| `scripts/bromium-crx-install.py` | CRX3 unpacker: strips CRX3 header, extracts ZIP contents into extensions directory. Called by `InstallCRX()` Pascal function. |

## Pitfalls

- **Chrome Web Store "Add to Chrome" opens external OS window** — CEF's extension manager intercepts `clients2.google.com/service/update2/crx` URLs at the network level, BELOW `OnBeforeBrowse`. Standard event interception (OnBeforePopup, OnOpenUrlFromTab, OnBeforeBrowse) does NOT catch this. Even `browser.Host.StartDownload(url)` fails because the extension manager grabs the URL before the download manager. The verified fix is a **multi-layer bypass** via JS injection + title-signal + curl download. See `references/chrome-webstore-install-fix.md` for the full pipeline and source locations in ucontrollerbrowser.pas.
- **`OnOpenUrlFromTab` uses `out` not `var`** — CEF4Delphi signature is `out aResult: Boolean`. Using `var` causes compile error: `Incompatible types: got "<procedure with var>" expected "<procedure with out>"`.
- **`OnBeforeBrowse` fires for ALL frame navigations** — Only intercept top-frame (`frame.Parent = nil`), user-initiated (`user_gesture = True`), non-redirect navigations. Otherwise every subframe resource load gets intercepted too.
- **Content scripts do NOT auto-inject on CEF MV3.** Despite `<all_urls>` in `content_scripts` matches, bridge objects (`window.__aethelgardBridge`, `window.__domScraper`, `window.__pageAutomation`) are `undefined` on real pages. Use `execute_javascript` (synchronous, fastest), manual content.js injection, CDP, or MV2 downgrade.
- **Bridge `.then()` callbacks require async IIFE.** CEF's V8 isolates the execution context before microtasks drain. The Pascal handler wraps bridge code in `(async()=>{...})()` to work around this.
- **`about:blank` in title = page hasn't loaded yet** — wait 4-8s or check for `Page loaded: 200` in `/tmp/bromium.log`.
- **`extension_bridge` only works on pages where the content script has injected.** Any HTTP(S) page works once content.js is injected. `about:blank` does NOT.
- **Title channel is 30-char truncated** in the CEF tab caption, but `get_title` IPC now returns the **full** stored title via `FTabs[i].LastTitle` (patched this session).
- **Agent script unescapes JSON conditionally.** `bromium_agent.py` tries `json.loads()` first; only falls back to stripping Pascal's `\"` escape sequences if the first parse fails. This preserves embedded quotes/brackets in titles.
- **`b` is `window.__aethelgardBridge`**, not `window.__aethelgard`. The `__aethelgard` object is the web-accessible inject.js wrapper.
- **Extension must be a subdirectory of `extensions/`** with its own `manifest.json`. Flat files in the root won't load.
- **Rebuild required** after adding new extensions or patching Pascal source — CEF only reads `--load-extension` at startup.
- **Page navigation is async** — `navigate` returns `"navigating"` status immediately. Title updates asynchronously. Always wait before reading title.
- **CRX curl downloads REQUIRE a browser User-Agent** — Google's update API (`clients2.google.com/service/update2/crx`) returns empty when curl's default UA is used. Always pass `-A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"` (or equivalent Chromium UA) to curl. Without it the download produces a 0-byte file. This applies to both the Pascal `Timer1Timer` curl call and any manual `curl` invocations.
- **Profile-based extensions need version-subdirectory flattening** — Extensions copied from `/tmp/bromium-profile/Default/Extensions/<id>/` store files under a version subdirectory (e.g. `<id>/0.1.10/manifest.json`). CEF's `--load-extension=<dir>` expects `manifest.json` directly in the subdirectory. After copying, move contents up: `cp -r <ext_dir>/<version>/* <ext_dir>/ && rm -rf <ext_dir>/<version>`. Verify with `ls <ext_dir>/manifest.json`.
- **`list_extensions` IPC only re-scans on nil** — The Pascal handler calls `LoadExtensions` only when `FExtensions = nil` (first call). Adding new extension directories while the browser is running won't update the list until restart, regardless of how many times you call `list_extensions`. Both IPC listing AND extension activation need a restart — they are not hot-reloadable.
- **`__MSG_*__` names resolve at runtime** — Some Chrome Web Store extensions (Web Developer, User-Agent Switcher) use `__MSG_extensionName__` in manifest.json's `name` field instead of a literal string. These are Chrome i18n message references resolved via `_locales/` at runtime. The Pascal scanner shows the raw message key — expected and harmless. The extension's real name appears in browser UI.

## Preventing External OS Windows — Chrome Web Store Install Fix

When the user clicks "Add to Chrome" on `chromewebstore.google.com`, CEF's extension manager intercepts the CRX download URL at the network level — below any browser event (`OnBeforePopup`, `OnOpenUrlFromTab`, `OnBeforeBrowse`). Even `browser.Host.StartDownload()` fails because the extension manager snatches the URL first.

The working fix uses **four layers, none of which involve navigating to the CRX URL within CEF**:

### Layer 1: CEF Command-Line Flags (in `dual_citizen_v2.lpr`)

These suppress OS-level dialog windows but are NOT sufficient alone:

```pascal
GlobalCEFApp.AddCustomCommandLine('--disable-features=ChromeExtensionsMenu,ChromeWebStoreIcon,ChromeWebStoreInstall,ExtensionInstallDialog,ExtensionInstallVerification');
GlobalCEFApp.AddCustomCommandLine('--disable-extensions-dialogs');
GlobalCEFApp.AddCustomCommandLine('--disable-extensions-file-access-check');
GlobalCEFApp.AddCustomCommandLine('--disable-extensions-http-throttling');
```

Note the extra `ChromeWebStoreInstall` flag — added July 2026 after discovering the four original flags weren't enough.

### Layer 2: JS Injection in `DoLoadEnd` (in `ucontrollerbrowser.pas`)

On **any** Chrome Web Store page (`chromewebstore.google.com` or `chrome.google.com/webstore`), inject JavaScript that hooks the "Add to Chrome" button. Must match broadly (not just `/detail/`) because SPA pushState navigations don't retrigger `DoLoadEnd`:

- **Button selector**: `document.querySelectorAll('button').filter(b => b.textContent.trim() === 'Add to Chrome')` — the button has **no** `action="add"` attribute, it's a plain `<BUTTON>` with auto-generated classes.
- **Hook action**: `e.preventDefault()` + `e.stopPropagation()` (prevents CEF's extension manager from activating), then sets `document.title = "BROMIUM_CRX:" + extId` (no navigation, no fetch — just a signal).
- **Re-hook interval**: `setInterval(bromiumHookButton, 500)` — Chrome Web Store is a SPA that may re-render the button; re-scan every 500ms.

**Why not fetch()?** CORS blocks cross-origin requests from `chromewebstore.google.com` to `clients2.google.com`.
**Why not window.location.href?** Even navigating _within_ CEF triggers the extension manager before `OnBeforeBrowse` can intercept.

### Layer 3: Timer-Based Detection + curl Download (in `Timer1Timer`)

The Pascal timer polls `FTabs[].LastTitle` for the `BROMIUM_CRX:` prefix every timer tick (~300ms):

1. Detects the signal → clears it (sets to `BROMIUM_DOWNLOADING` to prevent re-processing)
2. Sets `FPendingExtId`/`FPendingCrxPath` for state tracking
3. Calls `ExecuteProcess('/usr/bin/curl', ...)` synchronously — blocks the timer 2-5s but is the only reliable approach because curl runs as an external process completely outside CEF's network stack (extension manager cannot intercept). Backgrounding via shell `&` breaks due to Pascal string quoting issues with the double `sh -c` indirection.
4. On subsequent ticks, pending-state check finds the CRX file and calls `InstallCRX()`
3. CRX saved to `/tmp/bromium-crx-staging/<ext_id>.crx`
4. Calls `InstallCRX()` to unpack and install

### Layer 4: CRX3 Unpack via Python (`~/.local/bin/bromium-crx-install.py`)

The Pascal `InstallCRX()` function delegates to a Python helper script that:

1. Validates the CRX3 magic bytes (`Cr24`)
2. Reads version (LE u32) and header length (LE u32)
3. Skips the signed header data
4. Extracts the remaining ZIP data into `extensions/<ext_id>/`
5. Reads `manifest.json` for the display name
6. Returns the extension name (or empty string on failure)

The Python script writes its result to `/tmp/bromium-crx-install-result.json` which Pascal reads back.

### CEF Event Handlers (superseded for extension installs — still useful for regular popups)

The old triple-interception handlers still serve a purpose for regular popups (window.open, target=_blank) but do NOT catch Chrome Web Store extension installs (extension manager operates below the browser event layer). The working fix uses the BROMIUM_CRX title-signal protocol instead (see Layer 2 above):

| Event | What it catches | Hook in `AddTab()` |
|-------|----------------|-------------------|
| `OnBeforePopup` | `window.open()`, `<a target="_blank">`, popups | `@DoBeforePopup` |
| `OnOpenUrlFromTab` | Middle-click, drag-to-new-tab | `@DoOpenUrlFromTab` |
| `OnBeforeBrowse` | Top-frame navigations; CRX URLs now use `StartDownload` fallback | `@DoBeforeBrowse` |

**CEF event type pitfall:** `OnOpenUrlFromTab` uses `out aResult: Boolean`, NOT `var aResult: Boolean`. Using `var` causes an FPC type mismatch error.

### New IPC Commands

| Command | Args | Action |
|---------|------|--------|
| `install_crx` | `url=""` or `path=""` | Download CRX via `StartDownload` (URL mode) or install local CRX file (path mode). Returns status + extension name on success. |

### New Pascal Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `InstallCRX(crxPath)` | end of `ucontrollerbrowser.pas` | Calls Python helper to unpack CRX3 into extensions dir. Returns display name or ''. |
| `Timer1Timer` | mid-file | Extended: polls for `BROMIUM_CRX:` title signal, runs curl download, calls InstallCRX + LoadExtensions. |

### Verification

The fix is verified by navigating to a Chrome Web Store detail page and checking:
1. No OS-level window opens when "Add to Chrome" is clicked
2. The CRX file appears in `/tmp/bromium-crx-staging/`
3. The extension appears in the extensions directory and the 🧩 menu

## Build

```bash
cd ~/projects/aethelgard/fleet/pascal/dual-citizen-v2

# Clean stale artifacts
rm -f *.ppu *.o *.rst build_out/* 2>/dev/null
mkdir -p build_out

# Compile (fpc direct — lazbuild requires Lazarus packages not always available)
fpc -Mobjfpc -Sh -gl -O2 \
    -Fu/usr/lib/lazarus/4.4/lcl/units/x86_64-linux/gtk2 \
    -Fu/usr/lib/lazarus/4.4/lcl/units/x86_64-linux \
    -Fu/usr/lib/lazarus/4.4/packager/units/x86_64-linux \
    -Fu/usr/lib/lazarus/4.4/components/lazutils/lib/x86_64-linux \
    -Fu/usr/lib/lazarus/4.4/components/freetype/lib/x86_64-linux \
    -Fu/usr/lib/lazarus/4.4/components/lazcontrols/lib/x86_64-linux/gtk2 \
    -Fu/usr/lib/lazarus/4.4/components/ideintf/units/x86_64-linux/gtk2 \
    -Fu/home/craig/.aethelgard/workspace/browser/CEF4Delphi/packages/lib/x86_64-linux \
    -Fu/home/craig/.aethelgard/workspace/browser/CEF4Delphi/source \
    -Fu/home/craig/.aethelgard/workspace/browser/CEF4Delphi/dcpcrypt/src/lib/x86_64-linux \
    -Fl/home/craig/.aethelgard/workspace/browser/CEF4Delphi/cef_binary_current/Release \
    -FU./build_out -o./bromium dual_citizen_v2.lpr

# Copy to cef_controller (start-browser.sh uses this name)
cp bromium cef_controller
```

Output: ~36MB ELF binary. Build time: ~1.5s. Expect 15 warnings (pre-existing string type conversions), exit 0.

## Pitfalls

Systemd user service auto-recovers Bromium:

```bash
systemctl --user status dual-citizen-watchdog
sudo journalctl --user -u dual-citizen-watchdog -n 20 --no-pager

# Apply new binary: stop → copy → start
systemctl --user stop dual-citizen-watchdog
killall bromium 2>/dev/null; killall cef_controller 2>/dev/null
sleep 1
cp bromium cef_controller
systemctl --user start dual-citizen-watchdog
# Socket back in ~1-2s, process ~5s
```

The watchdog script at `~/.NOTTHEONETOEDIT/scripts/browser-watchdog.sh` checks every 30s: socket exists + PID alive. On failure: kills, removes socket, re-launches, waits 20s for socket. Verified recovery time: **~5s**. Service file: `~/.config/systemd/user/dual-citizen-watchdog.service`.
