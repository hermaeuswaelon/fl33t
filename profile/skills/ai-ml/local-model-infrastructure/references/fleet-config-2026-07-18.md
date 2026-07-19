# Active Fleet Configuration — 2026-07-18

## Models in ~/models/
```
 919M  LFM2.5-1.2B-Nova-Function-Calling.Q6_K.gguf        # 🜂 Primary tool-caller
 1.1G  qwen3-1.7b-instruct-q4_k_m.gguf                    # ⚡ Code/terminal
 1.6G  Qwen3-1.7B-Q6_K-Instruct.gguf                      # ⚡ Spare (higher quant)
 2.3G  Huihui-granite-4.1-3b-abliterated.i1-Q5_K_M.gguf   # ⚙️ Automation/JSON
 2.0G  LFM2-2.6B-Uncensored-X64.i1-Q6_K.gguf              # Reserve
 6.5G  Huihui-LFM2.5-8B-A1B-abliterated.i1-Q6_K.gguf      # Heavy lifter
 4.7G  Gemma-4-E2B-Uncensored-HauhauCS-Aggressive-Q8_K_P.gguf
 940M  mmproj-Gemma-4-E2B-Uncensored-HauhauCS-Aggressive-f16.gguf  # multimodal projector
```

## Running Services

| Service | Port | Model | API Key | Purpose |
|---------|------|-------|---------|---------|
| lfm-server | 8080 | LFM2.5-1.2B-Nova (919MB) | lfm-local-key | Agent tool-caller |
| qwen3-server | 8082 | qwen3-1.7b-instruct Q4_K_M (1.1GB) | qwen-local-key | Code/terminal work |
| granite-server | 8083 | Granite 4.1 3B abliterated Q5_K_M (2.3GB) | granite-local-key | Automation/JSON output |

## Service Files
All at `~/.config/systemd/user/`:
- `lfm-server.service`
- `qwen3-server.service`
- `granite-server.service`

## Management
`model-switch list|start|stop|restart|test|curl [name]` at `~/.local/bin/model-switch`

## Memory Budget
Total active: ~6.0 GB (LFM 1.1 + Qwen3 1.8 + Granite 3.1)
Available: 10 GB → 4 GB headroom ✅
