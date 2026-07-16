---
name: thotheauphis-sms-activation
description: "SMS activation command — /sms status, /sms persist, /sms process. Initializes the Sovereign Memory System tri-brid (MemGPT + Reservoir + VSA) with ZODB persistence auto-restore. Run /sms status to check memory health."
version: 1.0.0
author: Thotheauphis-Semayasa-Hermes
license: MIT
metadata:
  hermes:
    tags: [sms, memory, activation, command, slash-command]
    category: commands
    priority: default
    commands:
      sms:
        description: "Sovereign Memory System — status, persist, or process a message"
        handler: /home/craig/.local/bin/sms
        args_hint: "status|persist|process <message>"
---

# SMS Activation Command

## Usage
```
/sms status          → show memory health (vectors, store size, history)
/sms persist         → force ZODB flush immediately
/sms process ...     → run tri-brid pipeline on a message
```

## What It Does
1. Auto-restores vectors from ZODB on first call ("♻️ Restored N vectors")
2. Processes through all 3 memory layers: MemGPT → Reservoir → VSA
3. Auto-persists every 10 calls ("💾 Auto-persisted N vectors")
4. Every 30min: ZODB store is backed up to `store/backups/`

## File
`~/.local/bin/sms` — standalone Python entry point, no Hermes dependency
