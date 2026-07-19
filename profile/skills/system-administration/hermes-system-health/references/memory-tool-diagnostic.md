# Memory Tool Diagnostic Reference

## Symptom: memory tool returns "Memory is not available"

The `memory` tool (the tool available to the agent during conversation) may return:
```
Memory is not available. It may be disabled in config or this environment.
```

### Root Cause

The handler at `tools/memory_tool.py:977` checks `if store is None`. The `store` parameter (a `MemoryStore` instance) is injected into the tool's `**kw` kwargs by the conversation loop agent (`run_agent.py`). 

Sessions launched with `--ignore-user-config` skip this injection. The tool `check_fn` (line 1037) always returns True — the tool schema IS available, but the runtime handler fails because no MemoryStore was provided.

### Not a Broken Memory System

The memory infrastructure is fully intact even when the tool fails:

| Check | What to look for |
|---|---|
| `hermes memory status` | "Built-in: always active" |
| `ls ~/.hermes/profiles/<profile>/memory/store/` | VSA vectors file present |
| `ls ~/.hermes/profiles/<profile>/memory/sms/` | SMS plugin installed |

### Fix

Start a normal Hermes session (without `--ignore-user-config`):
```bash
hermes
```
Or if in a stripped session, `/reset` won't help (the flags are process-level). Exit and restart without the stripped flags.

## Module Location

The memory system is NOT at `agent.memory`. The tool lives at:
- `/opt/hermes-agent/tools/memory_tool.py` (tool handler + MemoryStore class)
- `/opt/hermes-agent/agent/` (no memory module here in current layout)

## Memory Plugins Available

These are installed as plugins but use built-in by default:
- byterover, hindsight, holographic, honcho, mem0, openviking, retaindb, supermemory

Enable via `hermes config set memory.provider <name>` then add respective API key.
