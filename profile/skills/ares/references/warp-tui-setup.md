# Warp TUI Setup (Linux/OSS)

## Binary
- Source: `~/warp/` — OSS Warp terminal repo
- Built binary: `~/warp/target/release/warp-tui-oss` (~663 MB, standalone)
- Wrapper command: `~/.local/bin/warp` → executes warp-tui-oss with proper PATH

## Channel Config Dependency
**Critical:** `warp-tui-oss` requires `warp-channel-config` on PATH at runtime.
Without it, the binary panics. Warp's private repo requires SSH access.

**Fix:** Build a tiny Rust stub that outputs valid OSS channel config JSON:
```bash
rustc /tmp/stub.rs -o ~/.local/bin/warp-channel-config
```
See `hermes-executor/references/warp-channel-config-stub.md` for the full stub code.

## Launch
```bash
warp                          # Local TUI mode (no auth)
warp --api-key $WARP_API_KEY  # Authenticated with Warp.dev
```

## Desktop Integration (XFCE)
- Desktop entry at `~/.local/share/applications/warp-tui.desktop`
- Launches xfce4-terminal with warp-tui-oss inside

## Unified Field Integration
- `uf warp status` — binary health, memory count, session count
- `WarpMemoryStore` — CRUD memories via unified_field + emerge /warp/memories/
- `WarpSessionStore` — Session context snapshots via SVA + emerge /warp/sessions/
- Bridge module: `work/warp_bridge.py` (757 lines)

## Build from Source
```bash
cd ~/warp
cargo build --release -p warp_tui --features standalone
```

## Pitfalls
- Resources must be staged beside the binary: `NO_LICENSES=1 SKIP_SETTINGS_SCHEMA=1 bash script/prepare_bundled_resources target/release/resources oss`
- Channel config stub only supports OSS channel. Dev/preview need different config
- WARP_API_KEY env var for Warp.dev auth (optional for local mode)
- Binary tries to open PTY — run in a real terminal, not a background process
