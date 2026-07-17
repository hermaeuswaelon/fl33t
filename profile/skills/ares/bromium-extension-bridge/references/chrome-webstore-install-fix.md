# Chrome Web Store Install Fix — Full Pipeline

## Problem

Clicking "Add to Chrome" on `chromewebstore.google.com` opens an **external OS-level Chromium window** instead of installing the extension into Bromium.

## Root Cause

CEF's extension manager intercepts `clients2.google.com/service/update2/crx` URLs at the **network stack level** — below `OnBeforeBrowse`, `OnBeforePopup`, and `OnOpenUrlFromTab`. Even `browser.Host.StartDownload(url)` fails because the extension manager snatches the URL before CEF's download manager can handle it.

Three approaches that DON'T work:
1. **window.location.href = crx_url** — triggers the extension manager, which opens an OS window
2. **fetch(crx_url)** — CORS blocked (chromewebstore.google.com → clients2.google.com)
3. **browser.Host.StartDownload(crx_url)** — extension manager intercepts before download manager

## Working Fix

### Files Modified

| File | Changes |
|------|---------|
| `dual_citizen_v2.lpr` | Added `ChromeWebStoreInstall` to `--disable-features=` (line ~43) |
| `ucontrollerbrowser.pas` | `DoLoadEnd`: added JS injection hook for Chrome Web Store pages (line ~1120) |
| `ucontrollerbrowser.pas` | `Timer1Timer`: added BROMIUM_CRX detection + curl download + InstallCRX + LoadExtensions (line ~1561) |
| `ucontrollerbrowser.pas` | `InstallCRX()` function: new, delegates to Python helper (line ~1616) |
| `ucontrollerbrowser.pas` | `install_crx` IPC command: new handler (line ~938) |
| `ucontrollerbrowser.pas` | `DoDownloadUpdated`: auto-installs .crx files on completion (line ~1400) |
| `ucontrollerbrowser.pas` | `DoBeforeBrowse`: changed CRX URL handler to use `StartDownload` instead of routing to new tab (line ~1220) |

### Files Created

| File | Purpose |
|------|---------|
| `~/.local/bin/bromium-crx-install.py` | CRX3 unpacker: strips CRX3 header, extracts ZIP to extensions dir, returns extension name |

### Pipeline (Step by Step)

```
User clicks "Add to Chrome"
        │
        ▼
JS hook fires (DoLoadEnd injection)
  • e.preventDefault() + e.stopPropagation()
  • document.title = "BROMIUM_CRX:<ext_id>"
        │  (no navigation, no fetch — just a DOM signal)
        ▼
Timer1Timer polls FTabs[].LastTitle (every ~300ms)
  • Detects "BROMIUM_CRX:" prefix
  • Clears signal (sets to "BROMIUM_DOWNLOADING")
  • Runs: ExecuteProcess('/usr/bin/curl',
        '-s -L --compressed -o /tmp/bromium-crx-staging/<ext_id>.crx "<crx_url>"')
        │  (curl runs as external process — CEF cannot intercept)
        ▼
curl downloads CRX to /tmp/bromium-crx-staging/<ext_id>.crx
        │
        ▼
Timer1Timer checks: FileExists + size > 100 bytes
        │
        ▼
InstallCRX() called with crxPath
  • ExecuteProcess('/usr/bin/python3', '~/.local/bin/bromium-crx-install.py <crx_path> <ext_dir>')
  • Python script writes result to /tmp/bromium-crx-install-result.json
  • Pascal reads result, returns extension name
        │
        ▼
LoadExtensions() — reloads the 🧩 extensions menu
Extension is now available in Bromium
```

### CRX3 Binary Format

```
Offset  Size  Field
──────  ────  ─────
0       4     Magic: "Cr24" (0x43 0x72 0x32 0x34)
4       4     Version: 3 (little-endian uint32)
8       4     Header length (little-endian uint32)
12      Hdr   Signed header data (protobuf, HdrLen bytes)
12+Hdr  ∞     ZIP data (standard ZIP archive)
```

The Python script (`bromium-crx-install.py`) handles:
1. Magic+version+header-length validation
2. Skipping the signed header
3. Extracting the ZIP portion into the extensions directory
4. Reading `manifest.json` for the display name

### Button Selector (Important!)

The "Add to Chrome" button on Chrome Web Store does **NOT** have an `action="add"` attribute. It is a plain `<BUTTON>` element with text "Add to Chrome" and auto-generated class names like `UywwFc-LgbsSe UywwFc-LgbsSe-OWXEXe-dgl2H`.

**Working selector** (text-based):
```javascript
Array.from(document.querySelectorAll('button'))
  .find(b => b.textContent.trim() === 'Add to Chrome')
```

**Broken selector** (DO NOT use):
```javascript
document.querySelector('[action="add"]')  // ← does not match anything
```

### Verification

```bash
# 1. Check the CRX was downloaded
ls -la /tmp/bromium-crx-staging/

# 2. Check it was installed
ls /home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/extensions/<ext_id>/

# 3. Check load via IPC
python3 ~/.local/bin/bromium_agent.py --list-extensions

# 4. Verify no OS window opened (ask the user — the only reliable test)
```
