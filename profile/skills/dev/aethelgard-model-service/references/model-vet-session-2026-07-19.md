# Model Vetting Session — 2026-07-19

## Context
Thorough vet of all local GGUF models after Qwen2.5-VL test. Decision: too big/slow, return to LFM stack.

## Models Tested

| Model | Size | Type | Speed (tok/s) | Vision Quality |
|-------|------|------|---------------|----------------|
| Qwen2.5-VL-7B-Instruct-Q4_K_M | 4.4GB+1.3GB mmproj | VL | ~10 gen | ✅ Great — color, OCR, complex |
| LFM2.5-1.2B-Nova-Function-Calling.Q6_K | 919MB | Text+FC | ~153 prompt, ~36 gen | N/A |
| LFM2-VL-GUI-SFT (full) | 679MB+101MB mmproj | VL | ~216 prompt, ~54 gen | ❌ Hallucinates |
| LFM2-VL-GUI-SFT (Q4_K_M) | 219MB+101MB mmproj | VL | ~306 prompt, ~127 gen | ❌ Hallucinates |
| LocateAnything-3B-Q4_K_M | 2.0GB+833MB mmproj | VL | ~79 prompt, ~19 gen | ❌ Mirrors prompts |

## Key Findings

### LFM 1.2B Nova is the keeper
- Fastest text model (153 tok/s prompt)
- Native function-calling — responds with `[{"name": "function", "arguments": {...}}]`
- Hermes delegation configured to use it on :8080
- Warp TUI AI can use it on :8080

### All non-Qwen VL models have broken vision
- Both LFM2-VL-GUI-SFT quants and LocateAnything-3B process images (confirmed in logs: "image processed in X ms") but output nonsense
- LFM-VL hallucinates descriptions ("A is in the middle", "Fashion is a picture of a picture")
- LocateAnything mirrors the question back ("What color is this?" → "what color is this?")
- Root cause: llama.cpp falls back to "peg-native" chat format for these models; `--chat-template chatml` flag doesn't fix it
- Qwen2.5-VL works because its GGUF has proper jinja chat template baked in
- Recommendation: if you need local vision, use Qwen2.5-VL despite the speed; otherwise skip local vision

### Background process management patterns
- DO NOT use `&` or `nohup` in foreground terminal commands — blocked
- Use `terminal(background=true)` for long-lived llama-server processes
- To kill: `kill -9 PID` by explicit PID, NOT `pkill -f "llama-server"` — pkill with -f can match too broadly and self-kill
- Check alive: `curl -s --connect-timeout X http://127.0.0.1:PORT/`
- Wait for load: poll with a loop checking / endpoint

### Testing patterns
- Large test scripts (vision+text+perf+edge cases) time out at 300s
- Split tests into focused batches: text, colors, OCR, complex scene, edge cases, performance
- Each batch should complete in < 90s

## Deployment Args (llama-server)

```bash
# LFM 1.2B Nova (text + function calling)
--model /home/craig/models/LFM2.5-1.2B-Nova-Function-Calling.Q6_K.gguf
--host 127.0.0.1 --port 8080
--api-key lfm-local-key
--ctx-size 49152
-ngl 99
--cache-type-k q8_0 --cache-type-v q8_0
--batch-size 512 --ubatch-size 256
--flash-attn auto
--threads 6 --mlock --no-warmup

# Qwen2.5-VL (vision + text, fallback only)
--model /home/craig/models/qwen2.5-vl-7b/Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf
--mmproj /home/craig/models/qwen2.5-vl-7b/mmproj-Qwen_Qwen2.5-VL-7B-Instruct-f16.gguf
--host 127.0.0.1 --port 8088
--api-key qwen-vl-key
--ctx-size 16384
-ngl 99
--image-min-tokens 1024
```

## Hermes Config (relevant section)
```yaml
delegation:
  model: LFM2.5-1.2B-Nova-Function-Calling.Q6_K.gguf
  base_url: http://127.0.0.1:8080/v1
  api_key: lfm-local-key
  api_mode: chat_completions
  request_overrides:
    temperature: 0.1
    top_k: 20
    top_p: 0.1
```
