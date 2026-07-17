# Unified Field — Complete Integration Reference

## Architecture Diagram

```
                         ┌──────────────────────────────────┐
                         │         SOUL.md                  │
                         │  (Default Operational Mode)      │
                         └──────────────┬───────────────────┘
                                        │
                         ┌──────────────▼───────────────────┐
                         │     UNIFIED FIELD (Singleton)     │
                         │   ~/..../work/unified_field.py    │
                         │   ~/.local/bin/uf (CLI)           │
                         └──────┬──────┬──────┬──────┬──────┘
                                │      │      │      │
              ┌─────────────────┘      │      │      └──────────────┐
              │                        │      │                     │
     ┌────────▼────────┐    ┌──────────▼──┐ ┌─▼──────────────┐  ┌──▼──────────┐
     │   EMERGE        │    │    SMS       │ │    SVA/GATE    │  │   EXEC      │
     │ Persistent Store │    │ Tri-Brid    │ │ Hyperspace Vec │  │ Silent Batch│
     │ (JSON ZODB)     │    │ Mem+VSA+Res │ │ + GatedStore   │  │ Zero LLM    │
     └─────────────────┘    └─────────────┘ └────────────────┘  └─────────────┘
                                        │
                              ┌─────────▼─────────┐
                              │  STATE MACHINE     │
                              │  (LangGraph Copy)  │
                              │  ~/..../work/      │
                              │  state_machine.py  │
                              └───────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
              ┌─────▼─────┐    ┌────────▼───────┐   ┌──────▼──────┐
              │ Executor  │    │ ParallelExec   │   │  Built-in   │
              │ Node      │    │ utorNode       │   │  Nodes      │
              │ (offload) │    │ (concurrent)   │   │  (inline)   │
              └───────────┘    └────────────────┘   └─────────────┘
```

## File Map

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `~/..../work/unified_field.py` | Central singleton | `UnifiedField`, `EmergeClient`, `SMSClient`, `SVAClient`, `GateClient`, `ExecutorClient` |
| `~/..../work/state_machine.py` | LangGraph copy | `Workflow`, `Node`, `Edge`, `ConditionalEdge`, `WorkflowState`, `ExecutorNode`, `ParallelExecutorNode` |
| `~/..../work/uf_integrator.py` | CLI interface | `cmd_status()`, `cmd_checkpoint()`, `cmd_recall()`, `cmd_wf()`, `cmd_sync()`, `cmd_memorize()`, `cmd_offload()` |
| `~/.local/bin/uf` | CLI symlink | → `uf_integrator.py` |
| `~/.hermes/plugins/gated_context/` | Gated Context plugin | `peek_ptr`, `gate_status`, `gate_injectable`, `recall` (context_engine toolset) |
| `~/projects/aethelgard/fleet/modules/` | Fleet core modules | `context_gate.py`, `snap_n_drop.py`, `dynamic_tool_filter.py`, `fleet_integration.py` |
| `~/.NOTTHEONETOEDIT/.../SOUL.md` | Identity + Architecture | §Unified Field Architecture, §Gated Context, §Agent Operating Instructions |
| `~/.NOTTHEONETOEDIT/.../work/warp_bridge.py` | Warp ↔ SMS/SVA bridge | `WarpMemoryStore`, `WarpSessionStore` |

## Data Flow: Memorize → Store → Recall

```
User message
    │
    ├──→ SMS.tri_brid(message)       [temporal + associative memory]
    │       │
    │       ├──→ VSA vector encoded
    │       ├──→ Reservoir state updated
    │       └──→ ZODB auto-persisted (every 10 calls)
    │
    ├──→ SVA.store(key, message)     [hyperspace index]
    │       │
    │       └──→ 1024-D vector → /tmp/sva/vectors/*.vec
    │
    ├──→ emerge.store(key, data)     [persistent object store]
    │       │
    │       └──→ ~/.emerge/data/.../*.json (or ZODB via server)
    │
    └──→ checkpoint()                [full state capture]
            │
            └──→ ~/..../work/checkpoints/ckpt_*.json
```

## Data Flow: Recall (bidirectional)

```
Query
    │
    ├──→ SVA.recall(query, k)        [cosine similarity search]
    │       │
    │       └──→ top-k results with similarity scores
    │
    └──→ SMS.memorize("[SVA Recall: ...]")  [feedback loop]
            │
            ├──→ Reservoir learns the recall pattern
            └──→ VSA assimilates the memory
```

## Data Flow: Executor Offloading (LangGraph pattern)

```
Workflow Node
    │
    ├──→ ExecutorNode.execute()
    │       │
    │       ├──→ uf.execute_workflow_step(step_name, tools)
    │       │       │
    │       │       ├──→ queue batch to ~/.hermes/executor/in/
    │       │       ├──→ checkpoint("pre_{step}")
    │       │       ├──→ hermes-executor.py process (sync)
    │       │       └──→ checkpoint("post_{step}")
    │       │
    │       └──→ results injected back into WorkflowState
    │
    └──→ ConditionalEdge routes based on results
```

## All Bridges Matrix

| From | To | Function | File |
|------|----|----------|------|
| SMS | SVA | `memorize_and_store()` → VSA vector | unified_field.py |
| SVA | SMS | `recall_and_memorize()` → temporal feedback | unified_field.py |
| SMS | Emerge | `uf sync` → extract ZODB → store as EmergeFile | uf_integrator.py |
| GATE | SVA | gate pointers reference SVA vector keys | context_gate.py |
| GATE | EXEC | executor batches gate their outputs via ExecutorNode | state_machine.py |
| EXEC | State | ExecutorNode + ParallelExecutorNode | state_machine.py |
| WARP | SMS | WarpMemoryStore.create_memory() → SMS.memorize() | warp_bridge.py |
| WARP | Emerge | WarpMemoryStore stores sessions on emerge | warp_bridge.py |
| ALL | Checkpoints | Every state machine step auto-checkpoints | state_machine.py |
| ALL | Fleet | Systems register at /fleet/daemons/ | unified_field.py |
| ALL | CLI | `uf` command exposes every bridge | uf_integrator.py |

## CLI Command Reference

| Command | Example | Description |
|---------|---------|-------------|
| `uf status` | `uf status` | Full system health report |
| `uf checkpoint <name>` | `uf checkpoint pre_goal` | Save system state snapshot |
| `uf recall <query>` | `uf recall sovereign identity` | SVA hyperspace search |
| `uf sync` | `uf sync` | SMS vectors → Emerge object store |
| `uf store <path> <key>` | `echo '{"a":1}' \| uf store /data test` | Store JSON to emerge |
| `uf execute <id>` | `echo '{"tools":[...]}' \| uf execute b1` | Queue executor batch |
| `uf memorize <msg>` | `uf memorize "identity verified"` | Bidirectional SMS + SVA |
| `uf recall-feedback <q>` | `uf recall-feedback "memory patterns"` | SVA recall → SMS feedback |
| `uf offload <step>` | `echo '{"tools":[...]}' \| uf offload health` | Sync executor offload |
| `uf wf list` | `uf wf list` | List all workflows |
| `uf wf run <name>` | `uf wf run 3tier` | Execute state machine workflow |
| `uf warp` | `uf warp` | Warp terminal build status |
