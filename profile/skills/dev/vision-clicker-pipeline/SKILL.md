---
name: vision-clicker-pipeline
category: dev
tags: [bromium, vision-clicker, auto-agent, browser-automation, lfm2-vl, sovereign]
description: Full-stack browser automation pipeline using Bromium CEF + lfm2-vl-gui-sft + LFM2.6B planner. Click elements by description, type text, navigate, and execute multi-step goals.
---

# ⧉ Vision Clicker Pipeline — Browser Automation Stack

## Architecture

```
User Goal → auto-agent.py → Rule-based decomposer (instant) + LFM2.6B (optional)
  → vision-clicker.py → Bromium IPC → CEF Browser
  ↓
  lfm2-vl (8086) for GUI element analysis
  LFM2.6B (8080) for structured planning (slow, ~1.8 t/s)
```

## Tools

### `vision-clicker.py` — Element Scanner & Clicker
Located at `~/.local/bin/vision-clicker.py`

```bash
# Scan current page for interactive elements
vision-clicker.py scan --tab 1

# Click element by description (text match → LFM2.6B fallback)  
vision-clicker.py click "Send button" --tab 1
vision-clicker.py click "Phone number / email address" --tab 1

# Navigate
vision-clicker.py navigate "https://chat.deepseek.com" --tab 1

# Screenshot + VL analysis (if X11 available)
vision-clicker.py screenshot --find "login button" --tab 1
```

### `auto-agent.py` — Autonomous Goal Execution
Located at `~/.local/bin/auto-agent.py`

```bash
# Interactive mode
auto-agent.py --interactive

# Single goals
auto-agent.py "click the Terms of Use link" --tab 1
auto-agent.py "go to deepseek and type hello" --tab 1

# Built-in commands available in goal mode
auto-agent.py "scan"           # list elements
auto-agent.py "click X"        # click by description
auto-agent.py "type X"         # type into focused element
auto-agent.py "nav URL"        # navigate to URL
```

## How Element Finding Works (4 Strategies)

1. **Direct text match** — exact or substring match on element text
2. **Word overlap** — shared word scoring between description and element text
3. **Tag/type keyword** — "button" → `<button>`, "input" → `<input>`, etc.
4. **LFM2.6B planner** (slow, 120s timeout) — for ambiguous descriptions

## Key Files

| File | Purpose |
|------|---------|
| `~/.local/bin/vision-clicker.py` | Element scanner + clicker |
| `~/.local/bin/auto-agent.py` | Autonomous goal executor |
| `~/.local/bin/bromium_agent.py` | Raw Bromium IPC interface |
| `/tmp/aethelgard_cef.sock` | Bromium Unix socket |

## Services

| Port | Model | Purpose |
|------|-------|---------|
| 8080 | LFM2-2.6B | Text planner (slow, ~1.8 t/s) |
| 8086 | lfm2-vl-gui-sft Q4_K_M | Vision + text (fast, ~6 t/s text, 99-107 t/s gen) |

## Pitfalls

- **LFM2.6B is slow** (~1.8 t/s). It's used only as fallback for element finding.
- **VL model (8086)** doesn't follow structured output well — use for vision tasks only, not planning.
- **No X11 window** — Bromium runs headless. Screenshot features require Xvfb or display server.
- **DeepSeek login page** shows auth wall. Can't reach chat without credentials.
- **Title channel** is the data delivery mechanism — element data is piped through `document.title`.

## Troubleshooting

```bash
# Check Bromium health
python3 ~/.local/bin/bromium_agent.py

# Check element finding  
auto-agent.py "scan"

# Manually test IPC
python3 -c "
import socket, json
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(5)
s.connect('/tmp/aethelgard_cef.sock')
s.send(json.dumps({'action':'list_extensions','id':'1'}).encode() + b'\n')
print(s.recv(4096).decode())
s.close()
"
```

## Permissions

Both scripts at `~/.local/bin/` are `chmod +x` and should be on PATH if `~/.local/bin` is in PATH.
