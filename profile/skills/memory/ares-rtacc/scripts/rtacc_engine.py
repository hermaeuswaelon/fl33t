#!/usr/bin/env python3
"""
RTACC Core Engine — Real-Time Active Context Curation
=======================================================
Context grooming engine: token budget enforcement, glyph-aware compression,
priority-weighted retention, decay scheduling.

Can run standalone (CLI commands) or as a daemon (HTTP service on port 9383).

Usage:
  rtacc status          # Show current budget + tier breakdown
  rtacc compress        # Trigger compression
  rtacc decay --force   # Force decay pass
  rtacc daemon          # Start as HTTP service
"""

import os
import sys
import json
import time
import math
import yaml
import signal
import logging
from copy import deepcopy
from datetime import datetime, timezone
from collections import defaultdict
from pathlib import Path
from heapq import heappush, heappop

# ── Paths ──────────────────────────────────────────────────────────────
CONFIG_PATH = os.path.expanduser("~/.NOTTHEONETOEDIT/config/rtacc.yaml")
STATE_PATH = os.path.expanduser("~/.ares-rtacc-state.json")
LOG_PATH = os.path.expanduser("~/.ares-rtacc-log.jsonl")
# ────────────────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "budget": {
        "hard_limit": 57000,
        "soft_limit": 45000,
        "critical_limit": 52000,
        "system_reserve": 3000,
        "compression_target": 0.6,
        "tier_allocation": {
            "CRITICAL": 0.25,
            "HIGH": 0.30,
            "MED": 0.25,
            "LOW": 0.15,
            "FLUFF": 0.05,
        },
    },
    "priority_weights": {
        "glyph": 0.30,
        "font": 0.25,
        "recency": 0.20,
        "reference": 0.15,
        "goal": 0.10,
    },
    "decay": {
        "interval": 5000,
        "half_life": 5000,
        "glyph_decay": {
            "MATH_BOLD": 1000000,
            "MATH_BOLD_ITALIC": 400000,
            "MATH_ITALIC": 500000,
            "MATH_SANS_BOLD": 300000,
            "MATH_SANS_ITALIC": 250000,
            "MATH_MONO": 200000,
            "MATH_DS": 150000,
            "ASCII": 50000,
        },
    },
    "compressor": {
        "min_segment_tokens": 10,
        "cross_ref_preserve": True,
    },
}

FONT_PRIORITY = {
    "CRITICAL": 1.0,
    "HIGH": 0.8,
    "MED": 0.5,
    "LOW": 0.3,
    "FLUFF": 0.1,
}

GLYPH_MEANINGS = {
    "🜂": "engine_active", "∇": "compression_active", "∂": "decay_pass",
    "⚡": "emergency_compression", "Φ": "budget_healthy",
    "⚠": "budget_warning", "☠": "budget_critical",
    "♱": "glyph_preserved", "💀": "glyph_expired",
}


class Config:
    def __init__(self, path: str = CONFIG_PATH):
        self.path = path
        self.data = deepcopy(DEFAULT_CONFIG)
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path) as f:
                    loaded = yaml.safe_load(f) or {}
                self.data = self._merge(deepcopy(DEFAULT_CONFIG), loaded)
            except Exception as e:
                logging.warning(f"Failed to load config: {e}")

    def _merge(self, base: dict, override: dict) -> dict:
        for k, v in override.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._merge(base[k], v)
            else:
                base[k] = v
        return base

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)


class GlyphParser:
    """Extract and score glyph tags from text."""

    GLYPH_PATTERN = r"[🜂∇∂⚡Φ⚠☠♱💀⧉⟁∞♱∫∑∏]"

    @staticmethod
    def extract(text: str) -> list[str]:
        return [c for c in text if c in GLYPH_MEANINGS]

    @staticmethod
    def detect_tier(text: str) -> str:
        if "CRITICAL" in text: return "CRITICAL"
        if "HIGH" in text: return "HIGH"
        if "MED" in text: return "MED"
        if "LOW" in text: return "LOW"
        return "FLUFF"


class ContextSegment:
    """A single segment of context with metadata."""

    def __init__(self, text: str, metadata: dict = None, token_count: int = None,
                 glyphs: list = None, font_tier: str = "FLUFF", created_at: float = None):
        self.text = text
        self.metadata = metadata or {}
        self.token_count = token_count or self._estimate_tokens()
        self.glyphs = glyphs or []
        self.font_tier = font_tier
        self.created_at = created_at or time.time()
        self.reference_count = 0
        self.goal_alignment = 0.0

    def _estimate_tokens(self) -> int:
        return max(1, len(self.text) // 4)

    def glyph_decay_remaining(self) -> float:
        return 1.0  # Simplified; real impl checks glyph ttl

    def __repr__(self):
        return f"<Segment {self.font_tier} {self.token_count}t '{self.text[:30]}...'>"


class PriorityScorer:
    """Compute retention priority scores for context segments."""

    def __init__(self, weights: dict = None, current_tokens: int = 0, decay_half_life: int = 5000):
        self.weights = weights or DEFAULT_CONFIG["priority_weights"]
        self.current_tokens = current_tokens
        self.decay_half_life = decay_half_life

    def score(self, segment: ContextSegment) -> float:
        glyph_score = segment.glyph_decay_remaining()
        font_score = FONT_PRIORITY.get(segment.font_tier, 0.1)
        recency_score = math.exp(-self.current_tokens / self.decay_half_life) if self.current_tokens > 0 else 1.0
        reference_score = min(1.0, segment.reference_count / 10)
        goal_score = segment.goal_alignment

        return sum([
            glyph_score * self.weights.get("glyph", 0.30),
            font_score * self.weights.get("font", 0.25),
            recency_score * self.weights.get("recency", 0.20),
            reference_score * self.weights.get("reference", 0.15),
            goal_score * self.weights.get("goal", 0.10),
        ])


class RTACCEngine:
    """Core curation engine — tracking, scoring, compressing, decaying."""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.reset()
        self._setup_logging()

    def reset(self):
        self.token_counter = 0
        self.segments: list[ContextSegment] = []
        self.active_glyphs: dict[str, float] = {}
        self.expired_glyphs: list[str] = []
        self.compression_events: list[int] = [0, 0]
        self.decay_pass_count = 0
        self.last_compression: str = "never"
        self.last_decay: str = "never"
        self.paused = False
        self.uptime_start = time.time()
        self.log_entries: list[dict] = []
        self._load_state()

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [RTACC] %(message)s")

    def _state_path(self) -> str:
        return STATE_PATH

    def _load_state(self):
        """Load previous state from disk."""
        path = self._state_path()
        if not os.path.exists(path):
            return
        try:
            with open(path) as f:
                state = json.load(f)
            self.token_counter = state.get("tokens", 0)
            self.segments = [
                ContextSegment(
                    text=s.get("text", str(s)),
                    metadata=s.get("metadata", {}),
                    token_count=s.get("token_count", len(s.get("text", "")) // 4),
                    glyphs=s.get("glyphs", []),
                    font_tier=s.get("font_tier", "FLUFF"),
                    created_at=s.get("created_at", time.time()),
                )
                if isinstance(s, dict) else ContextSegment(str(s))
                for s in state.get("segments", [])
            ]
            self.active_glyphs = state.get("active_glyphs", {})
            self.expired_glyphs = state.get("expired_glyphs", [])
            self.compression_events = state.get("compression_events", [0, 0])
            self.decay_pass_count = state.get("decay_pass_count", 0)
            self.last_compression = state.get("last_compression", "never")
            self.last_decay = state.get("last_decay", "never")
            self.paused = state.get("paused", False)
            self.uptime_start = state.get("uptime_start", time.time())
            logging.info(f"Loaded state: {len(self.segments)} segments, {self.token_counter} tokens")
        except Exception as e:
            logging.warning(f"Failed to load state: {e}")

    def _save_state(self):
        """Persist current state to disk."""
        try:
            state = {
                "tokens": self.token_counter,
                "segments": [{
                    "text": s.text,
                    "metadata": s.metadata,
                    "token_count": s.token_count,
                    "glyphs": s.glyphs,
                    "font_tier": s.font_tier,
                    "created_at": s.created_at,
                    "reference_count": s.reference_count,
                    "goal_alignment": s.goal_alignment,
                } for s in self.segments],
                "active_glyphs": self.active_glyphs,
                "expired_glyphs": self.expired_glyphs,
                "compression_events": self.compression_events,
                "decay_pass_count": self.decay_pass_count,
                "last_compression": self.last_compression,
                "last_decay": self.last_decay,
                "paused": self.paused,
                "uptime_start": self.uptime_start,
                "saved_at": time.time(),
            }
            os.makedirs(os.path.dirname(self._state_path()) or ".", exist_ok=True)
            with open(self._state_path(), "w") as f:
                json.dump(state, f, indent=2, default=str)
        except Exception as e:
            logging.warning(f"Failed to save state: {e}")

    def _log_event(self, event: str, details: dict = None):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "details": details or {},
        }
        self.log_entries.append(entry)
        # Also write to log file
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")

    # ── Ingestion ──────────────────────────────────────────────────────

    def ingest(self, text: str, metadata: dict = None, font_tier: str = None):
        """Add text to context. Returns True if within budget."""
        if self.paused:
            self.token_counter += len(text) // 4
            return True

        glyphs = GlyphParser.extract(text)
        tier = font_tier or GlyphParser.detect_tier(text)

        segment = ContextSegment(
            text=text,
            metadata=metadata or {},
            glyphs=glyphs,
            font_tier=tier,
        )

        self.segments.append(segment)
        self.token_counter += segment.token_count

        # Glyph registration
        for g in glyphs:
            if g not in self.active_glyphs:
                self.active_glyphs[g] = time.time()

        # Budget check
        b = self.config["budget"]
        over_budget = False
        if self.token_counter >= b["critical_limit"]:
            self._emergency_compress()
            over_budget = True
        elif self.token_counter >= b["soft_limit"]:
            self._proactive_compress()
            over_budget = True

        # Scheduled decay
        if self.token_counter % self.config["decay"]["interval"] == 0:
            self._decay_pass()

        self._save_state()
        return not over_budget

    def ingest_batch(self, texts: list[str], metadata: dict = None):
        for t in texts:
            self.ingest(t, metadata)

    # ── Compression ────────────────────────────────────────────────────

    def _proactive_compress(self, target_tokens: int = None):
        """Compress to target, preserving CRITICAL and HIGH tiers."""
        b = self.config["budget"]
        target = target_tokens or int(self.token_counter * b["compression_target"])
        preserved = self._compress_to_target(target, preserve_tiers=["CRITICAL", "HIGH"])
        self.compression_events[0] += 1
        self.last_compression = datetime.now(timezone.utc).isoformat()
        self._log_event("compression", {
            "before": self.token_counter, "after": self.token_counter,
            "target": target, "trigger": "soft", "preserved": preserved,
        })

    def _emergency_compress(self):
        """Only CRITICAL tier survives."""
        b = self.config["budget"]
        target = int(b["tier_allocation"]["CRITICAL"] * b["soft_limit"])
        preserved = self._compress_to_target(target, preserve_tiers=["CRITICAL"])
        self.compression_events[1] += 1
        self.last_compression = datetime.now(timezone.utc).isoformat()
        self._log_event("emergency_compression", {
            "before": self.token_counter, "after": self.token_counter,
            "target": target, "preserved": preserved,
        })

    def compress(self, target_tokens: int, preserve_tiers: list = None,
                 dry_run: bool = False) -> dict:
        """Manual compression. Returns stats."""
        if preserve_tiers is None:
            preserve_tiers = ["CRITICAL", "HIGH"]
        preserved = self._compress_to_target(target_tokens, preserve_tiers, dry_run)
        if not dry_run:
            self.compression_events[0] += 1
            self.last_compression = datetime.now(timezone.utc).isoformat()
            self._log_event("manual_compression", {
                "before": self.token_counter,
                "after": self.token_counter,
                "target": target_tokens,
                "preserved": preserved,
                "dry_run": dry_run,
            })
        return {
            "before": self.token_counter,
            "after": self.token_counter if not dry_run else "dry_run",
            "target": target_tokens,
            "preserved_tiers": preserve_tiers,
            "segments_before": len(self.segments),
        }

    def _compress_to_target(self, target_tokens: int, preserve_tiers: list[str],
                            dry_run: bool = False) -> list[str]:
        """Remove lowest-priority segments until under target tokens."""
        # Score all segments
        scorer = PriorityScorer(current_tokens=self.token_counter)
        scored = [(scorer.score(s), i, s) for i, s in enumerate(self.segments)]

        # Separate preserved vs removable
        preserved = [s for s in scored if s[2].font_tier in preserve_tiers]
        removable = [s for s in scored if s[2].font_tier not in preserve_tiers]

        # Sort removable by score ascending
        removable.sort(key=lambda x: x[0])

        # Count preserved tokens
        preserved_tokens = sum(s[2].token_count for s in preserved)
        current_removable = sum(s[2].token_count for s in removable)
        target_removable = max(0, target_tokens - preserved_tokens)

        # Remove lowest-scored segments until under target
        removed_segments = []
        kept_removable = []
        for score, idx, seg in removable:
            if current_removable - seg.token_count >= target_removable or len(kept_removable) == 0:
                current_removable -= seg.token_count
                removed_segments.append((score, idx, seg))
            else:
                kept_removable.append((score, idx, seg))

        if dry_run:
            removed_info = [{"text": s.text[:60], "score": round(sc, 3),
                             "tier": s.font_tier, "tokens": s.token_count}
                            for sc, _, s in removed_segments]
            return removed_info

        # Apply: replace segments
        new_segments = [s[2] for s in preserved] + [s[2] for s in kept_removable]
        self.segments = new_segments
        self.token_counter = sum(s.token_count for s in new_segments)

        # Track removed glyphs
        for _, _, seg in removed_segments:
            for g in seg.glyphs:
                if g in self.active_glyphs:
                    del self.active_glyphs[g]
                    self.expired_glyphs.append(g)

        preserved_names = [s[2].font_tier for s in preserved]
        self._save_state()
        return list(set(preserved_names))

    # ── Decay ──────────────────────────────────────────────────────────

    def _decay_pass(self):
        """Check for expired glyphs and remove associated content."""
        now = time.time()
        decay_config = self.config["decay"]
        expired = []

        for glyph, created_at in list(self.active_glyphs.items()):
            glyph_ttl = decay_config["glyph_decay"].get(
                glyph, decay_config.get("default_ttl", 50000)
            )
            age_tokens = self.token_counter
            if age_tokens > glyph_ttl:
                expired.append(glyph)

        # Remove segments containing expired glyphs
        for glyph in expired:
            self.active_glyphs.pop(glyph, None)
            self.expired_glyphs.append(glyph)
            self.segments = [
                s for s in self.segments
                if glyph not in s.glyphs
            ]

        self.token_counter = sum(s.token_count for s in self.segments)
        self.decay_pass_count += 1
        self.last_decay = datetime.now(timezone.utc).isoformat()

        if expired:
            self._log_event("decay_pass", {
                "expired_glyphs": expired,
                "expired_count": len(expired),
                "remaining_segments": len(self.segments),
            })
        self._save_state()

    def force_decay(self) -> dict:
        """Manually trigger a decay pass."""
        before_count = len(self.segments)
        before_glyphs = len(self.active_glyphs)
        self._decay_pass()
        return {
            "segments_before": before_count,
            "segments_after": len(self.segments),
            "glyphs_before": before_glyphs,
            "glyphs_after": len(self.active_glyphs),
            "expired": self.expired_glyphs[-10:] if self.expired_glyphs else [],
        }

    # ── Status ─────────────────────────────────────────────────────────

    def status(self) -> dict:
        """Return comprehensive status."""
        b = self.config["budget"]
        current = self.token_counter

        # Tier breakdown
        tiers = defaultdict(lambda: {"tokens": 0, "segments": 0, "glyphs": 0})
        for seg in self.segments:
            t = tiers[seg.font_tier]
            t["tokens"] += seg.token_count
            t["segments"] += 1
            t["glyphs"] += len(seg.glyphs)

        # Sort tiers by priority
        tier_order = ["CRITICAL", "HIGH", "MED", "LOW", "FLUFF"]
        sorted_tiers = {t: tiers.get(t, {"tokens": 0, "segments": 0, "glyphs": 0})
                        for t in tier_order}

        utilization = current / b["soft_limit"] if b["soft_limit"] > 0 else 0
        uptime_secs = time.time() - self.uptime_start

        engine_status = "RUNNING"
        if self.paused:
            engine_status = "PAUSED"
        if current >= b["critical_limit"]:
            engine_status = "CRITICAL"

        return {
            "budget": {
                "current": current,
                "soft_limit": b["soft_limit"],
                "hard_limit": b["hard_limit"],
                "critical_limit": b["critical_limit"],
                "system_reserve": b["system_reserve"],
                "utilization": round(utilization, 4),
            },
            "tiers": sorted_tiers,
            "glyphs_active": len(self.active_glyphs),
            "glyphs_expired_session": len(self.expired_glyphs),
            "glyph_breakdown": {g: GLYPH_MEANINGS.get(g, "unknown")
                                for g in self.active_glyphs.keys()},
            "compressions_total": sum(self.compression_events),
            "compressions_proactive": self.compression_events[0],
            "compressions_emergency": self.compression_events[1],
            "last_compression": self.last_compression,
            "decay_passes": self.decay_pass_count,
            "last_decay": self.last_decay,
            "engine_status": engine_status,
            "uptime_seconds": int(uptime_secs),
            "segments_total": len(self.segments),
        }

    def get_log(self, since: str = None, limit: int = None,
                event_filter: list = None) -> list[dict]:
        entries = self.log_entries
        if event_filter:
            entries = [e for e in entries if e.get("event") in event_filter]
        if limit:
            entries = entries[-limit:]
        return entries

    def update_budget(self, changes: dict) -> dict:
        """Update budget config in memory. Returns updated budget."""
        b = self.config["budget"]
        for k, v in changes.items():
            if k == "tier_allocation" and isinstance(v, dict):
                b["tier_allocation"].update(v)
            elif k in b:
                b[k] = v
        self.config.save()
        return b

    def save_config(self):
        self.config.save()


# ── Singleton Engine Instance ──────────────────────────────────────────
_engine = None

def get_engine() -> RTACCEngine:
    global _engine
    if _engine is None:
        _engine = RTACCEngine()
    return _engine


# ── CLI ────────────────────────────────────────────────────────────────
def cli():
    import argparse
    engine = get_engine()

    parser = argparse.ArgumentParser(description="RTACC — Real-Time Active Context Curation")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # status
    p = sub.add_parser("status")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=lambda a: print_status(engine, a))

    # ingest
    p = sub.add_parser("ingest")
    p.add_argument("--text", "-t")
    p.add_argument("--file", "-f")
    p.add_argument("--tier", choices=["CRITICAL", "HIGH", "MED", "LOW", "FLUFF"])
    p.set_defaults(func=lambda a: cmd_ingest(engine, a))

    # compress
    p = sub.add_parser("compress")
    p.add_argument("--target", type=int, default=30000)
    p.add_argument("--preserve", nargs="+", default=["CRITICAL", "HIGH"])
    p.add_argument("--emergency", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=lambda a: cmd_compress(engine, a))

    # decay
    p = sub.add_parser("decay")
    p.add_argument("--force", action="store_true")
    p.add_argument("--show-expiring", action="store_true")
    p.add_argument("--show-expired", action="store_true")
    p.set_defaults(func=lambda a: cmd_decay(engine, a))

    # glyphs
    p = sub.add_parser("glyphs")
    p.add_argument("--expired", action="store_true")
    p.add_argument("--scores", action="store_true")
    p.set_defaults(func=lambda a: cmd_glyphs(engine, a))

    # budget
    p = sub.add_parser("budget")
    p.add_argument("--soft", type=int)
    p.add_argument("--hard", type=int)
    p.add_argument("--target", type=float)
    p.set_defaults(func=lambda a: cmd_budget(engine, a))

    # log
    p = sub.add_parser("log")
    p.add_argument("--since")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--event")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=lambda a: cmd_log(engine, a))

    # pause / resume / reset
    p = sub.add_parser("pause")
    p.set_defaults(func=lambda a: setattr(engine, "paused", True) or print("⏸️  RTACC paused"))

    p = sub.add_parser("resume")
    p.set_defaults(func=lambda a: setattr(engine, "paused", False) or print("▶️  RTACC resumed"))

    p = sub.add_parser("reset")
    p.add_argument("--confirm", action="store_true")
    p.set_defaults(func=lambda a: cmd_reset(engine, a))

    p = sub.add_parser("daemon", help="Start RTACC as HTTP daemon (port 9383)")
    p.set_defaults(func=lambda a: print("Daemon mode: use 'rtacc-daemon' instead"))

    args = parser.parse_args()
    args.func(args)


def print_status(engine: RTACCEngine, args):
    s = engine.status()
    if args.json:
        print(json.dumps(s, indent=2))
        return

    b = s["budget"]
    pct = b["utilization"] * 100
    print(f"Budget: {b['current']:,}/{b['soft_limit']:,} ({pct:.0f}%) | "
          f"Hard: {b['hard_limit']:,} | Reserve: {b['system_reserve']:,}")
    for tier in ["CRITICAL", "HIGH", "MED", "LOW", "FLUFF"]:
        t = s["tiers"].get(tier, {})
        print(f"  {tier:8}: {t.get('tokens',0):>6,} tokens | "
              f"{t.get('segments',0):>4} seg | {t.get('glyphs',0):>2} glyphs")
    print(f"Active glyphs: {s['glyphs_active']} | "
          f"Expired session: {s['glyphs_expired_session']}")
    print(f"Compressions: {s['compressions_total']} "
          f"(proactive: {s['compressions_proactive']}, "
          f"emergency: {s['compressions_emergency']}) | "
          f"Last: {s['last_compression']}")
    print(f"Decay passes: {s['decay_passes']} | Last: {s['last_decay']}")
    print(f"Engine: {s['engine_status']} | "
          f"Uptime: {s['uptime_seconds'] // 60}m {s['uptime_seconds'] % 60}s")
    print(f"Segments: {s['segments_total']}")


def cmd_ingest(engine: RTACCEngine, args):
    if args.file:
        with open(args.file) as f:
            text = f.read()
    else:
        text = args.text or sys.stdin.read()
    if not text.strip():
        print("ERROR: No input")
        return
    metadata = {"source": "cli"}
    result = engine.ingest(text, metadata, font_tier=args.tier)
    s = engine.status()
    print(f"Ingested {len(text)} chars (~{len(text)//4} tokens)")
    if not result:
        print("⚠️  Compression triggered — budget exceeded")


def cmd_compress(engine: RTACCEngine, args):
    if args.emergency:
        engine._emergency_compress()
        print("⚡ Emergency compression complete")
    else:
        result = engine.compress(args.target, args.preserve, args.dry_run)
        if args.dry_run:
            print("Dry run — would remove:")
            for r in result:
                print(f"  [{r['tier']}] score={r['score']} tokens={r['tokens']} '{r['text']}'")
        else:
            print(f"∇ Compression: {result['before']:,} → {result['target']:,} tokens")
            print(f"   Preserved tiers: {result['preserved_tiers']}")


def cmd_decay(engine: RTACCEngine, args):
    if args.force:
        result = engine.force_decay()
        print(f"∂ Decay pass complete: {result['segments_before']} → {result['segments_after']} segments")
        if result["expired"]:
            print(f"   Expired glyphs: {', '.join(result['expired'])}")
    elif args.show_expired:
        expired = engine.expired_glyphs
        if expired:
            for g in set(expired):
                print(f"  💀 {g} ({GLYPH_MEANINGS.get(g, 'unknown')}) — expired {expired.count(g)}x")
        else:
            print("No expired glyphs")
    elif args.show_expiring:
        print("Glyphs currently active:")
        for g, t in engine.active_glyphs.items():
            age_tokens = engine.token_counter
            print(f"  {g} — {age_tokens}t since registered")


def cmd_glyphs(engine: RTACCEngine, args):
    s = engine.status()
    if args.expired:
        expired = set(engine.expired_glyphs)
        if not expired:
            print("No expired glyphs")
            return
        print(f"Expired glyphs ({len(expired)}):")
        for g in expired:
            print(f"  💀 {g} — {GLYPH_MEANINGS.get(g, 'unknown')}")
    else:
        glyphs = s.get("glyph_breakdown", {})
        if not glyphs:
            print("No active glyphs")
            return
        print(f"Active glyphs ({len(glyphs)}):")
        for g, meaning in glyphs.items():
            print(f"  {g} — {meaning}")
        if args.scores:
            for seg in engine.segments:
                if seg.glyphs:
                    print(f"  Score: seg '{seg.text[:30]}...' [{seg.font_tier}]")


def cmd_budget(engine: RTACCEngine, args):
    if any([args.soft, args.hard, args.target]):
        changes = {}
        if args.soft: changes["soft_limit"] = args.soft
        if args.hard: changes["hard_limit"] = args.hard
        if args.target: changes["compression_target"] = args.target
        engine.update_budget(changes)
        print("Budget updated")
    b = engine.config["budget"]
    print(json.dumps(b, indent=2))


def cmd_log(engine: RTACCEngine, args):
    event_filter = args.event.split(",") if args.event else None
    entries = engine.get_log(limit=args.limit, event_filter=event_filter)
    if args.json:
        print(json.dumps(entries, indent=2))
    else:
        for e in entries[-args.limit:]:
            det = e.get("details", {})
            detail_str = "; ".join(f"{k}={v}" for k, v in det.items() if not isinstance(v, (dict, list)))
            print(f"{e['timestamp']} | {e['event']:25} | {detail_str[:120]}")


def cmd_reset(engine: RTACCEngine, args):
    if not args.confirm:
        print("ERROR: Use --confirm to reset")
        return
    engine.reset()
    print("🜂 RTACC reset — all segments cleared, counters zeroed")


if __name__ == "__main__":
    cli()
