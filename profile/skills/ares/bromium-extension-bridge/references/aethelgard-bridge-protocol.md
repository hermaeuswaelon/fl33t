# Aethelgard Bridge — Message Protocol Reference

## Architecture

```
┌──────────────┐  chrome.runtime.connect   ┌───────────────┐
│  Page Context │ ◄──────────────────────► │  Background   │
│  (content.js) │   'aethelgard-bridge'    │  Service Worker│
│              │                          │  (background.js)│
│ window.      │  AGENT_TO_EXTENSION      │               │
│ __aethelgard │ ──────────────────────►  │ chrome.tabs   │
│ Bridge       │  {command, commandId,    │ chrome.       │
│              │   ...payload}            │ storage       │
│              │                          │ chrome.       │
│              │  EXTENSION_TO_AGENT       │ scripting     │
│              │ ◄──────────────────────  │               │
│              │  {commandId, payload}    │ fleet bus     │
└──────────────┘                          └───────────────┘
       │                                          │
       │ window.__aethelgardBridge                │ chrome.runtime.onConnect
       │ .send(cmd, payload)                      │ chrome.runtime.onMessage
       │ .then(result)                            │
       ▼                                          ▼
  Agent IPC Socket                     Popup UI (popup.html)
  (execute_javascript)                 (GET_STATE, PING_BUS)
```

## Message Types

### content.js → background.js (via `port.postMessage`)

| type | Direction | Payload |
|------|-----------|---------|
| `AGENT_TO_EXTENSION` | content → bg | `{command, commandId, ...args}` |
| `PAGE_STATE` | content → bg | `{url, title}` |
| `EVAL_RESULT` | content → bg | `{result, commandId}` |

### background.js → content.js (via `port.postMessage`)

| type | Direction | Payload |
|------|-----------|---------|
| `EXTENSION_TO_AGENT` | bg → content | `{commandId, payload}` |

### popup ↔ background (via `chrome.runtime.sendMessage`)

| type | Direction | Payload / Response |
|------|-----------|--------------------|
| `GET_STATE` | popup → bg | response: `{activeTabs[], busConnected, uptime}` |
| `PING_BUS` | popup → bg | response: `{connected}` |

## Bridge Commands (via `b.send(command, payload)`)

| Command | Args | Background handler |
|---------|------|-------------------|
| `ping` | — | Returns `{version, tabs: n, busConnected}` |
| `get_all_tabs` | — | `chrome.tabs.query({})` |
| `activate_tab` | `{tabId}` | `chrome.tabs.update(tabId, {active: true})` |
| `get_page_source` | — | `document.documentElement.outerHTML` via scripting |
| `get_storage` | `{key?}` | `chrome.storage.local.get(key)` |
| `set_storage` | `{data}` | `chrome.storage.local.set(data)` |
| `inject_script` | `{code}` | `chrome.scripting.executeScript({func: new Function(code), world: 'MAIN'})` |

## Page-Level API

The content script exposes two objects on `window`:

- **`window.__aethelgardBridge`** — Direct bridge to extension background
  - `bridge.send(command, payload)` → Promise
  - `bridge.isConnected()` → bool
  - `bridge.status()` → `{connected, url, title, pending}`

- **`window.__aethelgard`** — Web-accessible convenience wrapper (from `inject.js`)
  - `__aethelgard.send(command, payload)` → Promise
  - `__aethelgard.ping()` → shortcut
  - `__aethelgard.getTabs()` → shortcut
  - `__aethelgard.ready()` → bool

## CDP (DevTools Protocol) Fallback

When `extension_bridge` IPC is unavailable or you need to reach the background page directly:

```bash
# 1. List all targets (includes extension service workers)
curl -s http://127.0.0.1:9224/json/list | jq '.[] | select(.type == "service_worker" or .type == "background_page")'

# 2. Connect to the target's WebSocket and send CDP command
# ws_url from the list output
# Use a CDP client to call Runtime.evaluate with:
#   expression: "chrome.runtime.sendMessage({type:'PING'}, console.log)"
```

## Extension Lifecycle

| Event | What happens |
|-------|-------------|
| Extension loaded | `--load-extension` at CEF startup. `background.js` connects to fleet bus. |
| Content script injected | Every page load. `content.js` establishes `chrome.runtime.connect`. |
| Bridge connected | `onConnect` in background, tab added to `activeConnections`. |
| Bridge disconnected | `onDisconnect` in background, tab removed from state. |
| Tab navigated | Content script re-injects on new page. New bridge connection established. |
| Popup opened | `GET_STATE` message, displays active tabs, bus status, uptime. |
