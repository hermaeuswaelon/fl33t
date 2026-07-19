# systemd Service Templates for llama.cpp with Vulkan

## Template: Text-Only Model (hermes-lfm12)

```ini
[Unit]
Description=Hermes LFM 1.2B (Nova) - Fast Planner Model
After=network.target

[Service]
Type=simple
# Critical: Vulkan backend libraries live in build directory
Environment=LD_LIBRARY_PATH=/home/craig/llama.cpp-yuuko-grounders/build-vulkan/bin
# Run directly from build directory - do NOT copy to /usr/local/bin
ExecStart=/home/craig/llama.cpp-yuuko-grounders/build-vulkan/bin/llama-server \
    --model /home/craig/models/LFM2.5-1.2B-Nova-Function-Calling.Q6_K.gguf \
    --host 127.0.0.1 --port 8080 \
    --api-key lfm-local-key \
    --ctx-size 49152 \
    -ngl 99 \
    --cache-type-k q8_0 --cache-type-v q8_0 \
    --batch-size 512 --ubatch-size 256 \
    --flash-attn auto \
    --threads 6 --mlock --no-warmup
Restart=on-failure
RestartSec=5
Nice=5
StandardOutput=journal
StandardError=journal
# Allow mlock for model weights
LimitMEMLOCK=infinity

[Install]
WantedBy=default.target
```

## Template: Vision-Language Model (hermes-vl)

```ini
[Unit]
Description=Hermes LFM2-VL-GUI-SFT Fine-tuned GUI Vision Model
After=network.target

[Service]
Type=simple
Environment=LD_LIBRARY_PATH=/home/craig/llama.cpp-yuuko-grounders/build-vulkan/bin
ExecStart=/home/craig/llama.cpp-yuuko-grounders/build-vulkan/bin/llama-server \
    --model /home/craig/models/lfm2-vl-gui-sft-q4_k_m.gguf \
    --mmproj /home/craig/models/mmproj-lfm2-vl-gui-sft-q8_0.gguf \
    --host 127.0.0.1 --port 8086 \
    --api-key vl-local-key \
    --ctx-size 8192 \
    -ngl 99 \
    --cache-type-k q8_0 --cache-type-v q8_0 \
    --batch-size 256 --ubatch-size 128 \
    --flash-attn auto \
    --threads 6 --mlock --no-warmup
Restart=on-failure
RestartSec=10
NoNewPrivileges=true
LimitMEMLOCK=infinity
CPUQuota=50%

[Install]
WantedBy=default.target
```

## Key Parameters Explained

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `-ngl 99` | Full GPU offload | Offload all 99 layers to Vulkan; CPU fallback for unsupported ops |
| `--cache-type-k/v q8_0` | 8-bit KV cache | Reduces VRAM by ~4x vs fp16; negligible quality loss |
| `--flash-attn auto` | Auto Flash Attention | Enables fused attention kernel on Vulkan when available |
| `--mlock` | Lock memory | Prevents model swap; requires `LimitMEMLOCK=infinity` |
| `--no-warmup` | Skip warmup | Faster startup; first request pays warmup cost |
| `--batch-size 512` | Large batch | Better GPU utilization for prompt processing |
| `CPUQuota=50%` (VL) | Limit CPU | Vision model offloads less to GPU; cap CPU to leave headroom |

## Common Pitfalls

1. **Port conflict**: Another `llama-server` on same port → `journalctl` shows "couldn't bind HTTP server socket". Fix: `ss -tlnp | grep :PORT` then kill.
2. **Library path wrong**: Exit code 127 + "libllama-server-impl.so not found". Fix: `Environment=LD_LIBRARY_PATH=...` pointing to build-vulkan/bin.
3. **MLOCK fails**: "failed to mlock buffer: Cannot allocate memory". Fix: `LimitMEMLOCK=infinity` in service + `ulimit -l unlimited` for user.
4. **Model not found**: Check `--model` path exists and is readable by user.
5. **VL model mmproj mismatch**: `--mmproj` must match quantization (q8_0 projector for q4_k_m model works; q4_0 projector may not).