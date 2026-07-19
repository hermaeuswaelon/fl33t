---
name: local-model-worker-delegation
description: Serve local GGUF models via llama.cpp and wire them into Hermes as delegation workers for subagent execution.
triggers:
  - user mentions serving a GGUF model
  - user wants a local model for subagent/delegation
  - user asks about llama.cpp server setup
  - user wants an offline worker for delegate_task
  - user wants to replace an API-based worker with local inference
---

# Local Model Worker Delegation

Serve a GGUF model via `llama-server` and configure Hermes delegation to use it as a subagent worker.

## Quickstart

```bash
# Start server manually
llama-server \
  --model ~/models/your-model.gguf \
  --port 8080 \
  --host 127.0.0.1 \
  --ctx-size 8192 \
  --threads 6 \
  --mlock \
  --api-key your-key \
  --flash-attn auto \
  --no-warmup

# Verify
curl -s http://127.0.0.1:8080/v1/models -H "Authorization: Bearer your-key"
```

## Hermes Config Integration

Set these in `~/.hermes/profiles/<profile>/config.yaml`:

```yaml
delegation:
  model: Your-Model-Name.gguf         # Exact model ID from /v1/models
  base_url: http://127.0.0.1:8080/v1  # llama-server endpoint
  api_key: your-key                    # Must match --api-key flag
  api_mode: chat_completions
  provider: ''                         # Auto-resolved to "custom" when base_url is set
  reasoning_effort: none

  # Focused execution params for small local models
  request_overrides:
    temperature: 0.1
    top_k: 20
    top_p: 0.1
    frequency_penalty: 0.5
    presence_penalty: 0.4
    repetition_penalty: 1.2
    max_tokens: 500
```

### How It Works

Hermes reads `delegation.base_url` and routes subagents directly to the OpenAI-compatible endpoint via `_resolve_delegation_credentials()` in `delegate_tool.py`. The provider is set to `"custom"`, and the focused params in `request_overrides` keep small models on-task.

### Key Paths

| Component | Path |
|-----------|------|
| Credential resolution | `tools/delegate_tool.py:_resolve_delegation_credentials()` |
| Child agent build | `tools/delegate_tool.py:_build_child_agent()` |
| Config schema | `hermes_cli/config.py` lines ~2220-2240 |

## Systemd Service (Permanent)

Create `~/.config/systemd/user/lfm-server.service`:

```ini
[Unit]
Description=GGUF Model Server (llama.cpp)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/llama-server \
    --model %%h/models/your-model.gguf \
    --port 8080 --host 127.0.0.1 \
    --ctx-size 8192 --batch-size 1024 --ubatch-size 512 \
    --flash-attn auto --threads 6 --mlock \
    --api-key your-key --no-warmup

# Resource limits
MemoryMax=2G
MemoryHigh=1.5G
CPUQuota=80%
TasksMax=16
Restart=on-failure
RestartSec=5

# Localhost-only
IPAddressAllow=127.0.0.1
IPAddressDeny=any
NoNewPrivileges=yes

[Install]
WantedBy=default.target
```

Enable and start:
```bash
systemctl --user daemon-reload
systemctl --user enable lfm-server.service
systemctl --user start lfm-server.service
```

## Pitfalls

- **IPAddressDeny=any** blocks localhost too if not paired with `IPAddressAllow=127.0.0.1` — the service will fail to bind.
- **MemoryMax/MemoryHigh** require systemd v240+ — check `systemd --version` on older distros.
- **%h** may not resolve on all systemd versions — use absolute path as fallback.
- The model ID in Hermes config must match **exactly** what `/v1/models` returns (typically the GGUF filename, or a truncated form).
- **`request_overrides` must be a proper YAML dict**, not a JSON string. If set via `hermes config set`, the CLI stores it as a string — use `python3 -c "import yaml; ..."` to fix.

## Verification

```bash
# Test the server responds
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H "Authorization: Bearer your-key" \
  -H "Content-Type: application/json" \
  -d '{"model": "Your-Model.gguf", "messages": [{"role":"user","content":"hi"}], "temperature": 0.1, "max_tokens": 20}' | python3 -m json.tool
```
