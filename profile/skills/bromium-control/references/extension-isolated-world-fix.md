# Bromium Extension Isolated World Fix

## Problem

CEF (Chromium Embedded Framework) loads extension content scripts into an **isolated world** — separate JavaScript context from the page's main world. IPC-injected JS (e.g. via `bh eval` or `evaluate_js`) runs in the **main world** and cannot access `window.__aethelgardBridge`, `window.__domScraper`, etc.

## Root Cause

The Pascal binary (`dual-citizen-v2`) does NOT load extensions at all. `ScanExtensions` in the Pascal source only reads extension metadata for the UI menu — it never calls `CefExtension::LoadExtension()` or `CefRequestContext::LoadExtension()`. Searches for `LoadExtension`, `CefExtension`, `RegisterExtension` in the Pascal fleet source return zero matches.

**All 4 custom extensions (aethelgard-bridge, dom-scraper, page-automation, assistive-scanning) have content scripts that are never injected by CEF.**

## Fix: `<script>` Tag Injection into Main World

Each content.js was rewritten to inject a `<script>` element into the DOM, which runs in the main world:

```javascript
(function() {
  'use strict';
  // Prevent double injection
  if (document.querySelector('script[data-bromium="aethelgard-bridge"]')) return;

  const script = document.createElement('script');
  script.setAttribute('data-bromium', 'aethelgard-bridge');
  script.textContent = `
    (function() {
      // This runs in MAIN world — accessible from IPC eval
      window.__aethelgardBridge = {
        version: '2.0',
        // ... API methods
      };
    })();
  `;
  (document.head || document.documentElement).appendChild(script);
})();
```

## Test

```bash
# Verify bridge is visible in main world
bh eval "return typeof window.__aethelgardBridge"
# Should return: "object" (not "undefined")

# Or for dom-scraper
bh eval "return typeof window.__domScraper"
```

## Workaround: `bh-research`

Since extensions aren't loaded, created `bh-research` (`~/.local/bin/bh-research`) as a standalone research injector that:
1. Navigates to the target URL
2. Injects extraction JS directly via IPC (`code` field — not `js`)
3. Extracts all text content
4. Finds all links
5. Takes screenshots (via IPC screenshot command)

Uses the same IPC protocol as `bh` but doesn't depend on any extension being loaded.

## Patched Extensions

All in `~/projects/aethelgard/fleet/pascal/dual-citizen-v2/extensions/`:

| Extension | Fix Date | Technique |
|-----------|----------|-----------|
| aethelgard-bridge/content.js | 2026-07-18 | `<script>` tag + postMessage bridge to extension background |
| dom-scraper/content.js | 2026-07-18 | `<script>` tag injection |
| page-automation/content.js | 2026-07-18 | `<script>` tag injection |
| assistive-scanning/content.js | 2026-07-18 | `<script>` tag injection |

## IPC Protocol Note

The Pascal server expects `code` field (not `js`) in JSON commands sent to `/tmp/aethelgard_cef.sock`. Found via grep: the fleet bus was sending `js` and getting ignored.
