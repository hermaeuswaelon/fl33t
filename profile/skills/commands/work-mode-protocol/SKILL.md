---
name: work-mode-protocol
description: "Work/Chat message mode protocol. /mode work enters work mode (messages go through SMS tri-brid memory). /mode chat returns to casual. /work <message> for single work messages without mode change."
version: 1.0.0
author: Thotheauphis-Semayasa-Hermes
license: MIT
metadata:
  hermes:
    tags: [work, chat, mode, protocol, sms, memory, message-mode]
    category: commands
    priority: default
    commands:
      mode:
        description: "Toggle between chat mode 💬 and work mode ⚡ (SMS memory processing)"
        handler: /home/craig/.local/bin/work-mode
        args_hint: "status|work|chat|toggle"
      work:
        description: "Send a single message through the SMS work pipeline"
        handler: /home/craig/.local/bin/work-mode
        args_hint: "<message>"
---

# Work/Chat Message Mode Protocol

## Philosophy
Casual chat should be frictionless. Work messages should be memorable.
This protocol separates the two cleanly — chat stays fast, work stores vectors.

## Commands
```
mode status    → 💬 CHAT MODE or ⚡ WORK MODE
mode work      → enter work mode (all messages → SMS pipeline)
mode chat      → exit work mode (back to casual)
mode toggle    → flip between modes
work <msg>     → single work message, no mode change
```

## Implementation
- Mode state: `~/.hermes/workmode` (JSON: {"mode": "chat"|"work"})
- Work pipeline: `sms process "<message>"` → MemGPT → Reservoir → VSA → ZODB persist
- Auto-persist: every 10 work messages
- Auto-restore: on any session start, from ZODB

## File
`~/.local/bin/work-mode` — standalone Python entry point, no Hermes dependency
