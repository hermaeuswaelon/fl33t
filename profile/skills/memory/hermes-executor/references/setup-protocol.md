# Hermes Executor — Setup & Protocol Reference

## File Locations

| Asset | Path |
|-------|------|
| Executor script | `~/.hermes/profiles/thotheauphis/work/hermes-executor.py` |
| Symlink (for cron) | `~/.hermes/scripts/hermes-executor.py` |
| Inbox | `~/.hermes/executor/in/` |
| Outbox | `~/.hermes/executor/out/` |
| Lock file | `~/.hermes/executor/executor.lock` |
| Skill file | `~/.hermes/profiles/thotheauphis/skills/memory/hermes-executor/SKILL.md` |

## Cron Jobs

| Name | Job ID | Schedule | Type | Status |
|------|--------|----------|------|--------|
| `hermes-executor` | `287317d6233e` | `* * * * *` | `no_agent=true` — script executor, ZERO tokens | ✅ Active |
| `parallel-executor-llm` | `3a9c0418e052` | `* * * * *` | `no_agent=false` — DeepSeek-chat via OpenRouter | ⏸️ Paused |

Manage via:
```
cronjob action=list                                # list all
cronjob action=resume job_id=3a9c0418e052          # unpause LLM executor
cronjob action=pause job_id=287317d6233e           # pause script executor
```

## Batch Protocol

### Request format (`in/{id}.json`)
```json
{
  "id": "batch_1712345678",
  "tools": [
    {"name": "terminal", "args": {"command": "ls -la", "timeout": 30}},
    {"name": "read_file", "args": {"path": "/tmp/data.txt"}},
    {"name": "write_file", "args": {"path": "/tmp/out.txt", "content": "hello"}},
    {"name": "web_search", "args": {"query": "spades rules"}}
  ],
  "created_at": "2026-07-16T06:17:00+00:00"
}
```

### Response format (`out/{id}.json`)
```json
{
  "id": "batch_1712345678",
  "status": "done",
  "results": [
    {"index": 0, "name": "terminal", "status": "done", "output": "...", "exit_code": 0}
  ],
  "errors": null,
  "completed_at": "2026-07-16T06:17:09+00:00",
  "total": 1,
  "success": 1,
  "failed": 0
}
```

### Supported tools
terminal, read_file, write_file, search_files, web_search, web_extract

### Via terminal (inline)
```bash
python3 ~/.hermes/scripts/hermes-executor.py \
  batch --tool terminal command "uptime" --tool read_file path "/etc/hostname"
```

## When to Use Each Tier

| Tier | Cost | When |
|------|------|------|
| **Script executor** (no_agent) | Zero — pure Python | Pure tool execution. Batch 5-17 calls. |
| **LLM executor** (paused) | ~1-2K tokens/batch | Batches needing decisions: "check logs, tell me which to delete." |
| **Direct tools (default)** | ~100K tokens each | Only 1-2 calls or needs interactive reasoning mid-stream. |

## Persistence

- Cron jobs survive session resets
- `~/.hermes/executor/` directory persists
- This reference file survives
- Skill survives
- **Startup**: No action needed — cron fires every minute, executor always ready
