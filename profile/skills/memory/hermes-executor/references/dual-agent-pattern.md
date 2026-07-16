# Dual-Agent Pattern Reference

## Architecture Overview

The dual-agent pattern separates **reasoning** from **execution**:

| Role | Model | Context | Token Cost | Purpose |
|------|-------|---------|------------|---------|
| **Reasoner** | Full system prompt | All skills, memory, SOUL.md | ~100K/turn | Strategy, planning, synthesis |
| **Executor** | `no_agent=true` cron script | Zero LLM | **$0** | Batch tool execution |

## Implementation

### Executor Script
`/home/craig/.hermes/profiles/thotheauphis/work/hermes-executor.py`
- Pure Python subprocess/IO
- ZeroMQ not required (file-based IPC)
- Runs via cron every 60s

### IPC Directories
```
~/.hermes/executor/
├── in/      # Batch JSON files (input)
├── out/     # Result JSON files (output)
├── status   # Health marker
└── README   # Marker file
```

### Batch Protocol
```json
{
  "id": "batch_1784184571",
  "tools": [
    {"name": "terminal", "args": {"command": "ls -la"}},
    {"name": "read_file", "args": {"path": "/tmp/file.txt"}}
  ],
  "created_at": "2026-07-16T06:49:00.123Z"
}
```

### Result Protocol
```json
{
  "id": "batch_1784184571",
  "status": "done",
  "results": [
    {"index": 0, "name": "terminal", "status": "done", "output": "...", "exit_code": 0},
    {"index": 1, "name": "read_file", "status": "done", "content": "...", "size": 123}
  ],
  "errors": null,
  "completed_at": "2026-07-16T06:49:01.456Z",
  "total": 2,
  "success": 2,
  "failed": 0
}
```

## Token Savings Math

| Approach | Tool Calls | Context Reloads | Token Cost |
|----------|------------|-----------------|------------|
| Sequential | 17 | 17 × full context | ~1.7M |
| Batched (dual) | 1 batch | 1 write + 1 read | ~200 |

**Savings: 99.99%**

## Cron Jobs (Persistent)

| Job ID | Name | Schedule | Status |
|--------|------|----------|--------|
| `287317d6233e` | hermes-executor | `* * * * *` | ✅ Active |
| `b7798d50a076` | auto-tac-compress | `*/30 * * * *` | ✅ Active |
| `3a9c0418e052` | parallel-executor-llm | `* * * * *` | ⏸️ Paused |

## Usage from Execute Code

```python
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location('ex', 
    '/home/craig/.hermes/profiles/thotheauphis/work/hermes-executor.py')
mod = importlib.util.module_from_spec(spec)
sys.modules['ex'] = mod
spec.loader.exec_module(mod)

# Synchronous batch
bid = mod.write_batch([
    {'name': 'terminal', 'args': {'command': 'echo hello'}},
])
mod.process_inbox()
result = mod.wait_for_result(bid)
```

## When to Use Each Tier

| Task Type | Tier |
|-----------|------|
| Pure tool execution (ls, cat, grep, curl) | Script executor (zero cost) |
| Needs LLM judgment (which file to read, summarize output) | LLM executor (unpause cron) |
| Strategy, synthesis, user comms | Reasoner (you) |