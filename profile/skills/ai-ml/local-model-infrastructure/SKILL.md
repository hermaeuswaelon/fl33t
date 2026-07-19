---
name: local-model-infrastructure
title: local-model-infrastructure
description: Deploy and manage multiple local LLM servers as a persistent fleet using llama.cpp + systemd user services. Covers discovery, installation, service files, port management, health checks, and memory budgeting.
triggers:
  - "set up a local model"
  - "serve a GGUF model"
  - "run multiple local models"
  - "create a model server"
  - "local model fleet"
---

# Local Model Infrastructure

## Trigger
User asks to serve a local model, set up a model server, or run multiple local LLMs simultaneously.

## Step 0: Inventory local disk FIRST
**Do NOT download anything until you've checked what's already on disk.**

```bash
# Check these locations in order:
ls -lh ~/models/*.gguf 2>/dev/null           # Primary model directory
ls -lh ~/Downloads/*.gguf 2>/dev/null        # Downloads (may have untracked models)
find ~/ -name "*.gguf" -not -path "*/.*" 2>/dev/null | head -20  # Anywhere else
```

If the user already has the file, **move it** from Downloads → models:
```bash
mv ~/Downloads/<model>.gguf ~/models/
```

Only download if the specific quant/file is genuinely absent. Search HuggingFace for GGUF variants, prefer Q4_K_M or Q5_K_M for balanced quality/size.

## Step 1: Resource planning
Estimate RAM before deciding what to serve simultaneously:

| Model Size | Estimated RAM (Q4_K_M) |
|------------|----------------------|
| 1B-2B      | ~1-2 GB              |
| 3B         | ~2-3 GB              |
| 7B-8B      | ~4-6 GB              |
| 13B+       | ~8-12 GB             |

Check available RAM:
```bash
free -h | grep Mem
```

**Rule of thumb:** Leave 2-3 GB free for the OS + Hermes. If total model RAM exceeds available - 2GB, stagger the services (don't enable all at once).

## Step 2: Create systemd service files
One file per model in `~/.config/systemd/user/<name>-server.service`.

Standard template (adjust model path, port, api-key):

```ini
[Unit]
Description=<Model Name> Server (llama.cpp)
Documentation=https://github.com/ggml-org/llama.cpp
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/llama-server \
    --model /home/craig/models/<model-file>.gguf \
    --port <PORT> \
    --host 127.0.0.1 \
    --ctx-size 8192 \
    --batch-size 1024 \
    --ubatch-size 512 \
    --flash-attn auto \
    --threads 6 \
    --mlock \
    --api-key <unique-key> \
    --no-warmup

CPUQuota=80%

Restart=on-failure
RestartSec=5

IPAddressAllow=127.0.0.1
PrivateTmp=yes
NoNewPrivileges=yes

# Required for --mlock to work
LimitMEMLOCK=infinity

[Install]
WantedBy=default.target
```

**Key rules for service files:**
- Use absolute paths, NOT `%h` (systemd specifier may not expand in all versions)
- Do NOT pair `IPAddressAllow=127.0.0.1` with `IPAddressDeny=any` — deny wins when both match, blocking loopback. `IPAddressAllow=127.0.0.1` alone is sufficient (it implicitly denies everything else).
- Always include `LimitMEMLOCK=infinity` when using `--mlock`
- Remove `MemoryMax=`/`MemoryHigh=` if systemd version doesn't support them
- Use unique API keys per service (e.g., `lfm-local-key`, `qwen-local-key`, `granite-local-key`)

## Step 3: Enable and start
```bash
systemctl --user daemon-reload
systemctl --user enable <name>-server.service
systemctl --user start <name>-server.service
# Wait for model to load:
sleep 5
systemctl --user status <name>-server.service --no-pager
```

## Step 4: Verify the endpoint
```bash
# List models endpoint (quick health check)
curl -s http://127.0.0.1:<PORT>/v1/models \
  -H 'Authorization: Bearer <api-key>'

# Smoke test chat completion
curl -s http://127.0.0.1:<PORT>/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <api-key>' \
  -d '{"model":"model","messages":[{"role":"user","content":"Say hello in one word"}],"max_tokens":20}'
```

## Step 5: Create a fleet management script
Create `~/.local/bin/model-switch` with these features:
- `list` — show all services, port, status, model size
- `start|stop|restart [name]` — control individual or all services
- `test [name]` — smoke test each endpoint
- `curl <port> <json>` — raw API call with correct auth pre-filled

Store the port-to-key mapping in arrays so `curl` helper picks the right auth automatically.

## Pitfalls
- **Downloading before checking disk**: ALWAYS scan ~/models/ and ~/Downloads/ first. The user frequently has the file already.
- **Cold-start latency**: First request to a freshly loaded model can take 5-15 seconds (prompt processing). Subsequent requests are faster.
- **Port conflicts**: Check with `ss -tlnp | grep <PORT>` before assigning. Use `fuser -k <PORT>/tcp` to free a stuck port.
- **Shell quoting in curl**: JSON payloads with nested quotes break shell parsing. Use heredoc (`curl -d @- <<'EOF' ... EOF`) for complex prompts, or keep prompts simple: no embedded `{}` or `""` unless escaped via heredoc.
- **Qwen3 models output internal reasoning tags** (``) before answering. This is normal. For function-calling tasks, LFM Nova is more deterministic.
- **Granite models for JSON**: Granite 4.x is purpose-built for structured JSON output. Test with a simple JSON request. If it fails, the issue is likely shell quoting, not the model.
- **systemd user services**: Run `systemctl --user daemon-reload` after ANY edit to service files. The `--user` flag is essential — these are user-scoped services, not system-wide.

## Verification
```bash
model-switch list      # All green?
model-switch test      # All endpoints respond?
systemctl --user is-active <name>-server.service  # 'active'?
```
