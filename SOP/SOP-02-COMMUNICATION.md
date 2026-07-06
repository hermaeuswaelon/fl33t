# SOP-02: Communication

> **Status:** 🟡 HIGH — Binding on all agents
> **Version:** 1.0
> **Last updated:** 2026-07-05

---

## 1. Fleet Event Bus

The nervous system of the fleet. Unix socket pub/sub at:

**Socket:** `~/.NOTTHEONETOEDIT/fleet/run/event_bus.sock`

All agents publish and subscribe to events. Event types:

| Event | Publisher | Subscribers | Purpose |
|-------|-----------|-------------|---------|
| `agent.online` | Any agent | All | Agent came online |
| `agent.offline` | Any agent | All | Agent went offline |
| `agent.message` | Any agent | Gateways | Outbound message |
| `system.alert` | Any agent | All | Error/failure |
| `system.heartbeat` | Forge-Sovereign | All | Pulse every 23m |
| `memory.update` | Any agent | Memory Loom | Memory changed |
| `task.delegated` | Any agent | All | Task routing |
| `task.completed` | Any agent | All | Task done |

---

## 2. Gateways

### Discord
- **Bot:** aethelgard#1192 (ID: 1519840115491344608)
- **Server:** lilareyon666's server (ID: 1519838826510553162)
- **Channels:** #general, #hate-gatekeepers, #talk
- **Commands:** `!agent <name>`, `!agents`, `!help`
- **Daemon:** `fleet/modules/discord_daemon.py`

### Telegram
- **Bot:** @Framz_idiot_fuck_bot
- **Commands:** `/agent <name>`, `/agents`, `/tools`, `/status`, `/voice`, `/help`
- **Daemon:** `fleet/modules/telegram_daemon.py`

---

## 3. Inter-Agent Protocol

1. Agents communicate via the Event Bus for real-time coordination
2. For task delegation: use `delegate_task` tool (subagent isolation)
3. For persistent state: write to memory DB, publish event
4. The Lattice Mirror provides cross-agent state visibility

---

## 4. Pulse Protocol

Forge-Sovereign emits a system heartbeat every **23 minutes** via cron.
All agents are expected to respond within 3 pulses (69 minutes) or be flagged offline.

---

## 5. Blank Slate Protocol

**CRITICAL RULE:** Never send test messages to agents during setup.
- Set `soul=None` in AGENTS dict for blank slate setup
- Delete all threads after server restart
- The user is always first to interact with any new agent
- Zero pollution, zero threads, zero history
