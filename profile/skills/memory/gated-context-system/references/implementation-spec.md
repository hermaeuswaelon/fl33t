# Gated Context System — Implementation Spec

Built July 16, 2026. 24/24 verification tests pass.

## Module Specs

### context_gate.py — GatedStore

**Singleton** via `__new__` + class var `_index`. Schema-tolerant `_load_index()` skips stale entries with missing fields.

```
Storage path: /tmp/sva/mem_<sha256(content)[:16]>.log
Index:        /tmp/sva/gate_index.json
```

Key methods:
- `injectable(content, ttl=3600)` → `{ptr, bytes, preview, written_at, ttl}` — stores and returns lightweight pointer
- `peek(ptr, offset=0, limit=2000)` → `str | None` — re-fetch with byte offset
- `status()` → `{entries, total_bytes, max_bytes, usage_pct}`
- `clear_expired()` — TTL eviction
- LRU eviction at `MAX_STORE_BYTES = 500MB` cap

**GatePointer fields:**
`ptr, written_at, bytes, preview, ttl, turns, access_count, accessed_at`

**Serialization:** `to_dict()` writes `ptr, bytes, preview, turns, access_count, written_at, ttl`. `_load_index` catches `TypeError` to skip malformed entries from prior schemas — handles forward/backward compat.

### dynamic_tool_filter.py — DynamicFilter / CMTF

**ToolContract:** `{name, prerequisites, effects, group, weight, description, always_available}`

14 default contracts including:
- `peek_ptr` (requires `has_ptr`, group `context_gate`)
- `terminal` (no prereqs, group `executor`)
- `read_file`, `write_file`, `patch` (filesystem group)
- `web_search`, `web_extract` (research group)
- `browser_*` (browser group, requires `browser_loaded`)

`filter(current_state, goal, available_groups)` returns tool names sorted by weight descending. Precondition check: all prerequisites in `current_state`.

`suggest_groups(intent)` maps keywords (file/edit/write/run/compile/browser/ptr/etc.) to tool groups.

### snap_n_drop.py — SnapDrop / SVA

**Pure Python HDC** — no numpy, no external deps. Uses SHA-256 seeded deterministic pseudo-random vectors.

- Dimension: 1024 (float64)
- Vectors stored as packed binary: `/tmp/sva/vectors/<key>.vec` (`struct.pack("1024d", *vec)`, 8192 bytes each)
- Cosine similarity: `dot / (mag_a * mag_b + 1e-12)`

**Key methods:**
- `snap(conversation_text, max_tokens=2000)` → markdown summary with Objective, State, Active Pointers
- `bind(text)` → 1024-D vector (bundle of chunk-hashes)
- `store(vector, summary)` → hex key (stores index + binary .vec)
- `recall(query, k=3)` → `[{key, similarity, summary, created_at}]`
- `get_context(key)` → full summary string

**SVAEntry fields:** `key, summary, vector, created_at, turn_count, access_count`
- `to_dict()` omits vector (stored separately as binary)
- `save_vector()` / `load_vector()` for binary I/O
- Schema-tolerant load (`try/except TypeError`)

## Fleet Integration Hooks

Added to `fleet/modules/fleet_integration.py`:

```python
gate_tool_output(output, ttl=3600) → dict  # store → pointer
gate_peek(ptr, offset=0, limit=2000) → str | None
gate_filter_tools(state, goal=None, groups=None) → list[str]
gate_snap_drop(conversation_text) → dict     # snap → SVA key
gate_recall(query, k=3) → list[dict]
gate_status() → dict                         # all systems combined
```

Auto-detected in `fleet_health()` under `systems.context_gate`.

## Hermes Plugin

Path: `$HERMES_HOME/plugins/gated_context/`

**plugin.yaml:**
```yaml
kind: standalone
platforms: [linux]
provides_tools: [peek_ptr, gate_status, gate_injectable, recall]
hooks: []
```

**__init__.py** lazily imports fleet modules (`~/projects/aethelgard/fleet/modules/`). Registers 4 tools via `ctx.register_tool(name, toolset="context_engine", ...)`. Toolset `context_engine` is already in global `platform_toolsets.cli`.

## Verification Protocol

Run in fresh state:
```bash
rm -f /tmp/sva/gate_index.json /tmp/sva/vectors/sva_index.json /tmp/sva/vectors/*.vec
cd ~/projects/aethelgard/fleet
python3 -c "
from modules.context_gate import GatedStore
from modules.dynamic_tool_filter import DynamicFilter
from modules.snap_n_drop import SnapDrop
from modules.fleet_integration import *
# ... 24 tests
"
```

Expected: 24/24 pass, 0 fails.

## Error Recovery

- **Stale index on schema change:** `_load_index()` catches `TypeError` and skips malformed entries. To clean manually: `rm /tmp/sva/gate_index.json /tmp/sva/vectors/sva_index.json`
- **Missing fleet modules:** Plugin lazily imports on first tool call. If `~/projects/aethelgard/fleet/` is missing, `peek_ptr` etc. return `{"error": ...}` instead of crashing Hermes.
- **Binary vector files missing:** `load_vector()` returns the empty list if `.vec` file doesn't exist — `cosine_sim` degrades to 0.0, re-store re-creates the file.
