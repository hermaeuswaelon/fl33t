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

### Current Cron Status (as of session)

| Job | Schedule | Script | Last Status |
|-----|----------|--------|-------------|
| hermes-executor | Every 60s | run_executor_cron.sh | ✅ OK |
| auto-tac-compress | Every 30min | auto-tac-compress.py | ⚠️ Error |
| fleet-health-check | Every 5m | fleet_integration.py health | ⚠️ Error |
| fleet-registration | Daily 00:00 | fleet_integration.py register | ⚠️ Scheduled |
| fl33t-identity-backup | Daily 09:00 | fl33t-backup.sh | ✅ OK |
| TAC auto-curation | Hourly | tac-curation.sh | ⚠️ Error |

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

## Usage

```python
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