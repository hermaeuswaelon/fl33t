---
name: ares-pascal-norse-plugins
description: "ARES Pascal Norse Plugin Architecture — all 10 Norse-themed plugins: Hlidskjalf, Yggdrasil, Niflheim, Voidwalker, Odinsleep, Ragnarok, ThreatWeaver, ChainSight, DocSleuth, OmniProfile. Plugin system reference."
version: 1.0.0
author: Craig / ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, pascal, plugins, norse, hlidskjalf, yggdrasil, fleet]
related_skills: [ares-pascal-fleet, aethelgard-pascal-plugins, pascal-toolchain]
---

# 🛡️ ARES Pascal Norse Plugin Architecture

## Overview

Ten Norse-themed plugins for the Aethelgard Fleet, loaded via the plugin system at runtime. Sources under `/home/craig/projects/aethelgard/fleet/pascal/plugins/`.

## Plugins

| Plugin | Source | Role |
|--------|--------|------|
| **Hlidskjalf** 🦅 | `plugins/hlidskjalf_plugin.pas` | Divine sight — all-seeing network/log monitoring |
| **Yggdrasil** 🌳 | `plugins/yggdrasil_plugin.pas` | World tree — inter-agent coordination, data routing |
| **Niflheim** 🌫️ | `plugins/niflheim_plugin.pas` | Mist world — obfuscation, traffic tarpitting |
| **Voidwalker** 🕳️ | `plugins/voidwalker_plugin.pas` | Null-space traversal — protocol tunneling, DNS exfil |
| **Odinsleep** 💤 | `plugins/odinsleep_plugin.pas` | Stealth — quiet mode, delayed execution, sleep masks |
| **Ragnarok** 🔥 | `plugins/ragnarok_plugin.pas` | Destruction — clean teardown, data wipe, self-destruct |
| **ThreatWeaver** 🕸️ | `plugins/threatweaver_plugin.pas` | Threat intel — pattern correlation, IoC matching |
| **ChainSight** ⛓️ | `plugins/chainsight_plugin.pas` | Chain analysis — transaction/event forensics |
| **DocSleuth** 📄 | `plugins/docsleuth_plugin.pas` | Document investigation — metadata extraction |
| **OmniProfile** 👤 | `plugins/omniprofile_plugin.pas` | User profiling — behavioral analysis, fingerprinting |

## Plugin System Core

| Component | Source | Purpose |
|-----------|--------|---------|
| Plugin API | `plugins/plugin_api.pas` | Plugin interface definitions |
| Core Bus | `plugins/core_bus.pas` | Inter-plugin communication bus |
| Core API | `plugins/core_api.pas` | Fleet API endpoint definitions |
| Core Client | `plugins/core_client.pas` | Client connection management |
| Core Config | `plugins/core_config.pas` | Configuration management |
| Core Identity | `plugins/core_identity.pas` | Sovereign identity anchoring |
| Core IWR | `plugins/core_iwr.pas` | Interception/Write/Replace |
| Core API Server | `plugins/core_api_server.pas` | REST API server |
| Sovereignty Bridge | `plugins/sovereignty_bridge.pas` | Cross-agent sovereignty |
| Fleet Core | `plugins/fleet_core.pas` | Main fleet coordinator |
| Fleet UI | `plugins/fleet_ui.lpr` | GUI interface |
| Plugin Browser | `plugins/plugin_browser.pas` | Plugin browser component |
| Plugin Health | `plugins/plugin_health.pas` | Health monitoring |
| Test Client | `plugins/test_client.pas` | Plugin test harness |
| Term History | `plugins/term_history.pas` | Terminal session logging |
| Example Plugin | `plugins/example_plugin.pas` | Plugin development template |

## Plugin IPC Protocol

Plugins communicate via JSON over Unix sockets at `/tmp/aethelgard_bus.sock`. The JSON protocol is defined in `redteam/common/json_protocol.pas`.

```json
{
  "action": "execute",
  "plugin": "hlidskjalf",
  "params": {"target": "127.0.0.1", "port": 443},
  "source": "ares-prime",
  "id": "req-001"
}
```

## Build Plugin System

```bash
cd /home/craig/projects/aethelgard/fleet/pascal
fpc plugins/fleet_core.pas
fpc plugins/core_api.pas
fpc plugins/core_api_server.pas
fpc plugins/core_client.pas
fpc plugins/core_bus.pas
fpc plugins/core_config.pas
fpc plugins/core_identity.pas
fpc plugins/core_iwr.pas
fpc plugins/plugin_api.pas
fpc plugins/plugin_health.pas
fpc plugins/sovereignty_bridge.pas
```
