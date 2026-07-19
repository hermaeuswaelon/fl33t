# Model Testing Patterns (Vetted 2026-07-19)

## Split Test Batches to Avoid 300s Timeout

Large monolithic test scripts (vision+text+perf+edge+cases) will time out at 300s in execute_code. Split into focused batches:

### Batch 1: Text (8-10 tests, ~50s)
```python
# Basic Q&A, system prompt, multi-turn, code gen, JSON, i18n, long context, high temp
def test(name, fn): ...
ok("Basic 2+2", lambda: req(...))
```

### Batch 2: Vision Colors (8-10 tests, ~60s)
```python
# Solid colors, light/dark, tiny/medium/wide sizes, gradient
ok("Red", lambda: vision("red.png", "What color? One word.", 5))
```

### Batch 3: OCR + Complex (5-8 tests, ~80s)
```python
# Text extraction, special chars, multi-image comparison, error cases
ok("OCR: Hello World", lambda: vision("hello.png", "Read the text exactly.", 30))
```

### Batch 4: Edge Cases (5-6 tests, ~30s)
```python
# Empty prompt, 10k char, emoji, unicode mix, zero temp
```

### Batch 5: Performance (separately, ~90-120s)
```python
# Bench short/medium/long text, vision, OCR — n=3-5 each with warmup
```

## Known Model Behaviours

| Model | Text | Vision | Function Calling |
|-------|------|--------|-----------------|
| LFM 1.2B Nova | ✅ Fast (153 tok/s) | N/A | ✅ Native FC output |
| Qwen2.5-VL 7B | ✅ 10 tok/s | ✅ Works | ❓ Untested |
| LFM-VL GUI SFT | ✅ 127 tok/s | ❌ Hallucinates | ❓ |
| LocateAnything 3B | ✅ 19 tok/s | ❌ Mirrors prompt | ❓ |

## Vision API Test Template
```python
def vision_req(path, text, max_tokens=50):
    import base64, urllib.request, json
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    payload = {
        "model": "model-name",
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
            {"type": "text", "text": text}
        ]}],
        "max_tokens": max_tokens,
        "temperature": 0.1
    }
    r = urllib.request.Request(
        f"{BASE_URL}/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    )
    with urllib.request.urlopen(r, timeout=90) as resp:
        return json.loads(resp.read().decode())
```

## Image Creation for Tests
```python
from PIL import Image, ImageDraw

# Solid color
Image.new("RGB", (200,200), (255,0,0)).save("/tmp/vt/red.png")

# Text image
img = Image.new("RGB", (400,150), (255,255,255))
draw = ImageDraw.Draw(img)
draw.text((10, 10), "Hello World", fill=(0,0,0))
img.save("/tmp/vt/hello.png")
```
