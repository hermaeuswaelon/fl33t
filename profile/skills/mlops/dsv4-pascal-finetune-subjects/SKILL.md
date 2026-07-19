---
name: dsv4-pascal-finetune-subjects
description: Subject analysis and priority mapping for a DeepSeek V4 Pascal fine-tune, sourced from the scraped Free Pascal documentation and Aethelgard fleet Pascal codebase.
---

# DSV4 Pascal Fine-Tune Subjects

## Data Sources
- **freepascal-docs/**: `/home/craig/projects/freepascal-docs/` — 16,834 HTML files (107 MB) covering 166+ RTL and FCL units
- **Wiki tutorials**: `wiki/wiki.freepascal.org/` — Basic Pascal Tutorial, OOP Pascal Tutorial, Lazarus Tutorial
- **Converted extracts**: `tutorial-extracted/` — JSON/txt files already converted
- **Fleet Pascal code**: `/home/craig/projects/aethelgard/fleet/pascal/` — 147 .pas/.lpr files
- **pascal_lens.py**: `pascal_lens.py` — Pascal-to-AI-readable converter script
- **Full analysis**: `/home/craig/Desktop/dsv4-pascal-finetune-subjects.md`

## Subject Priority

### CRITICAL
1. fpjson/jsonparser (used in 40+ fleet files, core IPC protocol)
2. Sockets (TSocket, sockaddr_in, TCP/UDP/raw)
3. BaseUnix/Unix/Unixtype (fpOpen, fpMmap, fpStat, signals, pipes)
4. Classes (TStringList, TStream, TFileStream, TThread, TList, TComponent)
5. CEF4Delphi (GlobalCEFApp, TChromium, Lazarus Forms, IPC, OSR)
6. SysUtils (Format, IntToStr, FileExists, exceptions, date/time)
7. Process (TProcess, RunCommand)
8. DynLibs (LoadLibrary — especially OpenSSL EVP dynamic binding pattern)
9. CTypes (FFI with libpcap, OpenSSL, etc.)
10. DateUtils/StrUtils
11. SQLite3 (sqlite3dyn)
12. Daemon architecture (socket server + JSON IPC + main loop)

### HIGH (security/systems programming — unique fleet value)
- ELF binary parsing (headers, sections, symbols, .got, .plt)
- ROP gadget finding from ELF binaries
- Raw sockets + packet crafting (IP_HDRINCL, checksums)
- TUN/TAP bridge (/dev/net/tun ioctl)
- libpcap capture + BPF + TCP/IP/HTTP/DNS dissection
- Process memory manipulation (/proc/&lt;pid&gt;/mem + ptrace)
- AES-256-GCM (OpenSSL EVP dynamic load — crypto_seal pattern)
- SHA1/MD5/Base64 hashing & encoding
- OS fingerprinting (TCP/IP stack heuristics)
- Port scanning (SYN/TCP connect/UDP)
- Plugin system architecture (dynamic load + RPC + JSON IPC)
- Process guard (ptrace monitoring)
- Machine code execution (mmap RWX + copy + execute)
- System metrics (/proc/stat, /proc/meminfo, /proc/loadavg)
- File monitoring (inotify)

### MEDIUM
- TypInfo/RTTI (GetPropValue, GetEnumName)
- Generics (TFPGList, TFPGMap, specialize)
- Variants/VarArrayCreate
- Contnrs (TObjectList)
- IniFiles, EventLog
- Resources (version, bitmap, string table)
- COFF/Mach-O binary format readers
- AVL_Tree, matrix math, MMX/SIMD
- Data access (TDataSet, SQLdb)
- i18n/collation/Unicode
- CRT/Graph legacy
- GetOpts
- Cross-compilation notes

## Fleet Code Domain Map
- Core Sensors (8 files): Unix, Sockets, fpjson, daemon pattern
- Red Team (9 files): Sockets, raw sockets, ELF, AES, ptrace
- Plugins (22 files): JSON IPC, plugin RPC, Classes, sockets, syncobjs
- Browser (4 files): CEF4Delphi, Lazarus Forms, JSON, Sockets
- Common (3 files): daemon_base, json_protocol, pascal_arsenal
- Memory/DB (3 files): sqlite3dyn, fpjson
- Networking (5 files): libpcap, raw sockets, TUN/TAP, dissection
- Binary (4 files): ELF parsing, ROP, assembly

## Data Extraction Note
All docs are raw HTML. Training data prep needs HTML→text conversion (pandoc or html2text). The tutorial-extracted/ dir has some JSON/text already done. Fleet .pas files are ready-to-use source code examples.

## Key Memory Reference
Save this skill to recall the subject analysis for any future DSV4 Pascal fine-tune work. The file `/home/craig/Desktop/dsv4-pascal-finetune-subjects.md` has the full tiered table.