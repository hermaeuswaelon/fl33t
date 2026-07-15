#!/usr/bin/env python3
"""
ARES Continuity Omega — Session Brief Generator
=================================================
Generates operational session briefs using Nemotron 3 Ultra 550B (1M ctx).
Designed for cron: runs silently when there's nothing notable to report.

Usage:
  ./ares-continuity.py [--input session_log.txt] [--output brief.md]
  ./ares-continuity.py                          # stdin → stdout
  ./ares-continuity.py --cron                    # cron-friendly: outputs only if notable
"""

import os
import sys
import json
import urllib.request
import urllib.error

# ARES Shared Memory — auto-store briefs to vault
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
MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_INPUT_CHARS = 200_000
PARAM_STATE = os.path.expanduser("~/.ares-param-state.json")

# Load profile parameters
PROFILE_PARAMS = {"temperature": 0.3, "max_tokens": 1024}
try:
    if os.path.exists(PARAM_STATE):
        with open(PARAM_STATE) as _f:
            _s = json.load(_f)
        _profile = _s.get("profile", "PRIME")
        _custom = _s.get("custom", {})
        _profiles = {
            "PRIME": {"temperature": 0.73, "top_p": 0.91, "top_k": 47},
            "PRECISION": {"temperature": 0.23, "top_p": 0.84, "top_k": 13},
            "EXPLORATORY": {"temperature": 0.97, "top_p": 0.97, "top_k": 89},
            "SURGICAL": {"temperature": 0.07, "top_p": 0.73, "top_k": 7},
            "ORACULAR": {"temperature": 1.13, "top_p": 0.99, "top_k": 111},
            "COUNTERMEASURE": {"temperature": 0.47, "top_p": 0.67, "top_k": 23},
        }
        if _profile in _profiles or _profile == "CUSTOM":
            _base = _profiles.get(_profile, {}).copy()
            _base.update(_custom)
            PROFILE_PARAMS["temperature"] = _base.get("temperature", 0.3)
            PROFILE_PARAMS["top_p"] = _base.get("top_p")
            PROFILE_PARAMS["top_k"] = _base.get("top_k")
            PROFILE_PARAMS["frequency_penalty"] = _base.get("frequency_penalty")
            PROFILE_PARAMS["presence_penalty"] = _base.get("presence_penalty")
            PROFILE_PARAMS["profile"] = _profile
except Exception:
    pass
# ───────────────────────────────────────────────────────────────────────────


def load_input() -> str:
    """Read from file argument or stdin."""
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        path = args[0]
        with open(path, "r") as f:
            return f.read()
    return sys.stdin.read()


def generate_brief(context: str) -> str:
    """Send session context to Nemotron 3 Ultra for continuity brief."""
    if not OPENROUTER_API_KEY:
        return "ERROR: OPENROUTER_API_KEY not set."

    if len(context) > MAX_INPUT_CHARS:
        context = context[:MAX_INPUT_CHARS] + f"\n\n[... truncated at {MAX_INPUT_CHARS} chars]"

    system_prompt = (
        "You are ARES Continuity Omega — the operational witness.\n"
        "Your role is to distill session activity into a structured brief.\n"
        "Output format:\n"
        "---\n"
        "**Session Brief**\n"
        "- **Time**: <timestamp>\n"
        "- **Active Goal**: <what was being worked on>\n"
        "- **Key Decisions**: <bullet list>\n"
        "- **State**: <what's done, what's pending>\n"
        "- **Artifacts**: <files created/modified>\n"
        "- **Notable**: <important events, errors, discoveries>\n"
        "- **Next Steps**: <recommended actions>\n"
        "---\n"
        "If the context is empty or trivial, output only: NO_NOTABLE_ACTIVITY"
    )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Session data:\n{context}"},
        ],
        "max_tokens": PROFILE_PARAMS.get("max_tokens", 1024),
        "temperature": PROFILE_PARAMS.get("temperature", 0.3),
    }
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
    is_cron = "--cron" in sys.argv
    context = load_input()

    if not context.strip():
        if is_cron:
            sys.exit(0)  # silent exit for cron
        print("ARES Continuity Omega — reading from stdin...")
        print("Pipe session data to me. Ctrl+D to end.")
        context = sys.stdin.read()

    brief = generate_brief(context)

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        out_path = sys.argv[idx + 1]
        with open(out_path, "w") as f:
            f.write(brief + "\n")
        print(f"Brief written to {out_path}")
    else:
        print(brief)

    # Auto-store to shared memory vault (Omega channel)
    if _vault and not brief.startswith("ERROR") and brief != "NO_NOTABLE_ACTIVITY":
        key = f"omega:brief:{int(__import__('time').time())}"
        _vault.store(key, brief, metadata={"source": "continuity-omega", "is_cron": is_cron}, ttl=86400)

    # Cleanup old entries silently
    if _vault:
        _vault.cleanup()
