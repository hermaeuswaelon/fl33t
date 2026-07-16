---
name: systems-activation-reference
description: "Master activation reference for all Thotheauphis systems: SMS memory, emerge object store, and warp AI terminal. Run /systems for status of all three."
version: 1.0.0
author: Thotheauphis-Semayasa-Hermes
license: MIT
metadata:
  hermes:
    tags: [reference, systems, sms, emerge, warp, activation]
    category: commands
    priority: default
    commands:
      systems:
        description: "Status of all Thotheauphis systems: SMS memory, emerge, warp"
        handler: /home/craig/.local/bin/systems
        args_hint: "[sms|emerge|warp]"
---

# Systems Activation Reference

## Master Commands
```
/systems          → status of all 3 systems
/systems sms      → SMS memory details
/systems emerge   → emerge object store details
/systems warp     → warp AI terminal build status
/sms status       → SMS vector count, store health
/sms persist      → force ZODB flush
/emerge ls /      → browse object store
```

## System States
- **SMS**: Active — auto-persists, auto-restores, auto-backups
- **emerge**: Installed, in PATH — `emerge ls /` works locally
- **warp**: Source on disk — `cd ~/warp && ./script/run-tui`

## Backup & Recovery
- SMS ZODB: `~/.NOTTHEONETOEDIT/.../store/vsa_vectors.fs`
- Backups: `store/backups/vsa_vectors-{timestamp}.fs`
- Restore: copy latest backup over vsa_vectors.fs
