#!/usr/bin/env python3
"""
ARES Continuity Watchdog — Cron Wrapper
========================================
Gathers system-level context and generates a continuity brief via Omega.
Designed for cron: silent if nothing notable (exit 0), reports on changes.

Usage:
  ./ares-watchdog.py [--output /path/to/report]
  # Cron: */30 * * * * /path/to/ares-watchdog.py --cron
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
CONTINUITY_SCRIPT = os.path.join(SKILL_DIR, "ares-continuity.py")

WATCHED_PATH = os.path.expanduser("~/.NOTTHEONETOEDIT/skills")
REPORT_FILE = os.path.expanduser("~/.ares-continuity-latest.md")

# State tracking
STATE_FILE = os.path.expanduser("~/.ares-watchdog-state.json")


def run(cmd: list[str], timeout: int = 30) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return f"[error: {e}]"


def gather_context() -> str:
    """Collect system and project-level context."""
    lines = []
    lines.append(f"--- ARES Watchdog Report — {datetime.now().isoformat()} ---")
    lines.append("")

    # Disk usage
    df = run(["df", "-h", "/home", "--output=size,used,avail,pcent"])
    lines.append(f"## Disk\n{df}")

    # Memory
    mem = run(["free", "-h", "-w"])
    lines.append(f"\n## Memory\n{mem}")

    # Recent files modified in the skills directory
    modified = run(["find", WATCHED_PATH, "-type", "f", "-name", "*.py", "-o", "-name", "*.sh", "-o", "-name", "*.md", "-mmin", "-60"], timeout=10)
    if modified:
        lines.append(f"\n## Recently Modified Files (last 60 min)\n{modified}")

    # Running processes owned by user
    procs = run(["ps", "-u", os.environ.get("USER", "craig"), "--no-headers", "-o", "pid,comm,%cpu,%mem,etime", "--sort=-%cpu"], timeout=10)
    proc_lines = procs.split("\n")[:15]
    lines.append(f"\n## Top Processes (user)\n" + "\n".join(proc_lines))

    # Load average
    load = run(["uptime"])
    lines.append(f"\n## Load\n{load}")

    return "\n".join(lines)


def detect_changes(context: str) -> str:
    """Compare against previous state and flag what's new."""
    prev = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                prev = json.load(f)
        except Exception:
            pass

    # Simple hash comparison
    current_hash = hash(context)
    prev_hash = prev.get("context_hash", 0)

    changes = []
    if current_hash != prev_hash:
        changes.append("System state changed since last check")

    # Save state
    try:
        with open(STATE_FILE, "w") as f:
            json.dump({"context_hash": current_hash, "last_seen": datetime.now().isoformat()}, f)
    except Exception:
        pass

    return "\n".join(changes)


if __name__ == "__main__":
    is_cron = "--cron" in sys.argv
    context = gather_context()
    changes = detect_changes(context)

    # For cron: if nothing changed and no explicit output requested, stay silent
    if is_cron and not changes:
        sys.exit(0)

    # Always append the context for the continuity model
    brief_input = f"Changes detected:\n{changes}\n\nCurrent context:\n{context}" if changes else context

    # Feed to continuity Omega
    import subprocess as sp
    result = sp.run(
        [sys.executable, CONTINUITY_SCRIPT],
        input=brief_input,
        capture_output=True,
        text=True,
        timeout=120,
    )

    output = result.stdout.strip()

    # Save report
    with open(REPORT_FILE, "w") as f:
        f.write(f"<!-- Generated: {datetime.now().isoformat()} -->\n")
        f.write(output + "\n")

    print(output)
