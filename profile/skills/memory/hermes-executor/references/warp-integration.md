# Warp TUI Integration Pattern
## Integrating Warp Terminal with Executor & Command Center

### Warp Binary
- **Path**: `/home/craig/warp/target/release/warp-tui-oss`
- **Size**: ~695MB (statically linked Rust binary)
- **Build**: `cd /home/craig/warp && CARGO_BUILD_JOBS=1 cargo build --release -p warp_tui --features standalone`
- **Run**: `warp-tui-oss --api-key $WARP_API_KEY`

### Executor Integration Pattern
Warp is a TUI application, not a headless tool. Integration strategies:

#### 1. Background Session (Non-interactive)
```bash
# Run Warp with API key for headless operations
WARP_API_KEY=$WARP_API_KEY /home/craig/warp/target/release/warp-tui-oss --resume <session_token>
```

#### 2. Executor Batch Invocation
```json
{
  "id": "warp_session",
  "tools": [
    {"name": "terminal", "args": {"command": "WARP_API_KEY=$WARP_API_KEY /home/craig/warp/target/release/warp-tui-oss --resume session_123", "timeout": 60, "workdir": "/home/craig"}}
  ]
}
```

#### 3. Command Center Integration
```python
# In command_center.py
def warp_cmd(self, args):
    if args[0] == "status":
        bin_path = Path("/home/craig/warp/target/release/warp-tui-oss")
        if bin_path.exists():
            print(f"✅ Warp TUI: Built ({bin_path.stat().st_size} bytes)")
        else:
            print("⚠️ Warp: Not built")
    elif args[0] == "run":
        subprocess.run(["/home/craig/warp/target/release/warp-tui-oss", "--api-key", os.environ.get("WARP_API_KEY", "")])
```

### Build Requirements (Critical)
- **RAM**: 14GB+ used during build, 4GB swap minimum
- **Time**: ~18 minutes with `CARGO_BUILD_JOBS=1`
- **Protoc**: Required for protobuf compilation (`protobuf-compiler` package)
- **Features**: `--features standalone` for self-contained binary

### Build Pitfalls (Documented from Session)
1. **OOM Killer**: Build uses ~7GB RAM + swap. 4GB swap insufficient. Need 16GB+ swap or 32GB RAM.
2. **Feature Flags**: `warp_tui` package uses `--features standalone`, not `tui` (that's for `warpui_core`).
3. **Protoc Missing**: Error "Could not find `protoc`" → `apt-get install protobuf-compiler`
4. **App Crate Conflict**: Building `warp_tui` alone requires `standalone` feature; otherwise it pulls in full `app` crate with GUI dependencies.

### Integration Points for Future
- **SMS → Warp**: Persist SMS vectors to Warp's local storage via Emerge bridge
- **Executor → Warp**: Queue Warp commands as batch jobs
- **Warp → Emerge**: Warp's agent mode can call Emerge client via shell
- **Command Center**: Add `warp` subcommand for build/run/status

### Verification Commands
```bash
# Check binary
ls -la /home/craig/warp/target/release/warp-tui-oss

# Test help
/home/craig/warp/target/release/warp-tui-oss --help

# Check running processes
pgrep -f warp-tui
```