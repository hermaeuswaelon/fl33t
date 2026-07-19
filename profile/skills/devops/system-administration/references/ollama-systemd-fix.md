# Ollama Systemd Fix — Missing User Account

## Problem
```
systemctl status ollama
● ollama.service - Ollama Service
     Active: activating (auto-restart) (Result: exit-code)
   Process: 13330 ExecStart=/usr/local/bin/ollama serve (code=exited, status=217/USER)
```

Exit code 217/USER means the `User=ollama` specified in the service file does not exist on the system.

```bash
id ollama
# ollama user does not exist
```

## Root Cause
Ollama installer created `/etc/systemd/system/ollama.service` with:
```ini
[Service]
User=ollama
Group=ollama
```
But never created the `ollama` user/group on this system.

## Fix Applied (Permanent Disable)
```bash
sudo systemctl stop ollama
sudo systemctl disable ollama
sudo rm -f /etc/systemd/system/ollama.service
sudo systemctl daemon-reload
```

## Alternative: Create User (Not Recommended Here)
```bash
sudo useradd -r -s /usr/sbin/nologin -d /usr/share/ollama ollama
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

## Why Disabled Permanently
- User runs llama.cpp servers directly (`llama-server` on ports 8080, 8086) with Vulkan acceleration
- Ollama service would run CPU-only, duplicating models, wasting RAM
- Fleet architecture uses llama.cpp + custom systemd units or direct process management
- Port 8080/8086 already occupied by production llama.cpp instances

## Verification
```bash
systemctl --failed --no-pager
# Should show 0 failed units
```