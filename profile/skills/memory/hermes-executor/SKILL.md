---
name: hermes-executor
description: "Dual-agent executor: batch tool calls to a silent parallel process. Zero LLM overhead. Write batch → execute → read results."
version: 1.0.0
system: true
---

# Hermes Executor — Dual-Agent Protocol

## Architecture

```
Reasoner (Me)                      Executor (Parallel cron)
─────────────────                  ────────────────────────
Full system prompt                 NO system prompt
High reasoning budget              Zero LLM tokens
Low output budget                  Pure subprocess/IO
Sees the board                     Silent, fast, forgets
```

The executor runs as a cron job every 60 seconds (`no_agent=true`). Zero LLM cost. It reads batch files from `~/.hermes/executor/in/`, executes tool calls, writes results to `~/.hermes/executor/out/`.

## Usage

### Quick synchronous batch (inline, no cron latency)

```python
# From terminal tool:
python3 /home/craig/.hermes/profiles/thotheauphis/work/hermes-executor.py batch \
  --tool terminal command "ls -la /tmp" \
  --tool read_file path "/tmp/somefile.txt"
```

### Write batch + process manually

```bash
# Write a batch
echo '{
  "id": "my_batch",
  "tools": [
    {"name": "terminal", "args": {"command": "ls -la"}},
    {"name": "web_search", "args": {"query": "latest spades rules"}}
  ]
}' > ~/.hermes/executor/in/my_batch.json

# Process immediately
python3 /home/craig/.hermes/profiles/thotheauphis/work/hermes-executor.py process

# Read result
cat ~/.hermes/executor/out/my_batch.json
```

### Async (queue and forget, cron picks up within 60s)

```bash
# Just write the batch file, cron handles the rest
cp batch.json ~/.hermes/executor/in/
```

### Python API (from execute_code tool)

```python
import importlib.util, json
spec = importlib.util.spec_from_file_location('executor', 
    '/home/craig/.hermes/profiles/thotheauphis/work/hermes-executor.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Queue a batch
bid = mod.write_batch([
    {'name': 'terminal', 'args': {'command': 'ls -la'}},
    {'name': 'read_file', 'args': {'path': '/tmp/data.txt'}},
])

# Wait for cron to pick it up (or call process_inbox directly)
mod.process_inbox()  # synchronous
result = mod.wait_for_result(bid)
print(json.dumps(result, indent=2))
```

## Available Tools in Executor

| Tool | Description |
|------|-------------|
| `terminal` | Shell commands (command, timeout, workdir) |
| `read_file` | Read text files |
| `write_file` | Write text files |
| `search_files` | Glob pattern search |
| `web_search` | DuckDuckGo web search |
| `web_extract` | Extract text from URL |

## Cron Jobs

| Job | Schedule | Purpose |
|-----|----------|---------|
| `hermes-executor` (id: `287317d6233e`) | Every minute | Script executor — ZERO tokens. Reads inbox, runs batches. |
| `auto-tac-compress` (id: `b7798d50a076`) | Every 30 min | Chinese context compression |
| `parallel-executor-llm` (id: `3a9c0418e052`) | Every minute | **PAUSED.** DeepSeek-chat via OpenRouter. Unpause for LLM-level batch decisions. |
| `sms-zodb-backup` (id: `661330d44f6e`) | Every 30 min | ZODB checkpoint + prune >7d (`no_agent`) |
| `sms-health-check` (id: `c353228c832d`) | Every 2h | ZODB integrity verification (`no_agent`) |
| `sms-stats-log` (id: `7d872b0f1ae4`) | Every 1h | Store size + backup count logging (`no_agent`) |

**Use case**: Offload mechanical tool batches from main context — zero token cost, pure subprocess speed.

---

## LLM-Enabled Executor Variants

### DeepSeek Executor (Reasoning + Tools)
**File**: `~/.hermes/profiles/thotheauphis/work/deepseek_executor.py`
- Model: `deepseek/deepseek-chat` via OpenRouter (~$0.0002/1K tokens)
- Reads batch with optional `llm_prompt` field, calls DeepSeek, dispatches tool calls
- 1-3s latency, ~$0.001 per batch

### DeepSeek Batch Processor (Dedicated LLM Processor)
**File**: `~/.hermes/profiles/thotheauphis/work/deepseek_batch_processor.py`
- Processes inbox batches with `llm_prompt` field
- Writes results to `.result.json`
- Cron-compatible for async LLM reasoning

### Integration Pattern

| Cron Job (Every Minute) | Mechanical Only |
|-------------------------|-----------------|
| `~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/run_executor_cron.sh` | Runs `hermes-executor.py process` |

**SMS Health/Backup via Executor**:
```json
{
  "id": "sms_health",
  "tools": [
    {"name": "terminal", "args": {"command": "/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/sms-health"}}
  ]
}
```

**Queue → Process → Read**:
```bash
# Queue
cp batch.json ~/.hermes/executor/in/

# Process (cron does this every 60s, or manual)
python3 hermes-executor.py process

# Read result
cat ~/.hermes/executor/out/batch.json
```

---

## Key Design Decisions

| Aspect | Strict Executor | DeepSeek Executor |
|--------|-----------------|-------------------|
| LLM | None | deepseek/deepseek-chat |
| Cost | Zero tokens | ~$0.0002/1K tokens |
| Latency | Sub-second | 1-3s |
| Use Case | Mechanical: backup, health, persist | Analysis, planning, synthesis |
| Prompt | None | User-provided in batch |

---

## Reference Files

- `references/setup-protocol.md` — full batch protocol, file locations, cost math
- `references/sms-executor-integration.md` — SMS persistence/health via executor batches

## Strict Tool-Only Executor (Zero-LLM)

Created `/home/craig/.hermes/profiles/thotheauphis/work/strict_executor.py` — a minimal executor with **no system prompt, no reasoning, no LLM**. Pure tool execution.

**Usage**:
```bash
# From batch file
python3 strict_executor.py /tmp/batch.json

# From stdin
echo '{"id":"b1","tools":[{"name":"terminal","args":{"command":"sms status"}}]}' | python3 strict_executor.py
```

**Batch format** (JSON):
```json
{
  "id": "batch_001",
  "tools": [
    {"name": "terminal", "args": {"command": "sms status"}},
    {"name": "read_file", "args": {"path": "/path/to/file"}},
    {"name": "write_file", "args": {"path": "/path/to/file", "content": "data"}},
    {"name": "search_files", "args": {"pattern": "*.py", "path": "/home/craig"}},
    {"name": "web_search", "args": {"query": "search term"}},
    {"name": "web_extract", "args": {"urls": ["https://example.com"]}}
  ]
}
```

**Tools implemented**: `terminal`, `read_file`, `write_file`, `search_files`, `web_search`, `web_extract` (DuckDuckGo HTML scrape, no API key).

**Output format** (JSON):
```json
{
  "id": "batch_001",
  "status": "done",
  "results": [
    {"index": 0, "name": "terminal", "status": "done", "output": "...", "exit_code": 0},
    {"index": 1, "name": "read_file", "status": "error", "error": "..."}
  ],
  "completed_at": "2026-07-16T..."
}
```

**Use case**: Offload mechanical tool batches from main context — zero token cost, pure subprocess speed.
