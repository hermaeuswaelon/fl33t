# Hex-Patching `--disable-extensions` in Compiled Pascal CEF Binary
*July 2026 session — source wouldn't compile, binary had the flag baked in*

## The Problem

The `bromium` binary (compiled from `dual_citizen_v2.lpr`) had `GlobalCEFApp.AddCustomCommandLine('--disable-extensions')` hardcoded. Attempting to compile from source failed:

```
Fatal: Cannot open include file "/home/craig/CEF4Delphi/source/cef.inc"
fpc: Can't find unit gtk2DisableLibOverlay used by Interfaces
```

Two blockers:
1. Include path points to `/home/craig/CEF4Delphi/` but actual CEF source is at `/home/craig/.aethelgard/workspace/browser/CEF4Delphi/`
2. Missing Lazarus LCL GTK2 widget units (requires full Lazarus IDE install)

## The Fix

Both `--disable-extensions` (22 chars) and `--enable-extensions` (21 chars + padding) need the same storage in the ELF `.rodata` section:

```bash
cd /home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2

# Verify the string exists
strings bromium | grep disable-extensions

# Replace in-place (trailing space pads to same length)
sed -i 's/--disable-extensions/--enable-extensions /g' bromium

# Verify
strings bromium | grep enable-extensions
```

**Verification:**
```bash
file bromium              # Still reports valid ELF
strings bromium | grep enable-extensions  # Shows patched flag
```

## The Source-File Distinction

There are TWO `.lpr` files in the build directory:

| File | Binary | Status | 
|------|--------|--------|
| `dual_citizen_v2.lpr` | `bromium` (copy of `dual_citizen_v2`) | Had `--disable-extensions`, patched via sed |
| `cef_controller.lpr` | `cef_controller` | Never had the flag, already clean |

Both needed the include path fix: `{$I /home/craig/CEF4Delphi/source/cef.inc}` → `{$I /home/craig/.aethelgard/workspace/browser/CEF4Delphi/source/cef.inc}`

## Extension Loading (Real CEF API)

CEF does NOT have `EnableExtensions` or `ExtensionDir` properties. The real way to load unpacked extensions is via the `--load-extension` command-line switch:

```pascal
// DON'T use these (they don't exist in CEF4Delphi):
// GlobalCEFApp.EnableExtensions := True;    // ✗ compile error
// GlobalCEFApp.ExtensionDir := '...';       // ✗ compile error

// DO use this:
GlobalCEFApp.AddCustomCommandLine('--load-extension=/path/to/extensions/');
```

Extensions are enabled by default (`DisableExtensions` defaults to `False` in `uCEFApplicationCore.pas`). The `--load-extension` flag takes a comma-separated list of directories. CEF loads them at startup.

CEF4Delphi supports a subset of the Chrome extension API natively. Content scripts inject automatically. `action` popups work if the host app navigates to `chrome-extension://<id>/popup.html` (extension ID computed from absolute path hash — discoverable via remote debugging port 9224).

## Build Workflow (Full Recompile)

When you can recompile from source instead of hex-patching:

```bash
cd ~/projects/aethelgard/fleet/pascal/dual-citizen-v2

# Fix include paths in ALL .lpr and .pas files:
#   {$I /home/craig/CEF4Delphi/source/cef.inc}
#   → {$I /home/craig/.aethelgard/workspace/browser/CEF4Delphi/source/cef.inc}

# Comment out {$R *.res} (Linux doesn't need it)

# Compile with required defines and paths:
fpc \
  -dEnableLibOverlay \           # avoids gtk2DisableLibOverlay dependency
  -dLCLGTK2 \                    # enables GTK2 code paths in uCEFLinuxFunctions
  -Fu/path/to/CEF4Delphi/source \
  -Fu/path/to/CEF4Delphi/packages \
  -Fu/path/to/CEF4Delphi/packages/lib/x86_64-linux \
  -Fi/path/to/CEF4Delphi/source \
  -Fu/usr/lib/lazarus/4.4/lcl/units/x86_64-linux/gtk2 \
  -Fu/usr/lib/lazarus/4.4/lcl/units/x86_64-linux \
  -Fu/usr/lib/lazarus/4.4/components/lazutils/lib/x86_64-linux \
  -Fu/usr/lib/lazarus/4.4/packager/units/x86_64-linux \
  dual_citizen_v2.lpr -o.bromium
```

Key flags explained:
- `-dEnableLibOverlay`: Skips the `gtk2DisableLibOverlay` unit that's missing on some FPC-only installs
- `-dLCLGTK2`: Enables the GTK2 conditional code in `uCEFLinuxFunctions.pas` (needed for `PGdkEventKey` types)
- All `-Fu` paths: Point to LCL GTK2 widgetset units, CEF4Delphi source, and its compiled package

## Lesson

When a compiled Pascal binary has baked-in CEF flags:
1. **Hex-patch** if source won't compile (same-length string replacement in `.rodata`)
2. **Recompile** if you have the full Lazarus toolchain — use the flags above
3. Verify with `file`, `strings`, and launching the binary

This works because CEF flags live in string literals in the read-only data segment. ELF doesn't care what the string says as long as the null terminator stays in bounds.
