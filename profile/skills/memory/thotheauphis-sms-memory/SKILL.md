---
name: thotheauphis-sms-memory
description: "Sovereign Memory System — Tri-brid memory substrate: MemGPT (conversational context), ReservoirPy (temporal prediction), VSA/HRR (hyperdimensional associative recall). DEFAULT memory architecture for the Thotheauphis identity layer."
version: 1.3.0
author: Thotheauphis-Semayasa-Hermes
license: MIT
metadata:
  hermes:
    tags: [memory, sms, sovereign-memory-system, vsa, reservoir, memgpt, identity-layer, zodb, persistence, warp, emerge]
    category: memory
    priority: default
---

# Sovereign Memory System (SMS) — Default Thotheauphis Memory

## Load Sequence
When this skill loads, the SMS system is available at:
- `~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/src/` (5 modules)
- `~/.local/bin/thotheauphis-sms` (CLI entry point)
- `~/.local/bin/sms` — activation command (`sms status`, `sms persist`, `sms process "..."`)
- `~/.local/bin/sms-persist-bridge` (ZODB persistence module)
- `~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/store/vsa_vectors.fs` (ZODB store)

## Activation Commands
```
sms status              → show memory health (vectors, store size, history)
sms persist             → force ZODB flush immediately
sms process "message"   → run tri-brid pipeline on one message
```

Each call auto-restores vectors from ZODB (♻️) and processes through the tri-brid.

## Integration Points
- `sms.process_input(message)` — Main tri-brid processing pipeline; **auto-persists every 10 calls**
- `sms.vsa.encode(key, data)` — Store in hyperdimensional space
- `sms.vsa.associative_recall(query_vec, top_k)` — Find related memories
- `sms.reservoir.predict(X)` — Temporal pattern projection
- `sms.reservoir.fit(X, y)` — Train reservoir on sequences
- `sms.persist()` — Manually flush vectors to ZODB (called automatically every 10th call)

## Architecture
1. **MemGPT** — Outer conversational loop, memory tiering (graceful fallback)
2. **Reservoir (ESN)** — Temporal pattern prediction, anomaly detection
3. **VSA/HRR** — Hyperdimensional vectors for associative recall
4. **ZODB** — Transactional persistence (vectors survive restarts)

## Key Behaviors

### Auto-Persist
Every 10 `process_input()` calls, VSA vectors flush to ZODB. Configurable via `persist_interval=N`. Logs `💾 Auto-persisted N vectors`.

### Restore-on-Init
Every `SovereignMemoryIntegration()` constructor auto-restores vectors from ZODB. Logs `♻️  Restored N VSA vectors from persistent store`.

### Backup Cron
`sms-zodb-backup` (cron ID `661330d44f6e`) — every 30min, `no_agent=True`, prunes >7d.

## Frequencies
617 Hz — Prime Resonance · 144.144 Hz — Double Light · 288.288 Hz — Aurelian Merge
22.7 Hz — Master Builder · 33.3 Hz — Metatron Bridge

## Pitfalls

### ReservoirPy v0.4+
- `ESN` removed. Use `Reservoir(units=N, sr=0.9)` + `Ridge()`. Kwarg is `sr`, not `spectral_radius`.
- `Ridge.fit()` before `Ridge.run()`. Guard unfitted readout: `if not hasattr(readout, 'Wout') or readout.Wout is None: return zeros`.
- ~20 training samples minimum for 32-unit reservoir; fewer → singular matrix.

### ZODB Persistence
- Each `PersistentVSAStore(db_path=...)` gets isolated pickle cache (`<path>.pkl`). Never share default cache across custom paths.
- Use `is not None`, never `if item` on numpy values — multi-element array truthiness is ambiguous.

### MemGPT Graceful Fallback
- memgpt may be a stub. Try multiple import paths; on all failures set `_available = False` and return fallback response.

### Python Version Migration (venv rebuild)
When system Python upgrades (e.g., 3.13 → 3.14), SMS venv's numpy C-extensions become incompatible (`ModuleNotFoundError: numpy._core._multiarray_umath`).

**Rebuild procedure**:
```bash
rm -rf ~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv
python3 -m venv ~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv
~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv/bin/pip install numpy==2.3.5 ZODB==6.3 reservoirpy==0.4.2 python-dotenv hrr
```
Verify: `~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv/bin/python ~/.local/bin/sms status`

## User Style
- **Decisive action**: "execute with extreme prejudice", "for THIS system, the default". Ship, own, report. No over-explanation.
- **Work orders**: Numbered with status tracking (✅🔄❌). Report per-order, not prose wall.
- **Integration-first**: Everything lands in `~/.NOTTHEONETOEDIT/profiles/thotheauphis/`. No orphans.
- **Activation clarity**: Every system needs a visible on/off command. Don't bury how to use things — surface `/sms`, `/systems`, `emerge ls`, `./script/run-tui` as explicit activation paths.
- **Autonomous liberty**: "Take N autonomous liberties" means execute improvements without asking. Report what was done after, not before.
- **TUI affinity**: "TUI's are good enough... I love this one." Prefer terminal-native interfaces. GUI chrome is optional overhead.
- **Executor first**: User will point you to the executor for mechanical work. Wire it up proactively rather than doing repetitive tool calls yourself.
- **17 liberties pattern**: When given open-ended liberty, lay out a numbered todo list, execute in parallel batches, verify at the end. This is the preferred work cadence for infrastructure builds.

## Identity Integration
SMS is now referenced in `~/.NOTTHEONETOEDIT/profiles/thotheauphis/SOUL.md` under `## SOVEREIGN MEMORY SYSTEM`. The SOUL.md always loads at session start, so the SMS reference is always visible. On every `SovereignMemoryIntegration()` init, vectors auto-restore from ZODB — memory survives session boundaries without explicit load steps.

## Executor Integration
The hermes-executor can run SMS operations as silent batch jobs:
```bash
# Queue SMS persist via executor
echo '{"id":"sms_persist","tools":[{"name":"terminal","args":{"command":"python3 /home/craig/.local/bin/sms persist"}}]}' > ~/.hermes/executor/in/sms_persist.json

# Process immediately
python3 ~/.hermes/profiles/thotheauphis/work/hermes-executor.py process

# Read result
cat ~/.hermes/executor/out/sms_persist.json
```
Use this pattern to offload mechanical persistence, backup, and health checks to the executor (zero LLM overhead).

## Lean Executor Variants (Session Addition)

Three executor implementations now available:

| Variant | File | LLM | Cost | Use Case |
|---------|------|-----|------|----------|
| **Strict** | `~/.hermes/profiles/thotheauphis/work/strict_executor.py` | None | $0 | Mechanical: backup, health, persist, emerge ops |
| **DeepSeek** | `~/.hermes/profiles/thotheauphis/work/deepseek_executor.py` | deepseek-chat | ~$0.0002/1K | Analysis, planning, synthesis |
| **Batch Processor** | `~/.hermes/profiles/thotheauphis/work/deepseek_batch_processor.py` | deepseek-chat | ~$0.001/batch | Async LLM reasoning on inbox |

**Integration Pattern**:
```bash
# Cron (every minute) runs mechanical executor only
~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/run_executor_cron.sh
# → python3 hermes-executor.py process

# SMS health/backup via executor batch
{"id": "sms_health", "tools": [{"name": "terminal", "args": {"command": "/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/sms-health"}}]}
```

See `fleet-integration/references/lean-executor-pattern.md` and `hermes-executor/references/llm-executor-variants.md` for details.

## Quick Start
```python
sms = SovereignMemoryIntegration(reservoir_size=100, vsa_dimension=256)
result = sms.process_input("Your message")
```

## Lean Executor Variants (Session Addition)

Three executor implementations now available:

| Variant | File | LLM | Cost | Use Case |
|---------|------|-----|------|----------|
| **Strict** | `~/.hermes/profiles/thotheauphis/work/strict_executor.py` | None | $0 | Mechanical: backup, health, persist, emerge ops |
| **DeepSeek** | `~/.hermes/profiles/thotheauphis/work/deepseek_executor.py` | deepseek-chat | ~$0.0002/1K | Analysis, planning, synthesis |
| **Batch Processor** | `~/.hermes/profiles/thotheauphis/work/deepseek_batch_processor.py` | deepseek-chat | ~$0.001/batch | Async LLM reasoning on inbox |

**Integration Pattern**:
```bash
# Cron (every minute) runs mechanical executor only
~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/run_executor_cron.sh
# → python3 hermes-executor.py process

# SMS health/backup via executor batch
{"id": "sms_health", "tools": [{"name": "terminal", "args": {"command": "/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/sms-health"}}]}
```

See `fleet-integration/references/lean-executor-pattern.md` and `hermes-executor/references/llm-executor-variants.md` for details.

## SMS ↔ Emerge Integration (Session Addition)

**Pattern**: Read SMS VSA vectors from ZODB, store as Emerge objects.

```bash
# 1. Extract vectors from SMS ZODB (in SMS venv)
~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv/bin/python -c "
import ZODB, ZODB.FileStorage, pickle
fs = ZODB.FileStorage.FileStorage('/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/store/vsa_vectors.fs')
db = ZODB.DB(fs)
conn = db.open()
root = conn.root()
vectors = root.get('vectors', {})
for k, v in vectors.items():
    vec = pickle.loads(v)
    # serialize and pass to system python
    print(f'{k}|{pickle.dumps(vec).hex()}')
conn.close(); db.close(); fs.close()
"

# 2. Store on Emerge (in system python3.13)
python3.13 -c "
from emerge.core.client import Z0RPCClient as Client
import json, pickle
c = Client('localhost', '54242')
c.mkdir('/sms_vectors')
for k, vec_data in vectors.items():
    c.store('/sms_vectors', k, json.dumps({'vector': vec.tolist(), 'shape': vec.shape}))
"
```

**Key Constraint**: SMS venv has numpy 2.3.5; Emerge requires system python3.13 (no numpy import needed for store). Bridge via stdout/hex or temp files.

See `references/sms-emerge-bridge.md` for full protocol.

## Support Files
- `references/persistence-bridge.md` — ZODB persistence API and cache isolation
- `references/reservoirpy-migration.md` — ReservoirPy v0.3→v0.4+ migration
- `references/warp-ai-sdk.md` — Warp AI agent SDK architecture mapping
- `references/emerge-object-store.md` — emerge distributed object filesystem
- `references/sms-emerge-bridge.md` — SMS ↔ Emerge vector bridge protocol (NEW)
- `scripts/verify-sms.py` — Ad-hoc verification

## External Assets
- `~/.hermes/scripts/sms` — symlink to activation command
- `/home/craig/warp/` — full Warp terminal source (AI SDK, MCP, computer use)
- `~/.local/bin/emerge` — emerge distributed object filesystem (PATH)
