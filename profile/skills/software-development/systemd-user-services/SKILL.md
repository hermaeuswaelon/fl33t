---
name: systemd-user-services
category: software-development
description: Create persistent systemd user services for Python packages — wrapper launchers, env var plumbing, ZMQ port patching, and troubleshooting.
tags: [systemd, daemon, service, user-service, python-daemon, persistent, background]
version: 1
---

# systemd-user-services

Create persistent systemd **user** services for Python packages that weren't designed for standalone deployment — especially packages that assume Docker compose infrastructure (hardcoded hostnames like "broker", missing `BROKER` env vars, etc.).

## Trigger

Use when the user asks to:
- "Make X run as a service/daemon"
- "Create a systemd service for Y"
- "Run Z persistently in the background"
- "Make this server survive reboots"
- "Create a systemd user service for package X"

## Workflow

### 1. Explore the package startup

```bash
# Find the entry point and understand what env vars it needs
python3.13 -c "import thepackage; print(thepackage.__file__)"
cat ~/.local/bin/thepackage
python3.13 -c "from thepackage import cli; help(cli)"

# Check for env var requirements at module import time
grep -n "os.environ\[" ~/.local/lib/python3.13/site-packages/package/module.py
# Look for: BROKER, ISBROKER, HOST, PORT, DB_URL, etc.

# Check for hardcoded hostnames (Docker assumptions)
grep -n "broker\|tcp://" ~/.local/lib/python3.13/site-packages/package/module.py
```

### 2. Create a wrapper launcher script

The wrapper script handles things the package doesn't:

```python
#!/usr/bin/env python3
"""Package X — standalone launcher"""
import os
import sys
import logging

# Set env vars needed BEFORE the import
os.environ["ISBROKER"] = "1"   # or whatever the package needs

logging.basicConfig(level=logging.INFO, stream=sys.stderr)

# Import AFTER env vars
from package import Server

port = int(sys.argv[1]) if len(sys.argv) > 1 else 54242
server = Server(port=port)
server.setup()
server.rpcport = str(port)

# Patch broken methods (Docker hostnames, etc.)
_original_start = server.start
def patched_start():
    import zmq
    import platform
    import time
    import threading
    
    # Bind locally instead of connecting to "broker"
    ctx = zmq.Context()
    sock = ctx.socket(zmq.PUB)
    sock.bind("tcp://0.0.0.0:{}".format(server.port))
    
    # Start original threads manually
    ... 
    
server.start = patched_start
server.start()
```

Key patterns for the wrapper:
- **Log to stderr** — journald captures it
- **Set env vars BEFORE importing the package's server module**
- **Keep daemon threads** so the process stays alive via shutdown_event
- **Write PID file** for the systemd service
- **Handle SIGTERM/SIGINT** for clean shutdown

### 3. Write the systemd user service file

Put this at `~/.config/systemd/user/<service-name>.service`:

```ini
[Unit]
Description=Package X Server
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3.13 %h/.local/bin/wrapper-script 54242
Restart=always
RestartSec=5
TimeoutStopSec=10

# Environment — set every var the package needs
Environment=BROKER=
Environment=PYTHONPATH=%h/.local/lib/python3.13/site-packages

# Working directory controls where the package stores data
WorkingDirectory=%h/.data/pkg

# Output goes to journald
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=default.target
```

### 4. Enable and start

```bash
systemctl --user daemon-reload
systemctl --user enable service-name.service
systemctl --user start service-name.service

# Check status and logs
systemctl --user status service-name.service
journalctl --user -u service-name.service --no-pager -n 40
```

### 5. Verify with a client

```bash
python3.13 -c "
from package.client import Client
c = Client('localhost', '54242')
print(c.hello('test'))
print(c.list('/', 0, 0))
"
```

## Common pitfalls

### PYTHONPATH doesn't inherit
Systemd user services **do not** inherit `$PYTHONPATH` from the user's shell. If the package is installed in `~/.local/lib/python3.13/site-packages/`, you MUST add:
```
Environment=PYTHONPATH=%h/.local/lib/python3.13/site-packages
```
Otherwise you get `ModuleNotFoundError: No module named 'package'`.

### Docker hostnames in source code
Many packages that use ZMQ (ZeroMQ) hardcode a "broker" hostname for Docker compose. In standalone mode you need to:
- Bind the SUB socket locally instead of connecting to `"tcp://broker:%s" % port`
- Use `socket.bind("tcp://0.0.0.0:{}".format(port))` instead of `socket.connect(...)`
- Key sign: `ModuleNotFoundError` is NOT the only failure — look for `zmq.error.ZMQError: Address already in use` or `OSError: [Errno -5] No address associated with hostname` if the package tries to connect to an unresolvable host

### ZODB / SQLite relative paths
If the package creates database files with relative paths (e.g., `FileStorage("emerge.fs")`), set `WorkingDirectory=%h/.somewhere/data` in the service file. Otherwise the db gets created in whatever systemd considers the working directory (often `/` or the user's home root).

### ZMQ port conflicts
When patching a package's ZMQ startup, the SUB and PUB sockets need **different ports**. If the package's `setup()` already assigned a ZMQ SUB port, use a **separate free port** for the announcement PUB socket. Symptom: `zmq.error.ZMQError: Address already in use`.

### User linger
For user services to start at boot (before login), enable linger:
```bash
sudo loginctl enable-linger $(whoami)
```
Check: `loginctl show-user $(whoami) | grep Linger`.

### Thread lifecycle
If you replace the package's `start()` method, start threads as `daemon=True` and use a `threading.Event()` for the main thread to block on. The main thread blocks on `shutdown_event.wait()`, and `signal.signal(signal.SIGTERM, handler)` sets the event to trigger clean shutdown.

## Verification checklist

- [ ] `systemctl --user is-enabled <service>` → `enabled`
- [ ] `systemctl --user is-active <service>` → `active`
- [ ] Logs show server started without errors
- [ ] Client can connect and execute operations
- [ ] Database files created in expected directory
- [ ] PID file exists and matches `Main PID`
- [ ] Service survives `systemctl --user restart`
