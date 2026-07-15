# Slash Command Registration Architecture (Updated July 2026)

## Overview

Every entity in Hermes that wants a `/command` registers into the
**unified SlashRegistry**. There is one single source of truth, not four
parallel paths.

## The Six Registration Paths (all unified)

| Source | Method | Example | Load |
|--------|--------|---------|------|
| Built-in | `COMMAND_REGISTRY` static list | `/help`, `/model` | Always |
| Skill | `scan_skill_commands()` → auto-register | `/ctx-curation` | On invoke |
| Plugin | `register_command()` | `/my-plugin-cmd` | On invoke |
| Bundle | `bundles.yaml` → auto-register | `/my-bundle` | On invoke |
| **Toolset** | `bootstrap()` → auto-register per TOOLSET entry | `/nmap`, `/spotify` | **On-demand** |
| **MCP** | `bootstrap()` → auto-register per mcp_servers config | `/mcp-filesystem` | **On-demand** |

## Key Files

| File | Purpose |
|------|---------|
| `hermes_cli/slash_registry.py` | The `SlashRegistry` singleton -- single source of truth |
| `tools/on_demand_tools.py` | Runtime handler: injects tools into agent on /command |
| `plugins/on_demand_slash.py` | Plugin that wires registry into Hermes lifecycle |
| `unified_slash_bootstrap.py` | One-call `bootstrap()` for startup |

## Patches to Core

| File | Change |
|------|--------|
| `hermes_cli/commands.py` | Add `source`, `load_on_invoke`, `handler` to CommandDef; add `COMMAND_REGISTRY_EXTENSIONS`; add `rebuild_lookups()` |
| `tui_gateway/server.py` | Raise autocomplete cap 30 to 200; remove cap when filtering |
| `agent/skill_commands.py` | Register skills into unified registry after scan |
| `cli.py` (help handler) | /help auto-includes all categories from rebuild_lookups() |

## The 30-Item Cap Fix

The TUI's complete.slash handler now:
- Caps at 200 for bare / (was 30)
- Returns ALL matches when filter text is typed (e.g. /ct returns /ctx-curation immediately)
- Shows "N more..." hint when the cap truncates results

## On-Demand Loading Sequence

User types /nmap
  1. Complete.slash shows /nmap with "Load nmap + masscan tools" meta
  2. User hits Enter
  3. Plugin handler intercepts (register_command handler)
  4. enable_toolset_for_session("nmap", "toolset", agent, "session-xyz")
  5. resolve_toolset("nmap") gives ["netcat", "masscan", "nmap"]
  6. agent.enabled_tool_names += ["netcat", "masscan", "nmap"]
  7. agent.tool_schemas += registry schemas for those tools
  8. Returns confirmation: /nmap activated (3 tools loaded)
  9. NEXT TURN: LLM sees nmap tools for the first time

## Implementation Files (created July 2026)

The full 10-file implementation lives at:
~/.NOTTHEONETOEDIT/profiles/thotheauphis/work/

```
File                                Lines  Purpose
slash_registry.py                    311   Unified SlashRegistry singleton
on_demand_tools.py                   252   Runtime tool activation engine
unified_slash_bootstrap.py           236   One-call bootstrap() for startup
patches_commands_py.py               305   6 exact patches for commands.py
toolsets_on_demand.py                135   Toolset command auto-registration
mcp_on_demand.py                      95   MCP server command auto-registration
on_demand_slash_plugin.py            341   Plugin wiring lifecycle hooks
skill_registry_integration.py         95   skill_commands.py integration code
tui_autocomplete_fix.py              175   TUI cap fix + /help patch
ARCHITECTURE.md                      220   Installation guide and overview
Total: 10 files, ~2,165 lines
```

### Install Order

1. Copy slash_registry.py to hermes_cli/slash_registry.py (new file)
2. Copy on_demand_tools.py to tools/on_demand_tools.py (new file)
3. Apply patches from patches_commands_py.py to hermes_cli/commands.py
4. Apply the complete.slash handler from tui_autocomplete_fix.py to tui_gateway/server.py
5. Add _register_skills_in_slash_registry() into agent/skill_commands.py scan_skill_commands() and reload_skills()
6. Add bootstrap() call to cli.py or run_agent.py startup
7. (Optional) Install on_demand_slash_plugin.py as a plugin

### Test After Install

- Type / in the TUI -- should see up to 200 completions
- Type /nmap or /spotify or /vision -- activates that toolset
- Type /toolsets -- lists all available toolset commands
- Type /active-tools -- shows what's loaded
- Type /help -- now shows Skills, Toolsets, MCP Servers categories