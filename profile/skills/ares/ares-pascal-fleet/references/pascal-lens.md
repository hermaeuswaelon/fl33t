# Pascal Lens — Making FreePascal AI-Readable

## Problem
FreePascal/ObjFPC syntax (`begin..end`, `:=`, `.lpr`, `{$mode objfpc}`, `^` pointers, `TMyClass = class(TObject)`) is opaque to most LLMs. The `ucontrollerbrowser.pas` file is 957 lines — too large for AI analysis without structural extraction.

## Solution
`work/pascal_lens.py` converts Pascal to annotated pseudo-code with C-style syntax.

## Commands
```bash
# Analyze: extract structure without converting
python3 pascal_lens.py file.pas --analyze

# Convert: full annotated pseudo-code
python3 pascal_lens.py file.pas --full

# Batch: convert all .pas/.lpr in directory
python3 pascal_lens.py --dir /path/to/pas/

# CEF4Delphi type reference sheet
python3 pascal_lens.py --explain-types
```

## CEF4Delphi Key Types (for AI context)
| Pascal Type | Meaning |
|-------------|---------|
| `TCefApplication` | CEF app controller — manages lifecycle, flags, paths |
| `GlobalCEFApp` | Singleton TCefApplication instance — configure before StartMainProcess |
| `TControllerForm` | Main form wrapping the Chromium browser component |
| `TChromium` | The actual browser view — web page renderer |
| `CefWidgetSet` | GTK2 widget set for embedding CEF in Linux forms |
| `AddCustomCommandLine` | Adds a flag to CEF's command-line (passed to all subprocesses) |
| `StartMainProcess` | Call to start CEF subprocesses; returns False in renderer/subprocess |
| `DestroyGlobalCEFApp` | Cleanup CEF; must call at end |

## Dual Source Pitfall
The dual-citizen-v2 directory has TWO Pascal programs:
- `dual_citizen_v2.lpr` → compiles to `bromium` (37MB, full GUI, socket IPC)
- `cef_controller.lpr` → compiles to `cef_controller` (37MB, headless)

Editing one does NOT affect the other. Always check which `.lpr` the binary was built from.
