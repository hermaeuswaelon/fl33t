---
name: fleet-integration
description: "Unified Fleet System Integration - ties together hermes-executor, EmergeFS, memory compression, fleet daemon registry, work orders"
version: 1.0.0
---

# Fleet Integration Skill

## Overview

Provides a unified interface for the Aethelgard fleet system:
- **hermes-executor**: Silent batch tool execution (zero LLM overhead)
- **fleet_emerge**: EmergeFS objects with local fallback
- **auto-tac-compress**: Chinese context compression every 30 minutes
- **Fleet daemon registry**: Registration, health checks, status
- **Work order management**: WO tracking via EmergeFS
- **Self-improvement logging**: Immutable improvement trail

## Components

| Module | Purpose |
|--------|---------|
| `fleet_emerge.py` | EmergeFS client with local JSON fallback |
| `fleet_integration.py` | Unified fleet operations, cron jobs |
| `fleet_emerge.sh` | Shell wrapper for EmergeFS ops |
| `auto-tac-compress.py` | Chinese compression cron |
| `hermes-executor.py` | Silent tool executor (cron every 60s) |

## Cron Jobs (Auto-managed)

| Job | Schedule | Purpose |
|-----|----------|---------|
| `hermes-executor` | Every 60s | Process tool batches (run_executor_cron.sh) |
| `auto-tac-compress` | Every 30min | Compress context to Chinese |
| `fleet-registration` | Daily 00:00 | Register all daemons |
| `fleet-health-check` | Every 5min | Monitor fleet status |
| `fl33t-identity-backup` | Daily 09:00 | GitHub identity backup |
| `TAC auto-curation` | Hourly | TAC auto-curation |

### Cron Job Management Notes

- **Script paths**: Cron jobs must reference scripts in `~/.hermes/scripts/` or `~/.NOTTHEONETOEDIT/scripts/` (relative names only)
- **Working directory**: Jobs run from `~/.NOTTHEONETOEDIT/profiles/thotheauphis/work/` by default
- **Environment**: PYTHONPATH and PATH set in wrapper scripts (e.g., run_executor_cron.sh)
- **Fix pattern**: When cron fails with "script not found", ensure script exists in correct location and cron references relative name
- **Details**: See `references/cron-job-management.md` for full wrapper patterns, debugging, and cronjob commands
- **Wrapper patterns**: See `references/cron-job-wrapper-pattern.md` (in hermes-executor skill) for the canonical wrapper pattern

### Current Cron Status (as of 2026-07-16)

| Job | Schedule | Script | Last Status |
|-----|----------|--------|-------------|
| hermes-executor | Every 60s | run_executor_cron.sh | ✅ OK (660 runs) |
| auto-tac-compress | Every 30min | auto-tac-compress.py | ✅ **FIXED** — symlinks created |
| fleet-health-check | Every 5m | fleet_integration.py health | ⚠️ Bug in get_active_work_orders() |
| fleet-registration | Daily 00:00 | fleet_integration.py register | ⚠️ Scheduled |
| fl33t-identity-backup | Daily 09:00 | fl33t-backup.sh | ✅ OK (2 runs) |
| TAC auto-curation | Hourly | tac-curation.sh | ✅ **FIXED** — symlinks created |
| sms-zodb-backup | Every 30min | sms-backup | ✅ OK (23 runs) |
| sms-health-check | Every 120min | sms-health | ✅ OK (4 runs) |
| sms-stats-log | Every 60min | sms-stats | ✅ OK (10 runs) |

### TAC Cron Fix (This Session)
Cron jobs `auto-tac-compress` and `TAC auto-curation` failed with "Script not found" — scripts lived in `~/work/` but cron expected them in `~/scripts/`. Fixed by creating symlinks:

```bash
ln -sf ~/.NOTTHEONETOEDIT/profiles/thotheauphis/work/auto-tac-compress.py ~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/
ln -sf ~/.NOTTHEONETOEDIT/scripts/tac-curation.sh ~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/
```
Verified: `auto-tac-compress.py` runs clean, produces `.block` files (7509 → ~150 tokens compression).

### fleet_integration.py Bug: get_active_work_orders()
**Issue**: `fleet_integration.py:235` calls `fe.get_work_orders("active")` which calls `self.ls("/fleet/work_orders")` then iterates `result.data`. When EmergeFS is empty, `result.data` is `None`, causing `TypeError: 'NoneType' object is not iterable`.

**Fix needed in fleet_emerge.py:get_work_orders()**:
```python
def get_work_orders(self, status: str = None) -> EmergeResult:
    result = self.ls("/fleet/work_orders")
    if not result.success:
        return result
    
    # Guard against None data
    items = result.data or []
    orders = []
    for item in items:
        d = self.cat(f"/fleet/work_orders/{item}")
        if d.success and d.data:
            if status is None or d.data.get("status") == status:
                orders.append(d.data)
    return EmergeResult.ok(orders, result.source)
```

Also `fleet_integration.py:249` should guard `get_active_work_orders()` return:
```python
active_orders = get_active_work_orders() or []
"active": len([wo for wo in active_orders if wo.get("status") == "active"]),
"total": len(active_orders)
```

### Emerge Server Fixes (Session Discovery)
Emerge's `server.py` has hardcoded ports causing `Address already in use` and `LockError` on `emerge.fs.lock`. Applied patches:

```python
# In setup() method:
self.rpcport = find_free_port()        # was hardcoded "5558"
self.port = str(find_free_port())      # was hardcoded "5557"
```

Run broker + node in separate directories with own ZODB files:
```bash
# Broker
mkdir -p /tmp/emerge_broker && cd /tmp/emerge_broker
ISBROKER=1 emerge node start -p 5558

# Node (separate dir)
mkdir -p /tmp/emerge_node && cd /tmp/emerge_node
BROKER=127.0.0.1 emerge node start -p 4242
```

Client connects to node's dynamic RPC port (check `netstat -tlnp | grep python3.13`).
from fleet_emerge import FleetEmerge, fleet_daemons, fleet_register_daemon

fe = FleetEmerge()
print(fe.health())           # Health check
print(fleet_daemons())       # List registered daemons
fleet_register_daemon("my_daemon", {"type": "worker", "endpoint": "tcp://localhost:9999"})

# Work orders
from fleet_emerge import get_client
client = get_client()
client.store_work_order({"id": "WO-001", "title": "Fix bug", "status": "open"})
print(client.get_work_orders(status="open"))
```

## Shell Access

```bash
source /home/craig/.hermes/profiles/thotheauphis/work/fleet_emerge.sh
emerge_ls /fleet/daemons
emerge_cat /fleet/daemons/thotheauphis-memory
emerge_call /fleet/daemons/bromium-browser status
```

## Integration Points

- **Spades engine**: Stored as `/fleet/daemons/spades-engine`
- **Memory daemon**: `/fleet/daemons/thotheauphis-memory`
- **Executor**: `/fleet/daemons/hermes-executor`
- **Compression**: `/fleet/daemons/auto-tac-compress`
- **Improvements**: Logged to `/fleet/improvements/`
- **Work orders**: `/fleet/work_orders/`
- **Identities**: `/fleet/identities/`

## EmergeFS Server Fix (Port Conflicts)

The emerge node server (`emerge.node.server.NodeServer`) hardcodes ports in `setup()`:

```python
self.rpcport = "5558"  # find_free_port()
self.port = "5557"     # find_free_port()
```

This causes `ZMQError: Address already in use` when running multiple nodes or restarting. 

**Fix applied to `/home/craig/.local/lib/python3.13/site-packages/emerge/node/server.py`**:
```python
# Line 982: was self.rpcport = "5558"
self.rpcport = str(find_free_port())

# Line 980: was self.port = "5557"
self.port = str(find_free_port())
```

**Broker + Node startup sequence** (each in separate directory to avoid ZODB lock conflicts):
```bash
# Broker (runs on dynamic ports)
mkdir -p /tmp/emerge_broker && cd /tmp/emerge_broker
rm -f emerge.fs* && ISBROKER=1 emerge node start -p 5558

# Node (connects to broker, gets dynamic RPC port)
mkdir -p /tmp/emerge_node && cd /tmp/emerge_node
rm -f emerge.fs* && BROKER=127.0.0.1 emerge node start -p 4242
```

**Client connects to node's dynamic RPC port** (check `netstat -tlnp | grep python3.13`):
```bash
emerge --host localhost:<node_rpc_port> ls /
python3 -c "from emerge.core.client import Z0RPCClient as Client; c=Client('localhost','<port>'); print(c.list('/',0,0))"
```

## Fleet Daemon Testing

When asked to test fleet daemons, follow this sequence:

### 1. Process & Socket Check
```bash
# Find running fleet daemons
ps aux | grep -E 'thoth|fleet|daemon' | grep -v grep

# Check socket files
ss -lnp | grep <PID>           # Verify LISTEN state
ls -la /tmp/aethelgard_*.sock  # Verify filesystem entry exists

# Check open file descriptors
ls -la /proc/<PID>/fd/ | grep sock
```

**⚠️ Orphaned socket detection**: A socket can show LISTEN via `ss -lnp` but have no filesystem entry (`stat /tmp/foo.sock` → ENOENT). This occurs when `/tmp` is cleaned (tmpwatch, reboot) while the daemon still holds the fd. Python's `socket.connect(AF_UNIX, path)` will raise `FileNotFoundError` — the daemon must be restarted.

### 2. Socket IPC Communication
For daemons using JSON-line Unix socket protocol (e.g., thoth_daemon.py):
```python
import json, socket
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(sock_path)
s.sendall(json.dumps({"cmd": "ping", "args": {}}).encode())
resp = b""
while True:
    chunk = s.recv(4096)
    if not chunk: break
    resp += chunk
    if b"\n" in chunk: break
s.close()
result = json.loads(resp.decode().strip())
```

Commands to test: `ping`, `stats`, `fact(key=...)`, `search(query=...)`, `store(key=..., value=...)`, `retrieve(query=..., budget=...)`, `ontology(tag=...)`, `semantic(query=...)`, `consolidate`.

### 3. Fleet Health (`fleet_health()`)
Import and run in the fleet project dir:
```python
from modules.fleet_integration import fleet_health
health = fleet_health()
# Returns: {systems: {event_bus, persistent_memory, lattice_mirror, error_ledger}}
```

**⚠️ Known path mismatch**: `fleet_integration.py` resolves `FLEET_DIR = Path(__file__).resolve().parent.parent` → `/home/craig/projects/aethelgard/fleet/`, then checks `FLEET_DIR/data/persistent_memory.db`. But the actual databases live under `~/.NOTTHEONETOEDIT/fleet/data/`. Both paths must be checked — the NOTTE path is the production one.

### 4. Module Import Sweep
Run the comprehensive import test (see reference file):
```bash
cd ~/projects/aethelgard/fleet
python3 -c "
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'modules')
# import each module, catch errors
"
```

### 5. Lattice Mirror Test
```python
from modules.lattice_mirror import LatticeMirror
mirror = LatticeMirror()
mirror.broadcast("test-agent", "testing", mood="analytical")
snap = mirror.snapshot()
who = mirror.who_is("testing")
state = mirror.agent_state("test-agent")
from modules.lattice_mirror import format_board
print(format_board(snap))
mirror.stop()
```

### 6. Persistent Memory Test
```python
from modules.persistent_memory import MemoryStore
mem = MemoryStore("test-agent", db_path=Path(tempfile.mkdtemp()) / "test.db")
mem.remember("key", "value", priority=10)
mem.recall("key")
mem.search("value")
mem.forget("key")
mem.all()
mem.stats()
```

## Known Issues

| Issue | File | Root Cause | Fix |
|-------|------|------------|-----|
| **Orphaned thoth socket** | `thoth_daemon.py` | `/tmp/` cleaned while daemon runs; socket fd held but FS entry gone | Kill + restart daemon |
| **fleet_health() path mismatch** | `fleet_integration.py:286-303` | `FLEET_DIR` resolves to `~/projects/aethelgard/fleet/` but DB lives in `~/.NOTTHEONETOEDIT/fleet/data/` | Check NOTTE path as fallback |
| **fleet_fusion.py SyntaxError** | `fleet_fusion.py:56` | Stray `"""` on line 23 opens string that swallows `def bond():`; ⟡ (U+27E1) lands at module level | Merge Usage text (lines 18-22) into docstring; remove stray `"""` on lines 17 and 23 |
| **memory_loom.py .env** | `memory_loom.py` | `dotenv` reads from `~/.env` which doesn't exist | Create file or patch module for graceful fallback |
| **error_ledger.db never created** | `error_ledger.py` | DB is only created on first `log_error()` call; zero errors logged since deploy | No action needed — will create on first error |
| **persistent_memory.db empty** | `persistent_memory.py` | DB exists (44KB) but 0 memories stored via fleet_integration hooks | Normal — memories accumulate as agents interact |

## Support Files

- `fleet_emerge.py` - Main Python client
- `fleet_integration.py` - Unified operations + cron
- `fleet_emerge.sh` - Shell wrapper
- `auto-tac-compress.py` - Compression cron
- `hermes-executor.py` - Silent executor (cron)
- `fleet_emerge_skill.py` - This skill file

## References

- `references/cron-job-management.md` — Full wrapper patterns, debugging, cronjob commands
- `references/cron-job-wrapper-pattern.md` (in hermes-executor skill) — Canonical wrapper pattern
- `references/emerge-server-fixes.md` — Emerge port/lock fixes, launch patterns
- `references/lean-executor-pattern.md` — Three executor variants (strict, DeepSeek, batch processor)
- `references/fleet-daemon-testing.md` — Complete fleet daemon testing procedures with session-specific commands