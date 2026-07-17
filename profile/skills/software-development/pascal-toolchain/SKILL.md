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

## Lazarus / LCL Projects (GUI & CEF4Delphi)

When building Lazarus LCL projects (GTK2 widgetset) with CEF4Delphi on Linux, the full include/unit path set must be specified. The project file (`.lpi`) usually has baked-in paths — when they're stale, compile directly with `fpc`.

### CEF4Delphi Browser Build (dual_citizen_v2 / bromium)

```bash
cd ~/projects/aethelgard/fleet/pascal/dual-citizen-v2

fpc \
  -dEnableLibOverlay \        # skips missing gtk2DisableLibOverlay unit
  -dLCLGTK2 \                  # enables GTK2 codepaths in uCEFLinuxFunctions
  -Fu/path/to/CEF4Delphi/source \
  -Fu/path/to/CEF4Delphi/packages \
  -Fu/path/to/CEF4Delphi/packages/lib/x86_64-linux \
  -Fi/path/to/CEF4Delphi/source \
  -Fu/usr/lib/lazarus/X.Y/lcl/units/x86_64-linux/gtk2 \
  -Fu/usr/lib/lazarus/X.Y/lcl/units/x86_64-linux \
  -Fu/usr/lib/lazarus/X.Y/components/lazutils/lib/x86_64-linux \
  -Fu/usr/lib/lazarus/X.Y/packager/units/x86_64-linux \
  project.lpr -o.output_binary
```

**Key flags explained:**

| Flag | Why |
|------|-----|
| `-dEnableLibOverlay` | Skips `gtk2DisableLibOverlay` unit (missing on many distros) |
| `-dLCLGTK2` | Activates `{$IFDEF LCLGTK2}` blocks in `uCEFLinuxFunctions.pas` (PGdkEventKey types) |
| `-Fu/usr/lib/lazarus/X.Y/lcl/units/x86_64-linux/gtk2` | LCL GTK2 widgetset units (Gtk2Int, gtk2proc, etc.) |
| `-Fu/usr/lib/lazarus/X.Y/packager/units/x86_64-linux` | FPC `fcl-res` / resource handling |

### Lazarus .res Files on Linux

Lazarus `.res` files are Windows PE-format resources and can't be read on Linux. The `{$R *.res}` directive will fail:

```pascal
// ❌ Compile error on Linux:
{$R *.res}

// ✅ Fix — comment it out:
// {$R *.res}
```

If the project needs a `.res` file for the linker, create a minimal one with Python:

```python
import struct
with open('project.res', 'wb') as f:
    f.write(struct.pack('<HHIIII', 0x0000, 0x0020, 0xFFFF, 0x0000, 0x0000, 0x0000))
```

### CEF Extension Loading

CEF4Delphi has `DisableExtensions` (boolean, defaults to False), NOT `EnableExtensions` or `ExtensionDir`. Load unpacked extensions via command line:

```pascal
// ✅ Correct:
GlobalCEFApp.AddCustomCommandLine('--load-extension=/path/to/extensions/');

// ❌ Wrong — these properties don't exist:
// GlobalCEFApp.EnableExtensions := True;   // compile error
// GlobalCEFApp.ExtensionDir := '...';       // compile error
```

### Path Reference

| Component | Typical Path |
|-----------|-------------|
| CEF4Delphi source | `~/.aethelgard/workspace/browser/CEF4Delphi/source/` |
| CEF4Delphi packages | `~/.aethelgard/workspace/browser/CEF4Delphi/packages/` |
| CEF binary libs | `~/.aethelgard/workspace/browser/CEF4Delphi/cef_binary_XXX/Release/` |
| Lazarus LCL | `/usr/lib/lazarus/X.Y/lcl/units/x86_64-linux/` |
| Lazarus GTK2 widgetset | `/usr/lib/lazarus/X.Y/lcl/units/x86_64-linux/gtk2/` |

### CEF Event Type Signatures

CEF4Delphi event callbacks use specific Pascal calling conventions. Getting `var` vs `out` wrong causes a compile error:

```pascal
// ✅ Correct — CEF4Delphi uses `out` for Boolean results:
procedure DoOpenUrlFromTab(Sender: TObject; const browser: ICefBrowser;
  const frame: ICefFrame; const targetUrl: ustring;
  targetDisposition: TCefWindowOpenDisposition;
  userGesture: Boolean; out aResult: Boolean);

// ❌ Wrong — `var` causes:
// "Incompatible types: got '<procedure with var>' expected '<procedure with out>'"
```

Always check the actual CEF4Delphi event type definition in `uCEFChromiumEvents.pas` when hooking a new event. The type alias `TOnBeforeBrowse`, `TOnOpenUrlFromTab`, etc. is defined there.

### Pitfalls

- **Stale `.ppu` files** — FPC caches compiled units. After editing `.lpr` or `.pas` sources, delete `*.ppu` and `*.or` files before rebuild: `rm -f *.ppu *.or`
- **Include path mismatch** — The `.lpr` file has `{$I /path/to/cef.inc}` hardcoded. If CEF4Delphi moved, edit this path. The `.lpi` project file has separate `IncludeFiles` and `OtherUnitFiles` entries — update both.
- **The include file syntax** is `{$I /absolute/path/cef.inc}` — the IDE can't resolve it via its code tool manager if the path is wrong, but `fpc` will find it via `-Fi` on the command line.
- **Two binaries, two `.lpr` files** — The dual-citizen project compiles TWO programs from TWO source files (`dual_citizen_v2.lpr` → `bromium`, `cef_controller.lpr` → `cef_controller`). Editing one does NOT affect the other.

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
- **AI readability:** FreePascal source is opaque to most LLMs. Use `work/pascal_lens.py` to convert `.pas`/`.lpr` files to annotated pseudo-code. See `references/pascal-lens.md`.