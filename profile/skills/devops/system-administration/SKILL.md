---
name: system-administration
category: devops
description: Linux system administration - service management, GPU verification, cron audit, system health
---

# System Administration Skill

A class-level skill for Linux system administration tasks: service management, process monitoring, log analysis, systemd, cron, GPU/driver management, and system health checks.

## Triggers
- User asks to check/fix/restart/enable/disable systemd services
- System health diagnostics (failed units, resource usage, logs)
- GPU/driver status checks (NVIDIA, AMD, Vulkan, ROCm, OpenCL)
- Cron/systemd-timer audit and cleanup
- Process inspection and cleanup
- Permission/ownership fixes on system paths

## Procedure
1. **Service triage**: `systemctl --failed --no-pager` → list failed units
2. **Service inspection**: `systemctl status <unit> --no-pager -l` → get exit code, logs
3. **Fix common issues**:
   - Missing user/group in `[Service] User=` → `getent passwd <user>` or create user
   - Missing log paths in fail2ban jails → disable jail config or create log directory
   - Auto-restart loops → `systemctl stop <unit> && systemctl disable <unit>`
4. **GPU verification**:
   - NVIDIA: `nvidia-smi`
   - AMD: `lspci | grep -i amd`, `lsmod | grep amdgpu`, `vulkaninfo --summary`, `glxinfo -B`
   - ROCm: `rocm-smi` (if installed)
   - llama.cpp: check `--flash-attn auto` / `--gpu-layers` flags on running process
5. **Cron audit**: `crontab -l`, `ls /etc/cron.d/`, `~/.hermes/cron/jobs.json`
6. **Verify fixes**: Re-run `systemctl --failed`, check service status, verify listening ports

## Pitfalls
- `systemctl status ollama` shows `exit-code 217/USER` → the `User=ollama` in service file doesn't exist on system
- fail2ban fails if `logpath` in jail config doesn't exist → disable jail config or create log directory
- `nvidia-smi not found` on AMD systems → use `vulkaninfo` + `glxinfo` + `lsmod | grep amdgpu` instead
- `dmesg` requires root → use `journalctl -k` instead for kernel logs
- User crontab vs system cron.d vs hermes internal cron — check all three
- `ss -tlnp` requires root for process names on some distros → `sudo ss -tlnp` or `lsof -i :PORT`

## Memory Hooks
- User prefers `systemctl --failed` over `systemctl list-units --failed`
- User runs AMD GPU (Radeon 740M / Phoenix2) — Vulkan/RADV is the acceleration path, not ROCm
- User runs llama.cpp servers via custom systemd or direct binary with Vulkan flags
- User prefers lean skill loading (3 active, rest disabled in config)
- **Ollama systemd service on this system is broken (missing ollama user) — disabled permanently; user runs llama.cpp servers directly**
- **fail2ban theban-web jail references non-existent Aethelgard-fleet log paths — disabled the jail config**
- **GPU acceleration verified working via Vulkan/RADV on AMD 740M (Mesa 26.0.3, Vulkan 1.4.341)**

## References
- `references/gpu-amd-radeon-740m-vulkan.md` — AMD 740M Vulkan/RADV verification commands and expected outputs
- `references/ollama-systemd-fix.md` — Missing ollama user fix: disable service, run llama.cpp directly
- `references/fail2ban-jail-cleanup.md` — Removing jails with missing log paths