# ⎔ Bromium Red Team Suite — CEF-Level Reconnaissance

## Purpose

Exploits Bromium's CEF4Delphi architecture for reconnaissance that normal headless
browsers cannot perform:

- **Hidden element discovery** — finds `display:none`, `visibility:hidden`, zero-size,
  and opacity-0 elements that standard DOM serializers skip.
- **Cross-tab storage dump** — single-IPC sweep of every open tab's localStorage,
  sessionStorage, and document.cookie simultaneously.
- **Network interceptor** — wraps `fetch()` and `XMLHttpRequest` at the CEF level
  to capture all outbound requests after the hook is installed.
- **Native CEF clicks** — bypasses JS event-handler blocking (anti-bot protection,
  overlay modals, disabled pseudo-classes) by sending real mouse events.
- **Full rendered page snapshot** — captures XHR/fetch-loaded content that standard
  "view source" misses.

## Location

```
~/projects/aethelgard/fleet/tools/bromium_redteam.py
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `scan` | Full reconnaissance sweep across all open tabs → JSON + MD report |
| `dom-sniff [tab]` | Enumerate ALL elements, categorize hidden/zero-size |
| `extract-creds` | Dump localStorage/sessionStorage/cookies from all tabs |
| `snapshot` | Capture full page text + element counts from every tab |
| `interceptor <tab> install\|dump` | Install fetch/XHR interceptor or retrieve captured log |
| `click <x> <y> [tab] [depth]` | Native CEF click; depth > 0 re-scans DOM after click for newly revealed elements |
| `health` | Socket connectivity check + tab listing |
| `report` | Re-generate markdown report from last cached JSON |

## Output Directory

All results saved to `~/bromium-extractions/`:
- `redteam-<timestamp>.json` — full structured report
- `redteam-report-<timestamp>.md` — human-readable summary
- `redteam-dom-sniff-tabN-<timestamp>.json` — per-tab DOM enumeration
- `redteam-creds-<timestamp>.json` — credential sweep
- `redteam-snapshots-<timestamp>.json` — tab snapshots
- `redteam-snapshot-tabN-<timestamp>.txt` — full page text

## Fleet Integration

Wired into `bromium.sh` as:
```bash
bromium.sh redteam            # Full scan
bromium.sh redteam-dom [N]    # DOM sniff on tab N (default 2)
bromium.sh redteam-creds      # Extract credentials all tabs
bromium.sh redteam-snapshot   # Snapshot all tabs
bromium.sh redteam-interceptor [tab] [install|dump]
```

## Architecture

The suite is built on the same `_sock()` IPC layer as `bromium_agent.py`.
Each module is a pure Python function that:

1. Constructs a JavaScript payload (inline, no dependency on `__bromiumScan` API)
2. Sends it via `execute_javascript` IPC
3. Reads the result via the `__bromium_rt` private variable (two-call pattern)
4. Parses and categorizes the data client-side

## IPC Protocol Notes Specific to This Suite

- Uses `js_eval()` (the `window.__bromium_rt` two-call pattern) for ALL data
  retrieval to avoid title-channel collision with `get_page_text()`.
- The `_sock()` parser does NOT use `.replace('\\"', '"')` — that destroys
  JSON with embedded escaped quotes (e.g. tab titles containing JSON).
  Instead it tries `json.loads()` directly, then falls back to scanning
  for the first `{` or `[` character.
- JS enumeration wraps each element in `try/catch` because `getComputedStyle()`
  throws on detached nodes.

## Known Issues

- `extract-creds` fails against `data:` URIs with inline `<script>` tags
  because navigation overwrites the title channel before the eval completes.
  Workaround: navigate to an `https://` page with localStorage content instead.
- `js_eval_title()` → `js_eval_title_raw()` rename created two stale references
  at approx lines 152 and 460 in `bromium_redteam.py`. They need to be updated
  when the function is called again.
- Large DOM trees (>500 elements) may hit CEF's `document.title` length limit
  (~8KB). The `__bromium_rt` pattern avoids this by writing to a JavaScript
  variable instead, but the second read-back call still uses `document.title`.
  For very large payloads, chunk the export.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-17 | Initial build: dom_sniff, extract_creds, snapshot, interceptor, native_click |
