# Cron Job Wrapper Pattern for Hermes Executor
===============================================

## The Problem
Cron jobs run in a minimal environment. The hermes-executor.py script needs:
- Proper PYTHONPATH (for site-packages)
- Correct working directory
- PATH including ~/.local/bin
- HOME set correctly

## Solution: Wrapper Script Pattern

### Wrapper Script: `run_executor_cron.sh`
```bash
#!/bin/bash
# Cron wrapper for hermes-executor
# Ensures proper environment for cron execution

export PYTHONPATH="/home/craig/.local/lib/python3.13/site-packages:$PYTHONPATH"
export PATH="/home/craig/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export HOME="/home/craig"

cd /home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/work
python3 hermes-executor.py process 2>&1
```

### Cron Job Configuration
```bash
# Schedule: every minute
* * * * * /home/craig/.NOTTHEONETOEDIT/scripts/run_executor_cron.sh
```

Or via Hermes cronjob tool:
```bash
# Script must be in ~/.hermes/scripts/
# Cronjob references just the filename
cronjob action=create name="hermes-executor" script="run_executor_cron.sh" schedule="* * * * *" no_agent=true
```

## Key Points

1. **Script location**: Wrapper scripts must be in `~/.hermes/scripts/` (or `~/.NOTTHEONETOEDIT/scripts/`)
2. **Cronjob references**: Use just the filename, not full path
3. **Environment**: Always export PYTHONPATH, PATH, HOME explicitly
4. **Working directory**: cd to the work directory before running
5. **Error handling**: Redirect stderr to capture logs: `2>&1 | logger -t hermes-executor`

## Debugging Cron Failures

1. **Check last run**: `cronjob action=list` → look at `last_status` and `last_run_at`
2. **Run manually**: `bash /home/craig/.NOTTHEONETOEDIT/scripts/run_executor_cron.sh`
3. **Check wrapper exists**: `ls -la ~/.NOTTHEONETOEDIT/scripts/run_executor_cron.sh`
4. **Verify PYTHONPATH**: `python3 -c "import sys; print('\n'.join(sys.path))"`
5. **Check script is executable**: `chmod +x ~/.NOTTHEONETOEDIT/scripts/run_executor_cron.sh`

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Script not found | `Script not found: /path/to/script.sh` | Copy wrapper to `~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/` |
| Module not found | `ModuleNotFoundError: No module named '...'` | PYTHONPATH missing in wrapper |
| Permission denied | `Permission denied` | `chmod +x wrapper.sh` |
| Wrong directory | File not found errors | `cd /correct/workdir` in wrapper |

## Cronjob Management Commands

```bash
# List all jobs
cronjob action=list

# Create new cron job
cronjob action=create name="my-job" script="my-script.sh" schedule="* * * * *" no_agent=true

# Update script for existing job
cronjob action=update job_id="xxx" script="new-script.sh"

# Run job immediately (test)
cronjob action=run job_id="xxx"

# Pause/resume
cronjob action=pause job_id="xxx"
cronjob action=resume job_id="xxx"

# Remove job
cronjob action=remove job_id="xxx"
```

## Current Hermes Executor Cron Jobs

| Job ID | Name | Schedule | Script | Status |
|--------|------|----------|--------|--------|
| 287317d6233e | hermes-executor | * * * * * | run_executor_cron.sh | ✅ Running |
| b7798d50a076 | auto-tac-compress | */30 * * * * | auto-tac-compress.py | ✅ Running |
| a38cb78ba6b3 | fleet-registration | 0 0 * * * | fleet_integration.py register | ✅ Scheduled |
| 7a49292bad86 | fleet-health-check | every 5m | fleet_integration.py health | ✅ Scheduled |

## Wrapper Script Locations

- Primary: `/home/craig/.NOTTHEONETOEDIT/scripts/run_executor_cron.sh`
- Symlink: `/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/run_executor_cron.sh`
- Cronjob references: `run_executor_cron.sh` (just filename)

## Emergency Recovery

If cron stops working entirely:
```bash
# 1. Test wrapper manually
bash /home/craig/.NOTTHEONETOEDIT/scripts/run_executor_cron.sh

# 2. If works, check cron daemon
systemctl status cron

# 3. Restart cron if needed
sudo systemctl restart cron

# 4. Recreate cron job if corrupted
cronjob action=remove job_id="287317d6233e"
cronjob action=create name="hermes-executor" script="run_executor_cron.sh" schedule="* * * * *" no_agent=true
```