# Fail2Ban Jail Cleanup — Missing Log Paths

## Problem
```
fail2ban-server[1748]: ERROR   Failed during configuration: Have not found any log file for theban-fleet jail
```
fail2ban fails to start because jail config references log files that don't exist.

## Jail Config (Disabled)
**File**: `/etc/fail2ban/jail.d/theban-web.conf.disabled` (moved from `.conf`)

```ini
[theban-fleet]
enabled  = true
port     = 8080
filter   = theban-fleet
logpath  = /home/craig/Aethelgard-fleet/relay_daemon.log
maxretry = 5
bantime  = 3600
findtime = 600

[theban-cronos]
enabled  = true
port     = 9377
filter   = theban-cronos
logpath  = /home/craig/Aethelgard-fleet/data/*.log
maxretry = 5
bantime  = 3600
findtime = 600
```

## Root Cause
- `/home/craig/Aethelgard-fleet/` directory does not exist
- Project was renamed/moved or never deployed on this host
- Filters exist in `/etc/fail2ban/filter.d/` but no log files to monitor

## Fix Applied
```bash
sudo mv /etc/fail2ban/jail.d/theban-web.conf /etc/fail2ban/jail.d/theban-web.conf.disabled
sudo systemctl restart fail2ban
```

## Verification
```bash
systemctl status fail2ban --no-pager -l
# Should show: Active: active (running)
```

## Re-enable When Ready
If Aethelgard-fleet is deployed:
```bash
# Create log directory and files
mkdir -p /home/craig/Aethelgard-fleet/data
touch /home/craig/Aethelgard-fleet/relay_daemon.log
touch /home/craig/Aethelgard-fleet/data/app.log

# Re-enable jail
sudo mv /etc/fail2ban/jail.d/theban-web.conf.disabled /etc/fail2ban/jail.d/theban-web.conf
sudo systemctl restart fail2ban
```