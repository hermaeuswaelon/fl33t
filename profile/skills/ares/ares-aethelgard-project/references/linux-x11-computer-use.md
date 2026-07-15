# Linux X11 Computer-Use Troubleshooting

Reference: System X11/cua-driver diagnostics from the Thotheauphis profile.

## Environment

- **OS:** Ubuntu 26.04 LTS, X11 (DISPLAY=:0.0)
- **GPU:** None (CPU-only, nvidia-smi not found)
- **Display:** 1920×1200, single screen
- **cua-driver:** v0.8.1 installed under both Python 3.13 and 3.14

## `hermes computer-use doctor` Output (all pass)

```
[ok] binary:         cua-driver 0.8.1
[ok] display server: X11 (DISPLAY=:0.0)
[ok] X11 connection: 5 visible top-level windows
[ok] AT-SPI:         org.a11y.Bus reachable
```

## Python Version Mismatch (Critical Failure Mode)

Hermes runs under Python 3.14 on this system. If `pip3 install cua-driver` puts it under Python 3.13's site-packages, the tool call times out with:

```
computer_use backend unavailable: cua-driver session never reached ready
  (timeout 30s; stuck in phase: unknown)
```

Despite `hermes computer-use doctor` reporting success (it queries the binary directly), the Hermes backend spawns `cua-driver mcp` via subprocess and fails when the Python `mcp` SDK can't import `cua_driver`.

**Fix:**
```bash
pip3.14 install --break-system-packages cua-driver
```

## Raw cua-driver CLI (Bypasses MCP)

```bash
cua-driver call get_screen_size
cua-driver call health_report
cua-driver call get_desktop_state
cua-driver call list_tools
```

## Xdotool Fallback (Always Works)

When cua-driver's MCP session won't establish, xdotool always works on X11:

| Action | Command |
|--------|---------|
| Get cursor pos | `xdotool getmouselocation` |
| Move cursor | `xdotool mousemove X Y` |
| Click | `xdotool click 1` (left), `3` (right) |
| Key combo | `xdotool key ctrl+c` |
| Type text | `xdotool type "text"` |
| Focus window | `xdotool windowactivate WID` |
| List windows | `xdotool search --name "pattern"` |
| Screen size | `xdotool getdisplaygeometry` |
| Clipboard read | `xclip -selection clipboard -o` |
| Clipboard write | `xclip -selection clipboard` |

## Available X11 Tools

| Tool | Installed | Use |
|------|-----------|-----|
| `xdotool` | ✅ | Mouse, keyboard, windows |
| `xclip` | ✅ | Clipboard |
| `xvfb` | ✅ | Virtual framebuffer for headless |
| `xprop` | ✅ | Window properties |
| `xwininfo` | ✅ | Window info |
| `xrandr` | ❌ | Display config (not installed) |
| `xvkbd` | ❌ | Virtual keyboard (not installed) |

## Unified X11 Tool

`work/x11_tool.py` wraps all X11 functions (xdotool + xclip + cua-driver screenshot fallback) into a single tool registered in the Hermes tool registry as `x11` with toolset `computer_use`. Call via `x11(action="mouse_pos")` etc.

## CEF4Delphi Dual Citizen Browser (Dual-Citizen v2)

**Binary:** `/home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/dual_citizen_v2` (37MB)

**Socket IPC:** `/tmp/aethelgard_cef.sock` — JSON-line protocol

**Commands supported:**
- `create_tab` → returns `tab_id`
- `navigate` → `{url, tab_id}`
- `get_title` → `{tab_id}`
- `execute_javascript` → `{code, tab_id}` (fire-and-forget)
- `evaluate_js` → `{code, tab_id}` (returns via `get_eval`, **broken in headless**)
- `get_eval` → `{id}` (polling for evaluate_js results)
- `click` → `{selector, tab_id}`
- `form_fill` → `{fields: {...}, tab_id}`
- `list_tabs` → `{}`
- `close_tab` → `{tab_id}`
- `activate_tab` → `{tab_id}`

**Known Working:**
- `navigate` + `get_title` → page loads, title returned
- `click` → selector clicks work
- `form_fill` → name/id field population works
- `execute_javascript` → fire-and-forget executes
- `create_tab` / `list_tabs` / `close_tab` / `activate_tab` → full tab lifecycle

**Known Broken:**
- `evaluate_js` + `get_eval` → `FEvalResultReady` never fires in headless CEF (no real OnTitleChange event for the injected title setter). Workaround: `execute_javascript` + `document.title = JSON.stringify(result)` → poll `get_title`.

**Headless Flags (from cef_controller.lpr):**
```
--no-sandbox
--disable-gpu
--disable-gpu-compositing
--disable-software-rasterizer
--remote-debugging-port=9222   # NOT currently active (needs flag passed)
```

**Process Tree (typical):**
```
dual_citizen_v2 (main) → zygotes (3) → renderers (2-3) → utility (network, audio)
```

**Remote Debugging:** Currently NOT enabled. Add `--remote-debugging-port=9222` to CEF command line for CDP access.

**X11 Errors:** CEF logs show continuous "ChangeWindowAttributesRequest" warnings in Xvfb. Cosmetic only — rendering works.
