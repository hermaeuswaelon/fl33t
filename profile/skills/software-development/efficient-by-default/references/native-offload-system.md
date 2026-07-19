# Native Offload System & 108K Context Gate

Permanent native module at `/opt/hermes-agent/tools/offload_system.py`. Always on, no skill/plugin needed. Two subsystems:

## Auto-Offload

Wired into `model_tools.py`'s `handle_function_call()` — after the `transform_tool_result` plugin hook, every tool result >2KB is saved to disk as a JSONL record. The conversation carries only a lightweight pointer:

```json
{"offloaded": {"path": "/tmp/hermes-offload/session123/tool.abc.ts.jsonl",
               "tool": "terminal",
               "bytes": 15000,
               "preview": "first 200 chars..."}}
```

**File format:** Single JSONL line per offload. Fields: tool, call_id, turn_id, session_id, bytes, timestamp, result (full content).

**Retrieve:** `OffloadSystem.retrieve(path)` or any `read_file()` call against the pointer path.

**Cleanyp:** `OffloadSystem.clean(max_age_seconds=86400)` — removes files older than 24h (default). Called by cron or manually.

## 108K Context Gate

Wired into `agent/conversation_loop.py` — fires before the pre-API compression check. A HARD override that triggers compression regardless of cooldowns, deferrals, or `compression_enabled` status.

**Trigger:** `request_pressure_tokens >= HERMES_CONTEXT_GATE` (default 108000)

**Behavior:**
1. Logs `"108K Gate: ~N tokens >= 108,000 — forcing compression"` (WARNING level)
2. Overrides the normal `should_compress()` gate — compression runs even during cooldown
3. Status emits `"🧊 108K Gate: Pre-API compression..."` to distinguish from normal compression

## Config (env vars)

| Var | Default | Description |
|-----|---------|-------------|
| `HERMES_OFFLOAD_ENABLED` | 1 | Set 0 to disable auto-offload |
| `HERMES_OFFLOAD_THRESHOLD` | 2000 | Bytes; results above this are offloaded |
| `HERMES_OFFLOAD_DIR` | /tmp/hermes-offload | Base offload directory |
| `HERMES_CONTEXT_GATE` | 108000 | Token threshold for hard compression gate |

## Integration Points

| File | Hook | Purpose |
|------|------|---------|
| `model_tools.py` (line ~1364) | After `transform_tool_result` | Auto-offload large results before adding to messages |
| `conversation_loop.py` (line ~1013) | Before pre-API compression check | 108K gate override |

## Pitfalls

- **Pointer is a dict, not a tool schema pointer.** The offloaded pointer is injected directly into the `content` field of a `tool`-role message. The model sees it as a JSON dict in the result string. Some models may attempt to parse it as tool output — this is fine since the preview content is self-contained.
- **Offload dir is session-scoped.** Different sessions have different dirs. Cleanup targets the base dir recursively, so cross-session cleanup is safe.
- **Threshold is byte-based, not token-based.** 2KB ~ 500 tokens for English text, ~200 tokens for dense JSON. Conservative threshold ensures small-but-valuable results stay inline.
- **Gate uses `request_pressure_tokens`**, which is an estimate (chars/4). It may fire slightly early — that's safer than slightly late.
