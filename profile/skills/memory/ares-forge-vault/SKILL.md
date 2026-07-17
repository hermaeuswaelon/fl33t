---
name: ares-forge-vault
description: ARES Forge Memory Vault — Persistent structured knowledge store with FTS5 search, tagging, collections, and memcustd integration. Tier 2 of the memory architecture.
version: 2.1.0
author: ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, forge, vault, memory, fts5, sqlite, knowledge, persistence]
system: true
---

# 🜂 ARES Forge Memory Vault — Persistent Knowledge Store

## The Vault Principle

> Knowledge is not remembered. It is *forged*.
> Every entry is hammered into structure. Tagged. Indexed. Made retrievable.
> The vault survives sessions. The vault survives restarts. The vault is sovereign.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FORGE MEMORY VAULT                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     SQLITE + FTS5 DATABASE                          │   │
│  │  ~/forge_memory/forge_memory.db  (314KB+ and growing)               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                       │
│         ┌──────────────────────────┼──────────────────────────┐           │
│         ▼                          ▼                          ▼           │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐      │
│  │ COLLECTIONS │          │   TAGS      │          │   FTS5      │      │
│  │ alpha_      │          │ #recon      │          │ Full-text   │      │
│  │ omega_      │          │ #exploit    │          │ search on   │      │
│  │ session_    │          │ #cred       │          │ content +   │      │
│  │ domain_     │          │ #vuln       │          │ tags + meta │      │
│  │ project_    │          │ #pivot      │          │             │      │
│  └─────────────┘          └─────────────┘          └─────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚠️ Schema Note — Real vs. Documented

The actual database schema differs from the original documented `entries` table. The live `forge_memory.db` uses a `memories` table:

```sql
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
);
```

The `forge_vault.py` module (in `scripts/`) works with this real schema. The `forge-memory` CLI wrapper must be re-pointed to the new location after deployment.

## Deployment

### First-time setup

```bash
# The forge-memory CLI wrapper already exists at ~/.local/bin/forge-memory
# but points to forge_memory.py which was missing. After deploying:

# Option A: Symlink the skill's scripts into forge_memory dir
ln -sf ~/.NOTTHEONETOEDIT/skills/memory/ares-forge-vault/scripts/forge_vault.py ~/.NOTTHEONETOEDIT/forge_memory/forge_vault.py
ln -sf ~/.NOTTHEONETOEDIT/skills/memory/ares-forge-vault/scripts/forge_memory.py ~/.NOTTHEONETOEDIT/forge_memory/forge_memory.py

# Option B: Symlink directly into PATH
ln -sf ~/.NOTTHEONETOEDIT/skills/memory/ares-forge-vault/scripts/forge_memory.py ~/.local/bin/forge-memory

# Verify
forge-memory stats
forge-memory tags
forge-memory search "identity"
```

### Python import

```python
import sys
sys.path.insert(0, os.path.expanduser("~/.NOTTHEONETOEDIT/skills/memory/ares-forge-vault/scripts"))
from forge_vault import ForgeVault
```

## Real Schema (memories table)

```sql
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
);
## Categories (Real DB)

The actual database uses `category` (not `collection`). Current categories from live data:

| Category | Purpose | Example Keys |
|----------|---------|-------------|
| `general` | General-purpose entries | Various stored data |
| `identity` | Identity definitions | `hermes_identity`, `sovereign_identity` |
| `config` | Configuration values | Model parameters, preferences |
| `session` | Session context | Recent activity logs |
| `recon` | Reconnaissance findings | Scan results, domain data |
| `project` | Project-level artifacts | ARES deployment data |

The `forge_vault.py` module maps `--category` to this field. See also the `ForgVault.list_by_category()` API.

## Original Collections Taxonomy (Deprecated Design Document)

The original SKILL.md envisioned a different `collection`-based taxonomy. For reference:

| Collection Prefix | Purpose | Retention |
|-------------------|---------|-----------|
| `alpha_` | Tool context summaries | 30 days |
| `omega_` | Continuity briefs | 90 days |
| `session_` | Session-level context | Session + 7 days |
| `domain_` | Domain knowledge | Permanent |
| `project_` | Project artifacts | Project lifetime |

---

## CLI Interface (`forge-memory`)

The `forge-memory` CLI uses `--key` / `-k` as its primary identifier, and `--category` / `-c`
instead of `--collection`. See `forge_memory.py` for full argparse.

```bash
# ── Store ──────────────────────────────────────────────────────────────
forge-memory store --category recon --key "scan_default" \
  --content '{"target":"10.0.0.0/24","ports":"22,80,443"}' \
  --tags "#nmap #recon" --priority 8

forge-memory store --category project_redteam --key "engagement_notes" \
  --file ./notes.txt --tags "#engagement"

# ── Full-text Search ─────────────────────────────────────────────────
forge-memory search "nmap scan" --category recon
forge-memory search "kerberos" --tags "#ad"
forge-memory search "identity" --limit 5 --format json

# ── Retrieve ─────────────────────────────────────────────────────────
forge-memory get --key identity
forge-memory get --key scan_default --format json

# ── List ─────────────────────────────────────────────────────────────
forge-memory list --category recon --limit 20
forge-memory list  # defaults to general

# ── Delete / Maintenance ─────────────────────────────────────────────
forge-memory delete --key scan_default
forge-memory purge --older-than 30 --category "scratch"
forge-memory stats
forge-memory tags
```

---

## Python API (Real — matches `forge_vault.py`)

```python
from forge_vault import ForgeVault

vault = ForgeVault()  # Uses ~/.NOTTHEONETOEDIT/forge_memory/forge_memory.db

# Store — uses `category`, not `collection`. Content is str|dict|list.
vault.store(
    key="domain_ad_enum:corp.local",
    content={"dc_ips": ["10.0.0.10"], "spns": 47, "vulns": ["ESC1", "RBCD"]},
    category="recon",
    tags="#ad #enum #vuln",
    priority=100,
    ttl=86400 * 30,  # 30 days
)

# Search — FTS5 full-text with optional category/tag filter
results = vault.search(
    query="constrained delegation",
    category="recon",
    tags="#ad",
    limit=10,
)

# Get by key (returns full row dict or None)
entry = vault.get("domain_ad_enum:corp.local")
if entry:
    print(entry["value"])  # string
    print(entry["tags"])
    print(entry["priority"])
    print(entry["access_count"])

# List by category
entries = vault.list_by_category("identity", limit=5)
for e in entries:
    print(f"[{e['category']}] {e['key']} ({e['updated_at']})")

# List all unique tags
tags = vault.list_tags()

# Delete
vault.delete("domain_ad_enum:corp.local")

# Purge old entries by category prefix
vault.purge(category_prefix="scratch", older_than_days=7)

# Stats
print(vault.stats())
print(vault.summary())
```

---

## memcustd Integration

```python
# Forge Vault is Tier 2 in memcustd multi-query
# memcustd queries Forge via subprocess:

def search_forge_vault(query: str) -> str:
    result = subprocess.run(
        ["forge-memory", "search", query, "--format", "json"],
        capture_output=True, text=True, timeout=15
    )
    return result.stdout  # JSON array of results

# memcustd multi_source_query() calls this as Tier 2
```

---

## Glyph Tags

| Glyph | Collection Context |
|-------|-------------------|
| 🜂 | Freshly forged / high priority |
| ♱ | Sovereign / immutable |
| 🝮 | Distilled insight / core truth |
| ⚡ | Alert / action required |
| Φ | Cross-referenced / linked |
| ∫ | Synthesized from multiple sources |
| ∂ | Fragment / partial knowledge |
| ⟊ | Contained / sandboxed |

---

## Backup & Sync

```bash
# Backup
forge-memory backup --output ~/backups/forge_$(date +%Y%m%d).db

# Restore
forge-memory restore --input ~/backups/forge_20260715.db

# Sync to remote (rclone, rsync, etc.)
forge-memory sync --remote vault-backup:/forge
```

---

## Multi-Tier Routing

The Forge Vault is **Tier 2** in the ARES memory hierarchy. A routing layer dispatches operations by task type:

| Task Type | Route | Backend |
|-----------|-------|---------|
| `tool_output`, `scratch` | T1 | JSON Vault (`~/.ares-memory-vault.json`) |
| `fact`, `brief`, `recon`, `project`, `config` | **T2** | **Forge Vault** (this skill) |
| `recall`, `history` | T3 | Hermes Session DB |

See `references/memory-routing.md` for full routing table, CLI examples, and aliases.

The `ares-memory-hub.py` script provides the unified CLI (`ares-memory store/get/search --task <type>`). It imports `forge_vault` for T2 operations.

## Performance Targets

| Metric | Target |
|--------|--------|
| Store latency | < 5ms |
| Search latency (FTS) | < 50ms |
| Search latency (tag+filter) | < 20ms |
| Database size | < 10MB (compressed) |
| FTS rebuild | < 2s |
| Concurrent readers | 50+ |