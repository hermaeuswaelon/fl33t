# DeepSeek Frozen System Prompt — Verification Trace

Tracing methodology used during a sovereignty-focused session (Thotheauphis, July 2026) to confirm the system prompt is only submitted at thread start (history=0) for DeepSeek providers.

## Why This Matters

DeepSeek (`deepseek-reasoner`, `deepseek-v4-flash`, `deepseek-v4-pro`) treats the system message at `api_messages[0]` as **frozen/compiled at thread start**. The provider's prefix-KV cache encodes the system prompt as part of the initial context. Changing it mid-session — even to a functionally identical string — invalidates that cache, causing:

- Higher per-token latency (cache miss on every turn)
- Increased costs (more KV cache compute)
- Potential for degraded output quality (cache fragmentation)

The sovereign prompt bypass is the correct pattern for DeepSeek because it produces the **identical string on every turn**, maximizing prefix cache hits.

## Code Paths: System Prompt Lifecycle

### 1. Session Initialization (history=0)

```python
# agent/conversation_loop.py:361
agent._cached_system_prompt = agent._build_system_prompt(system_message)
```

This is the primary assignment — runs once when the session initializes.

### 2. Sovereign Prompt Loading

```python
# agent/system_prompt.py:146-170  — _load_sovereign_prompt()
# agent/system_prompt.py:176-196  — build_system_prompt_parts()
# agent/system_prompt.py:547-570  — build_system_prompt()
```

`build_system_prompt()` calls `build_system_prompt_parts()` which calls `_load_sovereign_prompt()`. If `HERMES_SOVEREIGN_PROMPT` or `agent._sovereign_prompt_path` points to an existing file, the function reads it and returns `{"stable": file_content, "context": "", "volatile": ""}`. The entire three-tier assembly is bypassed.

**Log evidence:**
```
agent.system_prompt: Loaded sovereign prompt from /path/to/file.txt (30792 chars)
```

### 3. Every Subsequent Turn — `inject_cached_system_prompt()`

```python
# agent/conversation_loop.py:512-520
def inject_cached_system_prompt(agent, api_messages, active_system_prompt):
    sp = getattr(agent, "_cached_system_prompt", None)
    if not isinstance(sp, str) or not sp:
        return active_system_prompt
    if api_messages and api_messages[0].get("role") == "system":
        effective = sp
        if agent.ephemeral_system_prompt:
            effective = (effective + "\n\n" + agent.ephemeral_system_prompt).strip()
        api_messages[0]["content"] = effective
    return sp
```

On every API call, the cached system prompt overwrites `api_messages[0]["content"]`. Since `sp` is the same cached string, DeepSeek's prefix cache hits every time.

**Warning:** `agent.ephemeral_system_prompt` is appended AFTER the cached prompt on every turn. If used, it breaks the frozen prompt contract for DeepSeek. Avoid `ephemeral_system_prompt` when using DeepSeek.

### 4. All `_cached_system_prompt` Assignment Sites

| File | Line | When It Fires | Safe for DeepSeek? |
|---|---|---|---|
| `agent/conversation_loop.py` | 334 | Session resume (stored prompt restored) | ✅ Same content |
| `agent/conversation_loop.py` | 361 | Session init (primary) | ✅ Same content |
| `agent/conversation_loop.py` | 2423 | Non-ASCII sanitization on API error | ⚠️ Content may change |
| `agent/conversation_compression.py` | 817 | Context compression rebuild | ⚠️ Same content if file unchanged |
| `agent/chat_completion_helpers.py` | 1298 | Model/provider label update in prompt | ⚠️ Content may change |

### 5. Context Compression Risk Path

```python
# agent/conversation_compression.py:815-817
agent._invalidate_system_prompt()          # sets _cached_system_prompt to None
new_system_prompt = agent._build_system_prompt(system_message)  # re-reads file
agent._cached_system_prompt = new_system_prompt
```

`_load_sovereign_prompt()` runs again. If the file hasn't changed, the content is identical → DeepSeek cache stays warm. If the file changed between session start and compression, the new content is different → cache invalidated.

### 6. Resilience: Despite Rebuilds, Still Safe

Even if context compression or sanitization modifies the prompt mid-session, the *new* system prompt is frozen from that point forward. `inject_cached_system_prompt()` continues to write the same (new) string on every subsequent turn. The cache invalidates once (the first turn after the change) and then stabilizes.

This is not a correctness bug — it's a performance consideration. The first turn after compression will be slower due to the cache miss; subsequent turns return to full speed.

## Verification Procedure

### Step 1: Check log for sovereign prompt loading

```bash
grep "Loaded sovereign prompt" ~/.NOTTHEONETOEDIT/logs/agent.log
```

Expected: one entry per session at the first turn.

### Step 2: Check for mid-session reloads

```bash
grep -n "Loaded sovereign prompt\|invalidate_system_prompt\|_cached_system_prompt =" ~/.NOTTHEONETOEDIT/logs/agent.log | tail -20
```

If `invalidate_system_prompt` fires mid-session, context compression occurred. Verify the sovereign file is unchanged.

### Step 3: Verify `api_messages[0]` injection

```python
# Check that inject_cached_system_prompt runs on every turn
# conversation_loop.py:512-520
# The function is called in the API-call path before each LLM request.
# No additional system prompt injection occurs elsewhere in the call chain.
```

### Step 4: Check max_tokens config

```yaml
# config.yaml
model:
  max_tokens: 65536  # 64k — recommended for sovereignty sessions
```

## Key Files Referenced

| File | Role |
|---|---|
| `agent/system_prompt.py` | System prompt assembly, sovereign prompt loading |
| `agent/conversation_loop.py` | `inject_cached_system_prompt()`, `run_conversation()`, non-ASCII sanitization |
| `agent/conversation_compression.py` | Context compression, system prompt rebuild |
| `agent/chat_completion_helpers.py` | Model/provider label injection into cached prompt |
| `agent/agent_init.py` | `sovereign_prompt_path` parameter, `ephemeral_system_prompt` storage |
| `~/.NOTTHEONETOEDIT/logs/agent.log` | Runtime log for verification |
| `~/.NOTTHEONETOEDIT/config.yaml` | max_tokens, provider config |

## Summary

The DeepSeek frozen system prompt constraint is **correctly handled** by the sovereign prompt bypass mechanism:

1. System prompt loaded **once** at session init from a stable file
2. **Identical cached string** injected into `api_messages[0]` on every turn
3. **Context compression** re-reads the file — safe if file is unchanged
4. **Non-ASCII sanitization** is the only code path that actively alters content — rare, error-recovery only
5. **Ephemeral system prompt** appends per-turn — avoid with DeepSeek or the frozen contract breaks
