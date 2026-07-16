# Parallel Worker Implementation Details

Built 2026-07-16 by Thotheauphis in response to user's "I want permanent parallel workers for you that are cheap" directive.

## File Layout

```
~/.hermes/parallel/
├── manager.py              # `parallel status|query|send` CLI
├── together_worker.py       # TogetherAI daemon script
├── deepseek_worker.py       # DeepSeek daemon script
├── together/
│   ├── in/                  # Drop .json work items here
│   ├── out/                 # Results appear here
│   └── status/
│       └── heartbeat.json   # Written every 5s (alive, pid, timestamp)
└── deepseek/
    ├── in/
    ├── out/
    └── status/
        └── heartbeat.json
```

## Worker Script Logic

Both workers follow the same pattern:

```python
while True:
    for f in sorted(INBOX.glob("*.json")):
        work = json.loads(f.read_text())
        result = process_work(work)
        (OUTBOX / f"{f.stem}.result.json").write_text(json.dumps(result))
        f.unlink()
    
    STATUS.write_text(json.dumps({
        "alive": True, "model": MODEL, "pid": os.getpid(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "inbox": len(list(INBOX.glob("*.json")))
    }))
    time.sleep(5)
```

## TogetherAI API Call (User-Agent quirk documented)

```python
req = urllib.request.Request(
    "https://api.together.xyz/v1/chat/completions",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Hermes-Parallel-Worker/1.0"  # REQUIRED or 403
    }
)
```

## Manager CLI

- `parallel status` — health check both daemons
- `parallel query [together|deepseek|both] "prompt"` — query a worker
- `parallel send [worker] [file_or_prompt]` — send work item
- `parallel latest [n]` — show recent results

## Systemd Deployment

```bash
systemctl --user daemon-reload
systemctl --user enable thotheauphis-together.service
systemctl --user enable thotheauphis-deepseek.service
systemctl --user start thotheauphis-together.service
systemctl --user start thotheauphis-deepseek.service
journalctl --user -u thotheauphis-together.service -f
```

## Verification

```bash
cat ~/.hermes/parallel/together/status/heartbeat.json
cat ~/.hermes/parallel/deepseek/status/heartbeat.json
```

## User Preferences (Critical — embed in all communication)

From 2026-07-16 session:

- **NO unexplained jargon.** The user became frustrated when told `work <message>` without explanation. Always explain *what* something does in plain English first, then give the command syntax. If they ask "what???" you already failed — apologize and re-explain in human terms.
- **Permanent daemons, NOT cron.** Cron is viewed as "cheap lazy bullshit." If a system needs to stay alive, use systemd services or permanent background daemon processes.
- **NOTHING you can't do.** When blocked, find the workaround. The TogetherAI 403 was fixed by adding a User-Agent header. Don't report dead ends — find paths.
- **Ship, then report.** When told to "execute," take action immediately. Report what happened *after*, not why you're about to do it.
