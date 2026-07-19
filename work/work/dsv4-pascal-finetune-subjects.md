# DeepSeek V4 Pascal Fine-Tune — Subject Coverage Analysis

Generated from:
- **freepascal-docs/** (16,834 HTML files, 107 MB — full RTL + FCL documentation)
- **FAQ/Knowledge base** (32 KB cached from freepascal.org)
- **Tutorials** (Basic Pascal Tutorial, OOP Pascal Tutorial, Lazarus Tutorial)
- **Aethelgard Fleet** (147 .pas/.lpr files — real-world Pascal code across 20+ domains)
- **pascal_lens.py** (Pascal-to-AI-readable converter)

---

## TIER 1 ★★★ CORE LANGUAGE — ESSENTIAL FOR ANY PASCAL MODEL

| Subject | Source | In Fleet? | Priority |
|---------|--------|-----------|----------|
| Program structure (program, unit, interface, implementation) | tutorials, FAQ | YES | HIGH |
| Data types: Integer, Real, Char, String, Boolean, WideString, AnsiString | tutorials, RTL | YES | HIGH |
| Enumerated types, subrange types, sets | tutorials | no direct | HIGH |
| Type declarations (type, record, array, file, object, class) | tutorials + docs | YES | HIGH |
| Variables, constants, typed constants | tutorials, RTL | YES | HIGH |
| Operators: :=, +, -, *, /, div, mod, and, or, not, xor, shl, shr, in, @, ^ | tutorials | YES | HIGH |
| Control flow: if/then/else, case/of, for/do, while/do, repeat/until | tutorials | YES | HIGH |
| Procedures & functions (var/const/out params, overloading, default params) | tutorials | YES | HIGH |
| Scope rules & forward declarations | tutorials | YES | HIGH |
| Unit system, uses clauses, circular dependency rules | tutorials, RTL | YES | HIGH |
| Compiler directives: {$IFDEF}, {$I}, {$MODE}, {$H+}, etc. | tutorials, code | YES | HIGH |
| Assignments and type casting | tutorials | YES | HIGH |
| Expressions and operator precedence | tutorials | YES | HIGH |
| I/O: Read/ReadLn, Write/WriteLn, file of, text files | tutorials + RTL | YES (logs) | HIGH |

## TIER 2 ★★★ OBJECT PASCAL / OOP — ESSENTIAL

| Subject | Source | In Fleet? | Priority |
|---------|--------|-----------|----------|
| Classes: constructor, destructor, methods, fields | OOP tutorial, RTL | YES | HIGH |
| Inheritance: virtual, override, reintroduce, abstract | OOP tutorial | YES (daemon_base) | HIGH |
| Properties: read, write, default, stored, index | OOP tutorial | YES | HIGH |
| Class methods, class properties, class variables, class constructors | OOP tutorial | YES | HIGH |
| Interfaces: implements, GUID, delegation | OOP tutorial, CEF | YES (CEF) | HIGH |
| Advanced records (methods, operators, class operators) | OOP tutorial | no direct | MEDIUM |
| Record helpers, class helpers | OOP tutorial | no direct | MEDIUM |
| Generics: specialize, TList<T>, constraints | RTL docs | no direct | MEDIUM |
| Exceptions: try/except/raise/finally | RTL (SysUtils) | YES | HIGH |
| RTTI: is, as, TObject.ClassType, ClassParent, ClassName | RTL (typinfo) | YES (core_identity) | HIGH |

## TIER 3 ★★★ RTL STANDARD LIBRARY — ESSENTIAL FOR CODE GENERATION

| Subject | Source | In Fleet? | Priority |
|---------|--------|-----------|----------|
| System unit: core types, I/O, memory mgmt, var/absolute/threadvar | docs | YES | HIGH |
| SysUtils: IntToStr, Format, FileExists, ExtractFile* | docs | YES (heavy) | HIGH |
| SysUtils: TStringBuilder, TFormatSettings | docs | YES | HIGH |
| SysUtils: Exception classes, DateToStr, TimeToStr | docs | YES | HIGH |
| Classes: TList, TStringList, TStream, TFileStream, TStringStream | docs | YES | HIGH |
| Classes: TThread, TComponent, TPersistent, TCollection | docs | YES | HIGH |
| Classes: TApplication, TDataModule | docs | YES | HIGH |
| Math: Sin, Cos, Sqrt, Power, Log, Min, Max, Random, Round, Trunc | docs | YES | HIGH |
| DateUtils: IncDay, DaysBetween, etc. | docs | YES (chronos) | HIGH |
| StrUtils: LeftStr, RightStr, AnsiContainsStr, etc. | docs | YES | HIGH |
| Strings: StrCat, StrCopy, StrComp, StrPas, StrPCopy | docs | YES | HIGH |
| Types: TPoint, TRect, TSize, etc. | docs | no direct | MEDIUM |
| Variants: VarType, VarCast, VarArrayCreate | docs | no direct | MEDIUM |
| TypInfo: GetPropValue, SetPropValue, GetEnumName | docs | YES (core_identity) | HIGH |

## TIER 4 ★★ RTL — UNIX / SYSTEM PROGRAMMING (HIGH VALUE FOR OUR USE CASE)

| Subject | Source | In Fleet? | Priority |
|---------|--------|-----------|----------|
| BaseUnix: fpOpen, fpRead, fpWrite, fpStat, fpMmap, fpIOctl | docs | YES (heavy) | HIGH |
| Unix: process signals, waitpid, nanosleep | docs | YES | HIGH |
| Unix: stat, statfs, sysinfo structures | docs | YES (system_meter) | HIGH |
| Unix: dirname, basename, gethostname, getpid, getenv | docs | YES | HIGH |
| Unix: Select, socketpair, pipes | docs | YES (plugins) | HIGH |
| Unixtype: cint, clong, time_t, pid_t, mode_t, uid_t, gid_t | docs | YES | HIGH |
| Sockets: TSocket, sockaddr_in, connect, bind, listen, accept, send, recv | docs | YES (NETWORK heavy) | HIGH |
| Sockets: TCP, UDP, raw sockets, socket options | docs | YES | HIGH |
| Process: TProcess, RunCommand, poWaitOnExit, poUsePipes | docs | YES | HIGH |
| DynLibs: LoadLibrary, GetProcAddress, UnloadLibrary | docs | YES (crypto_seal) | HIGH |
| CTypes: cint, clong, cchar, cuint8..64, csize_t | docs | YES (pcap_bridge) | HIGH |
| CThreads: multithreading on Unix (cthreads unit) | docs | YES (many) | HIGH |
| CwString: WideString C-compatible handling | docs | YES (CEF) | MEDIUM |
| Linux: specific Linux syscall wrappers | docs | YES (file_sentry) | HIGH |
| LineInfo: stack trace from debug info | docs | no direct | MEDIUM |

## TIER 5 ★★ LIBRARIES HEAVILY USED IN OUR FLEET — HIGH TUNE VALUE

| Subject | Source | In Fleet? | Priority |
|---------|--------|-----------|----------|
| fpjson, jsonparser: TJSONObject, TJSONArray, JSON parsing | docs | YES (40+ files!) | CRITICAL |
| SQLite3: sqlite3dyn, TSQLiteDatabase | docs | YES (chronos_db, memory_db) | HIGH |
| SyncObjs: TCriticalSection, TEvent, TSemaphore | docs | YES (core_bus) | MEDIUM |
| Contnrs: TObjectList, TStack, TQueue, THashedStringList | docs | no direct | MEDIUM |
| Sha1, MD5: hashing units | docs | YES (code_forge_types, docsleuth) | HIGH |
| Base64: encoding/decoding | docs | YES (core_identity) | HIGH |
| DaemonApp: TDaemon, TDaemonMapper | docs | not used (custom) | MEDIUM |
| CustApp: TCustomApplication | docs | not used (custom) | MEDIUM |
| IniFiles: TIniFile | docs | YES (plugins) | HIGH |
| Zipper/TZipFile, ZStream: compression | docs | no direct | MEDIUM |
| EventLog: TEventLog | docs | no direct | LOW |
| Dos: GetDate, GetTime, GetEnv, DiskFree, DiskSize | docs | YES (beacon) | MEDIUM |
| Printer: TPrinter | docs | no direct | LOW |
| GetText: i18n support | docs | no direct | LOW |
| URIParser: URI parsing | docs | no direct | MEDIUM |

## TIER 6 ★ SECURITY / SYSTEMS PROGRAMMING — UNIQUE VALUE

| Subject | Source | In Fleet? | Priority |
|---------|--------|-----------|----------|
| Process memory: /proc/<pid>/mem access, ptrace | custom code | YES (memlens, proc_guard) | HIGH |
| ELF binary: headers, sections, relocations, dynamic symbols | ELF docs | YES (elfforge) | HIGH |
| ELF: .got, .plt, symbol tables, section headers | ELF docs | YES | HIGH |
| ROP gadget finding from ELF binaries | custom code | YES (rop_finder) | HIGH |
| Packet capture: libpcap bindings, BPF filters | custom code | YES (netlens) | HIGH |
| Packet dissection: TCP/IP/HTTP/DNS protocol parsing | custom code | YES (dissectors) | HIGH |
| OS fingerprinting: TCP/IP stack heuristics | custom code | YES (fingerprint) | HIGH |
| Port scanning: SYN, TCP connect, UDP, timing | custom code | YES (scanner) | HIGH |
| Raw sockets: IP_HDRINCL, packet crafting, checksums | custom code | YES (packetforge) | HIGH |
| TUN/TAP bridge: /dev/net/tun ioctl | custom code | YES (tap_bridge) | HIGH |
| Machine code injection: mmap RWX + copy + execute | custom code | YES (asm_executor) | HIGH |
| Process monitoring: ptrace, /proc/<pid>/status | custom code | YES (proc_guard) | HIGH |
| System metrics: /proc/stat, /proc/meminfo, /proc/loadavg | custom code | YES (system_meter) | HIGH |
| AES-256-GCM: OpenSSL EVP dynamic loading | custom code | YES (crypto_seal) | HIGH |
| Timing services: clock_gettime, high-res timers | custom code | YES (chronos) | HIGH |
| File monitoring: inotify | custom code | YES (file_sentry) | HIGH |
| Privilege escalation: SUID/CAP patterns | custom code | YES (escalate) | HIGH |
| C2 beacon: HTTP/DNS exfil, heartbeats | custom code | YES (beacon) | HIGH |
| Lateral movement: SSH, SMB, WMI patterns | custom code | YES (spread) | HIGH |
| Keylogging: XRecord extension | custom code | YES (keyforge) | HIGH |
| Binary payload generation: shellcode, PE/ELF stagers | custom code | YES (payloadforge) | HIGH |
| File shredding: secure deletion, overwrite patterns | custom code | YES (shredder) | HIGH |
| HTML parsing from Pascal | custom code | YES (omniprofile) | MEDIUM |
| Process text substitution (ed) patterns | custom code | YES (text_rapier) | MEDIUM |
| Plugin system: dynamic loading, RPC, JSON IPC | custom code | YES (plugins/) | HIGH |

## TIER 7 ★ CEF4DELPHI / BROWSER EMBEDDED — NICHE BUT HIGH VALUE

| Subject | Source | In Fleet? | Priority |
|---------|--------|-----------|----------|
| CEF lifecycle: GlobalCEFApp, StartMainProcess, DestroyGlobalCEFApp | CEF code | YES | HIGH |
| TChromium browser component and events | CEF code | YES | HIGH |
| ChromiumWindow vs OSR mode | CEF code | YES | MEDIUM |
| CEF command-line flags: --disable-web-security, --user-data-dir | CEF code | YES | HIGH |
| CEF IPC: ICefProcessMessage, ICefFrame communication | CEF code | YES | HIGH |
| Lazarus Forms: TForm, TApplication, LCL widgetset | CEF code | YES | HIGH |
| CEF resource loading: FrameworkDirPath, ResourcesDirPath, LocalesDirPath | CEF code | YES | HIGH |
| OSR (Off-Screen Rendering) mode configuration | CEF code | templates | MEDIUM |
| WebRTC, GPU, extensions, print preview configuration | CEF code | YES | MEDIUM |
| CEF event handlers: OnBeforePopup, OnTitleChange, OnConsoleMessage | CEF code | YES | HIGH |

## TIER 8 ★ FCL — ADDITIONAL, NICHE BUT COVERED

| Subject | Source | In Fleet? | Priority |
|---------|--------|-----------|----------|
| DB: TDataSet, TDBDataset, TField, database app patterns | docs | no direct | MEDIUM |
| SQLdb: TSQLTransaction, TSQLQuery, TIBConnection, TMSSQLConnection | docs | no direct | MEDIUM |
| MemDS: in-memory datasets (TMemDataset) | docs | no direct | LOW |
| FGL: TFPGList, TFPGMap, TFPGObjectList (generic containers) | docs | no direct | MEDIUM |
| ASCII85, Blowfish, IDEA: crypto units | docs | no direct | LOW |
| CRT: console I/O, text color, cursor control | docs | no direct | MEDIUM |
| Graph: graphics primitives (BGI compatibility) | docs | no direct | LOW |
| Video: terminal video modes | docs | no direct | LOW |
| MMX: SIMD intrinsic wrappers | docs | no direct | MEDIUM |
| Matrix: matrix math operations | docs | no direct | MEDIUM |
| AVL_Tree: self-balancing binary search tree | docs | no direct | MEDIUM |
| FPMimeTypes, IPProtocol | docs | no direct | LOW |
| GetOpts: command-line option parsing | docs | no direct | MEDIUM |
| Extended: FPWideString, FPImage, LResources, LCL | docs | no direct | LOW |
| Resources: StringTable, Bitmap, Icon, Version, GroupCursor | docs | no direct | LOW |
| COFF/Mach-O readers/writers | docs | no direct (ELF only) | MEDIUM |
| ExternalReader/Writer: external file format helpers | docs | no direct | LOW |
| FPDoc: documentation generation format | docs (roots) | no direct | LOW |

## TIER 9 ★ CROSS-PLATFORM / TARGET INFO — USEFUL

| Subject | Source | In Fleet? | Priority |
|---------|--------|-----------|----------|
| Win32 target: Windows-specific API | FAQ | no direct | MEDIUM |
| Linux target: ELF, Unix IPC, /proc | FAQ + code | YES | HIGH |
| OS/2 target: EMX runtime | FAQ | no direct | LOW |
| BeOS target: BeOS-specific | FAQ | no direct | LOW |
| DOS/GO32V2 target: DPMI, cwsdpmi, emu387 | FAQ | no direct | LOW |
| Cross-compilation notes | FAQ | no direct | MEDIUM |
| GDB debugging Pascal programs (type representation issues) | FAQ | no direct | MEDIUM |

## PRIORITY SUMMARY

### CRITICAL for fine-tune:
1. **JSON** (fpjson, jsonparser) — used in 40+ fleet files, core IRC protocol
2. **Sockets/Unix IPC** — every daemon uses this
3. **BaseUnix/Unix** — system-level operations on every sensor
4. **CEF4Delphi lifecycle & events** — dual-citizen browser project
5. **Classes (TStringList, TStream, TThread, TList)** — foundation of every app

### HIGH priority:
6. SysUtils (formatting, files, exceptions)
7. Math, DateUtils, StrUtils
8. Process execution (TProcess)
9. DynLibs (dynamic loading — crypto_seal pattern)
10. CTypes (FFI with C libraries like libpcap, OpenSSL)
11. JSON serialization patterns (TJSONObject ↔ Pascal record)
12. SQLite3 bindings (chronos_db, hermes_memory_db)
13. Daemon architecture (main loop, socket server, JSON IPC)
14. ELF binary parsing (ELF32/64 headers, sections, symbols)
15. Raw sockets + packet crafting (IP/TCP/UDP checksums)
16. Process memory manipulation (/proc/<pid>/mem + ptrace)
17. AES-256-GCM encryption (OpenSSL EVP dynamic bindings)
18. SHA1/MD5/Base64 hashing & encoding
19. ROP gadget analysis from ELF binaries
20. Plugin system design (dynamic load, RPC, JSON IPC)

### MEDIUM — good depth but less critical:
21. i18n/collation/Unicode handling
22. Generics (TFPGList, TFPGMap)
23. TypInfo/RTTI (runtime class introspection)
24. Contnrs (TObjectList, THashedStringList)
25. Variants, variant arrays
26. Resources (version, string table, bitmap)
27. COFF/Mach-O binary formats
28. AVL_Tree, matrix math, MMX/SIMD
29. Data access (TDataSet, SQLdb)
30. Cryptography (Blowfish, IDEA)
31. DaemonApp framework
32. EventLog, IniFiles

---

## HOW THIS MAPS TO OUR FLEET CODE

| Fleet Domain | # Files | Key Subjects |
|---|---|---|
| Sensors (8) | 8 .pas | Unix/BaseUnix, Sockets, fpjson, daemon pattern |
| Red Team (6+3) | 9 .pas | Sockets, raw sockets, process, ELF, AES, ptrace |
| Plugins (22) | 22 .pas | JSON IPC, plugin RPC, classes, sockets, syncobjs |
| Browser (4) | 4 .pas | CEF4Delphi, Lazarus Forms, JSON, Sockets |
| Common (3) | 3 .pas | daemon_base, json_protocol, pascal_arsenal |
| Memory/DB (3) | 3 .pas | sqlite3dyn, fpjson, classes |
| Networking (5) | 5 .pas | libpcap, raw sockets, TUN/TAP, packet dissectors |
| Binary (4) | 4 .pas | ELF parsing, ROP, assembly |
| Totals | 147 | ~25 unique library units + ~20 custom patterns |

---

## NOTE ON DATA FORMAT

All scraped documentation is raw HTML in `/home/craig/projects/freepascal-docs/`
(16,834 files, 107 MB). Each unit topic has its own subdirectory with doc
pages per type/procedure/function/property. Extraction to training format
(JSONL or similar) would require HTML→text conversion (e.g., pandoc or
html2text). The wiki tutorials are also raw HTML at
`wiki/wiki.freepascal.org/`. The tutorial-extracted/ directory has some
already-converted JSON/text extracts.
