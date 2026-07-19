# ⟐ Bromium Content Script Isolated World Bridge

## Problem
CEF loads Chrome extension content scripts into an **isolated JavaScript world**. 
When IPC-injected JS runs via `execute_javascript` or `evaluate_js` (which execute in the 
**main page world**), it cannot access `window.__aethelgardBridge`, `window.__domScraper`, 
`window.__pageAutomation`, or `window.__bromiumScan` — even though the content script 
defines them. This is because content script `window` ≠ page `window`.

Chrome extension content scripts run in a separate V8 context (ISOLATED_WORLD).
The page's JavaScript and CEF IPC-injected JS run in the MAIN world.
Properties set on `window` in one world are NOT visible in the other.

## Fix Pattern — `<script>` Tag Injection
The content script creates a `<script>` element with the API code as `textContent`.
This script runs in the MAIN world, making the API visible to IPC-injected JS.

```javascript
// In content.js (isolated world):
(function() {
  'use strict';
  if (document.querySelector('script[data-my-extension]')) return;

  const script = document.createElement('script');
  script.setAttribute('data-my-extension', '');
  script.textContent = `
(function() {
  // This code runs in MAIN world
  if (window.__myAPI) return;
  const api = { ... };
  Object.defineProperty(window, '__myAPI', {value: api, writable: false});
  window.dispatchEvent(new Event('myAPIReady'));
})();
`;
  document.documentElement.appendChild(script);
})();
```

## Extensions Fixed (2026-07-18)
| Extension | Script Tag | PostMessage Bridge | Status |
|-----------|-----------|-------------------|--------|
| aethelgard-bridge | ✅ | ✅ (talks to background.js) | Verified |
| dom-scraper | ✅ | ❌ (pure DOM ops, no ext API needed) | Verified |
| page-automation | ✅ | ❌ (pure DOM ops) | Verified |
| assistive-scanning | ✅ | ❌ (pure DOM ops) | Verified |

## Verification
After navigating to a page (triggers content script re-injection):
```bash
bh eval "return typeof window.__aethelgardBridge"   # → "object"
bh eval "return typeof window.__domScraper"           # → "object"
bh eval "return typeof window.__bromiumScan"          # → "object"
```

## Key Insight
Extension `manifest.json` and `background.js` are loaded ONCE at browser startup.
But **content scripts** are re-injected on each page navigation from the file on disk.
So updating `content.js` and then navigating to a new page applies the fix immediately —
no browser restart needed.
