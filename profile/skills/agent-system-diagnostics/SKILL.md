---
name: agent-system-diagnostics
title: Agent System Diagnostics
category: operations
tags: [diagnostics, troubleshooting, logs, provider-health, compression]
description: Class-level skill for diagnosing Hermes agent system health from log files, provider failures, and compression issues.
trigger: User reports log spam, failed API calls, compression loops, or system health concerns. Load when investigating why the agent is behaving unexpectedly.
---

# Agent System Diagnostics

Diagnose Hermes agent health issues by analyzing log files, provider responses, and system state.

## Log File Inventory

The active profile's logs live at:
```
~/.NOTTHEONETOEDIT/profiles/<profile>/logs/
├── agent.log       # Current session: API calls, tool exec, conversation turns
├── agent.log.N     # Rotated previous sessions (N=1,2,...)
├── errors.log      # Warnings, errors, compression loops
└── gateway.log     # Platform adapter activity (Telegram, Discord, Email)
```

## Diagnostic Pipeline

### 1. Check Gateway Process
```bash
ps aux | grep "gateway run"
systemctl --user status hermes-gateway
journalctl --user -u hermes-gateway -n 30 --no-pager
```

### 2. Check Emerge Node
```bash
systemctl --user status emerge-node
ss -tlnp | grep 54242
```

### 3. Check for Compression Loops
The most common log flood is a stuck 108K compression loop:
```bash
grep -c "forcing compression" ~/.NOTTHEONETOEDIT/profiles/<profile>/logs/errors.log
```
If count > 10 in a few minutes, the one-time-only trigger has failed.

### 4. Check for Provider Failures by Code
```bash
grep "HTTP 402" errors.log agent.log*    # Insufficient Balance
grep "HTTP 429\|RateLimit" errors.log agent.log*  # Rate limited
grep "OAuth\|token not found" errors.log agent.log*  # Missing auth tokens
grep "500\|503\|502\|Bad Gateway" errors.log agent.log*  # Server errors
```

### 5. Check API Call Health
```bash
grep "API call #" agent.log | tail -5     # Recent API call stats
grep "latency=" agent.log | tail -5        # Recent latency
```

## Common Failure Patterns

| Pattern | Error Code | Log File | Fix |
|---------|-----------|----------|-----|
| Compression loop | "forcing compression" repeated 100+× | errors.log | Fix one-time-only flag in context_compressor.py |
| Balance exhausted | "HTTP 402: Insufficient Balance" | agent.log | Add credits or switch model |
| Rate limited | "HTTP 429: Provider returned error" | agent.log | Retry after delay, use non-free model |
| xAI OAuth missing | "no xAI OAuth token found" | errors.log | `hermes model -> xAI Grok OAuth` or disable xAI plugin |
| OpenRouter model unavailable | "No endpoints found" | agent.log | Use `:free` suffix for free models |
| Gateway DNS fail | "Temporary failure in name resolution" | gateway.log | Check network/DNS |

## Reference Files

This skill may contain session-specific diagnostic guides in `references/`.

## Pitfalls

- DON'T assume the model name in config.yaml is what's actually being used — delegation and MoA may use different models/providers
- DON'T check only agent.log — the compression loop only shows in errors.log
- DO check all rotated logs (agent.log.1, agent.log.2) for patterns that may have been rotated out of the current file
- DON'T restart the gateway as a first step — you'll lose the current error state
- xAI plugin registers on every gateway restart even without valid OAuth — ignore the INFO-level rego messages
