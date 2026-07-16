# Emerge Server Fixes — Session Notes

## Problem
Emerge's `node/server.py` hardcodes RPC and pub/sub ports, causing:
- `zmq.error.ZMQError: Address already in use (addr='tcp://0.0.0.0:5558')`
- `zc.lockfile.LockError: Couldn't lock 'emerge.fs.lock'`

## Root Cause
In `NodeServer.setup()` (lines 979-982):
```python
self.rpcport = find_free_port()
self.port = "5557"  # hardcoded
self.bindport = find_free_port()
self.rpcport = "5558"  # hardcoded - OVERRIDES the free port!
```

Also: Broker and Node share same `emerge.fs` file if run from same directory.

## Fix Applied (Session Patch)
```python
# Line 982: CHANGE
self.rpcport = str(int(self.rpcport) + 1)  # use find_free_port result + 1

# Line 980: CHANGE  
self.port = str(find_free_port())  # dynamic pub/sub port
```

## Working Launch Pattern

### Broker (port 5558)
```bash
mkdir -p /tmp/emerge_broker && cd /tmp/emerge_broker
rm -f emerge.fs*
ISBROKER=1 emerge node start -p 5558
```

### Node (dynamic port, e.g., 54242)
```bash
mkdir -p /tmp/emerge_node && cd /tmp/emerge_node  
rm -f emerge.fs*
BROKER=127.0.0.1 emerge node start -p 4242
```

### Client Connection
```bash
# Find node's actual RPC port
netstat -tlnp | grep python3.13 | grep -v 5558

# Connect
emerge --host localhost:<NODE_RPC_PORT> ls /
# Or via Python:
python3.13 -c "
from emerge.core.client import Z0RPCClient as Client
c = Client('localhost', '<NODE_RPC_PORT>')
print(c.list('/', 0, 0))
"
```

## Key Files
- `/home/craig/.local/lib/python3.13/site-packages/emerge/node/server.py` (patched in-place)
- Cron scripts in `~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/` for SMS/Emerge health

## Cron Integration
SMS cron scripts now use venv python explicitly:
```bash
#!/usr/bin/env python3
# /home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/sms-stats
import sys, pathlib, ZODB, ZODB.FileStorage, os
sys.path.insert(0, str(pathlib.Path.home() / '.NOTTHEONETOEDIT' / 'profiles' / 'thotheauphis' / 'memory' / 'sms'))
# ... read ZODB directly, no integration import needed
```

This avoids numpy import errors from system Python (3.14) vs venv (3.13).