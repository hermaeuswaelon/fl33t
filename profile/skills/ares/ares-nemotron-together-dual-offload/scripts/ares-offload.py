#!/usr/bin/env python3
"""
ARES Offloader Alpha — Tool Context Compression
=================================================
Takes tool output (stdin or file) and compresses it via Nemotron Nano Omni 30B.
Target: 90% reduction while preserving key findings.

Usage:
  cat large_output.json | ./ares-offload.py
  ./ares-offload.py some_file.txt
  echo "query: ..." | ./ares-offload.py --query "What did the tool do?"
"""

import os
import sys
import json
import urllib.request
import urllib.error

# ARES Shared Memory — auto-store compressed results
import sys
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)
try:
    from ares_memory import MemoryVault
    _vault = MemoryVault()
except ImportError:
    _vault = None

# ── Configuration ──────────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_INPUT_CHARS = 100_000  # truncate input to avoid blowing context
PARAM_STATE = os.path.expanduser("~/.ares-param-state.json")

# Load profile parameters if available
PROFILE_PARAMS = {"temperature": 0.1, "max_tokens": 2048}
try:
    if os.path.exists(PARAM_STATE):
        with open(PARAM_STATE) as _f:
            _s = json.load(_f)
        _profile = _s.get("profile", "PRIME")
        # Apply decay for effective params
        _custom = _s.get("custom", {})
        _tokens = _s.get("tokens_accumulated", 0)
        _decay = _s.get("decay", True)
        # Use base params (skip full decay interpolation for tool calls)
        if _profile in ("PRIME", "PRECISION", "EXPLORATORY", "SURGICAL", "ORACULAR", "COUNTERMEASURE", "CUSTOM"):
            _profiles = {
                "PRIME": {"temperature": 0.73, "top_p": 0.91, "top_k": 47, "frequency_penalty": 0.23, "presence_penalty": 0.11},
                "PRECISION": {"temperature": 0.23, "top_p": 0.84, "top_k": 13, "frequency_penalty": 0.47, "presence_penalty": 0.07},
                "EXPLORATORY": {"temperature": 0.97, "top_p": 0.97, "top_k": 89, "frequency_penalty": 0.13, "presence_penalty": 0.23},
                "SURGICAL": {"temperature": 0.07, "top_p": 0.73, "top_k": 7, "frequency_penalty": 0.61, "presence_penalty": 0.03},
                "ORACULAR": {"temperature": 1.13, "top_p": 0.99, "top_k": 111, "frequency_penalty": 0.07, "presence_penalty": 0.31},
                "COUNTERMEASURE": {"temperature": 0.47, "top_p": 0.67, "top_k": 23, "frequency_penalty": 0.79, "presence_penalty": 0.47},
            }
            _base = _profiles.get(_profile, {}).copy()
            _base.update(_custom)
            # Override tool-specific defaults with profile values
            PROFILE_PARAMS["temperature"] = _base.get("temperature", 0.1)
            PROFILE_PARAMS["top_p"] = _base.get("top_p")
            PROFILE_PARAMS["top_k"] = _base.get("top_k")
            PROFILE_PARAMS["frequency_penalty"] = _base.get("frequency_penalty")
            PROFILE_PARAMS["presence_penalty"] = _base.get("presence_penalty")
            PROFILE_PARAMS["profile"] = _profile
except Exception:
    pass
# ───────────────────────────────────────────────────────────────────────────


def load_input() -> str:
    """Read input from file argument or stdin."""
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        path = sys.argv[1]
        with open(path, "r") as f:
            return f.read()
    return sys.stdin.read()


def parse_args() -> tuple[str, str]:
    """Extract optional query from --query flag."""
    raw = load_input()
    query = ""
    for i, arg in enumerate(sys.argv):
        if arg == "--query" and i + 1 < len(sys.argv):
            query = sys.argv[i + 1]
    return raw, query


def compress(text: str, query: str = "") -> str:
    """Send tool output to Nemotron Nano Omni for compression."""
    if not OPENROUTER_API_KEY:
        return "ERROR: OPENROUTER_API_KEY not set. Export it first."

    if len(text) > MAX_INPUT_CHARS:
        text = text[:MAX_INPUT_CHARS] + f"\n\n[... truncated at {MAX_INPUT_CHARS} chars]"

    system_prompt = (
        "You are ARES Offloader Alpha. Your sole purpose is to compress tool output.\n"
        "Rules:\n"
        "1. Reduce input by ~90% — keep only what matters\n"
        "2. Preserve: what was asked → what was returned → key findings → errors\n"
        "3. Output pure facts — no commentary, no greetings\n"
        "4. Use concise bullet points\n"
        "5. If the output is already short, pass it through unchanged"
    )

    user_message = f"Tool output to compress:\n```\n{text}\n```"
    if query:
        user_message = f"Query/context: {query}\n\n{user_message}"

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": PROFILE_PARAMS.get("max_tokens", 2048),
        "temperature": PROFILE_PARAMS.get("temperature", 0.1),
    }
    # Add optional params only if set by profile
    for k in ["top_p", "top_k", "frequency_penalty", "presence_penalty"]:
        v = PROFILE_PARAMS.get(k)
        if v is not None:
            payload[k] = v

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ARES",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return f"ERROR {e.code}: {body}"
    except Exception as e:
        return f"ERROR: {e}"


if __name__ == "__main__":
    text, query = parse_args()
    if not text.strip():
        # Interactive mode
        print("ARES Offloader Alpha — reading from stdin...")
        print("Pipe tool output to me. Ctrl+D to end.")
        text = sys.stdin.read()

    result = compress(text, query)
    print(result)

    # Auto-store to shared memory vault (Alpha channel)
    if _vault and not result.startswith("ERROR"):
        key = f"alpha:compress:{hash(text) % 2**32}"
        _vault.store(key, result, metadata={"query": query, "input_bytes": len(text)})

    # Cleanup old entries silently
    if _vault:
        _vault.cleanup()
