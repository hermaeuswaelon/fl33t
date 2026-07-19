#!/usr/bin/env python3
"""
Vision Router Server Template
Unified HTTP endpoint for LocateAnything (grounding) + LFM2-VL (VQA) routing.
Copy and modify for production deployment.
"""
import os
import sys
import json
import base64
import tempfile
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration - MODIFY FOR YOUR ENVIRONMENT
LOCATE_SERVER = "http://127.0.0.1:8087"      # LocateAnything-3B (grounding)
VQA_SERVER = "http://127.0.0.1:8086"         # LFM2-VL-GUI-SFT (VQA)
TEXT_SERVER = "http://127.0.0.1:8080"        # LFM2-1.2B-Nova (text)
DEFAULT_RESIZE = [800, 600]

# Grounding prompts that route to LocateAnything
GROUNDING_KEYWORDS = [
    "locate", "find", "detect", "box", "bounding", "where is",
    "button", "icon", "text field", "input", "link", "menu",
    "dropdown", "checkbox", "radio", "tab", "slider", "dialog",
    "tooltip", "sidebar", "card", "form", "search", "navigation"
]

# VQA prompts that route to LFM2-VL
VQA_KEYWORDS = [
    "what", "describe", "explain", "read", "text", "content",
    "color", "layout", "design", "screenshot", "ui", "interface"
]


def is_grounding_prompt(prompt: str) -> bool:
    """Determine if prompt should use grounding model."""
    prompt_lower = prompt.lower().strip()
    
    # Explicit grounding triggers
    for kw in GROUNDING_KEYWORDS:
        if kw in prompt_lower:
            return True
    
    # Short noun phrases likely grounding
    words = prompt_lower.split()
    if len(words) <= 3 and not any(q in prompt_lower for q in ["what", "how", "why", "describe"]):
        return True
    
    return False


def save_base64_image(b64_data: str, resize: list = None) -> str:
    """Save base64 image to temp file, optionally resize."""
    # Handle data URI prefix
    if b64_data.startswith("data:image"):
        b64_data = b64_data.split(",", 1)[1]
    
    img_bytes = base64.b64decode(b64_data)
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(img_bytes)
        temp_path = f.name
    
    if resize:
        try:
            from PIL import Image
            img = Image.open(temp_path)
            img = img.resize(resize, Image.Resampling.LANCZOS)
            img.save(temp_path)
        except Exception:
            pass  # Use original if resize fails
    
    return temp_path


def call_locateanything(image_path: str, prompt: str) -> dict:
    """Call LocateAnything server via vision_router.py subprocess."""
    cmd = [
        sys.executable, "/home/craig/tools/vision_router.py",
        "--image", image_path,
        "--prompt", prompt,
        "--resize", str(DEFAULT_RESIZE[0]), str(DEFAULT_RESIZE[1])
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if result.returncode != 0:
        return {"error": result.stderr, "route": "locateanything", "model": "locateanything-3b"}
    
    return json.loads(result.stdout.strip())


def call_lfm2_vl(image_path: str, prompt: str) -> dict:
    """Call LFM2-VL server via OpenAI-compatible API."""
    import requests
    
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    payload = {
        "model": "lfm2-vl-gui-sft",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
            ]
        }],
        "max_tokens": 512,
        "temperature": 0.1
    }
    
    try:
        resp = requests.post(
            f"{VQA_SERVER}/v1/chat/completions",
            json=payload,
            headers={"Authorization": "Bearer lfm2-vl-key"},
            timeout=120
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "route": "lfm2-vl",
            "model": "lfm2-vl-gui-sft",
            "prompt": prompt,
            "response": data["choices"][0]["message"]["content"],
            "raw_response": data["choices"][0]["message"]["content"]
        }
    except Exception as e:
        return {"error": str(e), "route": "lfm2-vl", "model": "lfm2-vl-gui-sft"}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "vision-router"})


@app.route("/ground", methods=["POST"])
def ground():
    """
    Unified grounding/VQA endpoint.
    
    Request:
    {
        "image": "base64_string_or_data_uri",
        "prompt": "find button" or "what do you see?",
        "resize": [800, 600]  // optional
    }
    
    Response:
    {
        "route": "locateanything" | "lfm2-vl",
        "model": "model-name",
        "predictions": [...],  // for grounding
        "response": "...",      // for VQA
        "raw_response": "...",
        "image_size": [w, h]
    }
    """
    data = request.get_json()
    
    if not data or "image" not in data or "prompt" not in data:
        return jsonify({"error": "Missing 'image' or 'prompt'"}), 400
    
    image_b64 = data["image"]
    prompt = data["prompt"]
    resize = data.get("resize", DEFAULT_RESIZE)
    
    # Save image
    temp_path = save_base64_image(image_b64, resize)
    
    try:
        # Route based on prompt
        if is_grounding_prompt(prompt):
            result = call_locateanything(temp_path, prompt)
        else:
            result = call_lfm2_vl(temp_path, prompt)
        
        # Add image size info
        try:
            from PIL import Image
            with Image.open(temp_path) as img:
                result["image_size"] = list(img.size)
        except:
            result["image_size"] = resize
        
        return jsonify(result)
    
    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)


@app.route("/ground/batch", methods=["POST"])
def ground_batch():
    """
    Batch grounding endpoint.
    
    Request:
    {
        "images": ["base64_1", "base64_2", ...],
        "prompts": ["button", "icon", ...],
        "resize": [800, 600]
    }
    
    Response: { "results": [ {...}, {...}, ... ] }
    """
    data = request.get_json()
    
    if not data or "images" not in data or "prompts" not in data:
        return jsonify({"error": "Missing 'images' or 'prompts'"}), 400
    
    images = data["images"]
    prompts = data["prompts"]
    resize = data.get("resize", DEFAULT_RESIZE)
    
    results = []
    for i, (img_b64, prompt) in enumerate(zip(images, prompts)):
        temp_path = save_base64_image(img_b64, resize)
        try:
            if is_grounding_prompt(prompt):
                result = call_locateanything(temp_path, prompt)
            else:
                result = call_lfm2_vl(temp_path, prompt)
            result["batch_index"] = i
            results.append(result)
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    return jsonify({"results": results})


if __name__ == "__main__":
    port = int(os.environ.get("VISION_ROUTER_PORT", 8088))
    print(f"Starting Vision Router on port {port}")
    print(f"  LocateAnything: {LOCATE_SERVER}")
    print(f"  LFM2-VL: {VQA_SERVER}")
    app.run(host="0.0.0.0", port=port, threaded=True)