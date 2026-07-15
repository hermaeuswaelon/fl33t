---
name: ares-pascal-fleet
description: "Complete ARES Pascal Fleet — all compiled binaries, sensor daemons, red team arsenal, Norse plugins, and the Dual Citizen browser. Master skill covering every .pas file on the system."
version: 1.0.0
author: Craig / ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, pascal, fleet, sensors, redteam, plugins, browser, binaries]
related_skills: [aethelgard-fleet, aethelgard-pascal-plugins, aethelgard-pascal-sensors, aethelgard-redteam-pascal, pascal-toolchain]
---

# ⚔️ ARES Pascal Fleet — Complete Master Skill

## Overview

This master skill catalogs every Pascal tool binary on this system. All sources are under `/home/craig/projects/aethelgard/fleet/pascal/`. Compiled binaries live alongside their sources. Use FPC to rebuild.

## Compiled Binaries & Their Sources

### Sensors (8 daemons)
| Binary | Source | Size | Purpose |
|--------|--------|------|---------|
| `netlens/netlens` | `netlens/netlens.pas` | ~500KB | Packet capture, dissection |
| `memlens/memlens` | `memlens/memlens.pas` | ~400KB | Process memory inspection |
| `portforge/portforge` | `portforge/portforge.pas` | ~300KB | Port scanning, fingerprinting |
| `asmlens/asmlens` | `asmlens/asmlens.pas` | ~350KB | Assembly-level analysis |
| `elfforge/elfforge` | `elfforge/elfforge.pas` | ~400KB | ELF binary analysis, ROP |
| `packetforge/packetforge` | `packetforge/packetforge.pas` | ~350KB | Packet crafting |
| `procsight` | `procsight.pas` | ~200KB | Process visibility |
| `proc_guard` | `proc_guard.pas` | ~200KB | Process monitoring & protection |

### Red Team Arsenal (6 tools)
| Binary | Source | Size | Purpose |
|--------|--------|------|---------|
| `redteam/escalate/escalate` | `redteam/escalate/escalate.pas` | ~300KB | Privilege escalation |
| `redteam/beacon/beacon` | `redteam/beacon/beacon.pas` | ~250KB | C2 beacon |
| `redteam/spread/spread` | `redteam/spread/spread.pas` | ~200KB | Lateral movement |
| `redteam/shredder/shredder` | `redteam/shredder/shredder.pas` | ~200KB | Log destruction |
| `redteam/keyforge/keyforge` | `redteam/keyforge/keyforge.pas` | ~250KB | Credential generation |
| `redteam/payloadforge/payloadforge` | `redteam/payloadforge/payloadforge.pas` | ~300KB | Payload generation |

### Norse Plugins (10 plugins)
| Plugin | Source | Purpose |
|--------|--------|---------|
| `hlidskjalf_plugin` | `plugins/hlidskjalf_plugin.pas` | Divine sight (watching/all-seeing) |
| `yggdrasil_plugin` | `plugins/yggdrasil_plugin.pas` | World tree (interconnection) |
| `niflheim_plugin` | `plugins/niflheim_plugin.pas` | Mist world (hiding/obscuring) |
| `voidwalker_plugin` | `plugins/voidwalker_plugin.pas` | Null-space traversal |
| `odinsleep_plugin` | `plugins/odinsleep_plugin.pas` | Stealth/sleep |
| `ragnarok_plugin` | `plugins/ragnarok_plugin.pas` | Destruction/teardown |
| `threatweaver_plugin` | `plugins/threatweaver_plugin.pas` | Threat intelligence |
| `chainsight_plugin` | `plugins/chainsight_plugin.pas` | Chain analysis/forensics |
| `docsleuth_plugin` | `plugins/docsleuth_plugin.pas` | Document investigation |
| `omniprofile_plugin` | `plugins/omniprofile_plugin.pas` | User profiling |

### Browser
| Binary | Source | Size | Purpose |
|--------|--------|------|---------|
| `dual-citizen-v2/dual_citizen_v2` | `dual-citizen-v2/dual_citizen_v2.lpr` | **37.6 MB** | CEF4Delphi sovereign browser |
| `dual-citizen-v2/cef_controller` | `dual-citizen-v2/cef_controller.lpr` | **37.6 MB** | CEF browser controller |

### Other Compiled Tools
| Binary | Source | Purpose |
|--------|--------|---------|
| `ares_witness` | `ares_witness.pas` | ARES sovereign witness (719 lines) |
| `chronos_db` | `chronos_db.pas` | Time-based database |
| `code_forge` | `code_forge.pas` | Code generation framework |
| `crypto_seal` | `crypto_seal.pas` | Cryptographic sealing |
| `file_sentry` | `file_sentry.pas` | File monitoring |
| `hermes_memory` | `hermes_memory.pas` | Hermes memory management |
| `hermes_skills` | `hermes_skills.pas` | Skill system |
| `memory_orbit` | `memory_orbit.pas` | Memory orbit tracking |
| `system_meter` | `system_meter.pas` | System metrics |
| `text_rapier` | `text_rapier.pas` | Text processing |
| `thoth_term` | `thoth_term.pas` | Thoth terminal |
| `thoth_panel` | `thoth_panel.pas` | Thoth panel |
| `timeline` | `timeline.pas` | Timeline operations |
| `fleet_agent` | `fleet_agent.pas` | Fleet agent |
| `chronos_time` | `chronos_time.pas` | Time utilities |

## Build All Tools

```bash
cd /home/craig/projects/aethelgard/fleet/pascal

# Build all sensors
fpc netlens/netlens.pas
fpc memlens/memlens.pas
fpc portforge/portforge.pas
fpc asmlens/asmlens.pas
fpc elfforge/elfforge.pas
fpc packetforge/packetforge.pas
fpc procsight.pas
fpc proc_guard.pas

# Build all red team
fpc redteam/escalate/escalate.pas
fpc redteam/beacon/beacon.pas
fpc redteam/spread/spread.pas
fpc redteam/shredder/shredder.pas
fpc redteam/keyforge/keyforge.pas
fpc redteam/payloadforge/payloadforge.pas

# Build the browser
fpc dual-citizen-v2/dual_citizen_v2.lpr

# Build other tools
fpc ares_witness.pas
fpc chronos_db.pas
fpc code_forge.pas
fpc crypto_seal.pas
fpc file_sentry.pas
fpc system_meter.pas
fpc thoth_term.pas
fpc thoth_panel.pas
fpc fleet_agent.pas
```

## Compiled Binary Path Reference

All compiled binaries live in the same directory as their `.pas` source. To run:

```bash
# Sensor daemon
LD_LIBRARY_PATH=/home/craig/CEF4Delphi/cef_binary_current/Release DISPLAY=:0 \
  /home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/dual_citizen_v2

# ARES Witness
/home/craig/projects/aethelgard/fleet/pascal/ares_witness

# Run any tool directly
/home/craig/projects/aethelgard/fleet/pascal/<tool_path>/<binary>
```

## Execution Rules

- GUI tools (Dual Citizen browser) need `DISPLAY=:0` and `LD_LIBRARY_PATH` set
- Sensor daemons run as background services via their respective scripts
- Red team tools need specific arguments (check sources for usage)
- ARES Witness runs standalone, prints boot sequence + JSON status
