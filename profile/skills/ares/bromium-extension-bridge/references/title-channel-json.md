# Title Channel JSON Unescaping

## The Problem

The Pascal IPC handler returns JSON responses that contain Pascal-escaped double quotes (`\"`) inside string values. When the title channel carries nested JSON (e.g. after `inject_scan_api` sets `document.title = JSON.stringify({status:"injected"})`), the raw IPC response looks like:

```
{"id":"1","status":"ok","title":"{\"status\":\"injected\"}"}
```

Blindly replacing all `\"` with `"` produces invalid JSON:

```
{"id":"1","status":"ok","title":"{"status":"injected"}"}
```

This breaks `json.loads()` because the outer `title` string value is now unescaped.

## The Fix: Try Raw First, Only Unescape on Failure

```python
def parse_ipc_response(raw_text):
    def _try(s):
        try: return json.loads(s)
        except: return None
    # Try raw first — works when title is plain text
    parsed = _try(raw_text)
    if parsed is not None:
        return parsed
    
    # Fallback: Pascal sent \" for inner quotes
    cleaned = raw_text.replace('\\"', '"')
    for i, ch in enumerate(cleaned):
        if ch in ('{', '['):
            try: return json.loads(cleaned[i:])
            except: continue
    return {"error": "parse failed", "raw": raw_text[:200]}
```

## Reproduction

```
Raw response: {"id":"1","status":"ok","title":"{\"status\":\"injected\"}"}

After correct parse:
  {"id": "1", "status": "ok", "title": "{"status": "injected"}"}
  → parsed["title"] → '{"status":"injected"}'
  → json.loads(parsed["title"]) → {"status": "injected"}

After wrong unescape-first:
  {"id":"1","status":"ok","title":"{"status":"injected"}"}
  → json.loads() → JSONDecodeError (title string value is unescaped)
```

## All Affected IPC Commands

All commands that return `"method":"title_channel"` or set `document.title` asynchronously are affected:

- `execute_javascript` — JS code sets `document.title`, read with `get_title`
- `inject_scan_api` — returns `{"status":"injected"}` in title
- `get_elements` — returns `{"elements":[...]}` in title
- `get_page_text` — returns `{"text":"...","length":N}` in title
- `click_element` — returns `{"success":true,"tag":"a"}` in title
- `extension_bridge` — returns bridge response in title
- `evaluate_js` — returns wrapped eval result in title
