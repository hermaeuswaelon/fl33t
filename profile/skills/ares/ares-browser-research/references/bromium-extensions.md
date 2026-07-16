# Bromium Installed Extensions — Reference

Profile path: `/tmp/bromium-profile/Default/Extensions/`
As of: 2026-07-15

## Extension Inventory

| # | ID | Name | Version | Type | Auto-runs |
|---|-----|------|---------|------|-----------|
| 1 | `aabiopennjmopfippagcalmkdjlepdhh` | Better DeepSeek | 0.1.10 | content script | `chat.deepseek.com/*` |
| 2 | `ceacgaccjcomdbnoodjpllihjmeflfmg` | Science Research Assistant | 3.1.3 | popup | — |
| 3 | `liihfcjialakefgidmaadhajjikbjjab` | alphaXiv | 2.4.0 | content script | `arxiv.org/abs/*`, `*.google.com/*`, `duckduckgo.com/*`, `x.com/*` (+100 TLDs) |
| 4 | `ofaokhiedipichpaobibbnahnkdoiiah` | Instant Data Scraper | 1.6.0 | content script | `*://*/*` |
| 5 | `okngcalljddikhljpfhgmikklmmmdkkd` | Agent OS | 3.2.0 | popup | — |
| 6 | `ihdobppgelceaoeojmhpmbnaljhhmhlc` | Spoof Geolocation | 0.3.1 | — | — |
| 7 | `hnmpcagpplmpfojmgmnngilcnanddlhb` | *(locale key: wsext)* | 4.2.8 | — | — |
| 8 | `bbfnidnhpngjjbmmlakaogggmdnnjbnm` | *(locale key)* | 0.6.2 | content script | `<all_urls>` |
| 9 | `bfaoaaogfcgomkjfbmfepbiijmciinjl` | *(locale key)* | 0.11.27 | content script | `<all_urls>` (×2) |
| 10 | `cgenfommofedogdmkmjdndijcilplkmg` | *(locale key)* | 1.6.16 | content script | `<all_urls>`, `getvm.io` |
| 11 | `pmaonbjcobmgkemldgcedmpbmmncpbgi` | *(locale key)* | 1.3.5 | — | — |

## Extension IDs by Purpose

| Purpose | Extension |
|---------|-----------|
| DeepSeek research | `aabiopennjmopfippagcalmkdjlepdhh` (Better DeepSeek) |
| ArXiv research + search | `liihfcjialakefgidmaadhajjikbjjab` (alphaXiv) |
| General web scraping | `ofaokhiedipichpaobibbnahnkdoiiah` (Instant Data Scraper) |
| Scientific research | `ceacgaccjcomdbnoodjpllihjmeflfmg` (Science Research Assistant) |
| AI browser automation | `okngcalljddikhljpfhgmikklmmmdkkd` (Agent OS) |
| Location spoofing | `ihdobppgelceaoeojmhpmbnaljhhmhlc` (Spoof Geolocation) |

## Communication Methods

### Content Script Extensions (auto-run)
Extensions with `content_scripts` in manifest.json run automatically on matched URLs. No interaction needed — they inject their UI into the page DOM.

**Better DeepSeek** → auto-injects on `chat.deepseek.com/*` — enhances the chat UI with model selection, prompt templates, etc.
**alphaXiv** → auto-injects on `arxiv.org/abs/*` — adds discussion links, PDF viewer, etc.
**Instant Data Scraper** → auto-injects on `*://*/*` — adds a floating toolbar for scraping tables/lists.

### Popup Extensions (no toolbar UI)
Extensions like **Agent OS** and **Science Research Assistant** normally show a popup when clicked. Since Bromium has no toolbar, interact with them via `chrome.runtime.sendMessage()`:

```python
execute_js(f"""
  chrome.runtime.sendMessage('{extension_id}', {{
    action: 'query',
    text: '...'
  }}, response => {{
    console.log('Extension response:', response);
  }});
""")
```

### Manual Control via CDP
If CDP port 9224 is active, connect to the extension's background page and evaluate JS directly:

```python
targets = cdp_get_targets()
ext_target = [t for t in targets if 'extension' in t.get('url','').lower()]
cdp_evaluate(ext_target[0]['id'], '...JS...')
```

## Re-installing Extensions

If the profile is deleted and extensions need re-installation:
1. Navigate to `chrome-extension://<id>` for each extension
2. Or use `chrome.webstore.install()` via injected JS
3. Or place unpacked extension folders in `extensions/` directory

Location for unpacked extensions:
```bash
/home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/extensions/
```

Each extension folder must have a `manifest.json` at the root.
