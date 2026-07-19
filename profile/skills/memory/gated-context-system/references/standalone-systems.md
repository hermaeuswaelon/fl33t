# Standalone Systems — No Hermes Integration (as of Jul 2026)

These systems were audited and found to be **not integrated** with Hermes. Documenting saves future sessions from re-investigating.

## Emerge (emergefs v0.0.5)

**What it is:** A Z0RPC+ZODB distributed compute/filesystem node using ZeroMQ pub/sub.

**Status:** Standalone daemon, no Hermes integration.

| Property | Value |
|----------|-------|
| Package | `emergefs` v0.0.5 at `~/.local/lib/python3.13/site-packages/emerge/` |
| Daemon | `emerge-node-standalone` PID 2053402, running since Jul 16 |
| Port | 54242 (ZMQ/zerorpc) |
| Config | `~/emerge.ini` → localhost:4242 |
| Hermes refs | Zero references in config, tools, plugins, skills |
| Hermes integration needed | Hermes tool or MCP server connecting via ZMQ/zerorpc to port 54242 |

There is also an `emerge_fallback` directory referenced in the `.NOTTHEONETOEDIT` backup, but it was empty.

## Warp (Terminal Emulator)

**What it is:** The Warp terminal (Rust) — a GPU-accelerated terminal emulator with AI features.

**Status:** Checkout only, no binary built, no Hermes integration.

| Property | Value |
|----------|-------|
| Location | `~/warp/` |
| Branch | `master` (Warp upstream repo) |
| Binary | Not built |
| Build artifacts | 14GB in `target/` |
| Hermes refs | Zero references in config or tools |
| Integration path | Could build binary and configure Hermes to use Warp as terminal backend, or write an MCP bridge. Different product category though — Hermes is an AI agent, Warp is a terminal emulator. |

## MemGPT / mem0

**What it is:** External memory provider plugins for Hermes.

**Status:** Referenced in SMS skill description as aspirational tri-brid component, not actually installed.

| Property | Value |
|----------|-------|
| Listed in `hermes memory status` | As available plugin type (not installed) |
| Actual installation | No `mem0` or `memgpt` package/files found |
| Active memory system | Built-in MemoryStore (VSA-backed) |
| To install | `pip install mem0 && hermes config set memory.provider mem0` |
