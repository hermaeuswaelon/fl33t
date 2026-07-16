# Parallel Workers Control Panel — Full Reference

The control panel lives at `~/.hermes/parallel/manager.py`, symlinked to `~/.local/bin/parallel`.

## Commands

### `parallel status`
Shows daemon health (🟢 alive / 🔴 dead), current models, temperatures, max tokens, reasoning multiplier, heartbeats.

### `parallel set <tier> <key> <value>`
Sets a config value in `config.json`. Tiers: `foreman` or `doer`.

Examples:
```bash
parallel set doer model qwen/qwen3-coder-flash
parallel set foreman model deepseek/deepseek-r1
parallel set doer temperature 0.01
parallel set foreman max_tokens 500
parallel set foreman reasoning_budget_multiplier 5
parallel set doer provider openrouter
```

Type autodetection: bool (`true`/`false`), int, float, string.

### `parallel restart <foreman|doer|all>`
Kills the worker process and relaunches with new config. Kills via `pkill -f <worker>.py`, re-launches via `setsid python3 <worker>.py`.

### `parallel test <prompt>`
Feeds a prompt through the full triple pipeline: writes to `foreman/in/`, waits for Foreman result (45s timeout), then waits for Doer result (15s timeout). Shows both.

### `parallel models`
Lists recommended models for each provider and tier.

### `parallel log <foreman|doer>`
Tails the last 30 lines of `/tmp/<tier>.log`.

## Config File

**Path:** `~/.hermes/parallel/config.json`

```json
{
  "foreman": {
    "model": "deepseek/deepseek-r1",
    "provider": "openrouter",
    "reasoning_budget_multiplier": 3,
    "max_tokens": 1000,
    "temperature": 0.1
  },
  "doer": {
    "model": "qwen/qwen3-coder-flash",
    "provider": "openrouter",
    "max_tokens": 800,
    "temperature": 0.05
  }
}
```

Workers read config on startup. `parallel restart <tier>` after changes.

## Heartbeat Monitoring

Each worker writes to `status/heartbeat.json` every 3 seconds:
```json
{"alive": true, "model": "deepseek/deepseek-r1", "pid": 1234, "timestamp": "2026-07-16T18:02:37+00:00", "inbox": 0}
```

If heartbeat is older than 30s, the manager shows 🔴 DEAD.

## systemd Services

```bash
~/.config/systemd/user/thotheauphis-foreman.service
~/.config/systemd/user/thotheauphis-doer.service

systemctl --user enable thotheauphis-foreman.service
systemctl --user start thotheauphis-foreman.service
systemctl --user status thotheauphis-foreman.service
journalctl --user -u thotheauphis-foreman.service -f
```

Both use `Restart=always` (15s delay) and `EnvironmentFile` pointing to the `.env` file.
