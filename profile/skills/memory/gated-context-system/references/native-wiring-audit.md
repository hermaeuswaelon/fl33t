# Native Wiring Audit Methodology

How to determine if a subsystem is wired as a **native Hermes default** (core code / config / plugin) vs a **skill that needs manual invocation** vs a **standalone project**.

## 4-Path Check

For any system, check these four paths:

### 1. Core Code Wiring
Look in `/opt/hermes-agent/` — is the system referenced in:
- `tools/*.py` (tool implementations)
- `tools/registry.py` (tool registration)
- `toolsets.py` (toolset membership)
- `agent/` (prompt builders, memory integration)

Example: SMS (`thotheauphis-sms-memory`) is wired at line 1153 of `tools/memory_tool.py` via `_SMS_ACTIVE` flag — this is **core-level**.

### 2. Hermes Plugin System
Check `~/.hermes/plugins/<name>/` for:
- `plugin.yaml` (declares `provides_tools`, `hooks`, `kind`)
- `__init__.py` (tool registration code)
- The toolset name in plugin.yaml must appear in `platform_toolsets.cli` in `~/.hermes/config.yaml`

Example: `gated-context` plugin at `~/.hermes/plugins/gated_context/` registers 4 tools into `context_engine` toolset, which IS in `platform_toolsets.cli`.

### 3. Config Integration
Check `config.yaml` (main + profile):
- `skills.default` — skills auto-loaded in every session (no `/skill` needed)
- `platform_toolsets.cli` — toolset membership (tools appear after `/reset`)
- `skills.disabled` — explicitly disabled skills

Example: Both `thotheauphis-sms-memory` and `gated-context-system` are in `skills.default`.

### 4. Running Processes
Check `ps aux | grep <system>` for active daemons.
Check `ss -tlnp` for listening ports.

Example: Emerge has `emerge-node-standalone 54242` running but no Hermes config references it.

## Result Categories

| Category | Definition | Example |
|----------|------------|---------|
| **✅ Native Default** | Wired in core code OR plugin + toolset; no manual invocation needed | SMS, VSA, Context Gating, Smart Terminal |
| **⚡ Skill-Only** | Loaded as skill but not in plugins/toolset/core | Needs `/skill` or `skills.default` |
| **❌ Standalone** | Not connected to Hermes at all | Emerge, Warp |
| **⚡ Conceptual** | Described somewhere but not actually deployed | MemGPT in SMS skill |
