# CEF Extension Toolbar Limitation (Puzzle Piece)

## The Issue

The Chrome extensions toolbar popup (the puzzle piece icon → dropdown menu
showing installed extensions with pin/manage/options) does NOT appear in
CEF4Delphi-based browsers. This is **not a bug** — it's a CEF architecture
limitation.

## Root Cause

CEF4Delphi embeds Chromium's **rendering engine** (Blink + V8 + network stack)
but does NOT ship Chrome's proprietary browser UI chrome. The puzzle piece
menu lives in Chrome's browser UI layer (`chrome/browser/ui/views/extensions/`),
which is excluded from the CEF build. CEF provides the web view, not the
Chrome chrome.

## What DOES Work

All 20 extensions load and function correctly:
- Content scripts inject into pages
- Background/service workers run
- Network interception (uBlock, etc.) is active
- Extension APIs (`chrome.*`) are available to loaded extensions
- Better DeepSeek confirmed working on chat.deepseek.com

## How to Verify Extensions Are Loaded

### Via IPC (from any Python tool):

```python
import socket, json
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(10)
s.connect('/tmp/aethelgard_cef.sock')
s.send(json.dumps({'action':'list_extensions','id':'1'}).encode() + b'\n')
resp = b''
while True:
    try:
        chunk = s.recv(65536)
        if not chunk: break
        resp += chunk
    except socket.timeout: break
s.close()
print(resp.decode('utf-8','replace'))
```

### Via bromium_agent CLI:
```
python3 ~/.local/bin/bromium_agent.py --list-extensions
```

### Via chrome://extensions/:
Navigate to `chrome://extensions/` in any tab — the full Chrome extension
manager UI loads and shows all installed extensions with enable/disable/options.

## Workarounds for the Missing Puzzle Piece

| Approach | Effort | Result |
|----------|--------|--------|
| Navigate to chrome://extensions/ | 0 lines | Full extension manager UI |
| IPC list_extensions | 0 lines | JSON list of extension names |
| Build Portal GUI buttons | ~50 lines | Extension toggle in the Bromium Portal |

To build Portal GUI buttons: use the Aethelgard Bridge extension
(`window.__aethelgardBridge`) or the `extension_bridge` IPC to call
`chrome.management.setEnabled()` per extension.

## Additional CEF UI Limitations

| Feature | Present? | Workaround |
|---------|----------|------------|
| Address bar | ✅ (in Portal) | Portal provides its own |
| Bookmark bar | ❌ | Speed dial HTML page |
| Extensions puzzle piece | ❌ | chrome://extensions/ or IPC |
| Settings menu (hamburger) | ❌ | Portal toolbar buttons |
| DevTools | ✅ (F12) | Full Chrome DevTools |
| Right-click context menu | ✅ | Standard Chromium |
| Download bar | ❌ | Portal shows downloads |