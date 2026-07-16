# Warp Integration Pattern (Session Discovery)
## Warp Terminal + Fleet Integration

### Warp Binary
- **Path**: `/home/craig/warp/target/release/warp-tui-oss`
- **Build**: `CARGO_BUILD_JOBS=1 cargo build --release -p warp_tui --features standalone`
- **RAM**: ~7GB peak, 4GB swap minimum (16GB+ recommended)
- **Build Time**: ~18 minutes with `CARGO_BUILD_JOBS=1`

### Executor Integration
Warp is a TUI application. For executor integration:

```json
{
  "id": "warp_session",
  "tools": [
    {"name": "terminal", "args": {"command": "WARP_API_KEY=$WARP_API_KEY /home/craig/warp/target/release/warp-tui-oss --resume <session_token>", "timeout": 120, "workdir": "/home/craig"}}
  ]
}
```

### Command Center Integration
```python
def warp_cmd(self, args):
    if args[0] == "status":
        bin_path = Path("/home/craig/warp/target/release/warp-tui-oss")
        if bin_path.exists():
            print(f"✅ Warp TUI: Built ({bin_path.stat().st_size} bytes)")
        else:
            print("⚠️ Warp: Not built")
    elif args[0] == "run":
        subprocess.run([WARP_BIN, "--api-key", os.environ.get("WARP_API_KEY", "")])
```

### Build Pitfalls (Session Verified)
1. **OOM Killer**: 7GB RAM + swap. 4GB swap = SIGKILL. Need 16GB+ swap or 32GB RAM.
2. **Feature Flag**: Use `--features standalone` (not `tui` - that's for `warpui_core`).
3. **Protoc Required**: `protobuf-compiler` package for protobuf codegen.
4. **App Crate Conflict**: Without `standalone`, pulls full `app` crate with GUI deps.

### Integration Points for Fleet
- **SMS → Warp**: Persist SMS vectors to Warp's local storage via Emerge bridge
- **Executor → Warp**: Queue Warp commands as batch jobs  
- **Warp → Emerge**: Warp's agent mode can call Emerge client via shell
- **Command Center**: Add `warp` subcommand for build/run/status

### Verification
```bash
# Binary check
ls -la /home/craig/warp/target/release/warp-tui-oss

# Help test
/home/craig/warp/target/release/warp-tui-oss --help

# Process check
pgrep -f warp-tui
```

### Build Command (Verified Working)
```bash
cd /home/craig/warp
CARGO_BUILD_JOBS=1 cargo build --release -p warp_tui --features standalone
# ~18 minutes, 7GB RAM peak
```