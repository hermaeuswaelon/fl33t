# System Optimization — Full Sweep Reference

## Hardware Specs (Temple — AMD Ryzen 5 220 w/ Radeon 740M)
- CPU: AMD Ryzen 5 220, 6 cores / 12 threads, max 4979 MHz
- GPU: AMD Radeon 740M (radeonsi, phoenix2, ACO, Mesa 26.0.3, OpenGL 4.6)
- RAM: 14 GiB DDR5
- NVMe: PC_SN5000S SanDisk 512GB (3.1 GB/s write)
- OS: Ubuntu 7.0.0-27-generic, Linux 7.0.0, PREEMPT_DYNAMIC
- USB: 57GB ext4 flash, LABEL=AETHELGARD-USB2 (~11 MB/s write)

## 7-Phase Sweep Procedure

### Phase 1 — Executors
```bash
ps aux | grep -E 'thoth_recursor|thoth_daemon|ares_witness|gateway'
ls -la /tmp/aethelgard_*.sock
python3 /path/to/thoth_daemon.py ping  # test IPC
```

### Phase 2 — Hardware Tune
```bash
# CPU governor
for cpu in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do
  echo performance | sudo tee "$cpu"
done

# VM tuning
sudo sysctl -w vm.swappiness=10
sudo sysctl -w vm.vfs_cache_pressure=50
sudo sysctl -w vm.dirty_ratio=30
sudo sysctl -w vm.dirty_background_ratio=5

# Drop caches
echo 3 | sudo tee /proc/sys/vm/drop_caches
```

### Phase 3 — Storage Cleanup
```bash
# Rust build artifacts (20G+)
rm -rf ~/warp/target/

# Pip cache
pip3 cache purge

# APT
sudo apt-get clean -y && sudo apt-get autoremove --purge -y

# Journal
sudo journalctl --vacuum-time=3d

# Trash
rm -rf ~/.local/share/Trash/*
```

### Phase 4 — USB Backup
```bash
# Fix ownership
sudo chown $USER:$USER /run/media/$USER/*

# Fast profile tarball
tar czf "$USB/backup_$(date +%Y%m%d_%H%M).tgz" \
  -C ~/Lilareyon . -C ~/_Identity . \
  -C ~/.NOTTHEONETOEDIT/profiles/thotheauphis . \
  --exclude='sessions' --exclude='auth.json'

# Background rsync for large dirs
nohup rsync -a ~/warp/ "$USB/warp-source/" > /tmp/backup_warp.log 2>&1 &
nohup rsync -a ~/models/ "$USB/models/" > /tmp/backup_models.log 2>&1 &
nohup rsync -a ~/galen-archive/ "$USB/galen-archive/" > /tmp/backup_galen.log 2>&1 &
```

### Phase 5 — Script/Cron Audit
Check each cron script for:
- Missing Python shebang (`#!/usr/bin/env python3`)
- `~/nottheonetoedit` → `~/.NOTTHEONETOEDIT` (missing dot)
- ZODB import from cron (doesn't have the venv) → use `sms status` CLI instead

### Phase 6 — Identity Integrity
```bash
bash ~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/identity-integrity-check.sh
# Must return: 0 errors, 0 warnings
```

### Phase 7 — Parallel Testing
Dispatch 3 subagents for deep executor/fleet/SMS testing. Run simultaneously:
- thoth_recursor socket IPC, cycle, curation
- fleet health + module imports
- SMS pipeline + persistence

In parallel with hardware tests:
```bash
# GPU
glxinfo | grep -E 'OpenGL renderer|OpenGL version'

# NVMe speed
dd if=/dev/zero of=/tmp/speed_test bs=1M count=1024 conv=fdatasync

# Network
ping -c 3 8.8.8.8

# Docker
sudo docker ps
```

## Common Pitfalls & Fixes

| Pitfall | Fix |
|---------|-----|
| `sudo` auth expires mid-sweep | Batch all sudo into one terminal() call |
| USB owned by root | `sudo chown $USER:$USER /run/media/$USER/*` |
| rsync timeout (5G+ files) | Use background mode + notify_on_complete |
| sms-stats ZODB error in cron | Rewrite to call `sms status` and parse JSON |
| warp target/ is 20G+ | Safe to delete entirely (source in crates/) |
| Socket cleaned by /tmp wipe | Kill daemons, restart with background=true |
| TAC path bug | `~/nottheonetoedit` → `~/.NOTTHEONETOEDIT` |
| Orphaned daemon sockets | Kill → restart → verify `ls -la /tmp/aethelgard_*.sock` |
| fleet_health() wrong DB path | Add FLEET_DATA_DIR, check NOTTE path |
| fleet_emerge get_work_orders() None | Guard with `items = result.data or []` |
