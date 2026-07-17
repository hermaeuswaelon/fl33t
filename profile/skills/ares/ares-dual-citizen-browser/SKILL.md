---
name: ares-dual-citizen-browser
description: "ARES Dual Citizen Browser — CEF4Delphi Chromium-based sovereign browser. Launch, IPC control, tab management, spoofing, proxy configuration, lifecycle management."
version: 1.0.0
author: Craig / ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, browser, cef, chromium, dual-citizen, bromium, ipc]
related_skills: [ares-aethelgard-scripts, ares-pascal-fleet]
---

# ⎔ Bromium — Sovereign CEF Browser (formerly Dual Citizen)

## Overview

Bromium (née Dual Citizen v2) is a **37MB CEF4Delphi Chromium browser** with:
- Multi-tab support via native IPC socket (`/tmp/aethelgard_cef.sock`)
- Native CEF extension loading from local directory
- Browser fingerprint spoofing
- Proxy management
- Sovereign identity anchoring
- Full JavaScript execution control

## Locations

| Component | Path |
|-----------|------|
| **Binary** | `/home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/bromium` |
| **Symlink** | `/home/craig/.NOTTHEONETOEDIT/fleet/pascal/dual-citizen-v2/bromium` (→ `projects/.../bromium`) |
| **Old binary** | `dual_citizen_v2` still in same dir (kept for fallback) |
| **Launchers** | `/home/craig/Desktop/Scripts-Launchers/bromium.sh`, `super_browser.sh` |
| **CEF Libs** | `/home/craig/.aethelgard/workspace/browser/CEF4Delphi/cef_binary_131.4.1+chromium-131.0.6778.265_linux64/Release/libcef.so` (1.35GB!) |
| **Lifecycle CLI** | `/home/craig/.local/bin/cef-browser` |
| **Watchdog** | `/home/craig/.NOTTHEONETOEDIT/scripts/browser-watchdog.sh` |
| **Systemd** | `/home/craig/.config/systemd/user/dual-citizen-watchdog.service` |
| **Sources** | `/home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/` |
| **Ext dir** | `/home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/extensions/` |

## Launch

```bash
# Method 1: bromium binary (recommended)
cd /home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2 && \
  LD_LIBRARY_PATH="/home/craig/CEF4Delphi/cef_binary_current/Release" \
  DISPLAY=:0 \
  ./bromium

# Method 2: Lifecycle CLI (Python)
cef-browser start
cef-browser stop
cef-browser status
cef-browser navigate https://example.com

# Method 3: Desktop launcher
/home/craig/Desktop/Scripts-Launchers/bromium.sh
```

## Extensions (Native CEF)

Bromium loads unpacked Chrome extensions natively via CEF's `--load-extension` switch.

**🔴 Chrome Web Store installs — clicking "Add to Chrome":** CEF's extension manager intercepts `clients2.google.com/service/update2/crx` URLs at the network level, below all browser events. Standard event interception (OnBeforePopup, OnOpenUrlFromTab, OnBeforeBrowse) does NOT work. Even `browser.Host.StartDownload(url)` fails. The working fix uses JS injection + title-signal + curl download (external process, bypasses CEF's network stack entirely). See `bromium-extension-bridge` skill → "Preventing External OS Windows" section and its `references/chrome-webstore-install-fix.md`.

**Configuration in `dual_citizen_v2.lpr` and `cef_controller.lpr`:**
```pascal
// Extensions are enabled by default (DisableExtensions=False).
// Load unpacked extensions from a local directory:
GlobalCEFApp.AddCustomCommandLine('--load-extension=/home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/extensions/');
```

**Note:** CEF4Delphi does NOT have `EnableExtensions` or `ExtensionDir` properties. Using them causes a compile error. Always use `AddCustomCommandLine('--load-extension=...')` instead.

**Extension directory structure:**
```
/home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/extensions/
  └── <extension-name>/
      ├── manifest.json       # Chrome MV3 manifest
      ├── background.js        # Service worker
      ├── content.js           # Content script (injects into <all_urls>)
      ├── popup.html           # Action popup
      ├── popup.js             # Popup logic
      └── icons/               # SVG icons
```

**Extension IDs:** For unpacked extensions, the Chrome extension ID is computed from the absolute path hash. Discover the ID at runtime via the remote debugging port (`--remote-debugging-port=9224`) at `http://localhost:9224/json/list`.

### The Aethelgard Bridge Extension Pattern

The canonical extension at `extensions/aethelgard-bridge/` provides agent-to-extension IPC:

```
manifest.json       → MV3, content_scripts[<all_urls>], action popup
background.js       → Service worker: routes commands, pings fleet bus, manages state
content.js          → Injects window.__aethelgardBridge into every page
                     └── bridge.send(command, payload) → Promise → background.js
                     └── Connects via chrome.runtime.connect('aethelgard-bridge')
inject.js           → Web-accessible: window.__aethelgard = { send, getSource, getTabs, ping }
popup.html/js       → Shows connected tabs, bridge health, uptime, fleet bus status
```

The bridge routes commands through the extension background, giving access to full Chrome APIs:
- `chrome.tabs.query/update`
- `chrome.storage.local.get/set`
- `chrome.scripting.executeScript`

### Agent Access via IPC

Three IPC commands give the agent extension control:

```json
{"action":"list_extensions"}
// Returns: {"status":"ok","extensions":[{"name":"⟐ Aethelgard Bridge","dir":"aethelgard-bridge"}]}

{"action":"open_extension","name":"⟐ Aethelgard Bridge"}
// Opens the extension bridge in a new tab

{"action":"extension_bridge","code":"b.send('ping').then(r=>document.title=JSON.stringify(r))"}
// Sends JS through window.__aethelgardBridge on the active tab
// The 'b' variable is the bridge object, available in every page
```

### Extension Toolbar UI

The bromium GUI has a 🧩 button in the toolbar (next to "+ New Tab") that opens a popup menu listing all loaded extensions. Click any extension to open its bridge. The menu also includes "Reload Extensions" and "Open Extensions Folder".

```pascal
// In ucontrollerbrowser.lfm:
btnExtensions: TSpeedButton  // Caption='🧩', Flat=True, Left=1106

// In ucontrollerbrowser.pas:
FExtensions: TStringList     // name → dir mapping
popExtensions: TPopupMenu    // Built dynamically from scanned manifest.json files
LoadExtensions               // Scans FExtDir for subdirectories with manifest.json
btnExtensionsClick           // Shows popup menu or handles menu item selection
OpenExtensionPopup           // Opens bridge in a new tab
```

The form is built with Lazarus LCL (GTK2 widgetset) at `ucontrollerbrowser.pas` + `ucontrollerbrowser.lfm`.

## IPC Control via `cef-browser`

The lifecycle manager at `/home/craig/.local/bin/cef-browser` speaks native CEF4Delphi IPC:

```bash
# Tab management
cef-browser tab create --profile spoofed
cef-browser tab close 1
cef-browser tabs

# Browser control
cef-browser navigate https://google.com
cef-browser eval "document.title"
cef-browser url

# Spoofing
cef-browser spoof chrome_131
cef-browser profile list

# Proxy
cef-browser proxy get
cef-browser proxy set 127.0.0.1 8080
cef-browser proxy off
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│             cef-browser CLI (Python)                │
│           Communicates via /tmp/aethelgard_cef.sock │
├─────────────────────────────────────────────────────┤
│           Dual Citizen v2 (CEF4Delphi Pascal)        │
│           Chromium 131.0.6778 engine                 │
│           Multi-tab, spoof engine, Panoptes extns    │
├─────────────────────────────────────────────────────┤
│       Chromium Embedded Framework (libcef.so)        │
│       1.35GB compiled CEF binary                    │
└─────────────────────────────────────────────────────┘
```

## Source files: TWO Pascal programs, not one

There are TWO separate Pascal source files that compile to different binaries:

| Source | Binary | Role |
|--------|--------|------|
| `dual_citizen_v2.lpr` | `dual_citizen_v2` → copied as `bromium` | Full browser with GUI, tab management, IPC socket, spoofing |
| `cef_controller.lpr` | `cef_controller` | Minimal headless controller, smaller binary |

**IMPORTANT:** They are compiled from different `.lpr` files with different CEF configurations. Editing `cef_controller.lpr` does NOT affect the `bromium` binary. Always check which source file your compiled binary came from before patching.

### Enabling Extensions When Source Won't Compile

If the FPC/Lazarus toolchain is broken (missing units, wrong include paths), hex-patch the binary — OR recompile with the correct flags:

**Recompile (preferred):**
```bash
cd ~/projects/aethelgard/fleet/pascal/dual-citizen-v2

fpc \
  -dEnableLibOverlay \        # skips missing gtk2DisableLibOverlay
  -dLCLGTK2 \                  # enables GTK2 code in uCEFLinuxFunctions
  -Fu/path/to/CEF4Delphi/source \
  -Fu/path/to/CEF4Delphi/packages \
  -Fu/path/to/CEF4Delphi/packages/lib/x86_64-linux \
  -Fi/path/to/CEF4Delphi/source \
  -Fu/usr/lib/lazarus/4.4/lcl/units/x86_64-linux/gtk2 \
  -Fu/usr/lib/lazarus/4.4/lcl/units/x86_64-linux \
  -Fu/usr/lib/lazarus/4.4/components/lazutils/lib/x86_64-linux \
  -Fu/usr/lib/lazarus/4.4/packager/units/x86_64-linux \
  dual_citizen_v2.lpr -o.bromium
```

**Hex-patch (fallback):**
```bash
# Check if the flag exists
strings bromium | grep disable-extensions

# Replace in-place (same length: 22 chars for both)
sed -i 's/--disable-extensions/--enable-extensions /g' bromium

# Verify
strings bromium | grep -i enable-extensions
```

The strings are the same length so the ELF binary structure stays valid.

## Pitfalls

- **Socket race**: Browser takes 8-15s to create `/tmp/aethelgard_cef.sock`. Don't connect before it exists. Watchdog waits 15s.
- **DISPLAY required**: Without `DISPLAY=:0` set, the binary exits immediately with "X connection broken" — no output, no log, no socket.
- **LD_LIBRARY_PATH**: Must point to the exact Release directory containing `libcef.so` (~1.35GB file). Wrong path = silent crash with exit code 0.
- **Stale sockets**: If the browser crashes, the socket file may remain. Delete it before restarting: `rm -f /tmp/aethelgard_cef.sock`
- **Stale processes**: Kill old instances before launching: `pkill -9 -x bromium` or `pkill -9 -x dual_citizen_v2`
- **Path mismatches**: The `cef-browser` Python CLI hardcodes paths from the old repo layout (`~/aethelgard-repo/...`). Symlinks must exist for it to work.
- **CEF, not Chrome — HARD RULE**: Bromium uses CEF4Delphi, NOT regular Chromium, NOT Firefox, NOT the Chrome Web Store. This is a non-negotiable architectural constraint. Do NOT build Chrome Web Store extensions, Firefox add-ons, or any "regular chromium shit." Bromium loads extensions natively via `--load-extension` — drop a compatible `manifest.json` pack into the `extensions/` directory. For automating site interactions, use the Unix socket protocol (`execute_javascript`, `navigate`, `evaluate`). If you are about to build a Chrome extension, STOP — use the socket instead. This rule was explicitly enforced by the user after a correction.
- **`EnableExtensions`/`ExtensionDir` dont exist**: CEF4Delphi's `TCefApplication` has `DisableExtensions` (boolean, defaults to False), NOT `EnableExtensions` or `ExtensionDir`. Using the latter causes a compile error. Always use `AddCustomCommandLine('--load-extension=...')` to load unpacked extensions. If you see these in source code, they were added by someone who guessed — remove them.
- **`{$R *.res}` on Linux**: Lazarus `.res` files contain Windows resources. Comment this out (`// {$R *.res}`) when building on Linux. Without this, the linker fails with "Can't open resource file".

## Session Continuity — 80k Handoff Protocol

Long Bromium development sessions follow a strict 80k handoff protocol. When any agent in the chain (main session, MoA references, delegate_task sub-agents) hits 80k tokens, it must stop and write a comprehensive handoff.

**Thresholds** (in `~/.hermes/profiles/thotheauphis/work/active_compress.py`):
| Threshold | Value | Behavior |
|-----------|-------|----------|
| warn | 75,000 | Heads up |
| compress | 78,000 | Light compression if still running |
| max_context | **80,000** | HARD LIMIT — handoff and stop |

**Handoff file:** `~/tmp/bromium-moa-handoff.md`
**Required sections in a handoff:** MoA config, what's done (files/tests/proofs), what's left (exact TODOs with paths and commands), execution order (numbered steps only), lifecycle (PIDs, sockets, daemons).
**Rule:** Do NOT compress past 80k. Hit 80k? Handoff and stop.

Full details in `references/bromium-handoff-protocol.md`.

## Path Fixes Applied

The original scripts expected binaries at `~/aethelgard-repo/fleet/pascal/` but the actual location is `~/projects/aethelgard/fleet/pascal/`. Symlinks have been created to bridge:

```bash
/home/craig/.NOTTHEONETOEDIT/fleet/pascal/dual-citizen-v2 → /home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/
/home/craig/CEF4Delphi/cef_binary_current/Release → /home/craig/.aethelgard/workspace/browser/CEF4Delphi/cef_binary_131.4.1+.../Release/
```

---

## July 2026 Session: MCP + Vision Integration + Browser Bridge

**MCP Server:** `aethelgard-fleet` (in `projects/aethelgard/mcp/aethelgard_mcp_server.py`) now exposes 3 browser tools:
- `browser_ping` — health check
- `browser_navigate` — load URL in tab
- `browser_execute` — run JS, result via title channel

**Nemotron 3 Nano Omni (free vision executor):**
- Model: `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` via OpenRouter
- 30B A3B = 3B active params, 256K context, vision+audio+video built-in
- Dispatch pattern: `delegate_task(goal="...", model={"provider":"openrouter","model":"nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"}, toolsets=["browser","vision"])`

**Working IPC commands:**
```bash
create_tab → navigate → execute_javascript → get_title
click → form_fill → evaluate_js → get_eval        # Automation
list_extensions                                     # List loaded extensions
open_extension <name>                               # Open extension bridge in new tab
extension_bridge <code>                             # Send JS through window.__aethelgardBridge
set_proxy / get_proxy / spoof                       # Network control
```

**Bridge client:** `work/bromium_bridge.py` — unified CLI for navigating, searching, deep-researching, and talking to extensions via the socket. See `references/bromium-bridge.md`.

**Fixed pitfalls this session:**
- Navigation hangs on `about:blank` → force title update via `execute_javascript("document.title='TEST-'+Date.now()")`
- `get_eval` returns `undefined`/`pending` → use title channel for return values
- Remote debugging port 9222 not open → add `--remote-debugging-port=9222` to cef_controller.lpr
- Xvfb X errors → `export LIBGL_ALWAYS_SOFTWARE=1` before launch

## Social / Research Site Skills

The `bromium_bridge.py` tool implements slash-command-style browsing for common sites:

| Site | Bridge command | Pattern |
|------|---------------|---------|
| Reddit | `browse reddit` | Navigate → search via URL param → extract text |
| Facebook | `browse facebook` | Navigate → login detection → feed extraction |
| LinkedIn | `browse linkedin` | Navigate → search by keywords → profile extraction |
| Craigslist | `browse craigslist` | Navigate → location set → search |
| DeepSeek | `deepresearch <query>` | Navigate → fill textarea → click send → poll response |
| GitHub | `browse github` | Navigate → repo search |
| X/Twitter | `browse x` | Navigate → timeline extraction |

Each follows: `sock_send(navigate) → sleep → sock_send(execute_javascript) → sock_send(get_title)`.
For deepresearch, BetterDeepSeek extension handles response rendering. Bridge only injects query + triggers send.

**Pitfall:** `chrome.runtime.sendMessage()` from page JS requires `externally_connectable` in the extension manifest. Otherwise use CDP port 9224 to reach the background page.
