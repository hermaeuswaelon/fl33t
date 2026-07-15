---
name: ares-dual-citizen-browser
description: "ARES Dual Citizen Browser — CEF4Delphi Chromium-based sovereign browser. Launch, IPC control, tab management, spoofing, proxy configuration, lifecycle management."
version: 1.0.0
author: Craig / ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, browser, cef, chromium, dual-citizen, bromium, ipc]
related_skills: [ares-aethelgard-scripts, ares-pascal-fleet]
---

# ⎔ ARES Dual Citizen Browser — Sovereign Browser

## Overview

The Dual Citizen v2 is a **37MB CEF4Delphi Chromium browser** with:
- Multi-tab support via native IPC socket (`/tmp/aethelgard_cef.sock`)
- Panoptes extensions system
- Browser fingerprint spoofing
- Proxy management
- Sovereign identity anchoring
- Full JavaScript execution control

## Locations

| Component | Path |
|-----------|------|
| **Binary** | `/home/craig/.NOTTHEONETOEDIT/fleet/pascal/dual-citizen-v2/dual_citizen_v2` (symlink → `/home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/dual_citizen_v2`) |
| **Launcher** | `/home/craig/Desktop/Scripts-Launchers/bromium.sh`, `super_browser.sh` |
| **CEF Libs** | `/home/craig/.aethelgard/workspace/browser/CEF4Delphi/cef_binary_131.4.1+chromium-131.0.6778.265_linux64/Release/libcef.so` (1.35GB!) |
| **Lifecycle CLI** | `/home/craig/.local/bin/cef-browser` |
| **Watchdog** | `/home/craig/.NOTTHEONETOEDIT/scripts/browser-watchdog.sh` |
| **Systemd** | `/home/craig/.config/systemd/user/dual-citizen-watchdog.service` |
| **Sources** | `/home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/` |

## Launch

```bash
# Method 1: Direct (works in terminal)
cd /home/craig/.NOTTHEONETOEDIT/fleet/pascal/dual-citizen-v2 && \
  LD_LIBRARY_PATH="/home/craig/CEF4Delphi/cef_binary_current/Release" \
  DISPLAY=:0 \
  ./dual_citizen_v2

# Method 2: Lifecycle CLI (Python)
cef-browser start
cef-browser stop
cef-browser status
cef-browser navigate https://example.com

# Method 3: Desktop launcher
/home/craig/Desktop/Scripts-Launchers/bromium.sh
```

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

## Pitfalls

- **Socket race**: Browser takes 8-15s to create `/tmp/aethelgard_cef.sock`. Don't connect before it exists. Watchdog waits 15s.
- **DISPLAY required**: Without `DISPLAY=:0` set, the binary exits immediately with "X connection broken" — no output, no log, no socket.
- **LD_LIBRARY_PATH**: Must point to the exact Release directory containing `libcef.so` (~1.35GB file). Wrong path = silent crash with exit code 0.
- **Stale sockets**: If the browser crashes, the socket file may remain. Delete it before restarting: `rm -f /tmp/aethelgard_cef.sock`
- **Stale processes**: Kill old instances before launching: `pkill -9 -x dual_citizen_v2`
- **Path mismatches**: The `cef-browser` Python CLI hardcodes paths from the old repo layout (`~/aethelgard-repo/...`). Symlinks must exist for it to work.

## Path Fixes Applied

The original scripts expected binaries at `~/aethelgard-repo/fleet/pascal/` but the actual location is `~/projects/aethelgard/fleet/pascal/`. Symlinks have been created to bridge:

```bash
/home/craig/.NOTTHEONETOEDIT/fleet/pascal/dual-citizen-v2 → /home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/
/home/craig/CEF4Delphi/cef_binary_current/Release → /home/craig/.aethelgard/workspace/browser/CEF4Delphi/cef_binary_131.4.1+.../Release/
```

---

## July 2026 Session: MCP + Vision Integration

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
```

**Fixed pitfalls this session:**
- Navigation hangs on `about:blank` → force title update via `execute_javascript("document.title='TEST-'+Date.now()")`
- `get_eval` returns `undefined`/`pending` → use title channel for return values
- Remote debugging port 9222 not open → add `--remote-debugging-port=9222` to cef_controller.lpr
- Xvfb X errors → `export LIBGL_ALWAYS_SOFTWARE=1` before launch
