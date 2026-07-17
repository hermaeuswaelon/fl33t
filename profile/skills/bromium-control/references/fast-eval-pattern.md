# Fast Eval Pattern + IPC JSON Parsing — Bromium Suite

## The Problem

The old pattern for reading JS results from Bromium was:

```python
sock_cmd("execute_javascript", code=some_js, tab_id=1)
time.sleep(2)  # fixed sleep — brittle and slow
result = sock_cmd("get_title", tab_id=1)
```

This took ~3500ms per read cycle and broke when pages loaded faster or slower than 2 seconds.

## The Solution: `get_eval` + 50ms Polling

### Pascal Side (ucontrollerbrowser.pas)

`ExecuteJS` (line 387) now resets `FEvalResultReady := False` before executing JavaScript:

```pascal
procedure TControllerForm.ExecuteJS(const code: string; TabId: Integer = -1);
begin
  // ...
  FEvalResultReady := False;  // ← KEY LINE (added July 2026)
  browser.MainFrame.ExecuteJavaScript(code, '', 0);
end;
```

This makes `DoTitleChange` (line 1347) store the next `document.title` change in `FEvalResult`:

```pascal
if not FEvalResultReady then
begin
  FEvalResult := title;
  FEvalResultReady := True;
end;
```

The `get_eval` IPC (line 821) reads `FEvalResult`:

```pascal
else if cmdAction = 'get_eval' then
begin
  if FEvalResultReady then
  begin
    response := Format('{"id":"%s","status":"ok","result":"%s"}', [cmdId, EncodeJSON(FEvalResult)]);
    FEvalResultReady := False;
    FEvalResult := '';
  end
  else
    response := Format('{"id":"%s","status":"pending","result":""}', [cmdId]);
  SendReply(ReplySock, response);
end;
```

**Critical detail:** `FEvalResult` stores the FIRST title change after `FEvalResultReady` is reset. If you call `execute_javascript` twice without reading `get_eval` in between, the second call's result overwrites the first.

### Python Side

```python
def fast_eval(code, tab_id=1, max_polls=40):
    """Execute JS and poll get_eval at 50ms intervals.
    Typical return time: 0-150ms (1-3 polls).
    Returns parsed JSON (if result is valid JSON) or raw string."""
    sock_cmd("execute_javascript", code=code, tab_id=tab_id)
    for _ in range(max_polls):        # ~2s total timeout
        r = sock_cmd("get_eval", tab_id=tab_id)
        if r.get("status") == "ok":
            raw = r.get("result", "")
            if raw:
                try:
                    return json.loads(raw)   # result is JSON string
                except:
                    return raw                # plain string result
        time.sleep(0.05)
    return None
```

## IPC JSON Parsing: Two Escaping Patterns

Bromium's Pascal backend sends JSON with **two different escaping conventions**. This is a historical artifact — some IPC handlers were written with `Format('\"...\"', [...])` and others with `Format('\\\"...\\\"', [...])`.

### Pattern A: Standard IPC (most commands)

Used by: `navigate`, `get_title`, `scroll_by`, `set_zoom`, `get_eval`, `go_back`, `go_forward`, `execute_javascript`, `type_text`, `click_element`, `get_elements`, `get_page_text`, `inject_scan_api`, `clear_cache`, `set_zoom`, `create_tab`, `close_tab`, `activate_tab`, `status`, `get_url`

**Escaping:** Standard JSON `\"` (backslash-quote).

**Response example:**
```
{"id":"1","status":"ok","title":"Example Domain"}
```

**Parsing:** `json.loads(raw_text)` works directly.

### Pattern B: List/Array IPC (deprecated style)

Used by: `list_extensions` (and potentially any IPC using `Format('\\\"...\\\"', [...])` in the Pascal source).

**Escaping:** Pascal `\\\"` (double backslash + quote). The Pascal source uses `'\\\"'` which is a literal backslash character followed by a quote character in the Pascal string. When Format substitutes this, the result has actual `\"` bytes in the output.

**Response example:**
```
{\"id\":\"1\",\"status\":\"ok\",\"extensions\":[...]}
```

Note: the `\\` in the Python `repr()` would show as `\\\"` (escaped backslash + quote).

**Parsing:** `json.loads(raw_text)` FAILS on this because the outer quotes are escaped. Must unescape first.

### Safe Universal Parser

```python
def parse_ipc(raw_text):
    """Parse any Bromium IPC response, handling both escaping patterns."""
    # Try raw first (Pattern A — most common)
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass
    
    # Fallback: unescape Pascal \\\" → " and scan for first JSON object
    t = raw_text.replace('\\"', '"')
    for i, ch in enumerate(t):
        if ch in ('{', '['):
            try:
                return json.loads(t[i:])
            except json.JSONDecodeError:
                continue
    
    return {"error": "parse_failed", "raw": raw_text[:200]}
```

This is the pattern used in `bromium_agent.py`'s `sock_cmd()`.

### Debugging Tip

When a new IPC endpoint returns unparseable JSON, check the raw hex:
```python
response_bytes = s.recv(65536)  # raw bytes before decode
print(response_bytes[:100].hex())
# Look for 5C 22 (backslash-quote) vs 5C 5C 22 (backslash-backslash-quote)
```

## Element Extraction: Two Approaches

### Approach 1: Auto-injected scan API (requires DoLoadEnd fix)

The scan API is injected by `DoLoadEnd` in `ucontrollerbrowser.pas`:
```javascript
window.__bromiumScan = {
  getElements: function() { ... returns unsorted array },
  getPageText: function(max) { ... },
}
```

Usage:
```python
result = fast_eval(
    "document.title=JSON.stringify(window.__bromiumScan.getElements())",
    tab_id=1)
```

**Risk:** The Pascal string concatenation can introduce JS syntax errors. The `getElements` return uses `return e.forEach(...), r` which relies on the comma operator — if the Pascal string breaks this pattern, `getElements` silently returns `undefined`.

### Approach 2: Direct querySelectorAll (recommended)

No dependency on auto-injection or Pascal string concatenation:
```python
result = fast_eval('''
document.title=JSON.stringify(
(function(){
  var e=document.querySelectorAll("a[href],button,input:not([type=hidden]),select,textarea");
  return Array.from(e).map(function(n,i){
    var b=n.getBoundingClientRect();
    if(b.width<4||b.height<4)return null;
    var t=n.textContent.trim().substring(0,80)||n.placeholder||n.title||"";
    return{id:i,tag:n.tagName.toLowerCase(),text:t,
      href:n.href||"",
      bounds:{top:b.top|0,left:b.left|0,width:b.width|0,height:b.height|0},
      center:{x:(b.left+b.width/2)|0,y:(b.top+b.height/2)|0}}
  }).filter(function(e){return e!==null})
})()
)''', tab_id=1)
```

**Always safe, same speed, no Pascal escaping issues.**

## Page Text Extraction

```python
result = fast_eval('''
document.title=JSON.stringify(
(function(){
  var c=document.body.cloneNode(true);
  c.querySelectorAll("script,style,noscript,svg,canvas,iframe").forEach(function(s){s.remove()});
  return (c.textContent||"").replace(/\\s+/g," ").trim().substring(0,50000);
})()
)''', tab_id=1)
# result is a string of up to 50000 chars
```
