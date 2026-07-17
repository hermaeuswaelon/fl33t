# Batch CRX Install Workflow

Download and unpack 10+ Chrome Web Store extensions into Bromium's `extensions/` directory in one pass.

## Prerequisites

- `curl` with `-A` (User-Agent) flag
- `~/.local/bin/bromium-crx-install.py` — CRX3 unpacker
- Staging dir: `/tmp/bromium-crx-staging/`

## Download URL Format

```
https://clients2.google.com/service/update2/crx?
  response=redirect&
  prod=chromiumcrx&
  prodversion=131.0.6778.265&
  acceptformat=crx3&
  x=id%3D<EXT_ID>%26v%3D%26installsource%3Dondemand%26uc
```

## Critical: User-Agent Required

Google's update API returns **HTTP 204 (empty response)** when curl's default User-Agent is used. Always include:

```bash
-A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
```

## Per-Extension Steps

```bash
# 1. Download
EXT_ID="<id-here>"
curl -s -L --compressed \
  -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -o "/tmp/bromium-crx-staging/${EXT_ID}.crx" \
  "https://clients2.google.com/service/update2/crx?response=redirect&prod=chromiumcrx&prodversion=131.0.6778.265&acceptformat=crx3&x=id%3D${EXT_ID}%26v%3D%26installsource%3Dondemand%26uc"

# 2. Verify CRX3 magic
head -c 4 "/tmp/bromium-crx-staging/${EXT_ID}.crx"  # should print Cr24

# 3. Unpack into extensions dir
python3 ~/.local/bin/bromium-crx-install.py \
  "/tmp/bromium-crx-staging/${EXT_ID}.crx" \
  ~/projects/aethelgard/fleet/pascal/dual-citizen-v2/extensions

# 4. Restart Bromium to load new extensions
systemctl --user stop dual-citizen-watchdog
killall bromium cef_controller 2>/dev/null
sleep 1 && rm -f /tmp/aethelgard_cef.sock
systemctl --user start dual-citizen-watchdog
sleep 5
python3 ~/.local/bin/bromium_agent.py  # verify
```

## Profile Extension Flattening

Extensions copied from `/tmp/bromium-profile/Default/Extensions/<id>/` have a version subdirectory structure:

```
extensions/<id>/0.1.10/manifest.json   ← WRONG
extensions/<id>/manifest.json          ← NEEDED
```

CEF's `--load-extension=<dir>` expects `manifest.json` directly in the extension's directory. Fix:

```bash
EXT_DIR=~/projects/aethelgard/fleet/pascal/dual-citizen-v2/extensions
VERDIR=$(ls "$EXT_DIR/<id>/" | head -1)
cp -r "$EXT_DIR/<id>/$VERDIR/"* "$EXT_DIR/<id>/"
rm -rf "$EXT_DIR/<id>/$VERDIR"
ls "$EXT_DIR/<id>/manifest.json"  # verify
```

## Proven Extension IDs

These were verified working in a single session (July 2026):

| ID | Extension | Purpose |
|----|-----------|---------|
| `haeoijepjlgjkoefofnebcniaioihdae` | JSON Viewer | Format API responses |
| `gppongmhjkpfnbhagpmjfkannfbllamg` | Wappalyzer | Detect tech stack |
| `bfbameneiokkgbdmiekhjnmfkcnldhhm` | Web Developer | Dev toolbar |
| `pklblaefkkcmofjcobdmcflmdphecpne` | MarkDownload | Pages → markdown |
| `ojfebgpkimhlhcblbalbfjblapadhbol` | EditThisCookie (V3) | Cookie manager |
| `fdpohaocaechififmbbbbbknoalclacl` | GoFullPage | Full page screenshots |
| `jabopobgcpjmedljpbcaablpmlmfcogm` | WhatFont | Identify fonts |
| `bhchdcejhohfmigjafbampogmaanbfkg` | User-Agent Switcher | Spoof browser identity |
| `cppjkneekbjaeellbfkmgnhonkkjfpdn` | Clear Cache | One-click cache clearing |
| `mpiodijhokgodhhofbcjdecpffjipkle` | SingleFile | Save page as single HTML |
| `aabiopennjmopfippagcalmkdjlepdhh` | Better DeepSeek | DeepSeek UX enhancement |
| `jmbmjnojfkcohdpkpjmeeijckfbebbon` | Chromium Browser Automation | Record/play automation |
| `cadlpkhdkhlecgchhgaclpnbahfckppp` | Research Notes | Bookmark, annotate, highlight |
| `cjpalhdlnbpafiamejdnhcphjbkeiagm` | uBlock Origin | Ad blocker |

## File size reference

| Extension | CRX Size |
|-----------|----------|
| JSON Viewer | ~357 KB |
| Wappalyzer | ~34 MB |
| Web Developer | ~588 KB |
| MarkDownload | ~586 KB |
| EditThisCookie | ~1.1 MB |
| GoFullPage | ~1.8 MB |
| WhatFont | ~758 KB |
| User-Agent Switcher | ~836 KB |
| Clear Cache | ~691 KB |
| SingleFile | ~1.3 MB |
