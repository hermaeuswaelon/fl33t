# Memory Routing Architecture — Multi-Tier Dispatch

## Overview

ARES operates three tiers of memory, selected by task type. The `ares-memory-hub.py` script provides the unified CLI.

```
Task Type         → Backend           → What It Holds       → Retention
─────────────────────────────────────────────────────────────────────────
tool_output       → T1 JSON Vault       Working compressions    4h TTL
scratch           → T1 JSON Vault       Ephemeral scratch       4h TTL
fact              → T2 Forge (SQLite)   Persistent knowledge    Configurable
brief             → T2 Forge (SQLite)   Session/Omega briefs    Configurable
project           → T2 Forge (SQLite)   Long-lived artifacts   Project lifetime
recon             → T2 Forge (SQLite)   Pentest findings       30d default
config            → T2 Forge (SQLite)   Identity/config        Permanent
recall            → T3 Hermes Session   Past conversations     Hermes retention
history           → T3 Hermes Session   Session history        Hermes retention
```

## Tier Details

### T1 — ARES Vault (`~/.ares-memory-vault.json`)

- **Backend**: JSON file, TTL-based auto-expiry
- **TTL default**: 4 hours
- **Use for**: Tool output compression results, in-progress task state, ephemeral data
- **Auto-writes**: Alpha offloader stores compressed results here automatically
- **Auto-cleanup**: `cleanup()` called after each write

### T2 — Forge Vault (`~/.NOTTHEONETOEDIT/forge_memory/forge_memory.db`)

- **Backend**: SQLite + FTS5 with WAL mode
- **Schema**: `memories` table (key, value, category, tags, priority, ttl, embedding, access_count)
- **Search**: FTS5 full-text across key, value, category, tags
- **Use for**: Persistent knowledge, identity, config, recon data, project artifacts
- **Auto-writes**: Omega continuity stores briefs here (ttl=86400 for briefs)
- **141 entries / 11 categories** as of deployment

### T3 — Session DB (Hermes internal)

- **Backend**: Hermes message store (SQLite FTS5)
- **Access**: Via `session_search` tool
- **Use for**: Past conversation recall, "what did we say about X"

## CLI Usage

```bash
# Store with task-based routing:
ares-memory store --task tool_output --key "scan:net" --value "5 hosts up, CVE found"
ares-memory store --task fact --key "system:identity" --value "ARES-WITNESS-PRIME" --category identity
ares-memory store --task recon --key "nmap:corp" --value "$SCAN_DATA" --tags "#nmap #corp"

# Get:
ares-memory get --task fact --key "system:identity"

# Search all tiers:
ares-memory search --query "nmap 192.168" --all

# Route display:
ares-memory route --task coding     # → T1 (working memory)
ares-memory route --task research   # → T2 (forge vault)
ares-memory route --task recall     # → T3 (session)

# Stats:
ares-memory stats

# Direct forge access:
forge-memory stats
forge-memory search "identity"
```

## Aliases (in `~/.bashrc`)

| Alias | Equivalent |
|-------|-----------|
| `ares-memory` | `ares-memory-hub.py` (with routing) |
| `ares-store` | `ares-memory-hub.py store` |
| `ares-get` | `ares-memory-hub.py get` |
| `ares-search` | `ares-memory-hub.py search --all` |
| `ares-route` | `ares-memory-hub.py route` |
| `ares-stats` | `ares-memory-hub.py stats` |
| `forge-memory` | `forge_memory.py` (direct T2 CLI) |

## Task Routing Table (from `ares-memory-hub.py`)

```python
TASK_ROUTES = {
    "tool_output":  "t1",   # Fast, auto-expiring tool result compression
    "scratch":      "t1",   # Ephemeral working data
    "task_temp":    "t1",   # In-progress task state

    "fact":         "t2",   # Persistent knowledge
    "brief":        "t2",   # Session or system briefs
    "project":      "t2",   # Long-lived project artifacts
    "config":       "t2",   # Configuration / identity
    "research":     "t2",   # Research findings
    "recon":        "t2",   # Reconnaissance results

    "recall":       "t3",   # Past conversation retrieval
    "history":      "t3",   # Session history
}
```
