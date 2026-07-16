# Warp AI Agent SDK — Architecture Map

Source: `/home/craig/warp/` (AGPL-3.0, full terminal source)

## Key Crates

| Crate | Purpose | Key Files |
|-------|---------|-----------|
| `crates/ai` | Core AI: skills parser, project context, codebase index, diff validation, LLM ID, Grok sub | `src/agent/`, `src/skills/`, `src/index/`, `src/project_context/` |
| `crates/mcp` | MCP client: OAuth, SSE transport, runtime, `rmcp` integration | `src/runtime.rs`, `src/oauth.rs`, `src/sse_transport/` |
| `crates/computer_use` | Vision-based desktop control (macOS/Linux/Windows overlays) | `src/bin/use_computer.rs`, `src/overlay.rs`, platform dirs |
| `app/src/ai/agent_sdk/` | THE SDK: driver, memory store, provider model, profiles, config, MCP config, artifacts, secrets, schedule, OAuth flow | `driver.rs` (3873 lines), `memory_store.rs` (520 lines), `mcp.rs`, `provider.rs`, `profiles.rs` |
| `app/src/ai/agent/` | Agent conversation, tasks, todos, linearization | `conversation.rs`, `task.rs`, `task_store.rs`, `linearization.rs` |
| `app/src/ai/agent_management/` | Agent type selection, cloud setup, views | `agent_type_selector.rs`, `view.rs` |
| `app/src/ai/ambient_agents/` | Background ambient agents | `task.rs` |
| `crates/warp_multi_agent_client` | Multi-agent client | |

## Agent Driver (`driver.rs`, 3873 lines)

The central agent execution engine. Integrates:
- MCP server management (file-based + templatable)
- Skill parsing and resolution (`ai::skills::ParsedSkill`)
- Provider/LLM routing (`LLMId`, `LLMPreferences`)
- Agent conversation state machine
- Harness system for agent execution
- Blocklist AI history tracking
- Cloud environment support
- Computer use integration
- OAuth flow for MCP servers

## Memory Store (`memory_store.rs`, 520 lines)

Cloud-backed CRUD for agent memories:
- Stores: list, get, update, list agents per store
- Memories: list, create (content + reason + version), update (creates new version), delete, version history
- `CreateMemoryRequest`, `UpdateMemoryRequest`, `MemoryItem`, `MemoryStoreItem`, `MemoryVersionItem`

## MCP Architecture (`crates/mcp/`)
- OAuth2 authentication for MCP servers
- SSE (Server-Sent Events) transport
- Runtime management (start/stop/restart MCP servers)
- Two config sources: file-based (`FileBasedMCPManager`) and templatable (`TemplatableMCPServerManager`)

## Build & Run
```bash
cd ~/warp
./script/run-tui          # headless TUI (no GPU needed)
WITH_LOCAL_SERVER=1 ./script/run  # full GUI with local server
cargo build --release     # full production build (~15-30 min)
```
