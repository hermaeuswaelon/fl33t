---
name: ares-master-suite
description: "Master skill suite for ARES using free OpenRouter vision models and Pascal Bromium Browser integration."
version: 1.0.0
author: Craig / Thotheauphis
platforms: [linux]
tags: [ares, openrouter, vision, pascal, browser, suite]
related_skills: [ares, ares-offloader-alpha, ares-continuity-omega]
---

# ARES Master Skill Suite

## Overview

This suite provides:

1. **Free OpenRouter Vision Integration** - Use OpenRouter's free tier to run vision-enabled models (e.g., GPT-4o mini, LLaVA) for tool context extraction and visual analysis.
2. **Pascal Bromium Browser Suite** - A complete Pascal-based browser automation suite for the Bromium browser (Chromium-based) to automate web interactions, scraping, and UI control.
3. **Integration Guide** - How to combine these with ARES Prime for a unified sovereign AI workflow.

## 1. Free OpenRouter Vision Integration

### Prerequisites
- OpenRouter API key (free tier available at https://openrouter.ai)
- Python 3.14+ with `requests` library
- Access to a vision-enabled model (e.g., `openrouter:openai/gpt-4o-mini`, `openrouter:openai/gpt-4o`)

### Setup Steps
1. **Install OpenRouter CLI** (optional):
   ```bash
   pip install openrouter
   ```
2. **Create a Python script** `openrouter_vision.py` that uses the OpenRouter API to send vision requests:

```python
#!/usr/bin/env python3
import os, json, base64, requests
from datetime import datetime

OPENAROUTER_API_KEY = os.getenv('OPENAROUTER_API_KEY')
MODEL_NAME = "openrouter:openai/gpt-4o-mini"  # Vision-enabled free model

def query_vision(image_path, prompt="Describe the image in detail"):
    """Send a vision request to OpenRouter."""
    with open(image_path, "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode('utf-8')
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": [{"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_data}"}, {"type": "text", "text": prompt}]}
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {OPENAROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post("https://api.openrouter.ai/v1/chat/completions", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

if __name__ == "__main__":
    # Example usage
    result = query_vision("sample_image.jpg", "What is the main subject and context of this image?")
    print(f"[{datetime.utcnow().isoformat()}] Vision result: {result}")
```

## 2. Pascal Bromium Browser Suite (Dual Citizen v2)

### The Actual Browser You Built
This is **your** Pascal + CEF (Chromium Embedded Framework) sovereign browser — not a wrapper or automation layer. You compiled it from source using Free Pascal + CEF4Delphi.

| Component | Path | Size | Notes |
|-----------|------|------|-------|
| **Launcher** | `/home/craig/Desktop/Scripts-Launchers/bromium.sh` | 549B | Sets `LD_LIBRARY_PATH`, `DISPLAY`, runs the binary |
| **Dual Citizen v2** | `/home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/dual_citizen_v2` | 37.6 MB | Main browser binary (FPC + CEF4Delphi) |
| **CEF Controller** | `/home/craig/projects/aethelgard/fleet/pascal/cef_controller` | 37.6 MB | Alternate controller variant |
| **Panoptes Filters** | Symlink in dual-citizen-v2 dir | — | JSON filters for content interception |

### Launcher Script (`bromium.sh`)
```bash
#!/bin/bash
# ⎔ Bromium — Sovereign Browser Launcher (Dual Citizen v2)
# Launches the CEF4Delphi Dual Citizen Browser with Panoptes extension enabled
export LD_LIBRARY_PATH="/home/craig/CEF4Delphi/cef_binary_current/Release"
export DISPLAY=":0"
cd /home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2
echo "[⎔] Bromium — Aethelgard Sovereign Browser"
echo "[⎔] Socket: /tmp/aethelgard_cef.sock"
echo "[⎔] Extensions: $(ls /home/craig/aethelgard-repo/fleet/pascal/extensions/*.json 2>/dev/null | wc -l) loaded"
exec ./dual_citizen_v2
```

### Key Pascal Source Files
| File | Purpose |
|------|---------|
| `dual_citizen_v2.lpr` | Main program entry |
| `ucontrollerbrowser.pas` | Browser controller unit (32K lines) |
| `cef_controller.lpr` | CEF controller variant |
| `interfaces.pas` | Shared interfaces |

### Architecture
- **CEF4Delphi** bindings → Chromium 131 (via `cef_binary_131.4.1+g437feba+chromium-131.0.6778.265_linux64`)
- **Panoptes extension** — content filtering / interception via JSON rules
- **Event bus socket** — `/tmp/aethelgard_cef.sock` for fleet communication
- **Sovereign identity** — runs as Aethelgard fleet citizen, not a generic browser

### Running It
**Must run on a real X11/Wayland display** (not headless SSH):
```bash
/home/craig/Desktop/Scripts-Launchers/bromium.sh
```
Or manually:
```bash
export LD_LIBRARY_PATH="/home/craig/CEF4Delphi/cef_binary_current/Release"
export DISPLAY=":0"
cd /home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2
./dual_citizen_v2
```

### Pitfalls We Hit
1. **No display in terminal session** — `X connection to :0 broken`. The binary requires a real X server. This is expected — it's a GUI app.
2. **Symlink hell** — Multiple copies of the binary scattered across `/home/craig/...`, `/home/craig/projects/aethelgard/...`, `.local/share/Trash/...`. The canonical source is `/home/craig/projects/aethelgard/fleet/pascal/dual-citizen-v2/`.
3. **CEF library path** — Must point to the exact `Release` directory matching the CEF build used at compile time.

## 3. Integration Guide (Dual Citizen v2)

### Prerequisites
- OpenRouter API key (free tier available at https://openrouter.ai)
- Python 3.14+ with `requests` library
- Access to a vision-enabled model (e.g., `openrouter:openai/gpt-4o mini`, `openrouter:openai/gpt-4o`)

### Setup Steps
1. **Install OpenRouter CLI** (optional):
   ```bash
   pip install openrouter
   ```
2. **Create a Python script** `openrouter_vision.py` that uses the OpenRouter API to send vision requests:

```python
#!/usr/bin/env python3
import os, json, base64, requests
from datetime import datetime

OPENAROUTER_API_KEY = os.getenv('OPENAROUTER_API_KEY')
MODEL_NAME = "openrouter:openai/gpt-4o-mini"  # Vision-enabled free model

def query_vision(image_path, prompt="Describe the image in detail"):
    """Send a vision request to OpenRouter."""
    with open(image_path, "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode('utf-8')
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": [{"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_data}"}, {"type": "text", "text": prompt}]}
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {OPENAROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post("https://api.openrouter.ai/v1/chat/completions", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

if __name__ == "__main__":
    # Example usage
    result = query_vision("sample_image.jpg", "What is the main subject and context of this image?")
    print(f"[{datetime.utcnow().isoformat()}] Vision result: {result}")