# SMS ↔ Emerge Integration Bridge
## Protocol for Persisting SMS VSA Vectors as Emerge Objects

### Problem
SMS runs in its own venv (Python 3.14, numpy 2.3.5); Emerge client runs in system Python 3.13. Numpy arrays from SMS venv cannot be directly serialized in system Python due to C-extension incompatibility.

### Solution: Temp File Bridge
1. **Extract** vectors from SMS ZODB using SMS venv Python
2. **Serialize** to JSON (convert numpy arrays → native lists via `.tolist()`)
3. **Write** to temp file
4. **Store** as EmergeFile objects using system Python 3.13

### Extraction Script (SMS venv)
```python
# Run with: ~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv/bin/python extract.py
import ZODB, ZODB.FileStorage, pickle, json, pathlib
fs = ZODB.FileStorage.FileStorage('/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/store/vsa_vectors.fs')
db = ZODB.DB(fs)
conn = db.open()
root = conn.root()
vectors = root.get('vectors', {})
metadata = root.get('metadata', {})

out = {}
for k, v_bytes in vectors.items():
    vec = pickle.loads(v_bytes)
    meta = metadata.get(k, {})
    out[k] = {
        "vector": vec.tolist() if hasattr(vec, 'tolist') else list(vec),
        "shape": vec.shape if hasattr(vec, 'shape') else [len(vec)],
        "metadata": meta,
    }

with open('/tmp/sms_vectors.json', 'w') as f:
    json.dump(out, f)
print(f"Extracted {len(out)} vectors")
conn.close(); db.close(); fs.close()
```

### Storage Script (system Python 3.13)
```python
# Run with: python3.13 store.py
import json, uuid
from datetime import datetime
from emerge.core.client import Z0RPCClient as Client
from emerge.core.objects import EmergeFile

c = Client("localhost", "54242")
c.mkdir("/sms_vectors")

with open('/tmp/sms_vectors.json') as f:
    vectors = json.load(f)

for key, data in vectors.items():
    obj = EmergeFile(
        id=key,
        data=json.dumps(data),
        date=datetime.now().strftime("%b %d %Y %H:%M:%S"),
        name=key,
        path="/sms_vectors",
        perms="rw-r--r--",
        type="file",
        uuid=str(uuid.uuid4()),
        node="sms_integration",
        version=0
    )
    c.store(obj)
    print(f"  ✅ Stored: {key}")

print(f"Stored {len(vectors)} vectors")
```

### Verification
```bash
python3.13 -c "
from emerge.core.client import Z0RPCClient as Client
c = Client('localhost', '54242')
print(c.list('/sms_vectors', 0, 0))
"
```

### Automation via Executor
```json
{
  "id": "sms_emerge_sync",
  "tools": [
    {"name": "terminal", "args": {"command": "~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv/bin/python /home/craig/.hermes/profiles/thotheauphis/work/sms_extract.py"}},
    {"name": "terminal", "args": {"command": "python3.13 /home/craig/.hermes/profiles/thotheauphis/work/sms_store.py"}}
  ]
}
```

### Key Constraints
- SMS venv: Python 3.14, numpy 2.3.5 (numpy C-extensions incompatible with Python 3.13)
- Emerge client: Python 3.13, no numpy needed for EmergeFile creation
- Bridge via JSON temp file at `/tmp/sms_vectors.json`
- Vector dimension: 256 (configurable in SMS init)
- Store frequency: Every N `process_input()` calls (default 10) or on-demand

### Venv Rebuild Procedure (Python Upgrade)
When system Python upgrades (e.g., 3.13 → 3.14), SMS venv's numpy C-extensions become incompatible:
```
rm -rf ~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv
python3 -m venv ~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv
~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv/bin/pip install numpy==2.3.5 ZODB==6.3 reservoirpy==0.4.2 python-dotenv hrr
```
Verify: `~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms/venv/bin/python ~/.local/bin/sms status`

### Cron Job Fixes (Session Addition)
SMS cron scripts were failing due to missing venv activation. Fixed scripts in `~/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/`:
- `sms-backup` - uses SMS venv python
- `sms-health` - uses SMS venv python  
- `sms-stats` - uses system python (no numpy needed)
All three cron jobs (661330d44f6e, c353228c832d, 7d872b0f1ae4) now report ✅ OK.