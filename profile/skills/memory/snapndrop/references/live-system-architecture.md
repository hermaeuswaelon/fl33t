# Hermes Agent — Live System Architecture
Captured 2026-07-17 from config/cron/import analysis.

## Executor Chain (live)
```
cron (* * * * *) → run_executor_cron.sh → hermes-executor.py process
```
Runs every 60 seconds. Active day-to-day executor.
**Not wired**: executor_manager.py, executor_delegation.py, strict_executor.py

## Compression Chain (live)
```
cron (*/30 * * * *) → auto-tac-compress.py → active_compress.py → compress_alch.py
```
Runs every 30 minutes. Active compressor pipeline.
**Standalone, not wired**: hyper_compress.py, ctx_tight.py

## SMS→Emerge Pipeline
**All 5 files dead**: sms_to_emerge.py, sms_to_emerge_fixed.py, sms_to_emerge_final.py,
sms_emerge_integrate.py, sms_emerge_final.py. Zero imports, zero cron, zero skill hooks.

## System Integration
- **unified_field.py** has a cron checkpointer (every 4h) — the active integrator
- **agency_expansion_engine.py** — no cron, no imports, not wired
- **fleet_integration.py** — runs as `fleet_integration.py register` (daily) and
  `fleet_integration.py health` (every 5m) via cron. Active.

## Cron Jobs (12 total)
| Job | Schedule | Script | Status |
|-----|----------|--------|--------|
| hermes-executor | every minute | run_executor_cron.sh → hermes-executor.py process | ok |
| auto-tac-compress | */30 min | auto-tac-compress.py | error |
| TAC auto-curation | hourly | tac-curation.sh | error |
| fl33t-identity-backup | daily 9am | fl33t-backup.sh | ok |
| fleet-registration | daily midnight | fleet_integration.py register | error |
| fleet-health-check | every 5m | fleet_integration.py health | error |
| sms-zodb-backup | every 30m | sms-backup | ok |
| sms-health-check | every 120m | sms-health | ok |
| sms-stats-log | every 60m | sms-stats | ok |
| uf-system-checkpoint | every 240m | (runs unified_field.py) | error |

## Active Skills (from config.yaml default list)
thotheauphis-sovereign-prompt, thotheauphis-sms-memory, thotheauphis-sms-persistence,
thotheauphis-memory-system-alpha, thotheauphis-semayasa-hermes, ctx-curation,
ares-dual-offload, ares-omega-daemon, ares-rtacc, ares-rtacc-cli, ares-rtacc-engine,
hermes-executor, fleet-integration, compress-tac, ares-parameter-control,
ares-forge-vault, aethelgard-fleet-memory, ares-alpha-daemon, bromium-control

## Key Architecture Details (this user's Hermes build)
- **System prompt is cached/sent-once** — NOT resubmitted every turn
- **TUI footer gauge** tracks the messages array + cached system prompt against a 1M threshold
- The gauge measures `active = 1` messages array size, NOT cumulative `input_tokens`
- `--sovereign-prompt` replaces the ENTIRE system prompt (skills/tools/memory all bypassed)
