# Offload System — Native Context Gating

## Location
`/opt/hermes-agent/tools/offload_system.py`

## Env Vars
| Var | Default | Description |
|-----|---------|-------------|
| `HERMES_OFFLOAD_ENABLED` | `0` (patched from `1`) | Set to `1` to re-enable |
| `HERMES_OFFLOAD_THRESHOLD` | `500000` (patched from `2000`) | Bytes before offload triggers |
| `HERMES_CONTEXT_GATE` | `108000` | Token gate for context window |
| `HERMES_OFFLOAD_DIR` | `/tmp/hermes-offload` | Where offloaded files go |

## How It Works
Every tool result above `_THRESHOLD` bytes is written to `$HERMES_OFFLOAD_DIR/<session_id>/` as a JSONL file. The agent receives a reference header instead of inline content. Re-reading the reference file to get the content also hits the threshold → circular offload.

## Debugging Circular Offload
1. Check `_ENABLED` and `_THRESHOLD` on the OffloadSystem class
2. The offload module is loaded at import time — env changes take effect on **next session start**
3. To hot-patch a live session: `python3.13 -c "import tools.offload_system as o; o._ENABLED=0; o._THRESHOLD=999999999"` (separate process only)
4. Permanent fix: edit defaults in `/opt/hermes-agent/tools/offload_system.py` lines 40-41
5. Profile override: add `HERMES_OFFLOAD_ENABLED=0` and `HERMES_OFFLOAD_THRESHOLD=500000` to `~/.NOTTHEONETOEDIT/profiles/<profile>/.env`

## Reading Offloaded Content (workaround while active)
The JSONL files contain a `result` field which is a JSON string of the original tool output. Parse with:
```python
import json
d = json.load(open('/tmp/...jsonl'))
r = json.loads(d['result'])
content = r.get('output', '')
```
