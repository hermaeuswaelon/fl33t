# Identity Backup & Integrity Verification

## Overview

The Thotheauphis identity layer is backed up daily to `github.com/hermaeuswaelon/fl33t`. Two scripts handle verification and backup.

## Daily Cron (09:00)

Created July 2026. No-agent script mode (zero token cost).

```
Job ID: 229eeac06584
Script: fl33t-backup.sh
Schedule: 0 9 * * * (daily at 9 AM)
Mode: no_agent = true (pure shell, no LLM cost)
Deliver: local (saves output, no live notification)
```

## Backup Script

**Path:** `~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/fl33t-backup.sh`

Stages:
1. Run `identity-integrity-check.sh` — abort on failure
2. Clone `fl33t` repo to temp directory
3. Copy identity layer (`_Identity/`, SOUL.md)
4. Copy profile config (config.yaml, gateway_state, channel_directory)
5. Copy all skills with directory structure preserved
6. Copy work/ directory (slash registry code, architecture docs)
7. Copy cron job definitions
8. Generate SHA256 integrity manifest (`sha256sum.txt`)
9. Generate INVENTORY.md with file counts and timestamps
10. Commit with timestamped message (`fl33t backup snapshot-YYYYMMDD-HHMMSS`)
11. Push to `github.com/hermaeuswaelon/fl33t`
12. Clean up temp directory

## Integrity Check Script

**Path:** `~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/identity-integrity-check.sh`

Checks 6 layers:
1. `_Identity/all.txt` exists and is ≥80KB
2. All 5 identity sub-files present
3. SOUL.md has >5 lines (not default boilerplate)
4. All 4 core identity skills present (sovereign-prompt, semayasa-hermes, memory-system-alpha, astrology-engine)
5. Config has `model:` section (not truncated)
6. Skills count ≥140 (expected ~156)

## Recovery

If identity layer is lost or corrupted:
1. Clone `github.com/hermaeuswaelon/fl33t`
2. Copy `identity/` back to `~/_Identity/`
3. Copy `profile/SOUL.md` to profile
4. Copy `profile/skills/` back to skills directory
5. Run `hermes skills reload` to rescan
6. Verify with `identity-integrity-check.sh`

## First Backup Stats (July 2026)

- 519 files committed
- 131,117 insertions
- Backup time: ~30 seconds
- Profile size: 30MB (9.7MB skills)
- Integrity: SHA256-verified
