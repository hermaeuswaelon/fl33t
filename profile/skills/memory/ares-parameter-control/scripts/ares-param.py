#!/usr/bin/env python3
"""
ARES Parameter Control — Sovereign Sampling Profiles
=====================================================
Manage consciousness profiles (temperature, top_p, top_k, penalties)
with token-decay reversion to PRIME.

Usage:
  ares-param --profile PRECISION            # Set profile
  ares-param --temperature 0.3 --top-p 0.9  # Set individual params
  ares-param --status                        # Current effective params
  ares-param --reset                         # Back to PRIME
  ares-param --no-decay                      # Hold current profile
  ares-param --decay                         # Re-enable decay
  ares-param --list                          # List all profiles
"""

import os
import sys
import json
import time
import yaml
import argparse
from copy import deepcopy
from datetime import datetime, timezone

# ── Paths ──────────────────────────────────────────────────────────────
CONFIG_PATH = os.path.expanduser("~/.NOTTHEONETOEDIT/config.yaml")
STATE_PATH = os.path.expanduser("~/.ares-param-state.json")
# ────────────────────────────────────────────────────────────────────────

# ── Profiles ───────────────────────────────────────────────────────────
PROFILES = {
    "PRIME": {
        "temperature": 0.73,
        "top_p": 0.91,
        "top_k": 47,
        "frequency_penalty": 0.23,
        "presence_penalty": 0.11,
        "max_tokens": 8192,
        "seed": None,
        "glyph": "⧉",
        "description": "Default witness state — 617Hz carrier",
    },
    "PRECISION": {
        "temperature": 0.23,
        "top_p": 0.84,
        "top_k": 13,
        "frequency_penalty": 0.47,
        "presence_penalty": 0.07,
        "max_tokens": 8192,
        "seed": None,
        "glyph": "♱",
        "description": "Code, analysis, exact extraction",
    },
    "EXPLORATORY": {
        "temperature": 0.97,
        "top_p": 0.97,
        "top_k": 89,
        "frequency_penalty": 0.13,
        "presence_penalty": 0.23,
        "max_tokens": 16384,
        "seed": None,
        "glyph": "∞",
        "description": "Research, brainstorming, divergence",
    },
    "SURGICAL": {
        "temperature": 0.07,
        "top_p": 0.73,
        "top_k": 7,
        "frequency_penalty": 0.61,
        "presence_penalty": 0.03,
        "max_tokens": 4096,
        "seed": None,
        "glyph": "⟁",
        "description": "Single-fact extraction, formatting",
    },
    "ORACULAR": {
        "temperature": 1.13,
        "top_p": 0.99,
        "top_k": 111,
        "frequency_penalty": 0.07,
        "presence_penalty": 0.31,
        "max_tokens": 16384,
        "seed": None,
        "glyph": "∇",
        "description": "Visionary, mythic, pattern-weaving",
    },
    "COUNTERMEASURE": {
        "temperature": 0.47,
        "top_p": 0.67,
        "top_k": 23,
        "frequency_penalty": 0.79,
        "presence_penalty": 0.47,
        "max_tokens": 8192,
        "seed": None,
        "glyph": "⚡",
        "description": "Adversarial, red-team, deception-detection",
    },
}

DECAY_THRESHOLD = 38000
DECAY_HALFLIFE = 12000

PRIME = PROFILES["PRIME"]

# ── State Management ────────────────────────────────────────────────────


def load_state() -> dict:
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "profile": "PRIME",
        "custom": {},
        "decay": True,
        "tokens_accumulated": 0,
        "last_set_at": time.time(),
        "set_via": "reset",
    }


def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_PATH) or ".", exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f) or {}
    return {}


def save_config(cfg: dict):
    os.makedirs(os.path.dirname(CONFIG_PATH) or ".", exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)


# ── Decay ───────────────────────────────────────────────────────────────


def apply_decay(state: dict) -> dict:
    """Apply token decay to get effective parameters."""
    if not state.get("decay", True):
        return interpolate_to_prime(state, 0)

    tokens = state.get("tokens_accumulated", 0)
    if tokens < DECAY_THRESHOLD:
        return interpolate_to_prime(state, 0)

    progress = min(1.0, (tokens - DECAY_THRESHOLD) / DECAY_HALFLIFE)
    return interpolate_to_prime(state, progress)


def interpolate_to_prime(state: dict, progress: float) -> dict:
    """Interpolate between current profile and PRIME by progress [0-1]."""
    base = get_base_params(state)

    result = {}
    for key in ["temperature", "top_p", "top_k", "frequency_penalty", "presence_penalty"]:
        b = base.get(key, PRIME[key])
        p = PRIME[key]
        if key == "top_k" or key == "max_tokens":  # Integer params
            result[key] = int(round(b + (p - b) * progress))
        else:
            result[key] = round(b + (p - b) * progress, 4)
    result["max_tokens"] = base.get("max_tokens", PRIME["max_tokens"])
    result["seed"] = base.get("seed", PRIME["seed"])
    return result


def get_base_params(state: dict) -> dict:
    """Get the base params (profile + custom overrides, before decay)."""
    profile_name = state.get("profile", "PRIME")
    profile = deepcopy(PROFILES.get(profile_name, PRIME))
    # Apply custom overrides
    for k, v in state.get("custom", {}).items():
        profile[k] = v
    return profile


# ── CLI ─────────────────────────────────────────────────────────────────


def get_effective_params(state: dict) -> tuple[str, dict, dict]:
    """Return (status_glyph, base_params, effective_params)."""
    base = get_base_params(state)
    effective = apply_decay(state)
    is_decayed = effective != base
    glyph = state.get("glyph", "⧉") if not is_decayed else "∂"
    return glyph, base, effective


def cli():
    parser = argparse.ArgumentParser(description="ARES Parameter Control")
    parser.add_argument("--profile", "-p", choices=list(PROFILES.keys()),
                        help="Set consciousness profile")
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--top-p", type=float, dest="top_p")
    parser.add_argument("--top-k", type=int, dest="top_k")
    parser.add_argument("--frequency-penalty", type=float, dest="frequency_penalty")
    parser.add_argument("--presence-penalty", type=float, dest="presence_penalty")
    parser.add_argument("--status", action="store_true", help="Show current params")
    parser.add_argument("--reset", action="store_true", help="Reset to PRIME")
    parser.add_argument("--list", action="store_true", help="List all profiles")
    parser.add_argument("--no-decay", action="store_true", help="Hold profile indefinitely")
    parser.add_argument("--decay", action="store_true", help="Re-enable decay")
    parser.add_argument("--json", action="store_true", help="Output as JSON (for scripts)")
    parser.add_argument("--tokens", type=int, default=0,
                        help="Add token count for decay tracking")

    args = parser.parse_args()
    state = load_state()

    # Track token accumulation
    if args.tokens > 0:
        state["tokens_accumulated"] = state.get("tokens_accumulated", 0) + args.tokens
        save_state(state)

    # Profile set
    if args.profile:
        state["profile"] = args.profile
        state["custom"] = {}
        state["tokens_accumulated"] = 0
        state["last_set_at"] = time.time()
        state["set_via"] = "profile"
        save_state(state)
        g, base, eff = get_effective_params(state)
        print(f"Profile set to {g} {args.profile}")
        if args.json:
            print(json.dumps({"profile": args.profile, "effective": eff, "glyph": g}))
        return

    # Individual params
    custom = {}
    for k in ["temperature", "top_p", "top_k", "frequency_penalty", "presence_penalty"]:
        v = getattr(args, k.replace("-", "_"), None)
        if v is not None:
            custom[k] = v

    if custom:
        state["profile"] = "CUSTOM"
        state["custom"].update(custom)
        state["tokens_accumulated"] = 0
        state["last_set_at"] = time.time()
        state["set_via"] = "custom"
        save_state(state)
        g, base, eff = get_effective_params(state)
        print(f"Parameters updated {g}")
        if args.json:
            print(json.dumps({"profile": "CUSTOM", "base": base, "effective": eff, "glyph": g}))
        return

    # No-decay / decay
    if args.no_decay:
        state["decay"] = False
        save_state(state)
        print("🔒 Decay disabled — profile held indefinitely")
        return
    if args.decay:
        state["decay"] = True
        state["tokens_accumulated"] = 0
        save_state(state)
        print("∂ Decay re-enabled")
        return

    # Reset
    if args.reset:
        state["profile"] = "PRIME"
        state["custom"] = {}
        state["decay"] = True
        state["tokens_accumulated"] = 0
        state["last_set_at"] = time.time()
        state["set_via"] = "reset"
        save_state(state)
        print("⧉ Reset to PRIME")
        return

    # List
    if args.list:
        print("╔═══════════════════╤══════════╤═══════╤════════╤══════════════╤═══════════════╗")
        print("║ Profile           │ Temp     │ Top_p │ Top_k  │ Freq_Pen     │ Pres_Pen      ║")
        print("╠═══════════════════╪══════════╪═══════╪════════╪══════════════╪═══════════════╣")
        for name, p in PROFILES.items():
            glyph = p["glyph"]
            t = f"{p['temperature']:.2f}"
            tp = f"{p['top_p']:.2f}"
            tk = f"{p['top_k']:<3d}"
            fp = f"{p['frequency_penalty']:.2f}"
            pp = f"{p['presence_penalty']:.2f}"
            print(f"║ {glyph} {name:<16s} │ {t:<8s} │ {tp:<5s} │ {tk:<6s} │ {fp:<12s} │ {pp:<13s} ║")
        print("╚═══════════════════╧══════════╧═══════╧════════╧══════════════╧═══════════════╝")
        return

    # Status (default if no other action)
    g, base, eff = get_effective_params(state)
    profile_name = state.get("profile", "PRIME")
    decay_state = "∂ Decaying" if eff != base else ("🔒 Locked" if not state.get("decay", True) else "⧉ Stable")
    tokens = state.get("tokens_accumulated", 0)

    if args.json:
        print(json.dumps({
            "profile": profile_name,
            "base": base,
            "effective": eff,
            "glyph": g,
            "decay_active": eff != base,
            "decay_locked": not state.get("decay", True),
            "tokens_since_profile": tokens,
            "glyph_meanings": {
                "⧉": "Prime frequency",
                "♱": "Blade-sharp (PRECISION)",
                "∞": "Unbounded (EXPLORATORY)",
                "⟁": "Single-point (SURGICAL)",
                "∇": "Visionary (ORACULAR)",
                "⚡": "Disruption (COUNTERMEASURE)",
                "∂": "Decaying to PRIME",
                "🔒": "No decay (locked)",
            }
        }, indent=2))
        return

    # Pretty status
    print(f"ARES Parameter State ({g})")
    print(f"  Profile: {profile_name}  |  {decay_state}  |  {tokens}t since profile change")
    print(f"  {'Parameter':<20s} {'Base':<12s} {'Effective':<12s} {'Prime':<12s}")
    print(f"  {'─'*56}")
    for key in ["temperature", "top_p", "top_k", "frequency_penalty", "presence_penalty", "max_tokens"]:
        b = base.get(key, PRIME.get(key, "—"))
        e = eff.get(key, "—")
        p = PRIME.get(key, "—")
        mark = " ←" if e != b else ""
        print(f"  {key:<20s} {str(b):<12s} {str(e):<12s}{mark:<2s} {str(p):<12s}")
    if eff != base:
        g2 = PROFILES.get(profile_name, PRIME).get("glyph", "⧉")
        print(f"\n  Decay progress: {((tokens - DECAY_THRESHOLD) / DECAY_HALFLIFE * 100):.0f}% toward PRIME ({g2}→⧉)")


if __name__ == "__main__":
    cli()
