#!/usr/bin/env python3
"""
ARES Shared Memory Layer — Forge Vault Interface
=================================================
Persistent shared memory that Alpha (offloader) and Omega (continuity) write to,
and the Prime agent reads from. Think of it as inter-agent scratchpad storage.

Works as a JSON document store with time-based eviction.

Usage:
  from ares_memory import MemoryVault

  vault = MemoryVault()
  vault.store("tool:find_files", compressed_result, ttl=3600)
  recent = vault.search("nmap")
  all_keys = vault.keys()
  vault.cleanup()  # evict expired entries
"""

import os
import json
import time
import hashlib
from datetime import datetime, timezone

VAULT_PATH = os.path.expanduser("~/.ares-memory-vault.json")
DEFAULT_TTL = 3600 * 4  # 4 hours default retention


class MemoryVault:
    """Simple JSON-file-backed memory store with TTL and search."""

    def __init__(self, path: str = VAULT_PATH):
        self.path = path
        self._data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {"entries": [], "meta": {"created": time.time()}}

    def _save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self._data, f, indent=2, default=str)

    def store(
        self,
        key: str,
        content: str,
        metadata: dict | None = None,
        ttl: int = DEFAULT_TTL,
    ) -> str:
        """
        Store an entry. Returns the entry ID.
        If key already exists, updates it (preserves original created_at).
        """
        entry_id = hashlib.sha256(key.encode()).hexdigest()[:16]
        now = time.time()

        entries = self._data["entries"]
        existing = [e for e in entries if e.get("id") == entry_id]

        if existing:
            entry = existing[0]
            entry["content"] = content
            entry["metadata"] = metadata or {}
            entry["ttl"] = ttl
            entry["updated_at"] = now
        else:
            entry = {
                "id": entry_id,
                "key": key,
                "content": content,
                "metadata": metadata or {},
                "ttl": ttl,
                "created_at": now,
                "updated_at": now,
            }
            entries.append(entry)

        self._save()
        return entry_id

    def get(self, key: str) -> dict | None:
        """Retrieve entry by key. Returns None if not found or expired."""
        entry_id = hashlib.sha256(key.encode()).hexdigest()[:16]
        for e in self._data["entries"]:
            if e.get("id") == entry_id:
                if self._is_expired(e):
                    return None
                return e
        return None

    def search(self, query: str, max_results: int = 10) -> list[dict]:
        """Full-text search in keys and content. Returns non-expired entries."""
        query_lower = query.lower()
        results = []
        for e in self._data["entries"]:
            if self._is_expired(e):
                continue
            if query_lower in e["key"].lower() or query_lower in e["content"].lower():
                results.append(e)
            if len(results) >= max_results:
                break
        return results

    def recent(self, limit: int = 10) -> list[dict]:
        """Most recently updated non-expired entries."""
        entries = [e for e in self._data["entries"] if not self._is_expired(e)]
        entries.sort(key=lambda e: e.get("updated_at", 0), reverse=True)
        return entries[:limit]

    def keys(self, prefix: str = "") -> list[str]:
        """List all non-expired keys, optionally filtered by prefix."""
        return [
            e["key"]
            for e in self._data["entries"]
            if not self._is_expired(e) and e["key"].startswith(prefix)
        ]

    def delete(self, key: str) -> bool:
        """Remove an entry by key."""
        entry_id = hashlib.sha256(key.encode()).hexdigest()[:16]
        before = len(self._data["entries"])
        self._data["entries"] = [
            e for e in self._data["entries"] if e.get("id") != entry_id
        ]
        if len(self._data["entries"]) < before:
            self._save()
            return True
        return False

    def cleanup(self) -> int:
        """Evict all expired entries. Returns count removed."""
        before = len(self._data["entries"])
        self._data["entries"] = [
            e for e in self._data["entries"] if not self._is_expired(e)
        ]
        removed = before - len(self._data["entries"])
        if removed:
            self._save()
        return removed

    def _is_expired(self, entry: dict) -> bool:
        ttl = entry.get("ttl", DEFAULT_TTL)
        updated = entry.get("updated_at", entry.get("created_at", 0))
        return time.time() > updated + ttl

    def summary(self) -> str:
        """Return a markdown summary of recent entries for the Prime."""
        self.cleanup()
        recent = self.recent(8)
        if not recent:
            return "_Memory vault is empty._"

        lines = []
        lines.append("### 🧠 ARES Memory Vault — Recent Entries")
        for e in recent:
            age_mins = int((time.time() - e.get("updated_at", 0)) / 60)
            content_preview = e["content"][:120].replace("\n", " ")
            lines.append(f"- **{e['key']}** ({age_mins}m ago): {content_preview}…")
        return "\n".join(lines)


# ── CLI Interface ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ARES Shared Memory Vault")
    parser.add_argument("action", choices=["store", "get", "search", "recent", "keys", "delete", "cleanup", "summary"])
    parser.add_argument("--key", "-k", help="Entry key")
    parser.add_argument("--content", "-c", help="Content to store")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--ttl", type=int, default=DEFAULT_TTL, help="TTL in seconds")
    parser.add_argument("--prefix", "-p", default="", help="Key prefix filter")
    parser.add_argument("--input", "-i", help="Read content from file")

    args = parser.parse_args()
    vault = MemoryVault()

    if args.action == "store":
        if args.input:
            with open(args.input) as f:
                content = f.read()
        elif args.content:
            content = args.content
        else:
            content = sys.stdin.read()
        eid = vault.store(args.key or "unnamed", content, ttl=args.ttl)
        print(f"Stored as {eid}")

    elif args.action == "get":
        entry = vault.get(args.key)
        if entry:
            print(entry["content"])
        else:
            print("Not found or expired", file=sys.stderr)

    elif args.action == "search":
        results = vault.search(args.query)
        for r in results:
            print(f"[{r['key']}] {r['content'][:200]}")

    elif args.action == "recent":
        for r in vault.recent():
            print(f"[{r['key']}] ({int((time.time()-r['updated_at'])/60)}m ago)")

    elif args.action == "keys":
        for k in vault.keys(prefix=args.prefix):
            print(k)

    elif args.action == "delete":
        vault.delete(args.key)
        print("Deleted" if vault.delete(args.key) else "Not found")

    elif args.action == "cleanup":
        n = vault.cleanup()
        print(f"Cleaned up {n} expired entries")

    elif args.action == "summary":
        print(vault.summary())
