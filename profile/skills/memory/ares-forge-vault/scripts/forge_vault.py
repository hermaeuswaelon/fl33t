#!/usr/bin/env python3
"""
forge_vault — ARES Forge Memory Vault Python Module
====================================================
SQLite-backed persistent memory with FTS5 search, tag-based filtering,
TTL-based eviction, access tracking, and optional embedding storage.

Real DB schema (memories table, not entries):
  key, value, category, tags, priority, ttl, embedding, checksum, access_count

Usage:
  from forge_vault import ForgeVault
  vault = ForgeVault()
  vault.store("my:key", {"data": 42}, category="recon", tags="#nmap #scan")
  results = vault.search("nmap scan")
"""

import os
import json
import time
import sqlite3
import hashlib

DB_PATH = os.path.expanduser("~/.NOTTHEONETOEDIT/forge_memory/forge_memory.db")
DEFAULT_TTL = 86400 * 7  # 7 days


class ForgeVault:
    """Persistent SQLite-backed memory store with FTS5 search."""

    def __init__(self, db_path: str = DB_PATH):
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=5000")

    def store(
        self,
        key: str,
        content: dict | str | list,
        category: str = "general",
        tags: str = "",
        priority: int = 5,
        ttl: int = DEFAULT_TTL,
        embedding: bytes | None = None,
    ) -> dict:
        """Store or update a memory entry."""
        if isinstance(content, (dict, list)):
            content = json.dumps(content)
        checksum = hashlib.sha256(content.encode()).hexdigest()
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        existing = self._conn.execute(
            "SELECT id FROM memories WHERE key = ?", (key,)
        ).fetchone()

        if existing:
            self._conn.execute(
                """UPDATE memories SET value=?, tags=?, priority=?, ttl=?,
                   updated_at=?, checksum=?, embedding=COALESCE(?, embedding)
                   WHERE key=?""",
                (content, tags, priority, ttl, now, checksum, embedding, key),
            )
        else:
            self._conn.execute(
                """INSERT INTO memories (key, value, category, tags, priority, ttl,
                   created_at, updated_at, checksum, embedding)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (key, content, category, tags, priority, ttl, now, now, checksum, embedding),
            )

        self._conn.commit()
        return {"key": key, "category": category, "checksum": checksum}

    def get(self, key: str) -> dict | None:
        """Retrieve entry by key. Returns None if not found or expired."""
        row = self._conn.execute(
            "SELECT * FROM memories WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            return None
        if self._is_expired(row):
            self._conn.execute("DELETE FROM memories WHERE id = ?", (row["id"],))
            self._conn.commit()
            return None
        self._conn.execute(
            "UPDATE memories SET access_count = access_count + 1, last_access = ? WHERE id = ?",
            (time.strftime("%Y-%m-%d %H:%M:%S"), row["id"]),
        )
        self._conn.commit()
        return dict(row)

    def search(
        self,
        query: str,
        category: str | None = None,
        tags: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Full-text search via FTS5. Filters by category and/or tags if provided."""
        self._expire_stale()
        conditions = ["memories_fts MATCH ?"]
        params = [query]
        if category:
            conditions.append("category = ?")
            params.append(category)
        if tags:
            conditions.append("tags LIKE ?")
            params.append(f"%{tags}%")
        sql = f"""SELECT m.* FROM memories m
                  JOIN memories_fts f ON m.id = f.rowid
                  WHERE {' AND '.join(conditions)}
                  ORDER BY m.priority DESC, m.updated_at DESC
                  LIMIT ?"""
        params.append(limit)
        return [dict(row) for row in self._conn.execute(sql, params).fetchall()]

    def list_by_category(self, category: str, limit: int = 20) -> list[dict]:
        """List entries in a category, most recent first."""
        self._expire_stale()
        rows = self._conn.execute(
            "SELECT * FROM memories WHERE category = ? ORDER BY updated_at DESC LIMIT ?",
            (category, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def list_tags(self) -> list[str]:
        """List all unique tags across entries."""
        rows = self._conn.execute(
            "SELECT DISTINCT tags FROM memories WHERE tags != ''"
        ).fetchall()
        result = set()
        for r in rows:
            for tag in r["tags"].split(","):
                tag = tag.strip()
                if tag:
                    result.add(tag)
        return sorted(result)

    def delete(self, key: str) -> bool:
        """Remove an entry by key."""
        cur = self._conn.execute("DELETE FROM memories WHERE key = ?", (key,))
        self._conn.commit()
        return cur.rowcount > 0

    def purge(self, category_prefix: str = "", older_than_days: int = 30):
        """Purge expired or old entries by category prefix."""
        sql = "DELETE FROM memories WHERE 1=1"
        params = []
        if category_prefix:
            sql += " AND category LIKE ?"
            params.append(f"{category_prefix}%")
        if older_than_days:
            sql += " AND updated_at < datetime('now', ?)"
            params.append(f"-{older_than_days} days")
        cur = self._conn.execute(sql, params)
        self._conn.commit()
        return cur.rowcount

    def stats(self) -> dict:
        """Return aggregate statistics."""
        self._expire_stale()
        total = self._conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        by_cat = self._conn.execute(
            "SELECT category, COUNT(*) as cnt FROM memories GROUP BY category ORDER BY cnt DESC"
        ).fetchall()
        by_tag = self._conn.execute(
            "SELECT tags, COUNT(*) as cnt FROM memories WHERE tags != '' GROUP BY tags ORDER BY cnt DESC LIMIT 10"
        ).fetchall()
        oldest = self._conn.execute(
            "SELECT MIN(created_at) FROM memories"
        ).fetchone()[0]
        newest = self._conn.execute(
            "SELECT MAX(created_at) FROM memories"
        ).fetchone()[0]
        db_size = os.path.getsize(self._db_path) if os.path.exists(self._db_path) else 0
        return {
            "total_entries": total,
            "by_category": [dict(r) for r in by_cat],
            "top_tags": [dict(r) for r in by_tag],
            "oldest": oldest,
            "newest": newest,
            "db_size_bytes": db_size,
        }

    def summary(self) -> str:
        """Markdown summary for prime consumption."""
        s = self.stats()
        lines = [
            "### 🔨 Forge Memory Vault",
            f"- **Entries**: {s['total_entries']}",
            f"- **DB Size**: {s['db_size_bytes'] // 1024}KB",
            f"- **Date Range**: {s['oldest']} → {s['newest']}",
        ]
        if s["by_category"]:
            lines.append("- **By Category**:")
            for c in s["by_category"][:5]:
                lines.append(f"  - `{c['category']}`: {c['cnt']}")
        if s["top_tags"]:
            lines.append("- **Top Tags**:")
            for t in s["top_tags"][:5]:
                lines.append(f"  - `{t['tags']}`: {t['cnt']}")
        return "\n".join(lines)

    def _expire_stale(self):
        """Remove entries with non-zero TTL that have expired."""
        self._conn.execute(
            "DELETE FROM memories WHERE ttl > 0 AND "
            "datetime(updated_at, '+' || ttl || ' seconds') < datetime('now')"
        )
        self._conn.commit()

    def _is_expired(self, row: sqlite3.Row) -> bool:
        if row["ttl"] <= 0:
            return False
        updated = row["updated_at"]
        # Simple check: parse and compare
        try:
            import datetime
            updated_dt = datetime.datetime.strptime(updated, "%Y-%m-%d %H:%M:%S")
            return (datetime.datetime.now() - updated_dt).total_seconds() > row["ttl"]
        except Exception:
            return False

    def close(self):
        self._conn.close()
