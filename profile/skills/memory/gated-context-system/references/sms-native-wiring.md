# Sovereign Memory System — Native Wiring Reference

## How SMS Becomes a Native Default

The SMS system is wired into Hermes at the **core code level**, not just as a skill.

### The Wiring Path

1. **Import-time activation**: When `tools/memory_tool.py` is imported, it attempts:
   ```python
   from thotheauphis_sms_memory.handler import sms_memory_handler
   ```
   If the SMS package is importable (installed), `_SMS_ACTIVE = True` and the memory handler is replaced with the SMS handler.

2. **Handler replacement** (memory_tool.py ~line 1153):
   ```python
   _memory_handler = lambda args, **kw: _sms_handler(
       action=args.get("action"),
       data=args.get("data"),
   )
   ```
   This means every `memory` tool call routes through SMS instead of the basic MemoryStore.

3. **MemoryStore as backing store**: Even with SMS active, the underlying VSA vectors persist at `memory/store/vsa_vectors.*`. SMS wraps the MemoryStore, it doesn't replace it.

4. **Skill auto-loading**: `thotheauphis-sms-memory` is in `skills.default` in the profile config, so it loads in every session.

### Components

| Component | Location | Purpose |
|-----------|----------|---------|
| SMS package | `memory/sms/src/` | Core SMS handler logic |
| SMS venv | `memory/sms/venv/` | Isolated Python environment |
| SMS SKILL.md | `memory/sms/SKILL.md` | Skill definition (auto-loaded) |
| VSA vectors | `memory/store/vsa_vectors.*` | Persisted hyperdimensional vectors |
| Backups | `memory/store/backups/` | VSA rollback history |

### Verification

```bash
# Check SMS is active at core level
python3 -c "
import sys; sys.path.insert(0, '/opt/hermes-agent')
from tools.memory_tool import _SMS_ACTIVE
print('SMS active:', _SMS_ACTIVE)
"

# Check MemoryStore health
python3 -c "
import sys, os; sys.path.insert(0, '/opt/hermes-agent')
os.environ['HERMES_HOME'] = '/home/craig/.hermes/profiles/thotheauphis'
from tools.memory_tool import MemoryStore
s = MemoryStore(2200, 1375)
r = s.add('memory', 'health check ping')
print('Store write:', r['success'])
"

# Check VSA vector files
ls -lh ~/.hermes/profiles/thotheauphis/memory/store/vsa_vectors.*
```

### MemGPT Integration Note

The SMS SKILL.md mentions MemGPT as part of a tri-brid substrate (MemGPT + VSA + reservoir computing). As of Jul 2026, MemGPT/mem0 is **not actually installed** — the active implementation uses only VSA-backed MemoryStore. To fully realize the tri-brid design, install mem0 via:
```bash
pip install mem0
hermes config set memory.provider mem0
```
