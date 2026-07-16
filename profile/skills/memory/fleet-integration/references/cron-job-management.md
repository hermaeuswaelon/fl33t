# Cron Job Management Reference
## Fleet Integration Skill

### Common Cron Job Issues & Fixes

#### 1. "Script not found" errors
**Problem**: Cron job runs but reports "Script not found" even though script exists.
**Root Cause**: Cron jobs must reference scripts in `~/.hermes/scripts/` or `~/.NOTTHEONETOEDIT/scripts/` using relative names only.
**Fix**: 
1. Place script in `~/.hermes/scripts/` (symlink from work dir)
2. Update cron job to reference just the filename: `hermes-executor.py process` (not full path)
3. Ensure script has shebang and is executable

#### 2. Working directory issues
**Problem**: Script runs but fails due to relative imports or missing config.
**Root Cause**: Cron jobs don't inherit the same working directory as interactive shell.
**Fix**: Use wrapper script that sets PYTHONPATH, PATH, HOME and cd's to work dir:
```bash
#!/bin/bash
export PYTHONPATH="/home/craig/.local/lib/python3.13/site-packages:$PYTHONPATH"
export PATH="/home/craig/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export HOME="/home/craig"
cd /home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/work
python3 hermes-executor.py process 2>&1
```

#### 3. Module import errors
**Problem**: `ModuleNotFoundError` for local modules.
**Root Cause**: Python path doesn't include work directory.
**Fix**: Wrapper script sets PYTHONPATH, or use `sys.path.insert(0, str(WORK))` in script.

### Current Cron Jobs (as of 2026-07-16)

| Job ID | Name | Schedule | Script | Last Status |
|--------|------|----------|--------|-------------|
| 287317d6233e | hermes-executor | * * * * * | run_executor_cron.sh | ✅ OK |
| b7798d50a076 | auto-tac-compress | */30 * * * * | auto-tac-compress.py | ✅ OK |
| 7a49292bad86 | fleet-health-check | every 5m | fleet_integration.py health | ✅ Scheduled |
| a38cb78ba6b3 | fleet-registration | 0 0 * * * | fleet_integration.py register | ✅ Scheduled |
| 229eeac06584 | fl33t-identity-backup | 0 9 * * * | fl33t-backup.sh | ✅ OK |
| 84b387e39c9d | TAC auto-curation | 0 * * * * | tac-curation.sh | ⚠️ Error |

### Wrapper Script Pattern

Always use a wrapper script for cron jobs:
1. Set environment (PYTHONPATH, PATH, HOME)
2. Change to working directory
3. Call the actual script
4. Handle errors gracefully

Example: `run_executor_cron.sh`
```bash
#!/bin/bash
export PYTHONPATH="/home/craig/.local/lib/python3.13/site-packages:$PYTHONPATH"
export PATH="/home/craig/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export HOME="/home/craig"
cd /home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/work
python3 hermes-executor.py process 2>&1
```

### Cron Job Management Commands

```bash
# List all cron jobs
cronjob action=list

# Create new job (no_agent=true for zero-LLM scripts)
cronjob action=create name="my-job" script="my-script.py" schedule="*/5 * * * *" no_agent=true

# Update script
cronjob action=update job_id="xxx" script="new-script.py"

# Run job immediately
cronjob action=run job_id="xxx"

# Pause/resume
cronjob action=pause job_id="xxx"
cronjob action=resume job_id="xxx"

# Remove job
cronjob action=remove job_id="xxx"
```

### Debugging Failed Cron Jobs

1. Check `last_status` and `last_run_at` in `cronjob action=list`
2. Run script manually: `cd /workdir && python3 script.py`
3. Check wrapper script exists and is executable
4. Verify PYTHONPATH and PATH in wrapper
5. Check cron job references relative script name only