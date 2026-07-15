#!/usr/bin/env python3
"""
Forge Vault — Persistent Memory Store (Tier 2)
===============================================
SQLite + FTS5 memory backend with embeddings, categories, tags, TTL.
Wraps the existing forge_memory.db at ~/.NOTTHEONETOEDIT/forge_memory/

Usage:
  from forge_vault import ForgeVault
  v = ForgeVault()
  v.store(key="my_key", value="data", category="recon")
  results = v.search("query")
"""

import os
import json
import time
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

VAULT_DIR = os.path.expanduser("~/.NOTTHEONETOEDIT/forge_memory")
DEFAULT_DB = os.path.join(VAULT_DIR, "forge_memory.db")


class ForgeVault:
    """Tier 2 memory — persistent, searchable, tagged, with TTL."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DEFAULT_DB
        self._ensure_db()
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row

    def _ensure_db(self):
        """Create DB and tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        # Table creation is handled on first write if schema missing
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories'")
        if not c.fetchone():
            c.execute("""
                CREATE TABLE memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    value TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'general',
                    priority INTEGER NOT NULL DEFAULT 5,
                    tags TEXT NOT NULL DEFAULT '',
                    ttl INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                    access_count INTEGER NOT NULL DEFAULT 0,
                    last_access TEXT NOT NULL DEFAULT (datetime('now')),
                    checksum TEXT DEFAULT '',
                    embedding BLOB DEFAULT NULL
                )
            """)
            c.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                    key, value, category, tags,
                    content='memories', content_rowid='id'
                )
            """)
            # FTS triggers for auto-sync
            c.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
                    INSERT INTO memories_fts(rowid, key, value, category, tags)
                    VALUES (new.id, new.key, new.value, new.category, new.tags);
                END
            """)
            c.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
                    INSERT INTO memories_fts(memories_fts, rowid, key, value, category, tags)
                    VALUES ('delete', old.id, old.key, old.value, old.category, old.tags);
                END
            """)
            c.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
                    INSERT INTO memories_fts(memories_fts, rowid, key, value, category, tags)
                    VALUES ('delete', old.id, old.key, old.value, old.category, old.tags);
                    INSERT INTO memories_fts(rowid, key, value, category, tags)
                    VALUES (new.id, new.key, new.value, new.category, new.tags);
                END
            """)
            conn.commit()
        conn.close()

    def store(self, key: str, value: str, category: str = "general",
              tags: str = "", priority: int = 5, ttl: int = 0) -> bool:
        """Store or update an entry. Returns True if new, False if updated."""
        checksum = str(hash(value))
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        try:
            c = self._conn.cursor()
            c.execute("SELECT id FROM memories WHERE key = ?", (key,))
            existing = c.fetchone()
            if existing:
                c.execute("""
                    UPDATE memories SET value=?, category=?, tags=?, priority=?,
                        ttl=?, updated_at=?, checksum=?
                    WHERE key=?
                """, (value, category, tags, priority, ttl, now, checksum, key))
                return False
            else:
                c.execute("""
                    INSERT INTO memories (key, value, category, tags, priority, ttl, checksum)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (key, value, category, tags, priority, ttl, checksum))
                self._conn.commit()
                return True
        except sqlite3.Error as e:
            return f"ERROR: {e}"

    def get(self, key: str) -> dict | None:
        """Retrieve by key. Returns None if not found or expired."""
        c = self._conn.cursor()
        c.execute("SELECT * FROM memories WHERE key = ?", (key,))
        row = c.fetchone()
        if not row:
            return None
        entry = dict(row)
        if self._is_expired(entry):
            return None
        # Update access count
        c.execute("""
            UPDATE memories SET access_count = access_count + 1,
                last_access = datetime('now')
            WHERE id = ?
        """, (entry['id'],))
        self._conn.commit()
        return entry

    def search(self, query: str, category: str = None, limit: int = 10) -> list[dict]:
        """FTS5 full-text search across keys, values, categories, tags."""
        c = self._conn.cursor()
        if category:
            sql = """
                SELECT m.* FROM memories m
                JOIN memories_fts fts ON m.id = fts.rowid
                WHERE memories_fts MATCH ? AND m.category = ?
                ORDER BY rank
                LIMIT ?
            """
            c.execute(sql, (query, category, limit))
        else:
            sql = """
                SELECT m.* FROM memories m
                JOIN memories_fts fts ON m.id = fts.rowid
                WHERE memories_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """
            c.execute(sql, (query, limit))
        return [dict(r) for r in c.fetchall() if not self._is_expired(dict(r))]

    def search_by_tag(self, tag: str, category: str = None, limit: int = 20) -> list[dict]:
        """Search entries by tag substring."""
        c = self._conn.cursor()
        if category:
            c.execute("""
                SELECT * FROM memories
                WHERE tags LIKE ? AND category = ?
                ORDER BY priority DESC, updated_at DESC
                LIMIT ?
            """, (f"%{tag}%", category, limit))
        else:
            c.execute("""
                SELECT * FROM memories
                WHERE tags LIKE ?
                ORDER BY priority DESC, updated_at DESC
                LIMIT ?
            """, (f"%{tag}%", limit))
        return [dict(r) for r in c.fetchall() if not self._is_expired(dict(r))]

    def list_by_category(self, category: str, limit: int = 20) -> list[dict]:
        """List entries in a category."""
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM memories
            WHERE category = ?
            ORDER BY priority DESC, updated_at DESC
            LIMIT ?
        """, (category, limit))
        return [dict(r) for r in c.fetchall() if not self._is_expired(dict(r))]

    def categories(self) -> list[tuple[str, int]]:
        """List all categories with entry counts."""
        c = self._conn.cursor()
        c.execute("""
            SELECT category, COUNT(*) as cnt FROM memories
            GROUP BY category ORDER BY cnt DESC
        """)
        return [(r['category'], r['cnt']) for r in c.fetchall()]

    def delete(self, key: str) -> bool:
        """Remove an entry by key."""
        c = self._conn.cursor()
        c.execute("DELETE FROM memories WHERE key = ?", (key,))
        self._conn.commit()
        return c.rowcount > 0

    def cleanup(self) -> int:
        """Purge expired entries."""
        count = 0
        c = self._conn.cursor()
        for row in c.execute("SELECT id, ttl, updated_at FROM memories WHERE ttl > 0"):
            if self._is_expired(dict(row)):
                c.execute("DELETE FROM memories WHERE id = ?", (row['id'],))
                count += 1
        self._conn.commit()
        return count

    def stats(self) -> dict:
        """Return statistics."""
        c = self._conn.cursor()
        c.execute("SELECT COUNT(*) FROM memories")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT category) FROM memories")
        cats = c.fetchone()[0]
        return {"entries": total, "categories": cats}

    def _is_expired(self, entry: dict) -> bool:
        if not entry.get('ttl') or entry['ttl'] <= 0:
            return False
        updated = entry.get('updated_at', entry.get('created_at', ''))
        if not updated:
            return False
        try:
            updated_ts = datetime.strptime(updated, "%Y-%m-%d %H:%M:%S").timestamp()
        except (ValueError, TypeError):
            return False
        return time.time() > updated_ts + entry['ttl']

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
