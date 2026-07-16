# Pascal Lens — Making FreePascal Source AI-Readable

## Problem
FreePascal / Object Pascal source (`.pas`, `.lpr`, `.ppu`) is opaque to most LLMs because of:
- `begin`/`end` syntax (unfamiliar to coders raised on `{}`)
- `:=` for assignment
- `procedure`/`function` declaration style
- CEF4Delphi-specific types (`TCefApplication`, `TChromium`, `GlobalCEFApp`)
- `{$I }` include directives with absolute paths
- `.lpr` as program entry point convention

## Solution: `pascal_lens.py`

Located at `work/pascal_lens.py`. Converts Pascal source into annotated pseudo-code.

### Convert a file
```bash
python3 pascal_lens.py file.pas                     # → annotated pseudo-code
python3 pascal_lens.py file.pas --full               # + CEF4Delphi type reference
python3 pascal_lens.py file.pas --analyze            # → JSON structure analysis
```

### Analyze a directory
```bash
python3 pascal_lens.py --dir /path/to/pas/ --analyze  # Structure of all files
python3 pascal_lens.py --dir /path/to/pas/            # Convert all files
```

### CEF4Delphi type reference
```bash
python3 pascal_lens.py --explain-types                # Print all known CEF types
```

## What the lens does
- `begin` → `{`, `end;` → `}`
- `:=` → `=`
- `procedure Foo(x:Integer);` → `procedure Foo(x: Integer)`
- `function Bar: String;` → `function Bar → String`
- `Result := X;` → `result = X;`
- `Self` → `this`, `Inherited` → `super`
- `Length()` → `len()`, `Inc()` → `++`, `Dec()` → `--`
- Pascal comments → `//` or `/* */`
- Preserves all line numbers as `/* Ln */` markers

## Known CEF4Delphi types (20+ documented)
The lens includes a dictionary of CEF4Delphi types like `GlobalCEFApp` (singleton app controller), `Chromium1` (browser view component), `StartMainProcess` (CEF lifecycle), `AddCustomCommandLine` (flag injection), `ExtensionDir` (unpacked extension loading), etc.

## Example: analyzing dual_citizen_v2.lpr
```
Type:     program
Name:     dual_citizen_v2
Lines:    59
CEF API:  LogSeverity, LocalesDirPath, EnableMediaStream, FrameworkDirPath,
          GlobalCEFApp, DestroyGlobalCEFApp, EnableGPU, EnableExtensions,
          CustomWidgetSetInitialization, etc.
```

## Pitfalls
- The conversion is lossy (loses Pascal-specific semantics like `with`, `case`, `repeat`/`until`)
- Designed for *reading*, not for round-tripping back to Pascal
- Complex generics and advanced record types may not convert cleanly
- Use `--analyze` first to understand the file structure before reading the full conversion
