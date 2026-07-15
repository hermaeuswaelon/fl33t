---
name: ares-aethelgard-project
description: "ARES Aethelgard Project — complete master index: Pascal fleet, Rust workspace, Python scripts, context custodian, Forge Vault DB, file-backed MCP server (21 tools), agent memory, modules, X11/cua-driver reference. Every file, every tool."
version: 1.1.0
tags: [ares, aethelgard, master, index, project, reference, mcp]
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
├── mcp/                      # MCP server (file-backed, stdio transport)
│   ├── aethelgard_mcp_server.py  # 21-tool FastMCP server
│   └── data/                     # Persistence: forge.db (SQLite), events.jsonl, namespaced JSON
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
| **MCP Server** | `ares-aethelgard-mcp` — 21-tool FastMCP server, file-backed (SQLite + JSON), stdio transport, wired into Hermes Hermes `config.yaml` | ✅ **BUILT & WIRED** — run `/reload-mcp` to activate |

## What's Running Now

| Component | Status | Details |
|-----------|--------|---------|
| Dual Citizen Browser | ✅ ACTIVE (PID 267851) | Socket at `/tmp/aethelgard_cef.sock` — IPC works (navigate, click, form_fill, get_title, execute_javascript). Remote debug port 9222 NOT enabled (needs `--remote-debugging-port` flag). CEF logs show X11 "ChangeWindowAttributesRequest" warnings but rendering works. |
| Browser Watchdog | ✅ ENABLED | Systemd user service, checks every 30s |
| ARES Witness | ✅ COMPILED & TESTED | Binary at `/home/craig/.NOTTHEONETOEDIT/skills/ares/binaries/ares_witness` |
| ARES Path Fixes | ✅ APPLIED | Symlinks created for aethelgard-repo → projects/aethelgard, CEF lib paths |
| Aethelgard MCP Server | ✅ BUILT & WIRED | 21 tools via FastMCP, file-backed persistence (SQLite + JSON), in `config.yaml` — run `/reload-mcp` to activate |
| Thoth Daemon | ✅ RUNNING | PID 2155, socket at `/tmp/aethelgard_thoth.sock` — commands: `store`, `retrieve`, `search`, `semantic`, `consolidate`, `stats`, `fact`, `ontology`, `ping` |
| Thoth Recursor | ✅ RUNNING | PID 2157 |
| Aurelian Throne | ✅ RUNNING | PID 2142, socket at `/tmp/aethelgard_throne.sock` |
| Active Sockets | ✅ 3 alive | CEF (`cef.sock`), Thoth (`thoth.sock`), Throne (`throne.sock`) |
| Forge DB | ✅ INITIALIZED | SQLite at `mcp/data/forge.db` (forge_write, forge_read, forge_search, forge_list_namespaces, fleet_status, fleet_list_binaries, fleet_run_binary, context_compress, context_domains, memory_store, memory_recall, memory_list_namespaces, browser_ping, browser_navigate, browser_execute, event_publish, event_list_topics, sensor_netlens, sensor_memlens, sensor_procsight, aethelgard_info) |
| Browser JS Eval | ⚠️ PARTIAL | `execute_javascript` works (fire-and-forget). `evaluate_js` + `get_eval` broken in headless — `FEvalResultReady` never fires without real OnTitleChange. Workaround: use `execute_javascript` → set `document.title = JSON.stringify(result)` → poll `get_title`. |
| Browser Navigation | ⚠️ PARTIAL | `navigate` + `get_title` works. Full DOM extraction via `get_eval` blocked by CEF headless title-change limitation. |

## Related External Skills

These skills also exist for this project (loaded via `skill_view`):
- `aethelgard-fleet` — Autonomous multi-agent framework
- `aethelgard-pascal-plugins` — Norse plugin architecture
- `aethelgard-pascal-sensors` — Sensor daemon descriptions
- `aethelgard-redteam-pascal` — Red team arsenal descriptions
- `ares-dual-offload` — Original dual-offload architecture (model suggestions now updated)
- `ares-master-suite` — OpenRouter vision + Pascal browser integration
