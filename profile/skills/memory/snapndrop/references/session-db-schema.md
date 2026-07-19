# Hermes Session DB Schema Reference

Discovered during session 20260717_125654_6de41e while building Snap n Drop v2.

## Database Location

`~/.hermes/profiles/<profile>/state.db` — SQLite3, typically ~150 MB+ after extended use.

## Key Tables

### `sessions`
| Column | Type | Notes |
|--------|------|-------|
| `id` | TEXT | Primary key, format `YYYYMMDD_HHMMSS_<8-char>` |
| `source` | TEXT | `tui`, `cli`, `telegram`, etc. |
| `message_count` | INTEGER | Total messages in session |
| `input_tokens` | INTEGER | **Cumulative** input across ALL turns — NOT per-request |
| `output_tokens` | INTEGER | **Cumulative** output across ALL turns |
| `reasoning_tokens` | INTEGER | Cumulative reasoning tokens |
| `ended_at` | REAL | NULL if session is still active |
| `started_at` | REAL | Unix timestamp |

### `messages`
| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Auto-increment primary key |
| `session_id` | TEXT | FK to sessions |
| `role` | TEXT | `user`, `assistant`, `tool`, `system` |
| `content` | TEXT | Message body. Can be JSON for tool responses |
| `token_count` | INTEGER | **Often NULL** — not auto-populated by Hermes |
| `tool_calls` | TEXT | JSON array of tool call objects (if assistant role) |
| `active` | INTEGER | `1` = current, `0` = compacted/compressed |
| `compacted` | INTEGER | `1` = this message was replaced by compression |

### `session_model_usage`
Per-model billing/usage tracking for MOA and multi-provider setups.

| Column | Type | Notes |
|--------|------|-------|
| `session_id` | TEXT | FK to sessions |
| `model` | TEXT | Model name (e.g. `deepseek-reasoner`, `default` for MOA aggregator) |
| `billing_provider` | TEXT | Provider name (e.g. `deepseek`, `moa`, `togetherai`) |
| `input_tokens` | INTEGER | Cumulative input for THIS model only |
| `output_tokens` | INTEGER | Cumulative output |
| `reasoning_tokens` | INTEGER | Reasoning/deep-think tokens |
| `first_seen` / `last_seen` | REAL | Timestamps |

## Reading a Session (Read-Only)

```python
conn = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row

# Get active session
s = conn.execute("""
    SELECT id, message_count, input_tokens, output_tokens
    FROM sessions WHERE ended_at IS NULL
    ORDER BY started_at DESC LIMIT 1
""").fetchone()

# Get active messages array (the per-request context)
msgs = conn.execute("""
    SELECT role, content, tool_calls
    FROM messages WHERE session_id = ? AND active = 1
    ORDER BY id ASC
""", (s["id"],)).fetchall()
```

## Token Estimation

Use `tiktoken` with `cl100k_base` encoding (matching DeepSeek and OpenAI tokenizers):

```python
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")

def estimate_array_tokens(messages):
    total = 0
    for m in messages:
        content = m["content"] or ""
        total += len(enc.encode(content))
        total += 8  # per-message JSON wrapper overhead
        if m["tool_calls"]:
            tc = json.loads(m["tool_calls"])
            total += len(tc) * 15  # per-tool-call overhead
    return total
```

**Critical:** Do NOT use `sessions.input_tokens` as the gauge value. That field is **cumulative** across ALL turns — it will exceed 64k within 20-30 messages. The actual per-request context is only the messages where `active = 1`.

## TUI Gauge

The Hermes TUI has a built-in context gauge in the footer showing `XXk / 1M` (where 1M is the model's max context window). This gauge tracks the **messages array** plus **cached system prompt** overhead. The system prompt is sent once and cached; subsequent turns only send the messages delta.

## Snapshot Strategy

- Take SNAP before compression runs (check `compacted` column)
- SNAP captures `active = 1` messages only
- The snapshot transcript is ~3–9k tokens when encoded with cl100k
- DROP payload (`--sovereign-prompt`) replaces the ENTIRE system prompt — use only when the system handles prompt caching
