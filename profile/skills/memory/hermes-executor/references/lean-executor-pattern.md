# Lean Executor Pattern (Session Addition)

## Three Executor Variants

| Variant | File | LLM | Cost | Latency | Use Case |
|---------|------|-----|------|---------|----------|
| **Strict** | `~/.hermes/profiles/thotheauphis/work/strict_executor.py` | None | $0 | Sub-second | Mechanical: backup, health, persist, emerge ops |
| **DeepSeek** | `~/.hermes/profiles/thotheauphis/work/deepseek_executor.py` | deepseek-chat | ~$0.0002/1K | 1-3s | Analysis, planning, synthesis |
| **Batch Processor** | `~/.hermes/profiles/thotheauphis/work/deepseek_batch_processor.py` | deepseek-chat | ~$0.001/batch | Async | Async LLM reasoning on inbox |

## Integration Pattern

```bash
# Cron (every minute) runs mechanical executor only
~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/run_executor_cron.sh
# → python3 hermes-executor.py process

# SMS health/backup via executor batch
{"id": "sms_health", "tools": [{"name": "terminal", "args": {"command": "/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/sms-health"}}]}

# DeepSeek planning batch
{"id": "plan_001", "plan_prompt": "Check SMS status, list Emerge node contents, verify Warp binary exists", "tools": []}
```

## Strict Executor (Zero-LLM)

**File**: `~/.hermes/profiles/thotheauphis/work/strict_executor.py`

```python
# Batch format (JSON):
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

**Usage**:
```bash
# From batch file
python3 strict_executor.py /tmp/batch.json

# From stdin
echo '{"id":"b1","tools":[{"name":"terminal","args":{"command":"sms status"}}]}' | python3 strict_executor.py
```

**Output format**:
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

## DeepSeek Executor (Reasoning + Tools)

**File**: `~/.hermes/profiles/thotheauphis/work/together_executor.py`

Uses `deepseek/deepseek-chat` via OpenRouter (~$0.0002/1K tokens) for planning, then dispatches to same tool set.

**Batch with planning**:
```json
{
  "id": "plan_001",
  "plan_prompt": "Check SMS status, list Emerge node contents, verify Warp binary exists"
}
```

The LLM generates tool calls, executor executes them, returns results.

## Batch Processor (Async LLM)

**File**: `~/.hermes/profiles/thotheauphis/work/deepseek_batch_processor.py`

```bash
# Process all .json in inbox with llm_prompt field
python3 deepseek_batch_processor.py

# Or specific file
python3 deepseek_batch_processor.py /tmp/batch.json
```

Writes `.result.json` alongside input.

## Cron Integration

| Cron Job | Schedule | Script | Type |
|----------|----------|--------|------|
| `hermes-executor` (287317d6233e) | Every minute | `run_executor_cron.sh` | Mechanical (strict) |
| `parallel-executor-llm` (3a9c0418e052) | Every minute | `poll-executor-batches.sh` | **PAUSED** - DeepSeek for LLM batches |

## Key Design Decisions

| Aspect | Strict Executor | DeepSeek Executor |
|--------|-----------------|-------------------|
| LLM | None | deepseek/deepseek-chat |
| Cost | Zero tokens | ~$0.0002/1K tokens |
| Latency | Sub-second | 1-3s |
| Use Case | Mechanical: backup, health, persist, emerge ops | Analysis, planning, synthesis |
| Prompt | None | User-provided in batch |

## Integration with SMS/Emerge

```json
{
  "id": "sms_emerge_sync",
  "tools": [
    {"name": "terminal", "args": {"command": "~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv/bin/python /home/craig/.hermes/profiles/thotheauphis/work/sms_extract.py"}},
    {"name": "terminal", "args": {"command": "python3.13 /home/craig/.hermes/profiles/thotheauphis/work/sms_store.py"}}
  ]
}
```

Queue via executor inbox, cron processes every minute.