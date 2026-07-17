# Bromium Portal — Session 3 Feature Reference (Jul 2026)

## Page Elements Tab

A scrollable grid displaying all interactive elements from the current browser page, fetched via `inject_scan_api` + `get_elements` + `get_title` IPC.

**Location:** 5th notebook tab in ~/Desktop/bromium-portal.py

**How it works:**
1. `inject_scan_api` injects `window.__bromiumScan` JS into the page
2. `get_elements` calls `window.__bromiumScan.getElements()` → result stored in document.title
3. `get_title` reads document.title → parsed as JSON → elements rendered in 4-column grid

**Each element shows:** `[index] <tag> text` with color:
- 🔗 Cyan = link (`<a>`)
- 🖱 Green = button/input
- Plain = other interactive

**Actions:**
- Click any element → `click_element` IPC → 2s delay → auto-refresh
- Filter box filters by tag or text
- "Extract Text" saves page text to ~/bromium-extractions/
- "Extract Links" saves links to ~/bromium-extractions/

**SCAN mode integration:** Page element buttons are collected into `_scan_page_items` and included in `_collect_scan_items()` output, so SCAN mode can navigate them.

## Predictive Text Popup

Ctrl+P or toolbar "⌨ Text" button. Tkinter Toplevel with:

- Large input field (14pt font)
- 14 common phrase prediction buttons (the, https://, search for, go to, click, scroll down/up, new tab, back, extract page, hello, yes, no, please)
- Matching predictions highlight green as you type
- "Type & Close" sends text via `type_text` IPC, then closes

## Dwell Click Visual Indicator

When DWELL mode is active, hovering over any button shows a small (100x6px) orange progress bar above it. Bar fills over dwell_delay ms, then fires the click. Widget flashes green briefly on click.

**Implementation:** `_start_dwell()` creates a `Toplevel` with `overrideredirect(True)` and `attributes("-topmost", True)`, positioned above the widget. 10-step animation at `dwell_delay // 10` ms per step.

## Keyboard Shortcuts Added

| Key | Action |
|-----|--------|
| F3 | Refresh page elements |
| F4 | Scan current page |
| Ctrl+P | Predictive text popup |
