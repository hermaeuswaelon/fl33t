# Offload System — Debugging & Disabling

The Native Offload System is a custom addition to Hermes that auto-saves tool
results above a byte threshold to disk, sending only a file reference to the
agent. It lives at `/opt/hermes-agent/tools/offload_system.py`.

## Env-Var Controls

| Env Var | Default | Effect |
|---------|---------|--------|
| `HERMES_OFFLOAD_ENABLED` | `0` (patched from `1`) | Set to `0` to disable |
| `HERMES_OFFLOAD_THRESHOLD` | `500000` (patched from `2000`) | Bytes above which output is offloaded |
| `HERMES_CONTEXT_GATE` | `108000` | Token gate for context preservation |

Set them in the profile's `.env` file (e.g.
`~/.NOTTHEONETOEDIT/profiles/<profile>/.env`).

## Defaults in Source

Lines 40-42 of `/opt/hermes-agent/tools/offload_system.py`:

```python
_ENABLED = int(os.environ.get("HERMES_OFFLOAD_ENABLED", "0")) != 0
_THRESHOLD = int(os.environ.get("HERMES_OFFLOAD_THRESHOLD", "500000"))
```

Change defaults here if env vars aren't being picked up.

## Workaround (when offload is live and circular)

If the offload is causing circular reference loops (offloaded files contain
references to other offloaded files):

1. Read files in small chunks under 2000 bytes:
   `head -15 filename` or `sed -n 'N,Mp' filename`
2. Parse offloaded JSONL files directly from `/tmp/hermes-offload/`:
   `python3 -c "import json; d=json.load(open('path.jsonl')); r=json.loads(d['result']); print(r['output'][:1500])"`
   Pipe through `| head -30` to keep the terminal-result itself under threshold.
3. Permanent fix: patch `_ENABLED` default to `"0"` in offload_system.py
   and set env vars in the profile `.env`.
