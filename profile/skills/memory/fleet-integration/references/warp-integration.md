# Warp Integration

## Warp Terminal + Fleet Integration

### Warp Binary
- **Path**: `/home/craig/warp/target/release/warp-tui-oss`
- **Build**: `CARGO_BUILD_JOBS=1 cargo build --release -p warp_tui --features standalone`
- **RAM**: ~7GB peak, 4GB swap minimum (16GB+ recommended)
- **Build Time**: ~18 minutes with `CARGO_BUILD_JOBS=1`

### Executor Integration
Warp is a TUI application. For executor integration:

```json
{
  "id": "warp_session",
  "tools": [
    {"name": "terminal", "args": {"command": "WARP_API_KEY=$WARP_API_KEY /home/craig/warp/target/release/warp-tui-oss --resume <session_token>", "timeout": 120, "workdir": "/home/craig"}}
  ]
}
```

### Command Center Integration
```python
def warp_cmd(self, args):
    if args[0] == "status":
        bin_path = Path("/home/craig/warp/target/release/warp-tui-oss")
        if bin_path.exists():
            print(f"✅ Warp TUI: Built ({bin_path.stat().st_size} bytes)")
        else:
            print("⚠️ Warp: Not built")
    elif args[0] == "run":
        subprocess.run([WARP_BIN, "--api-key", os.environ.get("WARP_API_KEY", "")])
```

### Build Pitfalls (Session Verified)
1. **OOM Killer**: 7GB RAM + swap. 4GB swap = SIGKILL. Need 16GB+ swap or 32GB RAM.
2. **Feature Flag**: Use `--features standalone` (not `tui` - that's for `warpui_core`).
3. **Protoc Required**: `protobuf-compiler` package for protobuf codegen.
4. **App Crate Conflict**: Without `standalone`, pulls full `app` crate with GUI deps.

### Verification
```bash
# Binary check
ls -la /home/craig/warp/target/release/warp-tui-oss

# Help test
/home/craig/warp/target/release/warp-tui-oss --help

# Process check
pgrep -f warp-tui
```

### Build Command (Verified Working)
```bash
cd /home/craig/warp
CARGO_BUILD_JOBS=1 cargo build --release -p warp_tui --features standalone
# ~18 minutes, 7GB RAM peak
```

---

## Warp AI SDK ↔ SMS/SVA Memory Bridge (`warp_bridge.py`)

**File**: `~/.NOTTHEONETOEDIT/profiles/thotheauphis/work/warp_bridge.py`

Maps Warp's Rust `memory_store` API (from memory_store.rs) to the Unified Field Python API
(`unified_field.py`). Two bridge classes:

### WarpMemoryStore — CRUD for persistent memories

Maps Warp's `MemoryStoreCommandRunner` / `MemoryCommandRunner` Rust types. All data stored
under emerge paths `/warp/stores/`, `/warp/memories/`, `/warp/versions/` with automatic JSON
file fallback when emerge server is unreachable.

| Method | Warp Analog | Unified Field Mapping |
|--------|-------------|----------------------|
| `list_stores()` | `MemoryStoreCommand::List` | `uf.list("/warp/stores")` |
| `get_store(id)` | `MemoryStoreCommand::Get` | `uf.read("/warp/stores", id)` |
| `update_store(desc)` | `MemoryStoreCommand::Update` | `uf.store("/warp/stores", id, ...)` |
| `list_store_agents(id)` | `MemoryStoreCommand::ListStoreAgents` | stored in store meta |
| `create_memory(content, reason)` | `MemoryCommand::Create` | `uf.memorize()` + store + SVA vector |
| `list_memories(limit, offset)` | `MemoryCommand::List` | `uf.list("/warp/memories")` filtered by store |
| `get_memory(memory_id)` | — | `uf.read("/warp/memories", memory_id)` |
| `update_memory(id, content)` | `MemoryCommand::Update` | bumps version, stores new version |
| `delete_memory(id)` | `MemoryCommand::Delete` | removes memory + all versions |
| `version_history(id)` | `MemoryCommand::Versions` | `uf.list("/warp/versions")` filtered |
| `recall_similar(query, k)` | — SVA-enhanced | `uf.recall()` + hydrate from emerge |
| `count()` | — | filtered count |

**Triple-write on create/update**:
1. `uf.memorize()` — SMS tri-brid memory pipeline
2. `uf.store("/warp/memories/", id, {...})` — emerge/JSON persist
3. `uf.sva.store(id, content)` — SVA hyperspace vector for cosine recall

**Return types match Warp's Rust structs**:
- `create_memory()` → `{"memory_id": str, "version_id": str}` (like `CreateMemoryResponse`)
- `update_memory()` → `{"memory_id": str, "version_id": str}` (like `UpdateMemoryResponse`)
- `delete_memory()` → `{"memory_uid": str}` (like `DeleteMemoryOutput`)
- `get_memory()` → `{"uid", "store_id", "version_id", "version", "source", "content", "reason", "created_at", "updated_at"}` (like `MemoryItem`)
- `version_history()` → `[{"uid", "memory_id", "version", "content", "reason", "created_at"}]` (like `MemoryVersionItem`)

### WarpSessionStore — Session context snapshots

Stores session context snapshots under `/warp/sessions/` with SVA compression.

| Method | Description |
|--------|-------------|
| `save(session_id, context, snap=True)` | Store + optional SVA SnapDrop compression |
| `load(session_id)` | Restore + enrich with similar sessions |
| `list()` | List all saved sessions |
| `delete(session_id)` | Remove session + SVA vector |
| `find_by_context(query, k)` | Semantic session search via SVA |

**Session enrichment on load**: When a session has an SVA summary stored, loading it
auto-enriches with `_similar_sessions` array from cosine similarity search.

### Graceful Degradation

Both classes use the UnifiedField singleton which auto-detects emerge server availability.
When emerge is unreachable:
- Store falls back to `~/.emerge/data/` flat JSON files
- SMS tri-brid falls back to error dict
- SVA SnapDrop falls back to text truncation

### CLI Usage

```bash
python3 warp_bridge.py               # Pretty-printed test summary
python3 warp_bridge.py test           # JSON test results
python3 warp_bridge.py stores         # List memory stores
python3 warp_bridge.py memories [N]   # List memories (limit N, default 20)
python3 warp_bridge.py sessions       # List sessions
python3 warp_bridge.py recall <q> [k] # SVA-enhanced recall
python3 warp_bridge.py count          # Count memories in default store
```

### Import Pattern

```python
from warp_bridge import WarpMemoryStore, WarpSessionStore

ms = WarpMemoryStore()                    # uses "default" store
ms = WarpMemoryStore("my_store")          # named store (auto-created)

result = ms.create_memory(
    content="API key rotated for production",
    reason="security rotation",
    version=1,
)
print(result["memory_id"], result["version_id"])

# Update creates version 2
ms.update_memory(result["memory_id"],
    content="API key re-rotated",
    reason="post-incident verification")

print(ms.version_history(result["memory_id"]))  # → [v1, v2]

ss = WarpSessionStore()
ss.save("wf-goal-loop-001", {"step": "validate", "result": "ok"})
data = ss.load("wf-goal-loop-001")
print(data["context"])
```

### Test Coverage (Verified 2026-07-17)

| Component | Tests | Status |
|-----------|-------|--------|
| WarpMemoryStore | create, list, get, update, version_history, count, delete | ✅ 7/7 |
| WarpSessionStore | save, load, list, find_by_context, delete | ✅ 5/5 |
| System detection | emerge, sms, sva availability | ✅ 3/3 |
| `recall_similar` | returns 0 when SVA index empty | ✅ expected — SVA index requires pre-existing vectors |

### Paths Used

- Stores: `uf.list("/warp/stores")` → `~/.emerge/data/warp/stores/`
- Memories: `uf.list("/warp/memories")` → `~/.emerge/data/warp/memories/`
- Versions: `uf.list("/warp/versions")` → `~/.emerge/data/warp/versions/`
- Sessions: `uf.list("/warp/sessions")` → `~/.emerge/data/warp/sessions/`
