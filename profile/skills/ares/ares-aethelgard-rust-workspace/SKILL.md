---
name: ares-aethelgard-rust-workspace
description: "ARES Aethelgard Rust Workspace — crypto_seal (AES-256-GCM), event_bus (Unix socket pub/sub), memory_vault (SQLite vector store). Rust rewrite of core fleet infrastructure."
version: 1.0.0
author: Craig / ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, rust, crypto, event-bus, memory-vault, crypto-seal]
related_skills: [ares-pascal-fleet, ares-aethelgard-scripts]
---

# 🦀 ARES Aethelgard Rust Workspace

## Overview

Rust rewrite of core fleet infrastructure at `/home/craig/projects/aethelgard/rust/`. Three crates covering crypto, IPC, and memory.

## Crates

### 1. `crypto_seal` — AES-256-GCM Credential Sealing
- **Type**: Library
- **Source**: `rust/crypto_seal/src/`
- **Purpose**: Encrypt/unseal fleet credentials and secrets
- **Deps**: `aes-gcm` crate
- **Status**: Active development

### 2. `event_bus` — Unix Socket Pub/Sub
- **Type**: Binary + Library
- **Source**: `rust/event_bus/src/`
- **Purpose**: Replace the Python event bus with a high-performance Unix socket pub/sub
- **Topic filtering**, async (tokio), zero-copy where possible
- **Status**: Active development

### 3. `memory_vault` — SQLite-Backed Vector Store
- **Type**: Library
- **Source**: `rust/memory_vault/src/`
- **Purpose**: Persistent memory store with approximate vector search
- **Backed by SQLite**, matching the fleet forge-vault architecture
- **Status**: Active development

## Build Commands

```bash
cd /home/craig/projects/aethelgard/rust

# Build all crates
cargo build --workspace

# Check for issues
cargo check --workspace

# Run all tests
cargo test --workspace

# Release build
cargo build --release --workspace

# Lint
cargo clippy --workspace -- -D warnings
```

## Design Principles

1. **Zero runtime dependencies** where possible (stdlib preferred)
2. **Unix Domain Sockets** for IPC (matching the fleet standard)
3. **No GPU dependencies** (fleet runs on headless/GPU-less systems)
4. **All memory operations use safe Rust exclusively**
5. **Testing is mandatory** — every new function needs a test

## Integration Points

| Crate | Replaces | Socket Path |
|-------|----------|-------------|
| `event_bus` | `fleet/modules/event_bus.py` | `/tmp/aethelgard_bus.sock` |
| `memory_vault` | `~/.NOTTHEONETOEDIT/agent_memory/` | Direct SQLite (no socket) |
| `crypto_seal` | `fleet/pascal/crypto_seal.pas` | Library (no socket) |
