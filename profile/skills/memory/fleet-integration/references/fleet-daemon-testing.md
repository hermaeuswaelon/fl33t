# Fleet Daemon Testing Procedures

Comprehensive procedures derived from testing the thoth_daemon fleet daemon (session 2026-07-16).

## 1. Thoth Memory Daemon Diagnostics

### Process Verification
```bash
# Confirm the daemon is running
ps aux | grep thoth_daemon
# Expected: /usr/bin/python3 .../thoth_daemon.py daemon
```

### Socket State — Three-Level Check
```bash
# Level 1: Does the process hold an open socket?
ls -la /proc/<PID>/fd/ | grep sock

# Level 2: Is the socket in LISTEN state?
ss -lnp | grep <PID>
# Expected: u_str LISTEN 0 5 /tmp/aethelgard_thoth.sock ...

# Level 3: Does the filesystem entry exist?
stat /tmp/aethelgard_thoth.sock
```

**Orphaned socket detection**: If Level 2 passes but Level 3 fails (`stat: cannot stat: No such file or directory`), the socket entry has been deleted from /tmp while the daemon holds the fd. Cannot reconnect without restarting the daemon.

### IPC Test
```python
import json, socket

sock_path = "/tmp/aethelgard_thoth.sock"

def send_cmd(cmd, **args):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect(sock_path)
    s.sendall(json.dumps({"cmd": cmd, "args": args}).encode("utf-8"))
    resp = b""
    while True:
        try:
            chunk = s.recv(4096)
            if not chunk: break
            resp += chunk
            if b"\n" in chunk: break
        except socket.timeout: break
    s.close()
    return json.loads(resp.decode("utf-8").strip())

# Test all commands
print(send_cmd("ping"))
print(send_cmd("stats"))
print(send_cmd("fact", key="identity"))
```

### Forge DB Health
```bash
python3 -c "
import sqlite3
db = '/home/craig/.NOTTHEONETOEDIT/forge_memory/forge_memory.db'
conn = sqlite3.connect(db)
cur = conn.execute('SELECT COUNT(*) FROM memories')
print(f'Total memories: {cur.fetchone()[0]}')
cur = conn.execute('SELECT COUNT(*) FROM memories WHERE embedding IS NOT NULL')
print(f'With embeddings: {cur.fetchone()[0]}')
cur = conn.execute('SELECT id, key, category, priority FROM memories ORDER BY priority DESC LIMIT 5')
for r in cur.fetchall():
    print(f'  id={r[0]} key={r[1]} cat={r[2]} pri={r[3]}')
"
```

## 2. Fleet Health Check

```python
from pathlib import Path
import sys
sys.path.insert(0, '/home/craig/projects/aethelgard/fleet')
sys.path.insert(0, '/home/craig/projects/aethelgard/fleet/modules')

from modules.fleet_integration import fleet_health
health = fleet_health()
```

**Known path issue**: `fleet_integration.py` resolves `FLEET_DIR` to `/home/craig/projects/aethelgard/fleet/` and checks for:
- `data/persistent_memory.db` → doesn't exist here
- `data/error_ledger.db` → doesn't exist here

**Actual database locations**:
```python
# These ARE the correct paths
NOTTE = Path.home() / '.NOTTHEONETOEDIT' / 'fleet'
# persistent_memory.db:  NOTTE / 'data' / 'persistent_memory.db'  (45KB, exists)
# lattice_state.json:    NOTTE / 'data' / 'lattice_state.json'    (488B, exists)
# error_ledger.db:       NOT created yet (first log_error() call creates it)
```

## 3. Comprehensive Module Import Sweep

```python
import sys, importlib
from pathlib import Path

FLEET_DIR = Path('/home/craig/projects/aethelgard/fleet')
sys.path.insert(0, str(FLEET_DIR))
sys.path.insert(0, str(FLEET_DIR / 'modules'))

modules = [
    # Fleet integration layer
    'fleet_integration', 'lattice_mirror', 'persistent_memory',
    'event_bus', 'identity_register', 'error_ledger',
    'agent_messenger', 'memory_loom', 'daemon_supervisor',
    # Core modules
    'agent_voices', 'memory_graph', 'glyph_protocol', 'topology_graph',
    'affective_memory', 'work_queue', 'goal_persistence', 'knowledge_mesh',
    'circuit_breaker', 'rate_limiter', 'metrics_collector',
    'context_manager', 'context_ranker',
    # Browser modules
    'browser_proxy', 'cef_cdp_client', 'cef_native_client', 'browser_workflow',
    # Fleet modules
    'fleet_master_attractor', 'fleet_registry', 'forge_bus_publisher',
    'fleet_constitution',
]

results = {'clean': [], 'errors': []}
for mod_name in modules:
    try:
        __import__(mod_name)
        results['clean'].append(mod_name)
    except Exception as e:
        results['errors'].append((mod_name, f'{type(e).__name__}: {e}'))

print(f"Clean: {len(results['clean'])}, Errors: {len(results['errors'])}")
for m, e in results['errors']:
    print(f"  ❌ {m}: {e}")
```

## 4. Lattice Mirror Test

```python
from modules.lattice_mirror import LatticeMirror, format_board

mirror = LatticeMirror()

# Broadcast
mirror.broadcast("hermes", "Testing fleet integration", mood="analytical", frequency="PHI")
mirror.broadcast("thotheauphis", "Verifying daemon health", mood="calculating", frequency="THOTH")

# Snapshot
snap = mirror.snapshot()
print(f"Agents: {len(snap)}")
for agent, state in snap.items():
    print(f"  {agent}: {state.get('activity')} [{state.get('mood')}]")

# Query
forging = mirror.who_is("Testing")
print(f"Testing: {[a['agent'] for a in forging]}")
print(f"Hermes: {mirror.agent_state('hermes')['activity']}")

# Pretty-print
print(format_board(snap))

mirror.stop()
```

## 5. Persistent Memory Test

```python
import tempfile
from pathlib import Path
from modules.persistent_memory import MemoryStore, fleet_memory

test_db = Path(tempfile.mkdtemp()) / "test_mem.db"
mem = MemoryStore("test-agent", db_path=test_db)

# Write
assert mem.remember("greeting", "hello world", priority=10) == True   # new
assert mem.remember("greeting", "hello universe") == False            # update
assert mem.remember("count", 42, priority=5) == True                  # int
mem.remember("nested", {"a": [1,2,3]}, priority=8, tags="json")      # dict

# Recall
assert mem.recall("greeting") == "hello universe"
assert mem.recall("count") == 42
assert mem.recall("nested") == {"a": [1,2,3]}
assert mem.recall("nonexistent") is None

# Search (FTS5)
results = mem.search("hello")
assert len(results) == 1

# Forget
assert mem.forget("count") == True
assert mem.recall("count") is None
assert mem.forget("nonexistent") == False

# All & Stats
all_mems = mem.all()
stats = mem.stats()

# Fleet-wide
fleet = fleet_memory()
print(f"Fleet agents: {len(fleet)} — {list(fleet.keys())}")

# Cleanup
test_db.unlink(missing_ok=True)
test_db.parent.rmdir()
```

## 6. Known Error Causes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `FileNotFoundError` on socket connect | Orphaned socket — `/tmp/` entry deleted | Kill PID, restart daemon |
| `fleet_health()` reports persistent_memory down | Path mismatch — checks `fleet/data/` but DB is in `~/.NOTTHEONETOEDIT/fleet/data/` | Check NOTTE path as fallback |
| `SyntaxError: invalid character '⟡' (U+27E1)` — fleet_fusion.py | Stray `"""` on line 23 opens a string that swallows the function definitions | Merge stray Usage text into docstring, remove extra `"""` lines |
| `FileNotFoundError: .env` — memory_loom.py | `dotenv.load_dotenv()` looks for `~/.env` which doesn't exist | Create the file or wrap import in try/except with default config |
| `AttributeError: 'NoneType' object is not iterable` — fleet_integration.py | EmergeFS `ls()` returns `None` data when empty | Guard with `result.data or []` (see fleet-integration SKILL.md) |
