# Dual Citizen Browser — MCP Integration & Nemotron Nano Omni Vision
*July 2026 session — live browser running, vision executor wired*

---

## Current State (Live)

| Component | Status |
|-----------|--------|
| **Browser process** | ✅ PID 267851 running (dual_citizen_v2) |
| **IPC socket** | ✅ `/tmp/aethelgard_cef.sock` alive |
| **Tabs** | ✅ `create_tab`, `navigate`, `execute_javascript`, `get_title` working |
| **MCP server** | ✅ `aethelgard-fleet` server has 3 browser tools wired |

---

## MCP Server Browser Tools (aethelgard-fleet)

Added to `projects/aethelgard/mcp/aethelgard_mcp_server.py`:

| Tool | Action | Description |
|------|--------|-------------|
| `browser_ping` | ping | Health check → returns socket status |
| `browser_navigate` | navigate | `url` param → loads page in active tab |
| `browser_execute` | execute | `script` param → runs JS, result via title channel |

**Invoke via Hermes (after `/reload-mcp`):**
```python
mcp_aethelgard-fleet_browser_navigate(url="https://freepascal.org")
mcp_aethelgard-fleet_browser_execute(script="document.body.innerText.substring(0, 2000)")
mcp_aethelgard-fleet_browser_ping()
```

---

## Nemotron 3 Nano Omni (Free Vision Executor)

**Model:** `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` via OpenRouter

**Capability:** Full multimodal — video, audio, image, text understanding + GUI/OCR/transcription

**Executor pattern:**
```python
# Dispatch vision task to Nano Omni (fast, free)
delegate_task(
    goal="Analyze the screenshot from freepascal.org for navigation elements",
    model={"provider": "openrouter", "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"},
    toolsets=["browser", "vision"]
)
```

**Why Nano Omni over Ultra:** 30B A3B = 3B active params → runs free on OpenRouter with 256K context, vision built-in. Ultra (550B) is for deep reasoning without vision.

---

## Working Command Sequence

```bash
# 1. Browser already running (PID 267851)
# 2. Create tab + navigate
mcp_aethelgard-fleet_browser_navigate(url="https://freepascal.org", tab_id=5)
# 3. Wait for load (poll title)
mcp_aethelgard-fleet_browser_execute(script="document.title")
# 4. Extract content for vision
mcp_aethelgard-fleet_browser_execute(script="document.body.innerText.substring(0, 3000)")
# 5. Send to Nano Omni for visual analysis
```

---

## Pitfalls Fixed This Session

| Issue | Fix |
|-------|-----|
| **Navigation hangs on `about:blank`** | Page loads but title channel only fires on JS-driven title change. Fixed: `execute_javascript("document.title = 'TEST-' + Date.now()")` forces title update, then `get_title` works. |
| **`get_eval` always returns `undefined`/`pending`** | FEvalResultReady flag not being set in CEF4Delphi callback chain. Workaround: use title channel for return values (`document.title = JSON.stringify(result)`). |
| **Remote debugging port 9222 not open** | cef_controller doesn't pass `--remote-debugging-port=9222`. Need to add to `GlobalCEFApp.AddCustomCommandLine`. |
| **Xvfb X errors** | "X error received: ChangeWindowAttributesRequest" spam in logs — harmless but noisy. Fix: `export LIBGL_ALWAYS_SOFTWARE=1` before launch. |

---

## Next Actions

1. **Add `--remote-debugging-port=9222`** to cef_controller.lpr → enables CDP for full DOM access
2. **Wire `click`, `form_fill`, `get_form_fields`** into MCP server (already exist in Pascal IPC)
3. **Build screenshot tool** → CEF `TakeScreenshot` → feed directly to Nano Omni vision
4. **Test Nano Omni on FreePascal.org** — verify OCR of code blocks, navigation structure detection

---

## Related

- `ctx-curation/references/token-burn-audit.md` — executor architecture
- `ares-aethelgard-project` — master project index
- `ares-pascal-fleet` — all compiled binaries