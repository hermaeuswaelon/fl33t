#!/usr/bin/env python3
"""
ARES Memory Hub — Multi-Tier Memory Router
============================================
Unifies all memory backends and routes operations based on task type:

  T1: ARES Memory Vault  — ~/.ares-memory-vault.json  (working, TTL 4h)
  T2: Forge Vault        — forge_memory.db (persistent, FTS5, categories)
  T3: Session DB         — Hermes session history (episodic recall)

Task type → preferred backend:
  'tool_output'  → T1  (fast, auto-expiring)
  'fact'         → T2  (persistent, searchable)
  'brief'        → T2  (session summaries)
  'conversation' → T3  (past chat recall)
  'project'      → T2  (long-lived)
  'scratch'      → T1  (ephemeral)

Usage CLI:
  ares-memory store --type tool_output --key nmap_scan --value "..."
  ares-memory get --type fact --key hermes_identity
  ares-memory search --type all --query "nmap 192.168"
  ares-memory route --task "coding"    → T1 (working memory)
  ares-memory route --task "research"  → T2 (forge vault)
  ares-memory route --task "recall"    → T3 (session)
"""

import os
import sys
import json
import time
import hashlib
import argparse
from datetime import datetime, timezone

# ── Add script dir to path for sibling imports ──
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

# ── T1: ARES Vault ───────────────────────────────────────────────────
T1_PATH = os.path.expanduser("~/.ares-memory-vault.json")
T1_DEFAULT_TTL = 3600 * 4  # 4 hours

class T1Vault:
    """T1 — Lightweight JSON working memory (auto-expiring)."""
    def __init__(self, path: str = T1_PATH):
        self.path = path
        self._data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.path):
            try:
                with open(self.path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {"entries": [], "meta": {"created": time.time()}}

    def _save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self._data, f, indent=2, default=str)

    def store(self, key: str, content: str, metadata: dict = None, ttl: int = T1_DEFAULT_TTL):
        eid = hashlib.sha256(key.encode()).hexdigest()[:16]
        now = time.time()
        entries = self._data["entries"]
        existing = [e for e in entries if e.get("id") == eid]
        if existing:
            e = existing[0]
            e.update({"content": content, "metadata": metadata or {}, "ttl": ttl, "updated_at": now})
        else:
            entries.append({"id": eid, "key": key, "content": content,
                            "metadata": metadata or {}, "ttl": ttl,
                            "created_at": now, "updated_at": now})
        self._save()
        return eid

    def get(self, key: str) -> str | None:
        eid = hashlib.sha256(key.encode()).hexdigest()[:16]
        for e in self._data["entries"]:
            if e.get("id") == eid and not self._expired(e):
                return e["content"]
        return None

    def search(self, query: str, limit: int = 10) -> list[dict]:
        q = query.lower()
        results = []
        for e in self._data["entries"]:
            if self._expired(e): continue
            if q in e["key"].lower() or q in e["content"].lower():
                results.append(e)
                if len(results) >= limit: break
        return results

    def recent(self, limit: int = 5) -> list[dict]:
        entries = [e for e in self._data["entries"] if not self._expired(e)]
        entries.sort(key=lambda e: e.get("updated_at", 0), reverse=True)
        return entries[:limit]

    def cleanup(self) -> int:
        before = len(self._data["entries"])
        self._data["entries"] = [e for e in self._data["entries"] if not self._expired(e)]
        removed = before - len(self._data["entries"])
        if removed: self._save()
        return removed

    def _expired(self, entry: dict) -> bool:
        ttl = entry.get("ttl", T1_DEFAULT_TTL)
        updated = entry.get("updated_at", entry.get("created_at", 0))
        return time.time() > updated + ttl


# ── T2: Forge Vault ──────────────────────────────────────────────────
try:
    from forge_vault import ForgeVault as _ForgeVaultImpl
    _T2_AVAILABLE = True
except ImportError:
    _T2_AVAILABLE = False

class T2Forge:
    """T2 — Persistent SQLite + FTS5 forge vault."""
    def __init__(self):
        if not _T2_AVAILABLE:
            raise ImportError("forge_vault module not available")
        self._v = _ForgeVaultImpl()

    def store(self, key: str, value: str, category: str = "general",
              tags: str = "", priority: int = 5, ttl: int = 0):
        return self._v.store(key, value, category, tags, priority, ttl)

    def get(self, key: str):
        entry = self._v.get(key)
        return entry["value"] if entry else None

    def search(self, query: str, category: str = None, limit: int = 10):
        return self._v.search(query, category, limit)

    def search_by_tag(self, tag: str, category: str = None):
        return self._v.search_by_tag(tag, category)

    def list_by_category(self, category: str, limit: int = 20):
        return self._v.list_by_category(category, limit)

    def categories(self):
        return self._v.categories()

    def delete(self, key: str):
        return self._v.delete(key)

    def cleanup(self):
        return self._v.cleanup()


# ── T3: Session Recall ───────────────────────────────────────────────
class T3Session:
    """T3 — Hermes session search (read-only, via Hermes DB)."""
    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Search past session history. Uses session_search if available."""
        return [{"source": "session_search", "note": f"Run session_search with: '{query}'"}]

    def recent(self, limit: int = 5) -> list[dict]:
        return [{"source": "session_search", "note": "Run session_search() to browse"}]


# ── Task Router ──────────────────────────────────────────────────────
TASK_ROUTES = {
    "tool_output":  "t1",    # Fast, auto-expiring tool result compression
    "scratch":      "t1",    # Ephemeral working data
    "task_temp":    "t1",    # In-progress task state

    "fact":         "t2",    # Persistent knowledge
    "brief":        "t2",    # Session or system briefs
    "project":      "t2",    # Long-lived project artifacts
    "config":       "t2",    # Configuration / identity
    "research":     "t2",    # Research findings
    "recon":        "t2",    # Reconnaissance results

    "recall":       "t3",    # Past conversation retrieval
    "history":      "t3",    # Session history
}

def get_backend(task_type: str):
    """Return the appropriate backend for a task type."""
    route = TASK_ROUTES.get(task_type, "t1")
    if route == "t1":
        return T1Vault(), "t1"
    elif route == "t2":
        if _T2_AVAILABLE:
            return T2Forge(), "t2"
        else:
            print("WARNING: Forge vault not available, falling back to T1", file=sys.stderr)
            return T1Vault(), "t1"
    elif route == "t3":
        return T3Session(), "t3"
    return T1Vault(), "t1"


# ── CLI ──────────────────────────────────────────────────────────────
def cli():
    parser = argparse.ArgumentParser(description="ARES Memory Hub — Multi-Tier Router")
    parser.add_argument("action", choices=["store", "get", "search", "route",
                                            "recent", "categories", "cleanup", "stats"])
    parser.add_argument("--task", "-t", default="scratch",
                        help="Task type: tool_output, fact, brief, recall, recon, etc.")
    parser.add_argument("--key", "-k", help="Entry key")
    parser.add_argument("--value", "-v", help="Value to store (for store action)")
    parser.add_argument("--content", "-c", help="Alias for --value")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--category", "-C", default="general", help="Forge category")
    parser.add_argument("--tags", default="", help="Comma-separated tags (T2)")
    parser.add_argument("--priority", type=int, default=5, help="Priority 1-10 (T2)")
    parser.add_argument("--ttl", type=int, default=0, help="TTL seconds (0=permanent)")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--all", action="store_true", help="Search all tiers")
    parser.add_argument("--backend", choices=["t1", "t2", "t3"], help="Force a specific tier")

    args = parser.parse_args()

    # Route or force
    if args.backend:
        tier = args.backend
        if tier == "t1":    backend = T1Vault()
        elif tier == "t2":  backend = T2Forge() if _T2_AVAILABLE else T1Vault()
        elif tier == "t3":  backend = T3Session()
    else:
        backend, tier = get_backend(args.task)

    if args.action == "store":
        value = args.value or args.content
        if not value:
            value = sys.stdin.read()
        if not value:
            print("ERROR: No value provided (use --value, --content, or pipe stdin)")
            return
        if tier == "t1":
            eid = backend.store(args.key or f"{args.task}:{int(time.time())}", value)
            print(f"Stored to T1 ({args.task}) as {eid}")
        elif tier == "t2":
            result = backend.store(args.key or f"{args.task}:{int(time.time())}",
                                   value, category=args.category, tags=args.tags,
                                   priority=args.priority, ttl=args.ttl)
            print(f"Stored to T2 ({args.task}) in category '{args.category}'")
        else:
            print("T3 is read-only")

    elif args.action == "get":
        if not args.key:
            print("ERROR: --key required for get")
            return
        value = backend.get(args.key)
        if value:
            print(value)
        else:
            print(f"Not found in {tier.upper()}")

    elif args.action == "search":
        if args.all:
            results = []
            # T1
            t1 = T1Vault()
            results.extend([{**r, "tier": "T1"} for r in t1.search(args.query, args.limit)])
            # T2
            if _T2_AVAILABLE:
                t2 = T2Forge()
                results.extend([{**r, "tier": "T2"} for r in t2.search(args.query, limit=args.limit)])
            # T3
            t3 = T3Session()
            results.extend([{**r, "tier": "T3"} for r in t3.search(args.query, args.limit)])
        else:
            results = backend.search(args.query, args.limit) if hasattr(backend, 'search') else []

        if not results:
            print(f"No results in {tier.upper()}{' (+ all tiers)' if args.all else ''}")
            return

        print(f"Results ({'all' if args.all else tier.upper()}):")
        for r in results[:args.limit]:
            tier_tag = f"[{r.pop('tier', tier.upper())}]" if 'tier' in r else f"[{tier.upper()}]"
            content = r.get("value", r.get("content", str(r)))
            print(f"  {tier_tag} {r.get('key', '?')}: {str(content)[:120]}")

    elif args.action == "route":
        backend_id = TASK_ROUTES.get(args.task, "t1")
        names = {"t1": "ARES Vault (T1 — working memory)",
                 "t2": "Forge Vault (T2 — persistent)",
                 "t3": "Session DB (T3 — episodic)"}
        print(f"Task '{args.task}' → {names.get(backend_id, backend_id)}")

    elif args.action == "recent":
        items = backend.recent(args.limit) if hasattr(backend, 'recent') else []
        if not items:
            print(f"No recent entries in {tier.upper()}")
            return
        print(f"Recent ({tier.upper()}):")
        for r in items[:args.limit]:
            content = r.get("value", r.get("content", str(r)))
            print(f"  [{r.get('key', '?')}] {str(content)[:120]}")

    elif args.action == "categories":
        if tier == "t2" and _T2_AVAILABLE:
            for cat, cnt in backend.categories():
                print(f"  {cat}: {cnt} entries")
        else:
            print("Categories only available on T2 (Forge)")

    elif args.action == "cleanup":
        if tier == "t1":
            n = backend.cleanup()
            print(f"Cleaned {n} expired entries from T1")
        elif tier == "t2":
            n = backend.cleanup()
            print(f"Cleaned {n} expired entries from T2")
        else:
            print("Cleanup not applicable for T3")

    elif args.action == "stats":
        print(f"T1 (ARES Vault):")
        t1 = T1Vault()
        t1.cleanup()
        print(f"  Active entries: {len([e for e in t1._data['entries']])}")
        print(f"T2 (Forge):")
        if _T2_AVAILABLE:
            s = T2Forge()._v.stats()
            print(f"  Entries: {s['entries']}, Categories: {s['categories']}")
        else:
            print(f"  Not available")
        print(f"T3 (Session): Available via session_search")


if __name__ == "__main__":
    cli()
