# Hermes /compress Architecture

From `~/checkctx.txt` — how the system-level `/compress` and `/compact` commands work.

## Context Window Limits (DeepSeek)

| Model | Window | Effective UI | Notes |
|-------|--------|-------------|-------|
| V3/R1 | 128K | ~64K (Web) | Safe ceiling for reliability |
| V4-Pro | 1M | 1M (API) | Retrieval degrades: 94%@128K → 66%@1M |
| V4-Flash | 1M | 1M (API) | 6x faster than V3.2 at 1M; 89%@128K |

API is stateless — all history resent each request.

## Summarization Middleware (LangChain Deep Agents)

Trigger-based compression:

1. **Trigger** at ~85% utilization (~109K for 128K window)
2. **Cutoff**: retain ~10% (~13K tokens) as recent verbatim context
3. **Summarize**: prefix → single HumanMessage via separate LLM call
4. **Offload**: full history written to `{artifacts_root}/conversation_history/{thread_id}.md`
5. **Recovery**: summary contains file path; agent reads via file tools on demand

Key: Deep Agents offloads to disk (not deletion). Stock LangChain deletes.

## Checkpointing (Hermes Agent)

Dual-layer persistence:
- **Session deltas** (SQLite) — per-message JSON patches
- **Session checkpoints** (SQLite) — periodic full snapshots
- Recovery: load checkpoint → replay deltas → validate → resume

## Filesystem Checkpoint Manager (v2)

- Shared bare git store at `~/.hermes/checkpoints/store/`
- Auto-snapshot every turn before `write_file`/`patch`/`terminal --dangerous`
- Prune: 7 day retention, 500MB cap
- Commands: `hermes checkpoints list|show|rollback|prune|config`

## /compress-tac Integration

`/compress-tac` captures agent **working context** (goal, systems, subgoals) in Chinese. The system-level `/compress` handles conversation history summarization. They're complementary: one captures operational state, the other compresses conversation history.

## References

- `~/checkctx.txt` — Full research report: Agent Context Compression & Checkpointing Architecture
- `~/stealth.txt` — NHI-related; not directly compression but referenced alongside checkctx
