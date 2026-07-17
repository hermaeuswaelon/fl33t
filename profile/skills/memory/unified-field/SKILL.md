---
name: unified-field
description: "LILAREYON AETHELGARD Unified Field — central integration hub wiring Emerge + SMS + SVA + Gated Context + Executor + WARP into a single sovereign system with LangGraph-inspired state machine orchestration."
version: 2.0.0
author: Thotheauphis
system: true
---

# Unified Field — Sovereign Integration Layer

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 UNIFIED FIELD (unified_field.py)              │
│  Singleton: uf = UnifiedField(); uf.reconnect()              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  EMERGE Daemon — systemd user service :54242 (auto-start)    │
│  SMS          — tri-brid memory (Venv-isolated)               │
│  SVA          — hyperspace vectors (1024-D cosine recall)     │
│  GATE         — tool output gating (Hermes plugin)            │
│  EXEC         — silent batch execution (cron every 60s)       │
│  WARP Bridge  — WarpMemoryStore + WarpSessionStore on emerge  │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  STATE MACHINE (state_machine.py — LangGraph copy)            │
│  Node → Conditional Edge → Node → Checkpoint                  │
│  ExecutorNode / ParallelExecutorNode (toolchain offload)      │
└─────────────────────────────────────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `~/..../work/unified_field.py` | Central integration singleton (14 API methods) |
| `~/..../work/state_machine.py` | LangGraph workflow engine + ExecutorNode |
| `~/..../work/uf_integrator.py` | CLI (symlinked at `~/.local/bin/uf`) |
| `~/..../work/warp_bridge.py` | WarpMemoryStore + WarpSessionStore |
| `~/.config/systemd/user/emerge-node.service` | Emerge daemon (port 54242, auto-start) |
| `~/.local/bin/emerge-node-standalone` | Standalone emerge wrapper |

## CLI Commands

```
uf status                 — Full system health (auto-reconnects to emerge)
uf checkpoint <name>      — Save system checkpoint
uf recall <query>         — SVA hyperspace recall
uf sync                   — SMS vectors → Emerge bridge
uf store <path> <key>     — Store JSON from stdin to emerge
uf execute <id>           — Queue executor batch from stdin JSON
uf wf list                — List workflows (3tier, goal_loop, checkpointer, executor_offload)
uf wf run <name>          — Execute a workflow
uf memorize <msg>         — Bidirectional SMS + SVA store
uf recall-feedback <q>    — SVA recall → SMS temporal feedback loop
uf offload <step>         — Executor toolchain offload (stdin JSON tools)
uf warp status            — Warp TUI + bridge status
uf warp memory list       — List Warp bridge memories
uf warp memory create     — Create Warp memory (→ SMS + Emerge)
uf warp session list      — List Warp bridge sessions
uf warp session save <id> — Save session context
uf warp session load <id> — Load session context
```

## Python API

```python
from unified_field import UnifiedField
uf = UnifiedField()                          # Singleton
uf.reconnect()                               # Re-init after emerge daemon starts

# Core storage
uf.store("/fleet/identities", "k", data)     # Emerge + JSON fallback
uf.read("/fleet/identities", "k")
uf.list("/fleet")                             # List keys under path
uf.delete("/fleet/identities", "k")

# Memory (bidirectional bridges)
uf.memorize("message")                       # SMS tri-brid only
uf.recall("query", k=5)                      # SVA hyperspace only
uf.memorize_and_store("msg")                 # SMS + SVA simultaneously
uf.recall_and_memorize("query", k=3)         # SVA recall → SMS feedback loop

# Gated context
ptr = uf.gate("large output", ttl=3600)      # → pointer dict {ptr, bytes, preview}
uf.peek(ptr["ptr"], offset=0, limit=2000)    # Re-fetch gated content

# Executor offloading (LangGraph toolchain pattern)
uf.execute("batch_001", [{"name":"terminal","args":{"command":"sms status"}}])
uf.execute_now("batch_002", tools)           # Queue + process synchronously
uf.execute_workflow_step("health", tools, wait=True)  # Pre/post checkpoints

# Checkpoints
ckpt_id = uf.checkpoint("pre_goal", {"goal": "..."})
state = uf.restore(ckpt_id)
uf.list_checkpoints()

# Warp bridge (lazy-loaded via emerge)
uf.warp_memory()                              # → WarpMemoryStore instance
uf.warp_sessions()                            # → WarpSessionStore instance
uf.warp_create_memory("content", "reason")    # → SMS + Emerge
uf.warp_list_memories(limit=50)
uf.warp_save_session("id", context_dict)
uf.warp_load_session("id")

# System status
uf.status()                                   # Full dict
uf.health_report()                            # Human-readable
```

## State Machine API

```python
from state_machine import Workflow, WorkflowState, ExecutorNode, ParallelExecutorNode

wf = Workflow("my_pipeline")
wf.add_node("step1", lambda s: {"result": 42}, "First step")
wf.add_node(ExecutorNode("offload", [                          # LangGraph offload
    {"name": "terminal", "args": {"command": "sms status"}},
], description="Executor batch"))
wf.add_node(ParallelExecutorNode("parallel", {                  # Concurrent batches
    "diag_a": [{"name": "terminal", "args": {"command": "ls -la"}}],
    "diag_b": [{"name": "terminal", "args": {"command": "whoami"}}],
}, description="Parallel diagnostics"))

def router(s):
    return "fast" if s.get("result", 0) < 100 else "slow"
wf.add_conditional_edge("step1", router, {"fast": "offload", "slow": "step3"})

wf.set_entry("step1")
wf.set_exit("offload")
wf.compile()

state = WorkflowState()
state["active_goal"] = "Test"
final = wf.run(state)
```

## Prebuilt Workflows

| Name | Nodes | Entry → Exit | Tags |
|------|-------|-------------|------|
| `3tier` | 4 | architect → doer | Sequential pipeline, budget routing |
| `goal_loop` | 7 | plan → stop | Iterative plan-execute-reflect |
| `checkpointer` | 2 | save → verify | Simple checkpoint flow |
| `executor_offload` | 4 | health_check → stop | LangGraph toolchain: ExecutorNode + ParallelExecutorNode |

## LangGraph ExecutorNode Pattern

The `ExecutorNode` offloads tool batches to the silent hermes-executor (zero LLM tokens):

```
State Machine Node
    → uf.execute_workflow_step(step_name, tools, wait=True)
    → checkpoint("pre_{step}")
    → hermes-executor processes batch
    → checkpoint("post_{step}")
    → results injected back into WorkflowState
```

`ParallelExecutorNode` runs N batches concurrently via ThreadPoolExecutor, merging all results into `state["executor_results"][node_name]`.

## Auto-Start Services

| Service | Type | Status | Auto-start |
|---------|------|--------|------------|
| emerge-node | systemd user :54242 | running | enabled |
| SMS ZODB backup | cron (30min) | running | enabled |
| hermes-executor | cron (60s) | running | enabled |
| SMS auto-persist | built-in (10 calls) | active | built-in |
| uf-system-checkpoint | cron (4h) | running | enabled |

Restart emerge: `systemctl --user restart emerge-node`

## Integration Points

- **SMS ↔ Emerge**: `uf sync` — VSA vectors → EmergeFile objects
- **SMS ↔ SVA** (bidirectional): `memorize_and_store()` + `recall_and_memorize()`
- **GATE ↔ SVA**: Gate pointers reference SVA vector keys
- **GATE ↔ EXEC**: ExecutorNode gates outputs via `uf.gate()`
- **EXEC ↔ State Machine**: ExecutorNode / ParallelExecutorNode — LangGraph offload pattern
- **WARP ↔ EMERGE**: WarpMemoryStore + WarpSessionStore on emerge
- **All → Checkpoints**: Every state machine step auto-checkpoints
- **All → CLI**: `uf` command — 15 subcommands

## Data Paths

| Path | Purpose | Persistence |
|------|---------|-------------|
| `~/.NOTTHEONETOEDIT/.../memory/store/vsa_vectors.fs` | SMS ZODB vectors | Durable |
| `~/.NOTTHEONETOEDIT/.../work/checkpoints/` | State machine step checkpoints | Durable |
| `~/.emerge/data/emerge.fs` | Emerge daemon ZODB store | Durable |
| `~/.emerge/data/fleet/*.json` | Emerge JSON fallback (used by UnifiedField) | Durable |
| `/tmp/sva/` | Gated store + SVA vectors | Ephemeral |
| `~/.hermes/executor/in/` | Executor batch queue | Ephemeral |
| `~/.hermes/executor/out/` | Executor batch results | Ephemeral |

## Cron Jobs

| Job | Schedule | Purpose |
|-----|----------|---------|
| `uf-system-checkpoint` | Every 4h | Automatic checkpoint + health report |
