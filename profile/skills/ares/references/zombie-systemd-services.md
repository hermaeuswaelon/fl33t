# ⧉ Zombie Aethelgard Systemd Services — Cleanup Procedure ⧉

## Problem
Aethelgard fleet systemd services get stuck in `activating (auto-restart)` loops when:
- The underlying Python script is deleted or moved
- A directory in the ExecStart path no longer exists
- Dependencies are missing

The service repeatedly attempts to restart (every 3-5s by default), generating
endless connection attempts to whatever backend it targets (xAI/Grok, Ollama, etc.).

## Detection

```bash
# List all failing/auto-restarting services
systemctl --user list-units --state=failed,activating --type=service

# Check a specific service
systemctl --user status <service-name> --no-pager | head -15
# Look for "auto-restart" in Active line and "status=200/CHDIR" or "code=exited"
```

## Kill & Disable (permanent stop)

```bash
# Stop immediately + prevent future auto-restarts
systemctl --user stop <service-name>
systemctl --user disable <service-name>

# Verify
systemctl --user is-active <service-name>  # should return "inactive"
```

## Known Offenders (from real cleanup 2026-07-18)

| Service | Script Path | Status | Cause |
|---------|-------------|--------|-------|
| `grok-tools.service` | `~/Aethelgard-fleet/grok_env/tool_server.py` | ❌ zombie | Directory deleted |
| `aethelgard-event-bus.service` | `~/.NOTTHEONETOEDIT/fleet/modules/event_bus.py` | ❌ zombie | Script deleted |
| `aethelgard-memcustd.service` | `~/.NOTTHEONETOEDIT/context_custodian/memcustd.py` | ❌ zombie | Script deleted |
| `aethelgard-watcher.service` | fleet watcher script | ❌ zombie | Script deleted |

## Prevention
- Before removing a fleet script, check for systemd user units referencing it:
  `grep -l <script-path-or-dir> ~/.config/systemd/user/*.service`
- Then `stop && disable` before deleting the script
- When scaffolding new fleet services, add a [Unit] `ConditionPathExists=` guard:
  ```
  [Unit]
  ConditionPathExists=/path/to/script.py
  ```
