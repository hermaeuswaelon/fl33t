# System Audit & Optimization Workflow

## Trigger
User says "upgrade & optimize", "review all systems", "make everything optimal", or references system health/performance.

## Core Principle: Bias to Action
- Don't analyze first — dispatch immediately
- Run parallel tool calls for independent diagnostics
- Delegate subagents for deep testing while you fix surface issues
- Report results as they arrive, not when everything finishes
- A 70% first action beats 100% analysis that never shipped

## Five-Phase Workflow

### Phase 1: Full System Inventory (Parallel Dispatch)

Dispatch ALL of these simultaneously — none depend on each other:

```bash
# Disks & mounts
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,LABEL,MODEL
df -h
findmnt -D | head -30

# Hardware
uname -a
free -h
lscpu | grep -E 'Model name|CPU\(s\)|Core|Thread|MHz'
cat /proc/loadavg

# GPU
lspci | grep -iE 'vga|3d|display|radeon|amdgpu'
glxinfo | grep -E 'OpenGL renderer|OpenGL version'

# Daemons & services
ps aux | grep -E 'hermes|fl33t|sms|ares|executor|thoth|gateway' | grep -v grep
systemctl list-units --type=service --state=running

# Network
ping -c 3 8.8.8.8
ss -tlnp

# Storage usage
du -sh ~/* --exclude=.cache --exclude=.local | sort -rh | head -20
du -sh ~/.NOTTHEONETOEDIT/profiles/thotheauphis/

# Docker
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
```

### Phase 2: Identify Backup Candidates

Look for:
- Large directories (>500MB): `~/warp/target/`, `~/models/`, `~/galen-archive/`
- Build artifacts: Rust `target/`, `node_modules/`, `.cache/`
- Archives: `~/ORGANIZED_FILES/`, `~/Desktop/`
- The `AETHELGARD-USB2` flash drive (check `lsblk`)

### Phase 3: Backup Strategy

1. **Clean build artifacts first** to reduce backup size (e.g., `rm -rf ~/warp/target/` reclaims ~20G)
2. **Parallel transfer** via `terminal(background=true, notify_on_complete=true)`
3. **Also write a compressed tarball**: `tar czf $USB/backup_$(date +%Y%m%d).tgz ...`
4. **Write manifest**: `MANIFEST_ABSORBED.md` on the USB with hash/summary

### Phase 4: Fix Execution (Ordered by Impact)

1. **Memory tuning** — fastest impact:
   ```bash
   sudo sysctl -w vm.swappiness=10
   sudo sysctl -w vm.vfs_cache_pressure=50
   sudo sysctl -w vm.dirty_ratio=30
   echo 3 | sudo tee /proc/sys/vm/drop_caches
   ```

2. **CPU governor** — all cores to performance:
   ```bash
   for cpu in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do
     echo performance | sudo tee "$cpu"
   done
   ```

3. **Cleanup** — parallel execution:
   - `rm -rf ~/.local/share/Trash/*`
   - `pip3 cache purge`
   - `sudo journalctl --vacuum-time=3d`
   - `sudo apt-get clean && sudo apt-get autoremove --purge -y`

4. **System update**: `sudo apt-get update && sudo apt-get upgrade -y`

### Phase 5: Verification (Parallel Subagents + Direct Tests)

**Direct tests** (run in parallel batch):
- GPU: `glxinfo | grep -E 'OpenGL renderer|OpenGL version|direct rendering'`
- Disk: `dd if=/dev/zero of=/tmp/speed_test bs=1M count=1024 conv=fdatasync`
- Network: `ping -c 3 8.8.8.8` + `nslookup github.com`
- USB: Write test file, verify with `df -h`
- Identity: `bash ~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/identity-integrity-check.sh`
- SMS: `sms status`

**Subagent tasks** (dispatch 3 simultaneously via delegate_task):
- Daemon 1: thoth_recursor — socket, cycle, journal, library index
- Daemon 2: thoth_daemon/fleet — socket, ping, stats, module imports
- SMS: full tri-brid pipeline test, ZODB verification, sms process

**Cron test**: Force-run critical crons:
```bash
bash ~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/fl33t-backup.sh
bash ~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/sms-health
~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/sms-stats
```

## Common Fixes Catalog

| Symptom | Fix | Verification |
|---------|-----|--------------|
| Swap thrashing | swappiness=10, drop_caches | `free -h` → swap draining |
| CPU underclocked | performance governor | `cat /sys/.../scaling_governor` → performance |
| Missing daemon sockets /tmp/ cleaned | Kill daemon → restart with background=true | `ls -la /tmp/aethelgard_*.sock` + ping test |
| Python script: "import ZODB" fails | Rewrite to use CLI instead of raw ZODB | Run script → prints JSON |
| Cron: "script not found" | Script lives in wrong dir, create symlink or update cron script path | `cronjob action=list` → last_status=ok |
| Cron: path typo | Check for `~/nottheonetoedit` vs `~/.NOTTHEONETOEDIT` | `grep -rn "nottheonetoedit" scripts/` |
| Large dir on root | Move build artifacts to USB or clean | `df -h /` → reclaimed |
