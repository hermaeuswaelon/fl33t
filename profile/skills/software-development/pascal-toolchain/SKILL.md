---
name: pascal-toolchain
description: Free Pascal Compiler (FPC) toolchain for building Aethelgard Fleet and other Pascal projects — compilation, static linking, cross-platform, debugging
version: 1.0.0
author: Ares
platforms: [linux]
tags: [pascal, fpc, compiler, toolchain, aethelgard, fleet, static-linking, debugging]
---

# Pascal Toolchain (Free Pascal Compiler)

## Compiler
- **FPC**: Available via system package (`fpc` command)
- **Version**: 3.2.2+ (modern Object Pascal, ISO 7185/10206 compatible)
- **Target**: x86_64-linux (default), cross-compile supported

## Compilation Modes

### Standard (Dynamic Linking)
```bash
fpc -O2 program.pas -oprogram
# Dynamic linking to libc, smaller binary
```

### Release Optimized
```bash
fpc -O3 -Xs program.pas -oprogram
# -O3 = max optimization
# -Xs = strip symbols
```

### Static Linking (Deployment)
```bash
fpc -O3 -Xs -XX -CX -Cg -k-static program.pas -oprogram
# -XX = smartlink (dead code elimination)
# -CX = smartlink units
# -Cg = generate debug info (for strip)
# -k-static = pass -static to linker
```

### With Debug Symbols
```bash
fpc -g -gl -O1 program.pas -oprogram
# -g = generate debug info
# -gl = use line info
# -O1 = light optimization (preserves structure)
```

### Position Independent Executable (PIE)
```bash
fpc -O3 -Xs -CX -XX -k-pie program.pas -oprogram
# For ASLR compatibility
```

## Common Flags Reference

| Flag | Purpose |
|------|---------|
| `-O1/-O2/-O3` | Optimization level |
| `-Xs` | Strip symbols from binary |
| `-XX` | Smartlink (remove unused code) |
| `-CX` | Smartlink units |
| `-Cg` | Generate debug info (DWARF) |
| `-k-static` | Pass `-static` to linker |
| `-k-pie` | Pass `-pie` to linker |
| `-dRELEASE` | Define RELEASE conditional |
| `-dDEBUG` | Define DEBUG conditional |
| `-Mobjfpc` | Object Pascal mode (default) |
| `-Sh` | Use ansistring (default) |
| `-vh` | Verbose: show hints |
| `-vw` | Verbose: show warnings |

## Conditional Compilation
```pascal
{$IFDEF RELEASE}
  // Release-only code
{$ENDIF}

{$IFDEF DEBUG}
  WriteLn('Debug: ', Msg);
{$ENDIF}
```

Compile with:
```bash
fpc -dRELEASE program.pas
fpc -dDEBUG program.pas
```

## Units & Libraries

### Static Library (.a)
```bash
fpc -O3 -XX -CX -Cg mylib.pas
# Produces mylib.o, mylib.a (if using {$LINKLIB})
```

### Shared Library (.so) — Plugin
```bash
fpc -O3 -Xs -XX -CX -Cg -shared myplugin.pas -omyplugin.so
# Requires: library keyword, exports clause
```

### Using External C Libraries
```pascal
{$LINKLIB c}        // Link libc
{$LINKLIB ssl}      // Link libssl
{$LINKLIB crypto}   // Link libcrypto
```

```pascal
function SSL_new(ctx: PSSL_CTX): PSSL; cdecl; external 'ssl' name 'SSL_new';
```

## Aethelgard Fleet Build Patterns

### Sensor Daemon (Static)
```bash
cd /home/craig/projects/aethelgard/fleet/pascal/netlens
fpc -O3 -Xs -XX -CX -Cg -k-static netlens.pas -onetlens
```

### Red Team Daemon (Static)
```bash
cd /home/craig/projects/aethelgard/fleet/pascal/redteam/escalate
fpc -O3 -Xs -XX -CX -Cg -k-static escalate.pas -oescalate
```

### Norse Plugin (Shared Object)
```bash
cd /home/craig/projects/aethelgard/fleet/pascal/plugins
fpc -O3 -Xs -XX -CX -shared hlidskjalf_plugin.pas -ohlidskjalf_plugin.so
```

### Fleet Core (Dynamic, with plugins)
```bash
cd /home/craig/projects/aethelgard/fleet/pascal/plugins
fpc -O2 fleet_core.pas -ofleet_core
```

## Cross-Compilation

### Linux → Windows (x86_64)
```bash
# Requires mingw-w64
fpc -Twin64 -Xr/usr/x86_64-w64-mingw32 program.pas -oprogram.exe
```

### Linux → macOS (x86_64/arm64)
```bash
# Requires macOS SDK + cross-binutils
fpc -Tdarwin -XR/path/to/macos/sdk program.pas
```

## Debugging

### GDB
```bash
fpc -g -gl -O1 program.pas -oprogram
gdb ./program
(gdb) break main
(gdb) run
```

### FPC Built-in Heap Tracing
```pascal
uses HeapTrc;
// Add at program start
SetHeapTraceOutput('heap.trc');
```

### Valgrind
```bash
fpc -g -gl -O1 program.pas -oprogram
valgrind --leak-check=full --show-leak-kinds=all ./program
```

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| `ld: cannot find -lX11` | `apt install libx11-dev` |
| `ld: cannot find -lssl` | `apt install libssl-dev` |
| `Error: Illegal qualifier` | Check `{$mode}` directive |
| `Can't find unit` | Check `-Fu` include paths |
| Static linking fails (glibc) | Use musl: `fpc -k-static -Xr/path/to/musl` |

## Project Structure (Aethelgard)
```
/home/craig/projects/aethelgard/fleet/pascal/
├── common/              # Shared units
│   ├── daemon_base.pas  # TDaemonRunner, JSON-RPC
│   ├── json_protocol.pas # OKResponse, ErrorResponse
│   ├── pascal_arsenal.pas # Crypto, encoding, syscalls
│   └── irrational_timers.pas # φ/e-based timers
├── netlens/             # Network sensor
├── memlens/             # Memory sensor
├── portforge/           # Port scanner
├── asmlens/             # Assembly analysis
├── elfforge/            # Binary analysis
├── packetforge/         # Packet crafting
├── redteam/             # Offensive daemons
│   ├── escalate/
│   ├── shredder/
│   ├── beacon/
│   ├── keyforge/
│   ├── spread/
│   ├── keyforge/
│   └── payloadforge/
├── plugins/             # Norse plugins (.so)
│   ├── fleet_core.pas   # Core orchestrator
│   ├── plugin_api.pas   # Plugin interface
│   └── *_plugin.pas     # 10 Norse plugins
└── dual-citizen-v2/     # CEF browser controller
```

## Build All (Arsenal Script)
```bash
/home/craig/projects/aethelgard/fleet/pascal/redteam/arsenal.sh
# Builds all redteam daemons + plugins
```

## Verification
```bash
# Check binary type
file ./escalate
# ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, stripped

# Check dependencies
ldd ./elfforge_v2
# not a dynamic executable (static)

# Check exports (plugin)
nm -D ./hlidskjalf_plugin.so | grep Plugin_
# Plugin_GetMetadata, Plugin_Init, Plugin_Shutdown...
```

## Integration with Hermes
- Use `terminal(command="fpc ...", background=true, notify_on_complete=true)` for builds
- Spawn daemons with `terminal(background=true, notify_on_complete=true)`
- Communicate via Unix sockets (`nc -U`, Python `socket.AF_UNIX`)
- Fleet bus at `/tmp/aethelgard_bus.sock` for inter-daemon comms