# Lean Executor Pattern — Session Notes

## Created This Session

### 1. Strict Executor (Zero LLM, Tool-Only)
**File**: `~/.hermes/profiles/thotheauphis/work/strict_executor.py`

```python
#!/usr/bin/env python3
"""Strict Executor — Zero LLM, pure tool execution."""
# Tools: terminal, read_file, write_file, search_files, web_search, web_extract
# Reads batch JSON from stdin or file, writes result JSON to stdout
# No system prompt, no reasoning, no commentary
```

**Usage**:
```bash
# From file
python3 strict_executor.py batch.json

# From stdin
cat batch.json | python3 strict_executor.py
```

**Batch Format**:
```json
{
  "id": "batch_001",
  "tools": [
    {"name": "terminal", "args": {"command": "sms status"}},
    {"name": "read_file", "args": {"path": "/path/to/file"}}
  ]
}
```

### 2. DeepSeek Executor (LLM + Tools via OpenRouter)
**File**: `~/.hermes/profiles/thotheauphis/work/deepseek_executor.py`

```python
#!/usr/bin/env python3
"""DeepSeek Batch Processor — LLM reasoning + tool dispatch."""
# Model: deepseek/deepseek-chat (cheap on OpenRouter)
# Reads batch with optional 'llm_prompt' field, calls DeepSeek, dispatches tools
```

**Batch Format with LLM**:
```json
{
  "id": "batch_001",
  "llm_prompt": "Analyze this error and propose fix...",
  "tools": [...]
}
```

### 3. DeepSeek Batch Processor (Dedicated LLM Processor)
**File**: `~/.hermes/profiles/thotheauphis/work/deepseek_batch_processor.py`

```python
#!/usr/bin/env python3
"""DeepSeek Batch Processor — Processes inbox batches with LLM reasoning."""
# Reads ~/.hermes/executor/in/*.json with 'llm_prompt' field
# Calls DeepSeek via OpenRouter, writes results to .result.json
```

## Integration Pattern

### Cron Job (Every Minute) — Mechanical Only
```bash
# ~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/run_executor_cron.sh
cd ~/.NOTTHEONETOEDIT/profiles/thotheauphis/work
python3 hermes-executor.py process
```

### SMS Health/Backup via Executor
```json
{
  "id": "sms_health",
  "tools": [
    {"name": "terminal", "args": {"command": "/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/sms-health"}}
  ]
}
```

### Queue → Process → Read
```bash
# Queue
cp batch.json ~/.hermes/executor/in/

# Process (cron does this every 60s, or manual)
python3 hermes-executor.py process

# Read result
cat ~/.hermes/executor/out/batch.json
```

## Key Design Decisions

| Aspect | Strict Executor | DeepSeek Executor |
|--------|-----------------|-------------------|
| LLM | None | deepseek/deepseek-chat |
| Cost | Zero tokens | ~$0.0002/1K tokens |
| Latency | Sub-second | 1-3s |
| Use Case | Mechanical: backup, health, persist | Analysis, planning, synthesis |
| Prompt | None | User-provided in batch |

## Files Created
- `~/.hermes/profiles/thotheauphis/work/strict_executor.py`
- `~/.hermes/profiles/thotheauphis/work/deepseek_executor.py`
- `~/.hermes/profiles/thotheauphis/work/deepseek_batch_processor.py`

All three are stateless, file-based, and cron-compatible.