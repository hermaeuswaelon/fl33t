# X11 Desktop Control with xdotool + cua-driver

## Overview

Two-layer X11 control stack for Linux desktop automation:

1. **xdotool** (always available) — mouse, keyboard, window management, clipboard
2. **cua-driver** (when installed) — screenshots, element detection, AT-SPI tree

The `x11` tool in `work/x11_tool.py` wraps both in a single handler with fallback.

## xdotool Actions

| Action | Command | Purpose |
|--------|---------|---------|
| Get mouse | `xdotool getmouselocation` | Returns x,y coordinates |
| Move mouse | `xdotool mousemove X Y` | Move cursor to pixel |
| Click | `xdotool click N` | N=1 left, 2 middle, 3 right |
| Key combo | `xdotool key ctrl+c` | Press shortcut |
| Type | `xdotool type "text"` | Type text at cursor |
| List windows | `xdotool search --name .` | All window IDs |
| Focus window | `xdotool windowactivate ID` | Bring window to front |
| Get window name | `xdotool getwindowname ID` | Window title |
| Display size | `xdotool getdisplaygeometry` | Width x Height |

## cua-driver (when installed)

```
cua-driver 0.8.1
Location: ~/.local/lib/python3.13/site-packages/cua_driver/bin/cua-driver
```

### Health Check
```bash
cua-driver doctor
```
Checks: binary, install dir, home dir, telemetry, display server, X11 connection, AT-SPI.

### Key Tools
- `cua-driver list-tools` — all available MCP tools
- `cua-driver call get_desktop_state` — full-display screenshot
- `cua-driver call get_screen_size` — display dimensions
- `cua-driver call click` — click at element/coordinate
- `cua-driver call type_text` — type to a window

### MCP Mode (for Hermes integration)
```bash
cua-driver mcp
```
Runs as an MCP server that Hermes's `computer_use` tool connects to.

## Screenshot Fallback

```bash
import -window root /tmp/screenshot.png  # ImageMagick
```

When cua-driver is unavailable, ImageMagick's `import` command captures the full desktop. The x11 tool tries cua-driver first, falls back to `import`.

## Diagnosis

```bash
# X11 connection test
xdpyinfo | grep -E "dimensions|depths|number of screens"

# Window list
xdotool search --name "."

# Mouse position
xdotool getmouselocation

# cua-driver full health report
cua-driver doctor --json

# Run cua-driver as MCP server for debugging
cua-driver mcp --port 39456
```
