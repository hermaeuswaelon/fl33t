---
name: local-model-deployment
description: Deploy, test, and manage local GGUF models with llama.cpp — text and vision. Covers vetting methodology, known compat issues, background process lifecycle, and fallback patterns.
trigger: user asks about local models, deploying GGUF, testing VL models, llama-server setup, model vetting, or choosing between local models.
domain: devops
---

# Local Model Deployment

Deploy llama.cpp GGUF models as local API servers for text inference and vision tasks.

## Quickstart

### Launch a text model (fast)
```bash
~/llama.cpp-yuuko-grounders/build-vulkan/bin/llama-server \
  --model <path/to/model.gguf> \
  --host 127.0.0.1 --port 8080 \
  --api-key <key> \
  --ctx-size 49152 -ngl 99 \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --batch-size 512 --ubatch-size 256 \
  --flash-attn auto --threads 6 \
  --mlock --no-warmup
```

### Launch a vision model (slow, for vision tasks)
```bash
~/llama.cpp-yuuko-grounders/build-vulkan/bin/llama-server \
  --model <path/to/vl-model.gguf> \
  --mmproj <path/to/mmproj.gguf> \
  --host 127.0.0.1 --port 8088 \
  --api-key <key> \
  --ctx-size 16384 -ngl 99 \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --batch-size 256 --ubatch-size 128 \
  --flash-attn auto --threads 6 \
  --mlock --no-warmup \
  --image-min-tokens 1024
```

## Vetting Methodology

When evaluating which local model(s) to keep:

1. **Survey** — `ps aux | grep llama` / `lsof -i :<port>` for running servers
2. **Categorize** — text model vs vision model, size, load time
3. **Test text** — basic QA, system prompt adherence, function calling, JSON mode, multi-turn memory, high-temp creativity
4. **Test vision** — solid-color PNGs via base64 data URI (128px+), OCR (Hello World image), complex scene description
5. **Verdict** — max utility = one fast text model + one working vision model (if any)

## Known-Compatible Models

### ✅ Text models (confirmed working)
| Model | Speed | Notes |
|-------|-------|-------|
| LFM2.5-1.2B-Nova-Function-Calling Q6_K | ~153 tok/s | Function calling native. Best text model. |

### ✅ Vision models (confirmed working)
| Model | Speed | Notes |
|-------|-------|-------|
| Qwen2.5-VL-7B-Instruct Q4_K_M | ~15 tok/s gen, ~17s/image | Only reliable VL. Requires base64 data URIs. |

### ❌ Vision models (broken — do not use)
| Model | Failure mode |
|-------|-------------|
| LocateAnything-3B Q4_K_M | Prompt-mirroring regardless of chat template |
| LFM2-VL-GUI-SFT (any quant) | Hallucinates color/position, mirrors prompts |

## Vision API — Critical Details

### Image format for Qwen2.5-VL
Use **base64 data URIs** only. URLs and broken/small PNGs fail with "Failed to load image or audio file".

Generate test images with Python:
```python
import base64, struct, zlib

def create_png_dataurl(w, h, r, g, b):
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    raw = b''
    for y in range(h):
        raw += b'\x00' + bytes([r,g,b]) * w
    idat = chunk(b'IDAT', zlib.compress(raw))
    iend = chunk(b'IEND', b'')
    png = sig + ihdr + idat + iend
    return f'data:image/png;base64,{base64.b64encode(png).decode()}'
```

### Vision request format
```json
{
  "model": "qwen2.5-vl",
  "messages": [
    {"role": "user", "content": [
      {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
      {"type": "text", "text": "What color is this?"}
    ]}
  ],
  "max_tokens": 50
}
```

## Background Process Lifecycle

- Use Hermes `terminal(background=true, notify_on_complete=true)` — NOT shell `&` backgrounding
- Shell `&` processes get reaped when the conversation context switches
- Use `lsof -ti:<port>` to find orphaned servers, then `kill -9`
- Port mapping convention: `:8080` = text model, `:8088` = vision model

## Pitfalls

- **No auto-restart**: Do NOT create systemd services with `Restart=on-failure` or timers. Manual launch only.
- **Cross-profile write guard**: `~/.hermes/profiles/<profile>/` files are isolated per shell session. Use `cross_profile=True` only on explicit user direction.
- **VL != VL**: Not all VL models work with llama.cpp's multimodal serving even with matching mmproj. Always test with a simple solid-color base64 PNG first.
- **Model size vs speed**: 7B vision models are ~17s/image on 14GB RAM / 512MB VRAM. Don't expect real-time.
