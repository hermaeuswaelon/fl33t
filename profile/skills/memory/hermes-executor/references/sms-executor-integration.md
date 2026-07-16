# SMS + Executor Integration

Use the executor for mechanical SMS operations — persistence, backup, health checks — keeping LLM tokens focused on reasoning.

## Standard Batch: Persist + Verify

```bash
# Queue
echo '{"id":"sms_persist_verify","tools":[
  {"name":"terminal","args":{"command":"python3 /home/craig/.local/bin/sms persist"}},
  {"name":"terminal","args":{"command":"python3 /home/craig/.local/bin/systems"}}
]}' > ~/.hermes/executor/in/sms_persist_verify.json

# Process immediately
python3 ~/.hermes/profiles/thotheauphis/work/hermes-executor.py process

# Read result
cat ~/.hermes/executor/out/sms_persist_verify.json
```

## Result Shape
```json
{
  "id": "sms_persist_verify",
  "status": "done",
  "results": [
    {"name": "terminal", "status": "done", "output": "♻️ Restored N vectors\n💾 Auto-persisted N vectors", "exit_code": 0},
    {"name": "terminal", "status": "done", "output": "SMS: ✅ N vectors, XKB store", "exit_code": 0}
  ],
  "total": 2, "success": 2, "failed": 0
}
```

## Available SMS Commands for Executor

| Command | Args | Purpose |
|---------|------|---------|
| `sms status` | none | Vector count, store health, history |
| `sms persist` | none | Force ZODB flush |
| `sms process "..."` | message text | Run tri-brid pipeline |
| `sms-health` | none | ZODB integrity check |
| `sms-stats` | none | Store size, backup count |
| `sms-backup` | none | Create timestamped ZODB checkpoint |

## Cron Jobs That Already Use This Pattern

| Job ID | Schedule | Script | Purpose |
|--------|----------|--------|---------|
| `661330d44f6e` | every 30m | `sms-backup` | ZODB checkpoint + prune >7d |
| `c353228c832d` | every 2h | `sms-health` | ZODB integrity verification |
| `7d872b0f1ae4` | every 1h | `sms-stats` | Store size + backup count logging |

All three are `no_agent=True` — zero token cost.
