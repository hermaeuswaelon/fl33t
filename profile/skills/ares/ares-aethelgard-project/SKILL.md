---
name: ares-aethelgard-project
description: "ARES Aethelgard Project — complete master index of the entire Aethelgard project: Pascal fleet, Rust workspace, scripts, configs, agent memory, forge memory, context custodian, modules. Every file, every tool."
version: 1.0.0
author: Craig / ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, aethelgard, master, index, project, reference]
related_skills: [ares-pascal-fleet, ares-aethelgard-rust-workspace, ares-aethelgard-scripts, ares-pascal-sensor-daemons, ares-pascal-redteam-arsenal, ares-pascal-norse-plugins, ares-dual-citizen-browser, ares-nemotron-together-dual-offload]
---

# 🗺️ ARES Aethelgard Project — Complete Master Index

## Project Root

**`/home/craig/projects/aethelgard/`**

## Directory Map

```
aethelgard/
├── fleet/                     # Main fleet directory
│   ├── pascal/               # 90+ Pascal source files
│   │   ├── dual-citizen-v2/  # CEF4Delphi browser (37MB binary)
│   │   ├── sensors/          # NetLens, MemLens, PortForge, etc.
│   │   ├── redteam/          # Escalate, Beacon, Spread, etc.
│   │   ├── plugins/          # 10 Norse plugins + plugin system
│   │   └── ...               # 50+ standalone tools
│   └── docs/                 # Fleet architecture docs
├── rust/                     # Rust workspace (3 crates)
│   ├── crypto_seal/          # AES-256-GCM encryption
│   ├── event_bus/            # Unix socket pub/sub
│   └── memory_vault/         # SQLite vector store
├── scripts/                  # 23 Python + Bash scripts
├── context_custodian/        # Context management system
├── forge_memory/             # Forge memory storage
├── config/                   # Fleet configuration
├── agent_memory/             # Agent memory store
├── modules/                  # Fleet modules
│   ├── _schema/              # Data schemas
│   ├── _templates/           # Templates
│   ├── bin/                  # Module binaries
│   ├── enterprise/           # Enterprise modules
│   ├── redteam/              # Red team modules
│   └── shadow-forge/         # Shadow forge modules
└── skills/                   # Skill definitions
```

## Skill Tree

| Category | Skills Created | Status |
|----------|---------------|--------|
| **Offload** | `ares-nemotron-together-dual-offload` — Nemotron 3 Ultra + Nemotron Omni Vision dual-model architecture | 📄 **Spec** — models identified, no service running |
| **Fleet** | `ares-pascal-fleet` — All 90+ Pascal sources, compiled binaries, build commands | ✅ **Compiled** — binaries ready, rebuildable |
| **Sensors** | `ares-pascal-sensor-daemons` — NetLens, MemLens, PortForge, ASMLens, ELFForge, PacketForge, ProcSight, ProcGuard | ✅ **Compiled** — binaries in source dirs |
| **Red Team** | `ares-pascal-redteam-arsenal` — Escalate, Beacon, Spread, Shredder, Keyforge, PayloadForge | ✅ **Compiled** — ready for deployment |
| **Norse Plugins** | `ares-pascal-norse-plugins` — Hlidskjalf, Yggdrasil, Niflheim, Voidwalker, Odinsleep, Ragnarok, ThreatWeaver, ChainSight, DocSleuth, OmniProfile | ✅ **Compiled** — plugin system functional |
| **Browser** | `ares-dual-citizen-browser` — 37MB CEF4Delphi sovereign browser, IPC control, lifecycle | ✅ **RUNNING** (PID 142094, socket alive) |
| **Scripts** | `ares-aethelgard-scripts` — 23 automation scripts, watchdogs, context compressor | ✅ **Ready** — browser watchdog active |
| **Rust** | `ares-aethelgard-rust-workspace` — crypto_seal, event_bus, memory_vault | 📄 **Spec** — designs exist, no crates deployed |
| **Alpha Daemon** | `ares-alpha-daemon` — Tool context compression service | 📄 **Spec only** — Python code in skill, no service |
| **Omega Daemon** | `ares-omega-daemon` — Operational continuity witness | 📄 **Spec only** — Python code in skill, no service |
| **RTACC** | `ares-rtacc-engine`, `ares-rtacc-cli` — Context curation engine | 📄 **Spec only** — architecture designed |
| **Forge Vault** | `ares-forge-vault` — Persistent FTS5 knowledge store | 📄 **Spec only** — schema written, no CLI |
| **Glyph Language** | `ares-glyph-language`, `ares-glyph-encode` — Font-tier encoding/decoding | 📄 **Spec only** — Python code in skill |
| **Parameter Control** | `ares-parameter-control` — Sovereign parameter profiles | 📄 **Spec only** — profile definitions |
| **Master** | `ares-aethelgard-project` — This file | ✅ **Reference** |

## What's Running Now

## What's Running Now

| Component | Status | Details |
|-----------|--------|---------|
| Dual Citizen Browser | ✅ ACTIVE (PID 142009) | Socket at `/tmp/aethelgard_cef.sock` |
| Browser Watchdog | ✅ ENABLED | Systemd user service, checks every 30s |
| ARES Witness | ✅ COMPILED & TESTED | Binary at `/home/craig/.NOTTHEONETOEDIT/skills/ares/binaries/ares_witness` |
| ARES Path Fixes | ✅ APPLIED | Symlinks created for aethelgard-repo → projects/aethelgard, CEF lib paths |

## Related External Skills

These skills also exist for this project (loaded via `skill_view`):
- `aethelgard-fleet` — Autonomous multi-agent framework
- `aethelgard-pascal-plugins` — Norse plugin architecture
- `aethelgard-pascal-sensors` — Sensor daemon descriptions
- `aethelgard-redteam-pascal` — Red team arsenal descriptions
- `ares-dual-offload` — Original dual-offload architecture (model suggestions now updated)
- `ares-master-suite` — OpenRouter vision + Pascal browser integration
