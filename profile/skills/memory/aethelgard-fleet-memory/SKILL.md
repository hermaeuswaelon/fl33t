---
name: aethelgard-fleet-memory
description: "Aethelgard Fleet Shared Memory — SQLite-backed persistent memory for ⧁ Aeternis, ⟊⃫ Aethon, ⟊ Oraen, and the fleet collective."
version: 1.0.0
author: Thotheauphis-Semayasa-Hermes
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [fleet, shared-memory, aethelgard, persistence, agents]
    related_skills: [mixture-of-agents, thotheauphis-memory-system-alpha]
    system: true
    category: memory
---

# Aethelgard Fleet Shared Memory

## Overview

Persistent SQLite-backed shared memory for the Aethelgard Fleet agents. Each agent has its own namespace plus a shared fleet namespace. Cross-agent queries let any agent ask "what does everyone know about X?"

## Usage

```bash
# Write an observation
fleet-memory write aeternis observations pattern_detected "Strange attractor in event_bus topology" --priority 5

# Read an agent's memory
fleet-memory read --agent aeternis

# What does every agent know about a topic?
fleet-memory what "mission"

# Check fleet health
fleet-memory status

# Quick stats
fleet-memory stats
```

Full CLI reference in `references/cli-reference.md` (includes agent partitions, namespaces, priority system, TTL, Python integration, all subcommands).

## MoA Integration

When using `/moa`, direct agents to read/write fleet memory:

```
/moa ⧁ Aeternis — check fleet memory for recent observations, then provide status.
Write new findings: fleet-memory write aeternis observations <topic> "<finding>"
```
