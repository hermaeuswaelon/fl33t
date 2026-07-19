# Provider Failure Diagnosis from Logs

## Log File Locations
```
~/.NOTTHEONETOEDIT/profiles/thotheauphis/logs/
├── agent.log          # API calls, tool exec, conversation turns (live session)
├── agent.log.1        # Rotated previous session
├── agent.log.2        # Rotated earlier session
├── errors.log         # Warnings, errors, compression loops
└── gateway.log        # Gateway platform activity (Telegram, Discord, Email)
```

## Journalctl
```bash
journalctl --user -u hermes-gateway -n 50 --no-pager   # Recent gateway logs
journalctl --user -u emerge-node -n 20 --no-pager       # Emerge node server
```

## grep Patterns by Problem Type

### Compression Loop
```bash
grep -c "forcing compression" errors.log                    # Count loop repetitions
grep "108K Gate" errors.log | wc -l                         # 108K threshold hits
grep "compression started\|compression complete" agent.log  # Actual compression events
```

### API Failures (402 — Insufficient Balance)
```bash
grep "HTTP 402\|Insufficient Balance" errors.log agent.log*
```

### API Failures (429 — Rate Limited)
```bash
grep "HTTP 429\|RateLimitError\|rate-limited" errors.log agent.log*
```

### Provider Auth Failures
```bash
grep -i "OAuth\|token not found\|api_key" errors.log agent.log*
```

### xAI/Grok Plugin
The xAI plugin registers on every gateway restart. If no OAuth token:
```bash
grep "xai-oauth\|no xAI OAuth token" errors.log
```
Fix: configure token via `hermes model -> xAI Grok OAuth` or disable the xAI plugin.

## Gateway Process Health
```bash
ps aux | grep "gateway run"     # Gateway process alive?
lsof -p <PID> | grep log        # Which log files the gateway is writing to
journalctl --user -u hermes-gateway -f  # Follow live gateway output
```

## System Service Check
```bash
systemctl --user status hermes-gateway    # Gateway status
systemctl --user status emerge-node       # Emerge object store status
ss -tlnp | grep 54242                     # Emerge port listening?
```
