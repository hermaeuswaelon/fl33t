# Emerge Node Server — Standalone systemd user service

## Package overview

**emerge** is a Z0RPC+ZMQ+ZODB distributed object filesystem. Installed at `~/.local/lib/python3.13/site-packages/emerge/`.

Server module: `emerge.node.server.NodeServer`
Client API: `emerge.core.client.Z0RPCClient(host, port)`
CLI entry point: `~/.local/bin/emerge` → `from emerge.cli import cli`

## Env var requirements at import time

The server module checks `os.environ` at import time:

```python
IS_BROKER = "ISBROKER" in os.environ

if not IS_BROKER:
    BROKER = os.environ["BROKER"]  # REQUIRED unless ISBROKER set
    broker = Client(BROKER, "5558")
```

**Fix**: Set `ISBROKER=1` before importing `emerge.node.server`.

## Hardcoded Docker hostname in start()

`NodeServer.start()` line 1095:
```python
socket.connect("tcp://broker:%s" % str(self.port))
```

This fails in standalone mode because "broker" is unresolvable. Fix: replace with `socket.bind("tcp://0.0.0.0:%s" % port)`.

## ZODB data directory

`Z0DBFileSystem.setup()` (in `emerge.fs.filesystem`) uses a relative path:
```python
storage = ZODB.FileStorage.FileStorage("emerge.fs")
```

This creates `emerge.fs`, `emerge.fs.index`, `emerge.fs.lock`, and `emerge.fs.tmp` in whatever the current working directory is. The systemd service must set `WorkingDirectory=%h/.emerge/data`.

## Wrapper script: `~/.local/bin/emerge-node-standalone`

Full listing:

```python
#!/usr/bin/env python3
"""Emerge node server — standalone (no broker) launcher."""
import os
os.environ["ISBROKER"] = "1"

import logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)

import platform
import signal
import socket
import sys
import threading
import time
from contextlib import closing

import zmq
import zerorpc
from emerge.node.server import NodeServer

RPC_PORT  = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 54242
EMERGE_HOME = os.path.expanduser("~/.emerge")
PIDFILE = os.path.join(EMERGE_HOME, "run", "emerge-node.pid")

def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

def main():
    os.makedirs(os.path.dirname(PIDFILE), exist_ok=True)
    with open(PIDFILE, "w") as f:
        f.write(str(os.getpid()))

    server = NodeServer(port=RPC_PORT)
    server.setup()
    server.rpcport = str(RPC_PORT)
    sub_port = server.port  # port setup() assigned for ZMQ SUB

    shutdown_event = threading.Event()

    # RPC thread
    def rpc_loop():
        s = zerorpc.Server(server.api)
        s.bind("tcp://0.0.0.0:{}".format(server.rpcport))
        s.run()
    rpc_thread = threading.Thread(target=rpc_loop, daemon=True)
    rpc_thread.start()

    # SUB thread (replace get_messages)
    def sub_loop():
        ctx = zmq.Context()
        sock = ctx.socket(zmq.SUB)
        sock.bind("tcp://0.0.0.0:{}".format(sub_port))
        sock.subscribe("NODE")
        while not shutdown_event.is_set():
            try:
                if sock.poll(1000):
                    string = sock.recv_string()
            except Exception:
                break
    sub_thread = threading.Thread(target=sub_loop, daemon=True)
    sub_thread.start()

    time.sleep(0.5)

    # PUB announcement on separate port
    pub_port = str(find_free_port())
    ctx = zmq.Context()
    pub_sock = ctx.socket(zmq.PUB)
    pub_sock.bind("tcp://0.0.0.0:{}".format(pub_port))
    time.sleep(0.2)
    message = "NODE HI {} tcp://{}:{}".format(platform.node(), platform.node(), server.rpcport)
    pub_sock.send_string(message)
    pub_sock.close()

    signal.signal(signal.SIGTERM, lambda *a: shutdown_event.set())
    signal.signal(signal.SIGINT, lambda *a: shutdown_event.set())
    shutdown_event.wait()

    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)

if __name__ == "__main__":
    main()
```

## systemd service file: `~/.config/systemd/user/emerge-node.service`

```ini
[Unit]
Description=Emerge Node Server — Distributed Object Filesystem (standalone)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3.13 %h/.local/bin/emerge-node-standalone 54242
Restart=always
RestartSec=5
TimeoutStopSec=10

Environment=ISBROKER=1
Environment=EMERGE_HOME=%h/.emerge
Environment=PYTHONPATH=%h/.local/lib/python3.13/site-packages
WorkingDirectory=%h/.emerge/data

StandardOutput=journal
StandardError=journal
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=default.target
```

## Client test

```python
from emerge.core.client import Z0RPCClient as Client
c = Client('localhost', '54242')
print(c.hello('test-client'))    # None
print(c.list('/', 0, 0))         # []
c.mkdir('/test')
print(c.list('/', 0, 0))         # ['dir:/test']
print(c.get('/test'))            # {'date': ..., 'name': '/test', ...}
```
