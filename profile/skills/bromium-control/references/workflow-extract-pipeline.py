"""
Bromium Workflow: Multi-Page Content Extraction Pipeline

Demonstrates the recommended pattern for reliable browser-based extraction:
  navigate → poll_for_load → evaluate_js → poll_title → save

"Slow is smooth, smooth is fast" — one verified step at a time.
"""
import json, os, socket, time

SOCKET_PATH = "/tmp/aethelgard_cef.sock"

def sock_cmd(action, timeout=15, **kw):
    """Send command to Bromium IPC socket."""
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect(SOCKET_PATH)
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
    text = text.replace('\\"', '"')  # Strip Pascal double-escaped quotes
    for i, ch in enumerate(text):
        if ch in ('{', '['):
            try: return json.loads(text[i:])
            except: continue
    return {"status": "error", "error": "No valid JSON", "raw": text[:200]}

def navigate_and_wait(url, tab_id=1, max_wait=15):
    """Navigate and wait until page title confirms load."""
    sock_cmd("navigate", url=url, tab_id=tab_id)
    for _ in range(max_wait):
        time.sleep(1)
        result = sock_cmd("get_title", tab_id=tab_id)
        title = result.get("title", "")
        if title and title != "about:blank" and "BROMIUM_" not in title:
            return title
    return result.get("title", "TIMEOUT")

def extract_page(tab_id=1):
    """Extract full page content via JS, read back via title channel."""
    sock_cmd("execute_javascript", code="""
    (function() {
      var el = document.getElementById('mw-content-text') || document.body;
      var text = el.innerText || el.textContent || '';
      document.title = JSON.stringify({
        url: location.href,
        title: document.title,
        content: text.substring(0, 50000)
      });
    })();
    """, tab_id=tab_id)
    time.sleep(2)
    return sock_cmd("get_title", tab_id=tab_id)

# ── Usage example ──
if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://wiki.freepascal.org/Basic_Pascal_Tutorial/Introduction"
    
    print(f"Navigating to: {url}")
    title = navigate_and_wait(url)
    print(f"Loaded: {title[:60]}")
    
    result = extract_page()
    data = json.loads(result.get("title", "{}"))
    
    print(f"Extracted {len(data.get('content', ''))} chars")
    print(f"Preview: {data.get('content', '')[:200]}")
