# Deployment State — Session 2026-07-15

## What Was Built

### Memory Vault Integration
- `scripts/ares_memory.py` — Shared memory vault module (JSON-backed, TTL-based, auto-store by Alpha and Omega)
- `scripts/ares-watchdog.py` — Cron wrapper: system context → Omega → brief → vault
- Cron job `5f5421c6ca7b`: every 30min, system watchdog → continuity brief

### Memory Hub (Multi-Tier Router)
- `scripts/ares-memory-hub.py` — Unified CLI that routes by task type (T1 JSON vault, T2 Forge SQLite, T3 Session)
- Aliases: `ares-memory`, `ares-store`, `ares-get`, `ares-search`, `ares-route`, `ares-stats`
- Task routing: tool_output→T1, fact/brief/recon→T2, recall→T3

### Forge Vault (T2)
- `forge_vault.py` in forge-vault skill already existed with real schema (memories table)
- 141 entries across 11 categories in the live DB
- `forge-memory` CLI wrapper updated to point to correct location

### Pentagi
- Docker compose stack at `/home/craig/arsenal/pentagi/`
- Running: pentagi (8443), pgvector (5433), scraper (9444), pgexporter (9187)
- LLM provider: OpenRouter (OpenAI-compatible endpoint)
- Port conflicts on 5432 (system postgres) and 9443 resolved via .env overrides

## API Keys Stored In
- `~/.bashrc` — exports for OPENROUTER_API_KEY, TOGETHER_API_KEY, PYTHONPATH
- `~/.NOTTHEONETOEDIT/skills/ares/ares-nemotron-together-dual-offload/scripts/ares-offload.sh` — aliases + PYTHONPATH

## Skill Updates This Session
- `ares-nemotron-together-dual-offload`: version 3.0.0
  - Fixed TogetherAI model name (removed deprecated `-Free` suffix)
  - Fixed TogetherAI API auth header in docs
  - Replaced deprecated Mixtral-8x7B fallback with Qwen2.5-7B-Instruct-Turbo
  - Added scripts/ (offload, continuity, memory vault, watchdog)
  - Updated deployment docs with alias sourcing
- `ares-forge-vault`: version 2.1.0
  - Fixed Python API examples to match real `forge_vault.py` code
  - Added `references/memory-routing.md` — multi-tier routing documentation
  - Added Multi-Tier Routing section to SKILL.md
