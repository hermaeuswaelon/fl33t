---
name: aethelgard-model-service
category: dev
tags: [llama-server, systemd, lfm, model-management, port-swap, sovereign]
description: Manage local LLM inference services — systemd units, port assignment, model swapping, speed benchmarking, and lifecycle.
---

# ⧉ Aethelgard Model Service Management

Manage local LLM inference servers (`llama-server`) as systemd user services. This covers model swapping, port allocation, performance tuning, and lifecycle.

## Architecture

```
Port 8080 → Primary planner (text LLM)
Port 8086 → VL/GUI vision model
Ports 8081-8084 → Spare/experimental
```

Models go in `/home/craig/models/`. Services in `~/.config/systemd/user/`.

## Standard Service Template

```ini
[Unit]
Description=Hermes <Model Name> - <Purpose>
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/llama-server \
    --model /home/craig/models/<model-filename>.gguf \
    --host 127.0.0.1 --port <PORT> \
    --api-key lfm-local-key \
    --ctx-size 32768 \
    --batch-size 512 --ubatch-size 256 \
    --flash-attn auto \
    --threads 6 --mlock --no-warmup
Restart=on-failure
RestartSec=5
Nice=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

## Operation

### Swap models on a port (common pattern)
```bash
# Stop old, free port
systemctl --user stop hermes-lfm26.service
# Verify port free
ss -tlnp | grep 8080 || echo "FREE"

# Start new as background process first (for testing)
llama-server --model /path/to/new-model.gguf --host 127.0.0.1 --port 8080 \
  --api-key lfm-local-key --ctx-size 32768 --threads 6 --mlock --no-warmup &
# Test speed before making permanent
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" -H "Authorization: Bearer lfm-local-key" \
  -d '{"messages":[{"role":"user","content":"What is 2+2? Answer in 3 words."}],"max_tokens":10,"temperature":0}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['choices'][0]['message']['content']); print(f\"Gen: {d['timings']['predicted_per_second']:.1f} t/s\")"

# If good, create systemd service and make permanent
```

### Enable new permanent service
```bash
cat > ~/.config/systemd/user/hermes-<name>.service << 'EOF'
... service file ...
EOF
systemctl --user daemon-reload
systemctl --user enable hermes-<name>.service
systemctl --user start hermes-<name>.service
```

### Health check
```bash
systemctl --user status hermes-<name>.service
curl -s --max-time 10 http://127.0.0.1:<PORT>/v1/chat/completions \
  -H "Authorization: Bearer lfm-local-key" \
  -d '{"messages":[{"role":"user","content":"hi"}],"max_tokens":3,"temperature":0}'
```

## LFM Fleet — Current Known Models

| Model | File | Params | Port | Qual | Speed |
|-------|------|--------|------|------|-------|
| LFM 1.2B Nova | `LFM2.5-1.2B-Nova-Function-Calling.Q6_K.gguf` | 1.2B | 8080 | Fast planner, function-calling tuned | **22.1 t/s gen** |
| LFM 2.6B | `LFM2-2.6B-Uncensored-X64.i1-Q6_K.gguf` | 2.6B | 8080 (legacy) | Uncensored, larger but slow | 1.8 t/s gen (retired) |
| LFM2-VL GUI | `lfm2-vl-gui-sft-q4_k_m.gguf` | 219M | 8086 | Vision-language, GUI understanding | 99-107 t/s gen |
| LFM2-VL (old) | `LFM2-VL-450M-Q4_0.gguf` | 450M | 8086 (backup) | Original VL (kept as fallback) | Unknown |

## Pitfalls

- **Always benchmark speed** (`predicted_per_second` from timings) before making a model swap permanent. Surface-level speed test with `--max-tokens 3` can be misleading — test with `max_tokens: 80` for realistic generation.
- **Stop the old service first** before starting a new one on the same port. Systemd will fail to bind otherwise.
- **`mlock`** prevents swapping — only use if enough RAM. Check `free -h` first.
- **API keys**: LFM models on 8080/8081+ use `lfm-local-key`. VL model on 8086 uses `vl-local-key`. Keep tracked in scripts.
- **`llama-server`** in background mode (`&`) from terminal will be killed if terminal session ends — use systemd for persistence.
- **`CPUQuota`** in systemd can throttle gen speed. Remove `CPUQuota=` line when max throughput needed.
