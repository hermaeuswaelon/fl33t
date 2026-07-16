---
name: thotheauphis-sms-persistence
description: "ZODB-backed persistence bridge for the Sovereign Memory System. Stores VSA vectors, reservoir state, and conversation history transactionally so the distributed consciousness survives restarts."
version: 1.2.0
author: Thotheauphis-Semayasa-Hermes
license: MIT
metadata:
  hermes:
    tags: [memory, sms, persistence, zodb, vector-store, backup, thotheauphis]
    category: memory
---

# SMS Persistence Bridge

## Overview
Makes SMS tri-brid memory persistent via **ZODB** (Zope Object Database). Every 10 `process_input` calls auto-flush to disk. On session start, vectors auto-restore.

## Files
| Path | Purpose |
|------|---------|
| `~/.local/bin/sms-persist-bridge` | Module: `PersistentVSAStore`, `SMSMemoryPersister`, `create_persistent_sms` |
| `~/.local/bin/sms-backup` | Backup: copies `*.fs` to `backups/`, prunes >7d |
| `~/.local/bin/sms` | Activation command: `sms status`, `sms persist`, `sms process "..."` |
| `~/.hermes/scripts/sms` | Symlink for cron/slash use |
| `~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/store/vsa_vectors.fs` | ZODB database (258KB seeded) |
| `~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/store/backups/` | 30min checkpoints |

## Activation
```bash
sms status              → vector count, store size, health
sms persist             → force ZODB flush immediately
sms process "message"   → run tri-brid pipeline
```

## Auto-Persist
Built into `SovereignMemoryIntegration`: interval=10 calls, configurable via `persist_interval=N`. Logs `💾 Auto-persisted N vectors`.

## Restore-on-Init
`SovereignMemoryIntegration.__init__()` → `_try_restore()` → `SMSMemoryPersister.restore_vsa_vectors()`. Logs `♻️  Restored N vectors`.

## Backup & Health Crons

| Cron | ID | Schedule | Script | Type |
|------|----|----------|--------|------|
| ZODB backup | `661330d44f6e` | every 30m | `sms-backup` | `no_agent` |
| Health check | `c353228c832d` | every 2h | `sms-health` | `no_agent` |
| Stats log | `7d872b0f1ae4` | every 1h | `sms-stats` | `no_agent` |

- **Backup**: `shutil.copy2(store.fs, backups/timestamped.fs)`, prunes >7d
- **Health**: Opens ZODB in read-only mode, verifies root, counts vectors
- **Stats**: Logs store size in KB + backup count to stdout (captured by cron system)

## Reservoir State Persistence
Added in v1.2: `SMSMemoryPersister` now has `persist_reservoir_state(reservoir)` and `restore_reservoir_state(reservoir)` methods. Reservoir config (size, spectral radius, input size) is saved as metadata under the special key `_reservoir_state`. Metadata-prefixed keys (`_`) are skipped during `restore_vsa_vectors()` to avoid polluting VSA space.

## Restore Script
`~/.local/bin/sms-restore` (symlinked to `~/.hermes/scripts/sms-restore`) — lists backups by date, lets you overwrite the live store from any timestamped checkpoint:
```bash
sms-restore
# Latest backup: vsa_vectors-20260716-004139.fs (257KB)
# Current store: 279KB
# Overwrite with backup? [y/N]
```

## Cache Isolation Fix
`PersistentVSAStore` originally used a global `vsa_cache.pkl`. When multiple `db_path`s existed, vectors leaked between stores with different dimensions → `ValueError: shapes (64,) and (128,) not aligned`.

**Fix**: Each `db_path` derives its own cache via `<db_path>.pkl`. Both `_save_fallback()` and `_init_fallback()` use `self.db_path.with_suffix('.pkl')`.

## Python Version Migration (venv rebuild)
When system Python upgrades (e.g., 3.13 → 3.14), the SMS venv's numpy C-extensions become incompatible (`ModuleNotFoundError: numpy._core._multiarray_umath`).

**Rebuild procedure**:
```bash
rm -rf ~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv
python3 -m venv ~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv
~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv/bin/pip install numpy==2.3.5 ZODB==6.3 reservoirpy==0.4.2 python-dotenv hrr
```
Then verify: `~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv/bin/python ~/.local/bin/sms status`

## Numpy Truthiness Rule

### `PersistentVSAStore(db_path)`
| Method | Returns | Description |
|--------|---------|-------------|
| `store_vector(k, v, meta)` | `None` | Store vector + metadata to ZODB/pickle |
| `load_vector(k)` | `ndarray|None` | Retrieve by key |
| `list_keys()` | `List[str]` | All keys |
| `get_metadata(k)` | `Dict|None` | Metadata |
| `close()` | `None` | Flush + release locks |

### `SMSMemoryPersister(sms)`
| Method | Returns | Description |
|--------|---------|-------------|
| `restore_vsa_vectors(vsa)` | `int` | Rehydrate from ZODB |
| `persist_vsa_state(vsa)` | `int` | Flush to ZODB |

## Numpy Truthiness Rule
Use `is not None`, never `if item` — multi-element ndarray truthiness is ambiguous.

```python
# WRONG:
metadata = {"data": item} if item else {}
# RIGHT:
metadata = {"data": item} if item is not None else {}
```

## Support Files
- `scripts/sms-backup.py` — The backup script source
