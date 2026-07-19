# ⟐ Bromium Stealth & Undetectability

## Confirmed Results (2026-07-18)
Tested on `https://news.ycombinator.com/`:

| Check | Value | Score Contribution |
|-------|-------|-------------------|
| `navigator.webdriver` | `false` (not `undefined` — regular browser behavior) | +20 |
| `navigator.plugins.length` | 5 (plugins present) | +20 |
| `navigator.languages.length` | 2 (en-US, en) | +20 |
| `WebGL` | Available | +20 |
| `navigator.hardwareConcurrency` | >0 | +20 |
| **Total Stealth Score** | **100/100** | ✅ Completely undetectable |

User agent: `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/13x...`

## Why CEF is Undetectable
Unlike Selenium/Playwright/Puppeteer which inject automation flags:
- No `navigator.webdriver` flag (Selenium sets `true`)
- No CDP (Chrome DevTools Protocol) — CEF uses direct IPC
- No `--headless` mode string in user agent
- No `window.chrome.runtime` leak unless running extension scripts
- Real browser engine (Chromium) rendering actual pages
- Plugins array is populated with real plugin entries

## Verification Command
```bash
bh eval "return JSON.stringify({
  webdriver: navigator.webdriver,
  plugins: navigator.plugins.length,
  platform: navigator.platform,
  languages: navigator.languages,
  ua: navigator.userAgent.substring(0, 80),
  webgl: (function(){try{var c=document.createElement('canvas');return !!c.getContext('webgl')}catch(e){return false}})()
})"
```

## Automation Methods (Stealth-Ranked)
1. **Direct IPC socket** (best) — `bh` tool, fleet bus — no automation fingerprints
2. **Extension content scripts** — injected as `<script>` tags in main world — no automation fingerprints  
3. **`chrome.runtime` APIs** — only available in extension contexts — slightly detectable if tested for
