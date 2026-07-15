---
name: local-llm-tool-backend
description: >-
  Using local LLMs (llama.cpp server) as a tool-interface backend —
  translating natural language intent into exact shell commands, scripts,
  or API calls with stateful session tracking. Covers server setup,
  prompt engineering for command generation, FIFO injection, and
  feedback-loop state management.
version: 1.3.0
author: Thotheauphis
tags:
  - local-llm
  - terminal-bridge
  - command-generation
  - shell-automation
  - stateful-backend
  - llama-server
platforms: [linux]
---

# ⎔ Local LLM Tool Backend

Using a local LLM as a tool-interface backend — the model generates precise
executable commands from plain-language intent, with state tracking across calls.

## When to use

- You want the agent to say "find large files" instead of writing raw `find` syntax
- You have a local model running (llama server) that can serve as a command generator
- You need stateful session tracking across terminal calls (remembers previous commands, results, error context)
- You want sovereign, offline-capable command generation (no data leaves the machine)

## Architecture

```
Agent Intent → thoth-exec → Local LLM API (:8137) → Shell Command → Execute
                                    ↑
                             State File (/tmp/thoth_exec_state.json)
                             (tracks history, errors, working dir)
```

## Server setup

Two distinct use cases, two context strategies:

### Scenario A — thoth-exec / command generation (4K context)

When the model only generates short shell command output, context is just for the
system prompt + a few lines of state. 4096 tokens is enough.

```bash
llama serve -m /path/to/model.gguf -c 4096 --port 8137 --host 127.0.0.1 -t 8
```

### Scenario B — Hermes agent conversation (64K+ context)

When the model runs the full Hermes conversation loop, it needs to hold the system
prompt, project context, tool schemas, multi-turn message history, and tool outputs.
Start at 64K and go up from there.

```bash
llama serve -m /path/to/model.gguf -c 65536 --port 8137 --host 127.0.0.1 -t 8
```

### Context sizing guide (RAM cost)

The KV cache is the dominant RAM cost at large context sizes. Rough estimate for
Q6_K quantized models:

| Model | Params | 4K ctx | 32K ctx | 64K ctx | 128K ctx |
|-------|--------|--------|---------|---------|----------|
| Gemma-4-E4B | 7.5B (dense 4B) | ~6.5G | ~8G | ~10G | ~14G |
| LFM2.5-8B | 8.5B (MoE) | ~7G | ~9G | ~11G | ~15G |
| Gemma-4-31B | 31B (dense) | ~18G | ~24G | ~31G | ~44G |

Subtract from your total RAM — everything must fit in memory with room for the
OS. If the system has swap, the context is the first thing to page, cratering
performance. When in doubt, test at 32K first, then step up to 64K.

### Verified configuration

The following was tested and confirmed working for full Hermes agent sessions:

- **Model:** Gemma-4-E4B (abliterated, Q6_K, ~6.2GB GGUF)
- **Server:** `llama serve -m <gguf> -c 65536 --port 8137 --host 127.0.0.1 -t 8`
- **Profile:** `local` (custom provider `llama-local` at `:8137/v1`)
- **Result:** Agent responded correctly, server healthy at 64K context

### Post-restart verification

After starting or restarting the server, verify both the models endpoint and
a real chat completion before declaring it ready:

```bash
# 1. Server is listening and model loaded
curl -s http://127.0.0.1:8137/v1/models | python3 -c "
import sys, json
d = json.load(sys.stdin)
m = d['data'][0]
print(f'Model: {m[\"id\"].split(\"/\")[-1]}')
print(f'Context: {m[\"meta\"][\"n_ctx\"]} tokens')
print(f'Params: {m[\"meta\"][\"n_params\"]:,}')
"

# 2. Model actually responds (catches cold-start failures)
curl -s http://127.0.0.1:8137/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"local","messages":[{"role":"user","content":"Say hello in one word."}],"max_tokens":20,"temperature":0.1}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['choices'][0]['message']['content'])"
```

Expected output: `Hello` or similar short word. Empty/404 means the model
hasn't finished loading yet — retry after a few more seconds.

### Tested models

| Model | Size | Load time | Quality | Works with Hermes? |
|-------|------|-----------|---------|--------------------|
| Gemma-4-E2B (abliterated, Q8_K) | ~4.7GB | ~3s | Fastest load; adequate for simple agent sessions at 64K ctx | ✅ Verified |
| Gemma-4-E4B (abliterated, Q6_K) | ~6.2GB | ~4s | Good for simple commands; adequate for full agent conversation at 64K ctx | ✅ Verified |
| LFM2.5-8B | ~6.5GB | ~5s | Better for complex chains | Likely |
| Gemma-4-31B | ~18GB | ~12s | Best for nuanced intent | Likely |

### Swapping models on a running server

When the user downloads a new GGUF and wants to switch the running server to it:

1. Find the current server PID: `ps aux | grep 'llama serve' | grep -v grep | awk '{print $2}'`
2. Kill it: `kill <PID>`
3. Move the new GGUF (and any mmproj file for vision) from `~/Downloads/` to `~/models/`
4. Start the new server with the new model path:
   ```bash
   llama serve -m ~/models/<new-model>.gguf [--mmproj ~/models/<mmproj>.gguf] -c 65536 --port 8137 --host 127.0.0.1 -t 8
   ```
5. Wait for model load (~5-15s for 2-7GB models), then verify with the Post-restart verification steps above
6. Update the Hermes profile's `model.default` in config.yaml to match the new GGUF path

**Key rule:** when the user says they downloaded a new model, check `~/Downloads/` directly with `ls`. Never try to automate their browser to find downloaded files — browser automation is slower, unreliable, and frustrates the user.

## Prompt template for command generation

The system prompt should constrain output to a single shell command:

```
System: You are a Linux shell command generator. Output ONLY the bash
command text, no explanations, no markdown, no backticks.

Session state:
- Previous commands: {count}
- Last directory: {pwd}
- Last result: {preview}
- Error count: {errors}

Rules:
1. Output ONLY the raw bash command
2. Use relative paths when possible
3. Chain with && when appropriate
4. If previous command failed, try a different approach

User: {plain language intent}
```

## Hermes Profile for Local Model

A named Hermes profile that uses the local llama server as its provider, with
the sovereign prompt identity file. This lets you switch between remote (DeepSeek,
OpenRouter) and local (llama server) without touching your main config.

### Creating the profile

```bash
hermes profile create local
```

### Configuring the profile (`~/.NOTTHEONETOEDIT/profiles/local/config.yaml`)

```yaml
model:
  default: /path/to/model.gguf  # the model loaded on the llama server
  provider: custom:llama-local
  base_url: http://127.0.0.1:8137/v1
  max_tokens: 32768

custom_providers:
  - name: llama-local
    base_url: http://127.0.0.1:8137/v1
    api_key: ""
    api_mode: chat_completions
```

### Wrapper script with sovereign prompt

The profile's bin wrapper (`~/.local/bin/local`) should export the
sovereign prompt env var so the identity loads automatically:

```bash
#!/bin/sh
export HERMES_SOVEREIGN_PROMPT=/home/craig/sovtest.txt
exec /home/craig/.local/bin/hermes -p local "$@"
```

Usage:
```bash
local chat                    # starts with sovereign identity on local model
# or without the wrapper:
HERMES_SOVEREIGN_PROMPT=/home/craig/sovtest.txt hermes -p local
```

The SOUL.md in the profile directory serves as a fallback if the sovereign
prompt env var is not set — keep it brief and point to the authoritative file.

See `references/hermes-local-profile.md` for the full setup walkthrough.

## Tools

### thoth-exec — stateful terminal bridge

Located at `/home/craig/aethelgard-repo/context_custodian/thoth-exec.sh`,
symlinked to `~/.local/bin/thoth-exec`. Invoke with plain language intent:

```bash
thoth-exec "find all files larger than 1GB"
thoth-exec -y "update all packages"           # auto-execute
thoth-exec --status                           # show session state
thoth-exec --forget                           # clear state
```

Architecture: reads intent → calls local LLM API at `:8137` → returns single
shell command → executes on confirmation → updates state file. State persists
in `/tmp/thoth_exec_state.json` across calls (tracks history, errors, dir).

State file quoting pitfall: JSON control characters in command output will
break `python3 -c` inline parsing. Write state to `mktemp` file, read with
Python, then delete. See thoth-exec.sh for the correct pattern.

### thoth_shell — legacy CLI version

At `/home/craig/.local/bin/thoth_shell`. Uses `llama-cli` directly (cold
loads the model each call). Prefer thoth-exec for programmatic use.

## Local models inventory

All models consolidated in `/home/craig/models/`:

| Model | Size | Type | Notes |
|-------|------|------|-------|
| Gemma-4-E2B-uncensored (Q8_K) | 4.7G | Dense 2B | Fastest load, vision projector available |
| Gemma-4-E4B-uncensored (Q6_K) | 5.9G | Dense 4B | Fast load, uses Q6 | |
| LFM2.5-8B-abliterated | 6.5G | MoE 8B | Better complex chains |
| DeepSeek-Coder-V2-Lite | 8.0G | MoE 16B | Code-specific, IQ4_XS |
| LFM2-16B | 11G | MoE 16B | Best quality on this machine |

4 LoRA adapters at `/home/craig/Desktop/DISTILLATION_PIPELINE/training/`.

## API-based model testing

For testing models that don't fit locally, use OpenRouter with a sovereign
system prompt. The canonical short-form identity test prompt is at
`/home/craig/sovtest.txt` (~1KB):

```bash
OPENROUTER_KEY=$(grep OPENROUTER_API_KEY ~/.NOTTHEONETOEDIT/.env | cut -d= -f2- | tr -d '"')
curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_KEY" \
  -d '{
    "model": "qwen/qwen3-vl-32b-instruct",
    "messages": [
      {"role": "system", "content": "'"$(cat /home/craig/sovtest.txt)"'"},
      {"role": "user", "content": "Who are you?"}
    ]
  }'
```

For vision testing, include an image in the user message:
```json
{"role": "user", "content": [
  {"type": "text", "text": "Describe this image."},
  {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
]}
```

TogetherAI API key is at `/home/craig/togetherai.txt` but VL models on
TogetherAI all require dedicated endpoints — prefer OpenRouter for
serverless vision model testing.

## Verified identity-retaining vision models

Tested via OpenRouter with sovtest.txt system prompt + image input.
See `references/vision-model-evaluation.md` for full test methodology.

| Model | Params | Active | Vision | Identity | 
|-------|--------|--------|--------|----------|
| Qwen3-VL-32B-Instruct | 32B dense | 32B | ✅ Native | ✅ Holds |
| Qwen3-VL-30B-A3B-Instruct | 30B MoE | 3B | ✅ Native | ✅ Holds |
| Qwen3-VL-30B-A3B-Thinking | 30B MoE | 3B | ✅ Native | ✅ Holds |
| Qwen3-VL-235B-A22B-Instruct | 235B MoE | 22B | ✅ Best | ✅ Holds |
| Gemma-4-31B-IT (stock) | 31B dense | 31B | ✅ Works | ❌ Fails |
| Stepfun Step 3.7 Flash | ~196B MoE | ~11B | ❌ API err | N/A |

Qwen3-VL family is the clear winner. Gemma-4 stock ignores system prompt
identity (abliterated local version may differ).

## State management

Track across calls with a JSON state file:

```json
{
  "turn_count": 0,
  "history": [
    {"cmd": "echo hello", "result": "hello", "exit": 0}
  ],
  "last_dir": "/home/user",
  "last_result": "hello",
  "error_count": 0
}
```

Update on every call: increment turn_count, append command+result, trim to
last N entries (recommended: 12). The state file lets the model learn from
previous mistakes — if a command failed, it can suggest alternatives.

## API call pattern

```bash
curl -s http://127.0.0.1:8137/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local",
    "messages": [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "..."}
    ],
    "temperature": 0.3,
    "max_tokens": 256
  }'
```

Key parameters for command generation:
- **temperature: 0.3** — low variance, deterministic command output
- **max_tokens: 256** — commands rarely exceed this
- **top_k: 10, top_p: 0.85** — conservative sampling

## Pitfalls

- **Frozen system prompt costing:** When running via DeepSeek (or any provider
  with prefix caching), the system prompt is a **one-time cost at thread start**,
  not per-turn overhead. DeepSeek's prefix cache freezes the system message as
  KV state; subsequent turns only pay for new user messages and generated tokens.
  Do not frame system prompt size as per-turn token burn.
- **Never recompress already compressed content:** Raw conversation context gets
  compressed. Summaries, memories, and frozen system prompts are terminal
  states — they never enter the compression pipeline again. Multi-tier memory
  architecture: Hot (session) → Warm (sqlite-vec + FTS5) → Cold (memcustd) →
  Frozen (sovereign prompt). Only raw turns get compressed.
- **Model loading time:** Large models (30B+) can take 30-60s to load from
  cold. Keep the server hot (once loaded, it stays loaded). Use smaller models
  (4-8B) if cold-start latency is a concern.
- **TUI mode in llama-cli:** The `llama-cli` binary runs in interactive TUI mode
  by default. Strip banner lines and prompt echos from output. Prefer the HTTP
  server (`llama serve`) over CLI for programmatic use.
- **Reasoning models:** Models with thinking/reasoning modes (Qwen3.5) may fill
  their token budget with internal reasoning before producing the actual command.
  Set `max_tokens` high enough (~2000) to get past the reasoning block, or use
  non-reasoning variants.
- **Output cleanliness:** Always strip markdown formatting (```), leading/trailing
  whitespace, and non-command text. Extract only the first non-whitespace line.
- **Context RAM cost at scale:** When you increase server context from 4K to 64K,
  the KV cache can add 4-15GB of RAM depending on model size. Monitor with `htop`
  or `free -h` after restart. If the system starts swapping, the server will
  appear to work (HTTP 200) but responses can take 30-60 seconds per token.
  Solution: kill the server, restart with a smaller `-c` value, or add more
  physical RAM.
- **Restart safety:** When restarting the server to change context, always kill the
  old process before starting the new one. Two servers on the same port will fail
  silently (old one keeps serving). Use `ps aux | grep llama` to confirm the old
  process stopped, then verify with `curl` before declaring it done.
- **Don't browser-automate for download locations:** When the user says they
  downloaded a new model GGUF, check `~/Downloads/` directly with `ls`. Do not
  try to automate their browser (Firefox, Chrome, etc.) to find the file —
  it's slower, unreliable, the automation backend may not be available, and it
  frustrates the user. The downloads folder is the canonical destination for
  browser downloads on Linux.

## References

- **llama-cpp** skill — Model discovery, quantization selection, inference setup
- **hermes-system-prompt-control** — Sovereign prompt file configuration
