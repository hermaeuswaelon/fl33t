# Bromium Bridge — Socket-Driven Extension & Site Control

## File
`work/bromium_bridge.py` — unified Python CLI for driving Bromium and talking to its extensions.

## Why it exists
Bromium's extensions have no visible UI/menu to click. The bridge fills the gap by:
1. Using the Unix socket for navigation + JS execution (existing protocol)
2. Injecting `chrome.runtime.sendMessage()` calls via `execute_javascript` to reach extensions
3. Using CDP (port 9224) for extension background-page debugging

## Commands
| Command | What it does |
|---------|-------------|
| `navigate <url>` | Load URL in Bromium |
| `title` | Get current page title |
| `text` | Extract page body text |
| `js <code>` | Execute arbitrary JS |
| `browse <site>` | Open Reddit, Facebook, LinkedIn, Craigslist, DeepSeek, GitHub, X |
| `search <site> <query>` | Search Reddit/Craigslist/LinkedIn/GitHub/X |
| `deepresearch <query>` | Go to chat.deepseek.com, type query, hit send |
| `ext <extension_id> --action <action>` | Send message to an extension via chrome.runtime |
| `ext-list` | List installed extensions (from extensions/ dir or via CDP) |

## Extension communication
```python
# From any page, inject this JS to talk to extensions:
result = execute_js("""
  chrome.runtime.sendMessage('ext-id', {action: 'query', text: '...'})
""")
```

## CDP extension debugging
Bromium's CDP port is 9224. Extensions appear as CDP targets:
```bash
curl http://127.0.0.1:9224/json/list  # Lists all targets including extensions
```

## Social site patterns
Each `/reddit`, `/facebook`, `/linkedin`, `/craigslist` command follows the same pattern:
1. Navigate to site URL via socket
2. Wait for page load
3. Execute JS to interact (search box, login form, etc.)
4. Extract results
See `bromium_bridge.py browse_site()` for the implementation.

## Pitfalls
- `chrome.runtime.sendMessage()` from page context only works if extension declares `externally_connectable` in manifest.json. Otherwise use CDP to reach the background page directly.
- BetterDeepSeek extension works on chat.deepseek.com and handles the response rendering — bridge only needs to submit the query.
- Socket commands are fire-and-forget for navigation; poll `title` or inject JS to detect page load completion.
