#!/usr/bin/env python3
"""
⎔ Bromium Workflow: Reliable Multi-Page Content Extraction

This script demonstrates the proven pattern for extracting content from
multiple pages through the Bromium browser. Key design decisions:

1. Creates a dedicated tab (isolates from user navigation)
2. Polls title after navigation instead of fixed sleep()
3. Handles async JS eval → title channel readback timing
4. Saves structured JSON with metadata

Usage:
  python3 bromium-workflow-extraction.py [--urls URL_LIST] [--output DIR]

Requirements:
  - Bromium browser must be running (/tmp/aethelgard_cef.sock)
  - ~/.local/bin/bromium_agent.py available
"""

import json
import os
import socket
import sys
import time

SOCKET_PATH = "/tmp/aethelgard_cef.sock"


def sock_cmd(action, timeout=15, **kw):
    """Send command to Bromium IPC socket. Handles Pascal escape sequences."""
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(SOCKET_PATH)
    except OSError as e:
        return {"status": "error", "error": f"Socket connect failed: {e}"}
    payload = json.dumps({"action": action, "id": "1", **kw}).encode() + b"\n"
    s.send(payload)
    resp = b""
    while True:
        try:
            chunk = s.recv(65536)
            if not chunk:
                break
            resp += chunk
        except socket.timeout:
            break
    s.close()
    text = resp.decode("utf-8", errors="replace")
    text = text.replace('\\"', '"')  # Strip Pascal double-escaped quotes
    for i, ch in enumerate(text):
        if ch in ("{", "["):
            try:
                return json.loads(text[i:])
            except json.JSONDecodeError:
                continue
    return {"status": "error", "error": "No valid JSON", "raw": text[:200]}


def navigate_and_wait(url, tab_id=1, max_wait=15):
    """
    Core technique: Navigate and poll title until load completes.

    Never use a fixed sleep() after navigate — page load times vary
    wildly (2-15s depending on JS rendering, CDN, auth redirects).
    Polling the title in a loop is the only reliable approach.
    """
    sock_cmd("navigate", url=url, tab_id=tab_id)
    for _ in range(max_wait):
        time.sleep(1)
        result = sock_cmd("get_title", tab_id=tab_id)
        title = result.get("title", "")
        if title and title != "about:blank" and "BROMIUM_" not in title:
            return title
    return result.get("title", "TIMEOUT")


def extract_page_content(tab_id=1):
    """
    Evaluate JS to extract clean text content, read back via title channel.

    The JS sets document.title to a JSON payload. After a short delay
    (need to let the async callback drain), we read it back with get_title.
    """
    sock_cmd(
        "execute_javascript",
        code="""
(function() {
  // Try common content container selectors
  var el = document.getElementById('mw-content-text') ||
           document.querySelector('#bodyContent .mw-parser-output') ||
           document.querySelector('.content') ||
           document.body;
  var text = el.innerText || el.textContent || '';
  document.title = JSON.stringify({
    url: location.href,
    title: document.title,
    content: text.substring(0, 50000)
  });
})();
""",
        tab_id=tab_id,
    )
    time.sleep(2)  # Allow async callback to fire
    return sock_cmd("get_title", tab_id=tab_id)


def create_tab():
    """Create a new browser tab, return its ID."""
    result = sock_cmd("create_tab")
    tabs = sock_cmd("list_tabs")
    tab_ids = [t.get("tab_id") for t in tabs.get("tabs", []) if t.get("tab_id", 0) > 0]
    return max(tab_ids) if tab_ids else 1


def extract_pages(urls, output_dir, tab_id=None):
    """
    Extract content from multiple URLs through the Bromium browser.

    Args:
        urls: List of (display_name, url) tuples
        output_dir: Directory to save extracted JSON files
        tab_id: Bromium tab ID (creates new if None)

    Returns:
        (success_count, fail_count)
    """
    os.makedirs(output_dir, exist_ok=True)

    if tab_id is None:
        print("Creating dedicated extraction tab...")
        tab_id = create_tab()
        print(f"  Using tab: {tab_id}")

    success = 0
    fail = 0

    for display_name, url in urls:
        safe_name = (
            url.replace("https://", "")
            .replace("/", "_")
            .replace("?", "_")
            .replace("&", "_")
        )[:80]
        outfile = os.path.join(output_dir, f"{safe_name}.json")

        sys.stdout.write(f"[→] {display_name:40s} ... ")
        sys.stdout.flush()

        # Step 1: Navigate and wait
        page_title = navigate_and_wait(url, tab_id)

        # Step 2: Handle empty pages
        if "there is currently no text" in page_title.lower():
            print(f"✗ Empty page: {page_title[:50]}")
            fail += 1
            continue

        # Step 3: Extract content
        content_result = extract_page_content(tab_id)

        # Step 4: Save as structured JSON
        data = content_result.get("title", "{}")
        try:
            parsed = json.loads(data) if isinstance(data, str) else data
            parsed["extracted_url"] = url
            parsed["extracted_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

            with open(outfile, "w") as f:
                json.dump(parsed, f, indent=2, ensure_ascii=False)

            chars = len(parsed.get("content", ""))
            print(f"✓ {chars:>5} chars  [{page_title[:40]}]")
            success += 1
        except (json.JSONDecodeError, TypeError) as e:
            print(f"✗ Parse error: {e}")
            with open(outfile.replace(".json", ".raw.txt"), "w") as f:
                f.write(str(data))
            fail += 1

        time.sleep(1)  # Polite interval

    return success, fail


# ── Example Usage ──────────────────────────────────────────────────────

if __name__ == "__main__":
    # Example: Extract Free Pascal Wiki tutorial pages
    PAGES = [
        ("Introduction", "https://wiki.freepascal.org/Basic_Pascal_Tutorial/Introduction"),
        ("Program Structure", "https://wiki.freepascal.org/Basic_Pascal_Tutorial/Chapter_1/Program_Structure"),
        ("Variables & Data Types", "https://wiki.freepascal.org/Basic_Pascal_Tutorial/Chapter_1/Variables_and_Data_Types"),
        ("IF Statement", "https://wiki.freepascal.org/Basic_Pascal_Tutorial/Chapter_3/IF"),
        ("Procedures", "https://wiki.freepascal.org/Basic_Pascal_Tutorial/Chapter_4/Procedures"),
        ("Arrays", "https://wiki.freepascal.org/Basic_Pascal_Tutorial/Chapter_5/Arrays"),
        ("OOP Introduction", "https://wiki.freepascal.org/Basic_Pascal_Tutorial/Chapter_7/Object_Oriented"),
    ]

    out = os.path.expanduser("~/projects/freepascal-docs/tutorial-extracted")
    ok, fail = extract_pages(PAGES, out)
    print(f"\nDone: {ok} OK, {fail} failed")
    print(f"Output: {out}")
