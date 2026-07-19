# Vulkan 740M Configuration Reference

## Hardware
- GPU: AMD Radeon 740M (RDNA 3, 4 CUs)
- Driver: ROCm 6.x / Mesa Vulkan (RADV)
- VRAM: Shared system memory (no dedicated VRAM)

## Build Configuration
```bash
# Build llama.cpp with Vulkan
cmake -B build-vulkan \
  -DGGML_VULKAN=ON \
  -DGGML_CUDA=OFF \
  -DGGML_METAL=OFF \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_CURL=ON
cmake --build build-vulkan --config Release -j$(nproc)
```

## Runtime Flags (All Models)
```bash
# Common Vulkan flags
-ngl 99                    # Offload all layers to GPU
--flash-attn auto          # Use flash attention if available
--cache-type-k q8_0        # 8-bit quantized KV cache (keys)
--cache-type-v q8_0        # 8-bit quantized KV cache (values)
--batch-size 512           # Batch size for prompt processing
--ubatch-size 256          # Micro-batch size
--mlock                    # Lock memory
--no-warmup                # Skip warmup
```

## Model-Specific Configurations

### 1. LocateAnything-3B (Grounding) — Port 8087
```bash
./llama-server \
  -m ~/models/locateanything/locateanything-3b-Q4_K_M.gguf \
  --mmproj ~/models/locateanything/mmproj-locateanything-3b-bf16.gguf \
  -c 8192 \
  --flash-attn auto \
  -ngl 99 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --batch-size 512 \
  --ubatch-size 256 \
  --port 8087 \
  --special \
  --api-key locateanything-key
```
- Context: 8192 (projector + image tokens)
- Special mode: `--special` preserves `<ref><box>` tokens
- Quantization: Q4_K_M (model) + bf16 (mmproj)
- Performance: ~15-20 tok/s generation on 740M

### 2. LFM2-VL-GUI-SFT (VQA) — Port 8086
```bash
./llama-server \
  -m ~/models/lfm2-vl-gui-sft-q4_k_m.gguf \
  --mmproj ~/models/mmproj-lfm2-vl-gui-sft-q8_0.gguf \
  -c 32768 \
  --flash-attn auto \
  -ngl 99 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --batch-size 512 \
  --ubatch-size 256 \
  --port 8086 \
  --api-key lfm2-vl-key
```
- Context: 32768 (long conversation + image)
- Quantization: Q4_K_M (model) + Q8_0 (mmproj)
- Performance: ~10-15 tok/s generation on 740M

### 3. LFM2-1.2B-Nova (Text/Function) — Port 8080
```bash
./llama-server \
  -m ~/models/LFM2.5-1.2B-Nova-Function-Calling.Q6_K.gguf \
  -c 49152 \
  --flash-attn auto \
  -ngl 99 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --batch-size 512 \
  --ubatch-size 256 \
  --port 8080 \
  --api-key lfm-local-key
```
- Context: 49152
- Quantization: Q6_K
- Performance: ~38 tok/s generation on 740M
- Running via systemd: `hermes-lfm12.service`

## Memory Management

### System RAM Impact
With all 3 models loaded + KV caches:
- LocateAnything: ~2.5 GB (model) + ~0.5 GB (KV) = ~3 GB
- LFM2-VL: ~4 GB (model) + ~1 GB (KV) = ~5 GB
- LFM2-1.2B: ~2 GB (model) + ~1.5 GB (KV) = ~3.5 GB
- **Total: ~11.5 GB system RAM**

On 16 GB system: acceptable. On 8 GB: swap pressure.

### q8_0 KV Cache Savings
- fp16 KV: 2 bytes × 2 (K+V) × layers × heads × head_dim × ctx
- q8_0 KV: 1 byte × 2 × layers × heads × head_dim × ctx + overhead
- **~50% KV memory reduction** with minimal quality loss

## Troubleshooting

### "Vulkan initialization failed"
```bash
# Check Vulkan support
vulkaninfo | grep -E "(deviceName|deviceType)"
# Ensure RADV is active
export RADV_PERFTEST=aco
```

### OOM on model load
```bash
# Reduce context size
-c 4096  # instead of 8192/32768

# Reduce batch size
--batch-size 256 --ubatch-size 128

# Use lower quantization
Q3_K_M instead of Q4_K_M
```

### Slow generation
```bash
# Ensure Vulkan is actually used
-ngl 99  # must be 99, not 0
--flash-attn auto

# Check GPU utilization
watch -n 1 radeontop
```

## Performance Baseline (740M, 16GB RAM)

| Model | Quant | Context | Gen Speed | VRAM |
|-------|-------|---------|-----------|------|
| LocateAnything-3B | Q4_K_M | 8k | ~15-20 tok/s | ~3 GB |
| LFM2-VL-GUI-SFT | Q4_K_M | 32k | ~10-15 tok/s | ~5 GB |
| LFM2-1.2B-Nova | Q6_K | 48k | ~38 tok/s | ~3.5 GB |

## Service Management

### Systemd Service (LFM2-1.2B)
```ini
# ~/.config/systemd/user/hermes-lfm12.service
[Unit]
Description=Hermes LFM2-1.2B Nova Server
After=network.target

[Service]
Type=simple
ExecStart=/home/craig/llama.cpp-yuuko-grounders/build-vulkan/bin/llama-server \
  -m /home/craig/models/LFM2.5-1.2B-Nova-Function-Calling.Q6_K.gguf \
  -c 49152 --flash-attn auto -ngl 99 --cache-type-k q8_0 --cache-type-v q8_0 \
  --batch-size 512 --ubatch-size 256 --port 8080 --api-key lfm-local-key
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

```bash
systemctl --user enable --now hermes-lfm12
journalctl --user -u hermes-lfm12 -f
```

### Manual tmux Sessions (Grounding + VQA)
```bash
# Session 1: LocateAnything
tmux new -s locate
cd ~/llama.cpp-yuuko-grounders/build-vulkan/bin
./llama-server -m ~/models/locateanything/locateanything-3b-Q4_K_M.gguf --mmproj ~/models/locateanything/mmproj-locateanything-3b-bf16.gguf -c 8192 --flash-attn auto -ngl 99 --cache-type-k q8_0 --cache-type-v q8_0 --batch-size 512 --ubatch-size 256 --port 8087 --special

# Session 2: LFM2-VL
tmux new -s lfm2vl
cd ~/llama.cpp-yuuko-grounders/build-vulkan/bin
./llama-server -m ~/models/lfm2-vl-gui-sft-q4_k_m.gguf --mmproj ~/models/mmproj-lfm2-vl-gui-sft-q8_0.gguf -c 32768 --flash-attn auto -ngl 99 --cache-type-k q8_0 --cache-type-v q8_0 --batch-size 512 --ubatch-size 256 --port 8086
```

## Quick Health Check
```bash
# All ports responding
for port in 8080 8086 8087 8088; do
  echo "Port $port:"
  curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$port/health || echo "DOWN"
  echo
done

# Test grounding
curl -s -X POST http://127.0.0.1:8088/ground -H "Content-Type: application/json" \
  -d '{"image": "'$(base64 -w0 test.png)'", "prompt": "button"}' | python3 -m json.tool

# Test VQA
curl -s -X POST http://127.0.0.1:8088/ground -H "Content-Type: application/json" \
  -d '{"image": "'$(base64 -w0 test.png)'", "prompt": "What do you see?"}' | python3 -m json.tool
```