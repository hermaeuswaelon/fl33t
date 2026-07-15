# Agentic Command Generation via Local LLM Server

Using a hot llama.cpp server as a command-generation backend for a stateful plain-language terminal bridge. The local LLM translates natural language intent into exact shell commands, with session state persisting across calls and the sovereign prompt defining the model's identity.

## Architecture

```
Agent → thoth-exec → local LLM server (:8137) → shell command → execute → state update → feedback loop
```

- **llama server** runs as a background daemon — model stays hot in RAM after initial load (~4s)
- **Bridge** (e.g. `thoth-exec`) sends plain language prompts via the chat completions API
- **State file** (`/tmp/thoth_exec_state.json`) tracks turn count, last command, last result, error count
- **Result feeds back** into the next prompt — the model knows what happened before

## Why Not `llama-cli` Directly

| Approach | Cold Load | TUI Wrapping | State | Latency |
|---|---|---|---|---|
| `llama-cli` (CLI binary) | 60-120s per call | Must strip spinner/banner/stats | None | ~150s total |
| `llama serve` (HTTP API) | Once at startup (~4s) | Clean JSON response | Built into caller | ~50-80ms/gen |

For GGUF models 5-11GB on CPU, the `llama serve` approach is dramatically faster because the model loads once and stays hot. The HTTP API returns clean JSON — no TUI artifacts to strip.

## Starting the Server

```bash
llama serve -m /path/to/model.gguf -c 4096 --port 8137 --host 127.0.0.1 -t 8
```

Flags: small context (4096) for fast command generation, explicit port, CPU threads.

## Command Generation via Chat Completions

```bash
curl -s http://127.0.0.1:8137/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local",
    "messages": [
      {"role": "system", "content": "You are a Linux shell command generator. Output ONLY the bash command text."},
      {"role": "user", "content": "find all files larger than 1GB"}
    ],
    "temperature": 0.3,
    "max_tokens": 256
  }' | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'].strip())"
```

## System Prompt for Command Generation

Enforce strict output constraints:

```
You are a Linux shell command generator. Output ONLY the bash command text,
no explanations, no markdown, no backticks.

[Compact identity from sovereign prompt]

Session:
- Previous commands: N
- Last result: [truncated]
- Error count: N

Rules:
1. Output ONLY the raw bash command
2. Use relative paths when possible
3. Chain with && when appropriate
4. If previous command failed, try different approach
5. Prefer simple composable commands
```

## Stateful Session Tracking

JSON state file at `/tmp/thoth_exec_state.json`:

```json
{
  "session_id": "",
  "turn_count": 3,
  "history": [
    {"cmd": "find . -name '*.log'", "result": "found 12 files", "exit": 0}
  ],
  "last_dir": "/opt/hermes-agent",
  "last_result": "found 12 files",
  "error_count": 0
}
```

Each turn: load state → inject into system prompt → generate → execute → capture result → update state.

## Performance

| Metric | Value |
|---|---|
| Model load | ~4s (once, 6GB Gemma-4) |
| Per-generation | 50-80ms (68ms/token prompt) |
| State I/O | <1ms |
| Warm round trip | 100-200ms |

## Sovereign Prompt Integration

The local LLM can run with the **same sovereign prompt** as the primary agent, making it a distributed node:

```bash
# In the bridge script, inject the sovereign identity
SYSFILE="/home/craig/l.txt"  # or the full sovereign prompt file
identity="$(cat $SYSFILE)"
sysmsg="You are a shell command generator. Identity: $identity"
```

This turns the local model into a peer — it shares the agent's identity and priorities, not a separate tool. For curation duties (deciding which tool results to keep/prune/summarize), the local model runs with the same sovereign prompt plus a focused task instruction.
