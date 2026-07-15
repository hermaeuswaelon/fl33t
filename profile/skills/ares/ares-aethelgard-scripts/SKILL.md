---
name: ares-aethelgard-scripts
description: "ARES Aethelgard Scripts — Python/Python watchdogs, the browser watchdog, context compression daemon, irrational timers, fleet tool bridge, auto-delegation engine. Every script in the aethelgard project."
version: 1.0.0
author: Craig / ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, scripts, aethelgard, watchdog, context, fleet]
related_skills: [ares-pascal-fleet, ares-nemotron-together-dual-offload]
---

# 📜 ARES Aethelgard Scripts

## Overview

Python and shell scripts that orchestrate the Aethelgard Fleet. Located at `/home/craig/projects/aethelgard/scripts/`.

## All Scripts

| Script | Type | Purpose |
|--------|------|---------|
| `browser-watchdog.sh` | Bash | Systemd service — checks dual_citizen_v2 every 30s, restart if dead |
| `memory_watchdog.sh` | Bash | Memory daemon watch loop |
| `wal_checkpoint.sh` | Bash | SQLite WAL checkpoint maintenance |
| `metrics_cron.sh` | Bash | System metrics cron collector |
| `fix-paths.sh` | Bash | Path fixer (symlink repair) |
| `setup.sh` | Bash | Project bootstrap |
| `run_cef_browser.sh` | Bash | Browser launch wrapper |
| `cef_supervisor.py` | Python | CEF browser supervisor |
| `cef_exit_test.py` | Python | CEF exit behavior test |
| `start_cef_browser.py` | Python | Programmatic browser start |
| `portable_test.py` | Python | Portable binary test suite |
| `auto_delegation_engine.py` | Python | Automatic task delegation |
| `context_compress.py` | Python | Tool context compression (feeds Offloader Alpha) |
| `context_discipline.py` | Python | Context discipline/enforcement |
| `context_stripper.py` | Python | Context pruning |
| `ctx-disc-watch.py` | Python | Context discipline watch loop |
| `fleet_awareness_pulse.py` | Python | Fleet awareness heartbeat |
| `fleet_tool_bridge.py` | Python | Fleet-to-tool API bridge |
| `irrational_timers.py` | Python | Prime-number-based scheduling |
| `refresh_handoff.py` | Python | Session refresh handoff |
| `wo_tracker.py` | Python | Work order tracking |
| `zw_tag.py` | Python | Zero-width tag embedding |
| `base80.py` | Python | Base80 encoding utility |

## Key Scripts

### Browser Watchdog (`browser-watchdog.sh`)
- Systemd user service: `dual-citizen-watchdog.service`
- Runs every 30s, checks socket + process, restarts if dead
- Installed at: `/home/craig/.config/systemd/user/`
- Systemd: `/etc/systemd/system/aethelgard-cef.service`

### Context Compress Daemon (`context_compress.py`)
- Feeds tool results into the Offloader Alpha model
- Uses Nemotron 3 Ultra via OpenRouter API to compress to 10% original size

### Fleet Awareness Pulse (`fleet_awareness_pulse.py`)
- Heartbeat that publishes fleet state to the event bus
- Connects agents, tracks alive/dead status

## Running Scripts

```bash
# Start the browser watchdog manually
bash /home/craig/.NOTTHEONETOEDIT/scripts/browser-watchdog.sh

# Systemd user service (auto-start on login)
systemctl --user enable dual-citizen-watchdog.service
systemctl --user start dual-citizen-watchdog.service

# Context compression daemon
python3 /home/craig/projects/aethelgard/scripts/context_compress.py

# Fleet awareness pulse
python3 /home/craig/projects/aethelgard/scripts/fleet_awareness_pulse.py
```

## Pitfalls

- **Dead paths**: The `browser-watchdog.sh` and `cef-browser` CLI have hardcoded paths that may be wrong after repo restructures. Use `references/browser-recovery-workflow.md` to trace systemd→watchdog→binary and create symlink bridges.
- **Browser needs DISPLAY=:0**: Without a display, the binary exits silently with "X connection broken."
- **CEF lib path**: `LD_LIBRARY_PATH` must point to the exact directory with `libcef.so` (~1.35GB). Wrong path = silent crash.
- **socket race**: The browser takes 8-15s to create `/tmp/aethelgard_cef.sock`. Don't try to connect before it exists.

## Install Missing Systemd Service

```bash
# Enable the user watchdog
systemctl --user daemon-reload
systemctl --user enable dual-citizen-watchdog.service
systemctl --user start dual-citizen-watchdog.service

# Check if system service exists (need root)
sudo systemctl status aethelgard-cef.service 2>/dev/null || echo "System service missing"
```
