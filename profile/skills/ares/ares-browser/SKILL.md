---
name: ares-browser
description: "ARES Browser Umbrella — Bromium (CEF4Delphi) browser control, IPC bridge, extension management, research suite, and Bromium Portal. Consolidated from 4 original skills."
version: 3.0.0
author: Craig / Thotheauphis
platforms: [linux]
metadata:
  hermes:
    tags: [ares, browser, umbrella, consolidated, bromium, cef, ipc, extensions, portal, research]
    related_skills: [ares, ares-mythic, ares-pentest]
---

# ⎔ ARES Browser Umbrella

## About This Skill

This is the **ARES Browser umbrella skill**, consolidating 4 original skills:
- `ares-browser-research` — Browser research suite for navigating/extracting content
- `ares-dual-citizen-browser` — Bromium CEF4Delphi browser lifecycle and IPC control
- `bromium-extension-bridge` — Extension bridge and agent control via Unix socket
- `bromium-portal` — Stephen Hawking Edition v3.3 desktop command center

Load this skill when working with the Bromium browser, CEF4Delphi IPC, extension loading, web scraping, social site automation, or the desktop portal GUI.

---

# Part 1: Bromium Browser Architecture

## Overview

Bromium (née Dual Citizen v2) is a **37MB CEF4Delphi Chromium browser** with multi-tab support, native IPC socket, extension loading, spoofing, and proxy management.

**Binary:** `/home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/bromium`
**Socket:** `/tmp/aethelgard_cef.sock`
**CDP:** Port 9224 (remote debugging)
**CEF Libs:** `/home/craig/.aethelgard/workspace/browser/CEF4Delphi/cef_binary_131.4.1+chromium-131.0.6778.265_linux64/Release/` (1.35GB libcef.so)
**Watchdog:** Systemd `dual-citizen-watchdog.service`
**Lifecycle CLI:** `~/.local/bin/cef-browser`

## Launch
```bash
cd /home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2 && \
  LD_LIBRARY_PATH="/home/craig/CEF4Delphi/cef_binary_current/Release" \
  DISPLAY=:0 \
  ./bromium
```

## Architecture
```
┌─────────────────────────────────────┐
│  bromium_agent.py (preferred CLI)   │
│  bromium_bridge.py (work/)          │
├─────────────────────────────────────┤
│  Dual Citizen v2 (CEF4Delphi)       │
│  Chromium 131.0.6778 engine         │
│  Multi-tab, spoof engine            │
├─────────────────────────────────────┤
│  Chromium Embedded Framework        │
│  libcef.so (1.35GB)                 │
└─────────────────────────────────────┘
```

## IPC Commands

Send JSON via Unix socket:
```python
import socket, json
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(10)
s.connect("/tmp/aethelgard_cef.sock")
s.send(json.dumps({"action": "navigate", "url": "...", "tab_id": 1}).encode() + b'\n')
resp = s.recv(65536).decode()
```

| Action | Purpose |
|--------|---------|
| `navigate` | Load URL in tab |
| `get_title` | Read page title |
| `execute_javascript` | Run JS fire-and-forget |
| `list_tabs` / `create_tab` / `close_tab` / `activate_tab` | Tab management |
| `list_extensions` | List loaded unpacked extensions |
| `open_extension` | Activate extension in new tab |
| `extension_bridge` | Send JS through window.__aethelgardBridge |

## Two Pascal Programs
| Source | Binary | Role |
|--------|--------|------|
| `dual_citizen_v2.lpr` | `bromium` | Full browser with GUI, IPC, spoofing, tabs |
| `cef_controller.lpr` | `cef_controller` | Minimal headless controller |

## Session Continuity — 80k Handoff Protocol
Thresholds: warn=75K, compress=78K, max_context=80K (HARD LIMIT). Write handoff file to `~/tmp/bromium-moa-handoff.md`.

## Pitfalls
- Socket race: browser takes 8-15s to create socket
- DISPLAY=:0 required (exits silently without X)
- LD_LIBRARY_PATH must point to exact Release dir with libcef.so
- CEF, not Chrome — use `--load-extension` NOT Chrome Web Store
- `EnableExtensions`/`ExtensionDir` don't exist in CEF4Delphi — use `AddCustomCommandLine('--load-extension=...')`
- Navigation destroys all JS context — re-inject after every navigate
- content scripts do NOT auto-inject on CEF MV3 — use `execute_javascript`
- Bridge `.then()` callbacks require async IIFE wrapper

---

# Part 2: Extension Bridge

## Agent CLI (preferred over raw socket)
```bash
python3 ~/.local/bin/bromium_agent.py                    # Health check
python3 ~/.local/bin/bromium_agent.py --navigate <url> --tab 1
python3 ~/.local/bin/bromium_agent.py --title --tab 1
python3 ~/.local/bin/bromium_agent.py --list-extensions
python3 ~/.local/bin/bromium_agent.py --list-tabs
python3 ~/.local/bin/bromium_agent.py --eval "document.title = 'OK'" --tab 1
```

## Extension Architecture
Extensions loaded from `extensions/` subdirectory or from browser profile at `/tmp/bromium-profile/Default/Extensions/`.

### The Aethelgard Bridge Extension
Located at `extensions/aethelgard-bridge/` (MV3, content_scripts[<all_urls>]):
- `window.__aethelgardBridge` — bridge object in every page
- Commands: `ping`, `get_all_tabs`, `activate_tab`, `get_page_source`, `get_storage`, `set_storage`, `inject_script`

### Profile-Based Extensions (11 installed)
| ID | Name |
|----|------|
| `aabiopennjmopfippagcalmkdjlepdhh` | Better DeepSeek |
| `ceacgaccjcomdbnoodjpllihjmeflfmg` | Science Research Assistant |
| `liihfcjialakefgidmaadhajjikbjjab` | alphaXiv |
| `ofaokhiedipichpaobibbnahnkdoiiah` | Instant Data Scraper |
| `okngcalljddikhljpfhgmikklmmmdkkd` | Agent OS |
| `ihdobppgelceaoeojmhpmbnaljhhmhlc` | Spoof Geolocation |

## Chrome Web Store Install Fix
Four-layer bypass to prevent external OS windows when clicking "Add to Chrome":
1. CEF command-line flags (`--disable-features=ChromeExtensionsMenu,ChromeWebStoreInstall,...`)
2. JS injection in `DoLoadEnd` — hooks button, sets `document.title = "BROMIUM_CRX:" + extId`
3. Timer-based detection + curl download (external process, bypasses CEF extension manager)
4. CRX3 unpack via Python (`~/.local/bin/bromium-crx-install.py`)

## Build Commands
```bash
cd ~/projects/aethelgard/fleet/pascal/dual-citizen-v2
rm -f *.ppu *.o *.rst build_out/* 2>/dev/null; mkdir -p build_out
fpc -Mobjfpc -Sh -gl -O2 \
    -Fu/usr/lib/lazarus/4.4/lcl/units/x86_64-linux/gtk2 \
    -Fu/usr/lib/lazarus/4.4/lcl/units/x86_64-linux \
    -Fu/usr/lib/lazarus/4.4/packager/units/x86_64-linux \
    -Fu/usr/lib/lazarus/4.4/components/lazutils/lib/x86_64-linux \
    -Fu/usr/lib/lazarus/4.4/components/lazcontrols/lib/x86_64-linux/gtk2 \
    -Fu/home/craig/.aethelgard/workspace/browser/CEF4Delphi/packages/lib/x86_64-linux \
    -Fu/home/craig/.aethelgard/workspace/browser/CEF4Delphi/source \
    -Fl/home/craig/.aethelgard/workspace/browser/CEF4Delphi/cef_binary_current/Release \
    -FU./build_out -o./bromium dual_citizen_v2.lpr
cp bromium cef_controller
```

---

# Part 3: Browser Research Suite

## Quick Start
```bash
cd /home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/work
python3 bromium_bridge.py navigate https://example.com
python3 bromium_bridge.py title
python3 bromium_bridge.py text
python3 bromium_bridge.py js "document.title"
```

## Social / Research Site Navigation
```bash
python3 bromium_bridge.py browse reddit
python3 bromium_bridge.py search reddit "sovereign AI"
python3 bromium_bridge.py search craigslist "developer"
python3 bromium_bridge.py browse linkedin
python3 bromium_bridge.py deepresearch "research question"
```
Pattern: `sock_send(navigate) → sleep → execute_js → get_title`

## DeepResearch Pipeline (chat.deepseek.com)
1. Navigate to chat.deepseek.com
2. Inject bridge content script
3. Type query via `nativeSetter` + `Event('input')`
4. Click send / Enter keydown
5. Poll for response (up to 60s across 5 DOM selectors)
6. Return extracted text

## CDP Access
```bash
curl http://127.0.0.1:9224/json/list        # List all targets
curl http://127.0.0.1:9224/json/version      # Browser version
```

## Related Tools in `work/`
| Tool | File | Purpose |
|------|------|---------|
| Bromium Bridge | `work/bromium_bridge.py` | Unified CLI |
| Pascal Lens | `work/pascal_lens.py` | .pas→pseudo-code converter |
| Ctx Tight | `work/ctx_tight.py` | Verbose→broken English compression |
| TAC | `work/tac.py` | Thotheauphis auto-curator |

---

# Part 4: Bromium Portal — Stephen Hawking Edition v3.3

## Overview
Tkinter desktop GUI (~2070 lines) for the Bromium browser with 5 accessibility modes designed for single-switch control.

**Location:** `~/Desktop/bromium-portal.py`
**Launcher:** `~/Desktop/Scripts-Launchers/bromium.sh portal`

## Accessibility Modes
| Mode | Key | Description |
|------|-----|-------------|
| NORMAL | Default | Standard UI with speed dial, toolbar, tabs |
| SCAN | F2/Space | Row-column scanning cycles continuously |
| DWELL | F2 | Hover auto-click with configurable delay |
| LARGE | F2 | Large-button accessibility mode |

## Single-Switch Flow
Space → SCAN mode starts → Space selects row → Space selects column → page loads → Space selects element → native click → auto-restart

## Speed Dial
70+ dark-themed tiles in 12 categories: Facebook Hub, Meta Family, Microblogging, Video, Professional, Visual, Audio, Communities, Messaging, Creator Tools, Casino Audit, Development.

## Casino Audit Dashboard
Dedicated tab reading local monitor files (`~/Desktop/Casino-Monitor/`): pulse status, timegate config, balance history, surveillance log. Quick actions and categorized audit resources grid.

## Keyboard Shortcuts
| Key | Action |
|-----|--------|
| F1 | Help |
| F2 | Cycle accessibility mode |
| F3 | Refresh page elements |
| F4 | Scan current page |
| F5 | Refresh browser status |
| F6 | Toggle reading mode |
| Space | Select row/column item |

## Pitfalls
- Patching large Python files shifts line numbers — work top-to-bottom
- Subagent delegation gets interrupted on >10-15 tool calls
- Canvas inside sidebar changes widget tree (master is now Canvas, not Frame)
- Portal won't start without Bromium socket — launch Bromium first
- Two speed dials must stay in sync: HTML file + `CATEGORY_SITES` constant

---

# Part 5: Original Skill Files (Preserved)

## `ares-browser-research` References
- None (references dir exists but empty)

## `ares-dual-citizen-browser` References
- `references/hex-patch-extensions.md`
- `references/bromium-bridge.md`
- `references/browser-mcp-vision.md`
- `references/bromium-handoff-protocol.md`

## `bromium-extension-bridge` References
- `references/title-channel-json.md`
- `references/batch-crx-install.md`
- `references/aethelgard-bridge-protocol.md`
- `references/chrome-webstore-install-fix.md`
- `scripts/bromium-crx-install.py`

## `bromium-portal` References
- `references/social-casino-expansion-catalog.md`
