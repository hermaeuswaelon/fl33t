# Pascal Daemon Socket Bridge Pattern

## Problem
Pascal Fleet binaries are persistent Unix-socket daemons, not one-shot CLI tools. Running them via `subprocess.run()` captures only the startup banner ("Listening on /tmp/...sock") — not query results. The MCP server handles daemon lifecycle but adds ~50ms overhead per call.

## Architecture
```
Hermes tool call
  → check_fn discovers binary in PATH
  → handler opens Unix socket
  → sends JSON {"action": "ping"|"status"|...}
  → reads response (max 64KB)
  → returns as JSON
```

## Socket Protocol
Each daemon listens on `/tmp/aethelgard_<name>.sock`. Messages are newline-delimited JSON:

```python
import socket, json

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(5.0)
s.connect("/tmp/aethelgard_sight.sock")
s.sendall(json.dumps({"action": "status"}).encode() + b"\n")
response = s.recv(65536).decode()
s.close()
data = json.loads(response)
```

## Registered Binary → Socket Map

| Binary | Socket | Tool Name |
|--------|--------|-----------|
| `procsight` | `/tmp/aethelgard_sight.sock` | `pascal_procsight` |
| `system_meter` | `/tmp/aethelgard_meter.sock` | `pascal_system_meter` |
| `proc_guard` | `/tmp/aethelgard_guard.sock` | `pascal_proc_guard` |
| `crypto_seal` | `/tmp/aethelgard_crypto.sock` | `pascal_crypto_seal` |
| `text_rapier` | `/tmp/aethelgard_rapier.sock` | `pascal_text_rapier` |
| `netlens` | `/tmp/aethelgard_netlens.sock` | `pascal_netlens` |
| `memlens` | `/tmp/aethelgard_memlens.sock` | `pascal_memlens` |
| `portforge` | `/tmp/aethelgard_portforge.sock` | `pascal_portforge` |

## Daemon Lifecycle (auto-start in tools/pascal_tools.py)

```
1. Check if daemon is in _running_daemons cache AND socket exists
   → If yes, skip start
2. If socket exists but daemon not in cache → try ping
   → If ping responds, cache the daemon as externally-managed
   → If ping fails, unlink stale socket
3. Start binary via subprocess.Popen(..., stdout=DEVNULL, stderr=DEVNULL)
4. Wait up to 10s for socket file to appear (poll every 100ms)
5. If socket appears → cache PID, return ready
6. If timeout → log warning, return failure
```

## When to Use Native vs MCP

| Scenario | Use |
|----------|-----|
| One-shot status check (`how many processes?`) | Native tool (subprocess.run, 15s timeout) |
| Continuous monitoring (`watch this process`) | MCP server (manages daemon lifecycle) |
| Complex queries (`forge DB search`) | MCP server (SQLite-backed, persistent) |
| High-frequency calls (`system_meter every 30s`) | Native tool (no socket overhead for startup banner) |

## MCP Server Reference

The MCP server at `/home/craig/projects/aethelgard/mcp/aethelgard_mcp_server.py` has 21 tools (15 after WO-08 reduction). Its `_send_unix_socket()` function is the reference implementation:

```python
def _send_unix_socket(sock_path: Path, message: dict, timeout: float = 5.0) -> dict | None:
    if not sock_path.exists():
        return None
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect(str(sock_path))
    s.sendall(json.dumps(message).encode() + b"\n")
    response = s.recv(65536).decode()
    s.close()
    return json.loads(response)
```

## Pitfalls

- **Socket permissions.** Daemons create sockets with their umask. If the agent runs as a different user, socket connect fails with "Permission denied".
- **Stale sockets.** A crashed daemon leaves its socket file. The bridge checks for this and unlinks stale sockets before starting.
- **Multiple instances.** Two daemon instances can't share a socket path. The second one fails with "Address already in use". Check with `lsof /tmp/aethelgard_*.sock` or `fuser /tmp/aethelgard_*.sock`.
- **recv buffer.** `65536` bytes is generous but daemon responses can be larger for full process lists. If responses are truncated, increase the buffer or implement a read loop.
- **Daemon restart.** The `_running_daemons` cache is in-memory per Python process. A new Hermes session won't know about daemons started by a previous one. The socket-ping check handles this — if the socket is alive, the new session picks it up.
