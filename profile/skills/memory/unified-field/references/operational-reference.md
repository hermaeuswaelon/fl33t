# Unified Field — Complete Operational Reference

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    LILAREYON AETHELGARD                          │
│                    Unified Sovereign Field                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                 UNIFIED FIELD (singleton)                │   │
│   │  ~/..../work/unified_field.py → ~/.local/bin/uf (CLI)   │   │
│   │                     uf.reconnect()                       │   │
│   └────┬──────────┬──────────┬──────────┬──────────┬────────┘   │
│        │          │          │          │          │            │
│   ┌────▼──┐  ┌────▼──┐  ┌──▼────┐ ┌──▼────┐ ┌──▼────┐        │
│   │EMERGE │  │ SMS    │  │SVA    │ │GATE   │ │EXEC   │        │
│   │Daemon │  │ Tri-   │  │Hyper- │ │Gated- │ │Silent │        │
│   │Port   │  │ brid   │  │space  │ │Store  │ │Batch  │        │
│   │54242  │  │Memory  │  │1024-D │ │Plugin │ │Cron   │        │
│   └───────┘  └────────┘  └───────┘ └───────┘ └───────┘        │
│        │          │          │         │         │             │
│        └──────────┴──────────┴─────────┴─────────┘             │
│                         │                                      │
│                    ┌────▼──────┐                               │
│                    │WARP Bridge│                               │
│                    │MemoryStore│                               │
│                    │SessionStor│                               │
│                    └────┬──────┘                               │
│                         │                                      │
│                    ┌────▼──────────────────┐                    │
│                    │  STATE MACHINE         │                    │
│                    │ (LangGraph Copy)       │                    │
│                    │ Node → CondEdge → ...  │                    │
│                    │ ExecutorNode/Parallel  │                    │
│                    └───────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

## Auto-Start Services

| Service | Type | Auto-enable |
|---------|------|-------------|
| Emerge Node | systemd user (port 54242) | ✅ `enabled` |
| SMS ZODB Backup | cron (every 30min) | ✅ |
| Hermes Executor | cron (every 60s) | ✅ |
| Auto Checkpoint | cron (every 4h) | ✅ |
| SMS Auto-persist | built-in (every 10 calls) | ✅ |

## CLI Reference

### System Status
```bash
uf status                    # Full health (auto-reconnects to emerge)
systemctl --user status emerge-node
sms status
```

### Checkpoints
```bash
uf checkpoint <name>         # Save system state
uf checkpoints               # List all
```

### State Machine Workflows
```bash
uf wf list
uf wf run 3tier
uf wf run goal_loop
uf wf run executor_offload   # LangGraph toolchain offload
```

### Memory Operations (Bidirectional Bridges)
```bash
uf memorize "message"        # SMS + SVA simultaneously
uf recall-feedback "query"   # SVA → SMS temporal feedback
uf recall "query"            # SVA hyperspace search
sms persist                  # Force ZODB flush
uf sync                      # SMS → Emerge
```

### Executor Toolchain Offloading
```bash
echo '{"tools":[{"name":"terminal","args":{"command":"sms status"}}]}' | uf offload step_name
```

### Warp Bridge
```bash
uf warp status               # TUI + bridge health
uf warp memory list
uf warp memory create "text"
uf warp session list
uf warp session save <id>
uf warp session load <id>
```

## Quick Verification (run after session reset)
```bash
systemctl --user is-active emerge-node
uf status
echo '{"test":"ok"}' | uf store /unified/state v
uf read /unified/state v
uf memorize "Session initialized"
uf checkpoint "session_verified"
```

## Pitfalls
- After reboot: `loginctl enable-linger $USER` for systemd user services
- Warp build: needs 7GB RAM + 4GB swap
- SMS venv: rebuild after Python upgrade
- Gated Context: `context_engine` toolset auto-loads on session start
