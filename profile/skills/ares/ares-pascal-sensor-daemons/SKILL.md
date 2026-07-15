---
name: ares-pascal-sensor-daemons
description: "ARES Pascal Sensor Daemons — run, configure every sensor: NetLens (packet capture), MemLens (process memory), PortForge (port scanning), ASMLens (assembly analysis), ELFForge (ELF parsing), PacketForge (packet crafting), ProcSight, ProcGuard."
version: 1.0.0
author: Craig / ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, pascal, sensors, daemons, netlens, memlens, portforge, elfforge]
related_skills: [ares-pascal-fleet, pascal-toolchain, aethelgard-pascal-sensors]
---

# 🕵️ ARES Pascal Sensor Daemons

## Overview

Eight sensor daemons for network, memory, process, and binary analysis. All written in Pascal, compiled with FPC. Sources under `/home/craig/projects/aethelgard/fleet/pascal/`.

## Daemon Reference

### 1. NetLens — Network Packet Capture
- **Binary**: `netlens/netlens`
- **Source**: `netlens/netlens.pas`
- **Purpose**: Real-time packet capture and dissection
- **Dependencies**: `libpcap` (via `pcap_bridge.pas`)
- **Usage**: `./netlens/netlens [interface] [filter]`

### 2. MemLens — Process Memory Inspection
- **Binary**: `memlens/memlens`
- **Source**: `memlens/memlens.pas`
- **Purpose**: Read process memory, pattern search, injection detection
- **Components**: `proc_mem.pas`, `pattern_search.pas`

### 3. PortForge — Port Scanning & OS Fingerprinting
- **Binary**: `portforge/portforge`
- **Source**: `portforge/portforge.pas`
- **Purpose**: TCP/UDP port scanning, service fingerprinting
- **Components**: `scanner.pas`, `fingerprint.pas`, `portforge_v2.pas`

### 4. ASMLens — Assembly-Level Analysis
- **Binary**: `asmlens/asmlens`
- **Source**: `asmlens/asmlens.pas`
- **Purpose**: Disassembly, instruction-level analysis
- **Components**: `asm_executor.pas`

### 5. ELFForge — ELF Binary Analysis
- **Binary**: `elfforge/elfforge`
- **Source**: `elfforge/elfforge.pas`
- **Purpose**: ELF parsing, ROP gadget finding, binary manipulation
- **Components**: `elf_parser.pas`, `rop_finder.pas`, `elfforge_v2.pas`

### 6. PacketForge — Packet Crafting
- **Binary**: `packetforge/packetforge`
- **Source**: `packetforge/packetforge.pas`
- **Purpose**: Raw packet construction, tap bridge, template system
- **Components**: `packet_templates.pas`, `raw_socket.pas`, `tap_bridge.pas`, `packetforge_v2.pas`

### 7. ProcSight — Process Visibility
- **Binary**: `procsight`
- **Source**: `procsight.pas`
- **Purpose**: List processes, open handles, loaded modules

### 8. ProcGuard — Process Monitoring
- **Binary**: `proc_guard`
- **Source**: `proc_guard.pas`
- **Purpose**: Monitor process creation/termination, protect critical processes

## Quick Start

```bash
cd /home/craig/projects/aethelgard/fleet/pascal

# Build all sensors
fpc netlens/netlens.pas -onetlens/netlens
fpc memlens/memlens.pas -omemlens/memlens
fpc portforge/portforge.pas -oportforge/portforge
fpc asmlens/asmlens.pas -oasmlens/asmlens
fpc elfforge/elfforge.pas -oelfforge/elfforge
fpc packetforge/packetforge.pas -opacketforge/packetforge
fpc procsight.pas
fpc proc_guard.pas

# Run a sensor (example: NetLens)
sudo ./netlens/netlens eth0
```
