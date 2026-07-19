# Vision-Guided Click Pipeline — LFM2-VL + Bromium

## Service Stack

| Service | Port/PID | API Key | Purpose |
|---------|----------|---------|---------|
| Bromium socket | `/tmp/aethelgard_cef.sock` | none | Browser IPC |
| LFM2-VL (hermes-vl) | 127.0.0.1:8086 | `vl-local-key` | Vision analysis |
| LFM2.6B (hermes-lfm26) | 127.0.0.1:8080 | `nous-research` | Text planning |
| Bromium CDP | 127.0.0.1:9224 | none | DevTools (may be disabled) |

## Quick Test

```bash
# 1. Navigate browser
python3 ~/.local/bin/bromium_agent.py --navigate "https://example.com" --tab 1

# 2. Get elements with bounding boxes
python3 ~/.local/bin/bromium_agent.py --get-elements --tab 1

# 3. Click element 0
python3 ~/.local/bin/bromium_agent.py --click-element 0 --tab 1

# Or native click at pixel coords (bypasses JS)
python3 -c "
import socket, json
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(8)
s.connect('/tmp/aethelgard_cef.sock')
s.sendall(json.dumps({'action':'native_click','x':398,'y':180,'tab_id':1,'id':'1'}).encode()+b'\n')
import time; time.sleep(1)
data = s.recv(4096)
print(data.decode()[:500])
s.close()
"

# 4. Check VL model responds
curl -s http://127.0.0.1:8086/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer vl-local-key" \
  -d '{"model":"lfm2-vl","messages":[{"role":"user","content":"ping"}],"max_tokens":10}'
```

## DOM Bot Pattern (preferred)

```python
import socket, json, time

SOCK = '/tmp/aethelgard_cef.sock'

def sock_cmd(action, **kw):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(15)
    s.connect(SOCK)
    payload = json.dumps({"action": action, "id": "1", **kw}).encode() + b"\n"
    s.send(payload)
    resp = b""
    while True:
        try:
            chunk = s.recv(65536)
            if not chunk: break
            resp += chunk
        except socket.timeout: break
    s.close()
    text = resp.decode("utf-8", errors="replace")
    try: return json.loads(text)
    except: return {"raw": text[:200]}

# Navigate
sock_cmd("navigate", url="https://chat.deepseek.com", tab_id=1)
time.sleep(4)

# Get elements
sock_cmd("get_elements", tab_id=1)
time.sleep(2)
# Read result from title channel:
result = sock_cmd("get_title", tab_id=1)
# result["title"] contains JSON with elements array

# Click at specific element center
sock_cmd("native_click", x=398, y=180, tab_id=1)

# Type text
sock_cmd("type_text", text="Hello world", tab_id=1)
```

## Vision Pipeline (full autonomous loop)

```
1. LFM2.6B (8080) receives goal → plans steps
2. For each step:
   a. Screenshot via Bromium JS or CDP
   b. LFM2-VL (8086) analyzes screenshot → identifies element + coords
   c. Bromium native_click at coords
   d. Read page state → loop
3. Report completion
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Socket connects but empty response | CEF still processing | Add `time.sleep(1-2)` before recv |
| `get_elements` returns login page | Site requires auth | Navigate to public URL or handle login |
| VL model gibberish/no coords | 320M model limited accuracy | Use DOM path as fallback |
| `native_click` misses target | Zoom ≠ 1.0, scroll offset | Get bounds from get_elements, account for scroll |
| CDP 9224 unreachable | CEF config no `--remote-debugging-port` | Use IPC socket instead |
