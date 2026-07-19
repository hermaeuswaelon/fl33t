# Daemon Auto-Restart Purge Protocol

Session date: 2026-07-19
Context: LFM 1.2B Nova and other model daemons kept respawning after being killed.

## Root-Cause Checklist

When a model process keeps respawning after `kill -9`, check ALL of these:

### 1. systemd Restart= policy
```bash
systemctl --user list-units --type=service --all | grep -iE 'llama|model|qwen|vl|recursor|thoth|doer|foreman|throne'
```
Look for `auto-restart` in the status column → service has `Restart=on-failure` or `Restart=always`.

**Fix**: `systemctl --user stop <unit>` then `systemctl --user disable <unit>`

### 2. systemd timers (the silent reaper)
```bash
systemctl --user list-timers --no-legend
systemctl --user cat <timer-name>  # reveals what it fires and how often
```
Timers can have `OnUnitActiveSec=5min` + `OnBootSec=1min` making them respawn near-instantly.

**Fix**: `systemctl --user stop <timer>` then `systemctl --user disable <timer>`

### 3. Custom watchdog scripts
```bash
ls -la ~/.aethelgard/              # thoth_perf_watchdog.py, etc.
ls -la ~/.local/bin/               # fleet-daemons, fleet-hog-killer
ls -la ~/projects/aethelgard/fleet/site/   # fleet-irrational-update-loop.sh
```
These can re-spawn model processes independently of systemd.

**Fix**: Comment out or delete the spawn lines in the script, or remove the script's trigger (its timer/service).

### 4. Boot/startup hooks
```bash
ls -la ~/.config/systemd/user/default.target.wants/  # symlinks to enabled services
```

## Known Auto-Restart Traps (this system)

| Trap | Mechanism | Fix |
|------|-----------|-----|
| `hermes-lfm12.service` | systemd Restart=on-failure | `stop + disable` |
| `sovereign-memory.service` | systemd auto-restart | `stop + disable` |
| `thoth-perf-watchdog.timer` | Timer fires every 5min, spawns hog-killer which can re-spawn models | `stop + disable`, also check what hog-killer does |
| `hermes-vl.service` | systemd | already disabled |
| `thoth-recursor.service` | systemd | `stop + disable` |
| `fleet-site-update.service` | systemd | `stop + disable` |
| `fleet-irrational-update-loop.sh` | Perpetual shell loop | Kill the process, comment out cron/timer |

## Purge Procedure

```bash
# 1. Identify all model processes
ps aux | grep -iE 'llama-server|llama-cli'

# 2. Stop and disable every service that could restart them
for svc in hermes-lfm12.service sovereign-memory.service hermes-vl.service \
           thoth-recursor.service aurelian-throne.service; do
  systemctl --user stop "$svc"
  systemctl --user disable "$svc"
done

# 3. Stop and disable timers
for tmr in thoth-perf-watchdog.timer; do
  systemctl --user stop "$tmr"
  systemctl --user disable "$tmr"
done

# 4. Kill remaining PIDs
sudo kill -9 <PID>

# 5. Verify
ps aux | grep llama-server  # should only show the one you want to keep
systemctl --user is-enabled hermes-lfm12.service sovereign-memory.service  # all 'disabled'
```

## Key Insight

Killing a process is NEVER enough on this system. The service unit in systemd will restart it within seconds. The only lasting fix is:
1. Stop the service
2. Disable the service  
3. Stop and disable any timer that fires the service
4. Check for watchdog scripts that spawn processes directly

## Qwen2.5-VL Deployment Notes (this session)

- Build: `~/llama.cpp-yuuko-grounders/build-vulkan/` took ~700s
- Vulkan: 1.4.341, AMD HawkPoint2, cmake 4.2.3
- Qwen2.5-VL needs `--image-min-tokens 1024` flag to avoid grounding warnings
- f16 mmproj (~1.3G) used — bf16 same size, no difference
- Tested text → "4", vision (red square) → "Red" — both passing
- Port: 8088, API key: `qwen-vl-key`
- Model path: `~/models/qwen2.5-vl-7b/Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf` (4.4G)
