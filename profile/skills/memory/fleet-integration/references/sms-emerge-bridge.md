# SMS ↔ Emerge Bridge Protocol

## Purpose
Bridge the Sovereign Memory System (SMS) ZODB vector store with EmergeFS distributed object filesystem so tri-brid memory vectors persist across the fleet and are queryable via Emerge.

## Key Constraint
- **SMS venv**: Python 3.11, numpy 2.3.5, ZODB 6.3
- **Emerge client**: System Python 3.13, **no numpy import** (uses native lists)
- **Bridge**: stdout hex-encoded pickles from SMS venv → stdin for system Python emerge client

## Protocol

### 1. Extract Vectors from SMS ZODB (SMS venv)
```bash
~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv/bin/python -c "
import ZODB, ZODB.FileStorage, pickle
fs = ZODB.FileStorage.FileStorage('/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/store/vsa_vectors.fs')
db = ZODB.DB(fs)
conn = db.open()
root = conn.root()
vectors = root.get('vectors', {})
for k, v in vectors.items():
    vec = pickle.loads(v)
    print(f'{k}|{pickle.dumps(vec).hex()}')
conn.close(); db.close(); fs.close()
"
```

Output format: `key|hex_pickled_numpy_array` (one per line)

### 2. Store on Emerge (system Python)
```bash
python3.13 -c "
from emerge.core.client import Z0RPCClient as Client
import json, pickle, sys
c = Client('localhost', '54242')  # Use node's RPC port from netstat
c.mkdir('/sms_vectors')
for line in sys.stdin:
    k, hexdata = line.strip().split('|', 1)
    vec = pickle.loads(bytes.fromhex(hexdata))
    c.store('/sms_vectors', k, json.dumps({'vector': vec.tolist(), 'shape': list(vec.shape)}))
"
```

### 3. Query from Emerge
```bash
emerge -h localhost:54242 cat /sms_vectors/state_latest
# Returns JSON: {"vector": [...], "shape": [256]}
```

## Integration Points

### Cron Integration
Add to `fleet_integration.py`:
```python
def sync_sms_to_emerge() -> Dict[str, Any]:
    """Periodic sync of SMS vectors to EmergeFS."""
    import subprocess
    # Run SMS extraction
    sms_cmd = [
        '/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv/bin/python',
        '-c', EXTRACT_SCRIPT
    ]
    result = subprocess.run(sms_cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return {"error": result.stderr}
    
    # Pipe to emerge client
    emerge_cmd = ['python3.13', '-c', STORE_SCRIPT]
    result = subprocess.run(emerge_cmd, input=result.stdout, capture_output=True, text=True, timeout=60)
    return {"synced": result.returncode == 0, "stderr": result.stderr}
```

### Emerge Node Port Discovery
The emerge node's RPC port is dynamic. Discover via:
```bash
netstat -tlnp | grep python3.13 | grep :5[0-9][0-9][0-9]
# Or check emerge node startup logs
```

Default broker: `5558`, Node RPC: varies (e.g., `54242`)

## Data Schema on Emerge
```
/sms_vectors/
  state_latest          → {"vector": [float...], "shape": [dim]}
  msg_0                 → {"vector": [float...], "shape": [dim]}
  msg_1                 → {"vector": [float...], "shape": [dim]}
  ...
```

## Verification
```bash
# Check vectors exist on emerge
emerge -h localhost:54242 ls /sms_vectors

# Check vector count matches SMS
sms status  # shows vectors: N
emerge -h localhost:54242 ls /sms_vectors | wc -l  # should match N+1 (dir entry)
```

## Troubleshooting
- **Port mismatch**: Emerge node RPC port changes on restart. Update bridge script or use `emerge.ini` with dynamic port discovery.
- **Pickle version**: Both ends use same Python major version (3.11 vs 3.13) — use `protocol=4` in `pickle.dumps()` for cross-version safety.
- **Large vectors**: 1024-dim vectors ≈ 8KB pickled. Batch if >100 vectors.
- **ZODB lock**: SMS must not be actively writing during extract. Run during SMS idle period (between auto-persist intervals).

## Related Skills
- `thotheauphis-sms-memory` — Source ZODB store
- `thotheauphis-sms-persistence` — ZODB persistence bridge
- `fleet-integration` — Fleet-level EmergeFS operations