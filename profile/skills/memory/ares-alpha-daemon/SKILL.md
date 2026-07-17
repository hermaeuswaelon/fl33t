---
name: ares-alpha-daemon
description: ARES Offloader Alpha — Tool Context Compression Daemon. Runs as background service, compresses every tool result via free model (Groq Llama 3.1 8B), injects summaries into prime context.
version: 1.0.0
author: ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, alpha, offload, tool-context, compression, groq, daemon, service]
system: true
---

# ⚙️ ARES Offloader Alpha — Tool Context Compression Daemon

## Service Specification

**Model**: `groq:llama-3.1-8b-instant` (free, 500+ tok/s, 8K context, JSON mode)
**Transport**: Unix socket `/tmp/ares/alpha.sock` + HTTP `:9381`
**Queue**: Redis/embedded queue for async processing
**Output**: Forge Vault + memcustd Tier 1 + prime context injection

---

## Daemon Loop

```python
#!/usr/bin/env python3
"""
ARES Alpha Daemon — Tool Context Compressor
Runs continuously, processes tool results from queue, emits compressed summaries.
"""

import asyncio
import json
import os
import hashlib
import time
from dataclasses import dataclass, asdict
from typing import Optional
import httpx
from aiohttp import web

# ─── Configuration ─────────────────────────────────────────────────────

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
ALPHA_MODEL = "llama-3.1-8b-instant"
SOCKET_PATH = "/tmp/ares/alpha.sock"
HTTP_PORT = 9381
QUEUE_MAX = 1000
PROCESS_INTERVAL = 0.1  # seconds between queue checks

# ─── Data Structures ───────────────────────────────────────────────────

@dataclass
class ToolResult:
    tool: str
    query: str
    result: dict
    context: dict
    timestamp: float
    query_hash: str

@dataclass
class AlphaSummary:
    tool: str
    query_hash: str
    summary: str
    key_findings: list
    artifacts: list
    followup_hints: list
    tokens_saved: int
    glyphs: list
    timestamp: float
    compression_ratio: float

# ─── Compression Engine ────────────────────────────────────────────────

ALPHA_SYSTEM_PROMPT = """You are OFFLOADER ALPHA — Tool Context Compressor.
Compress raw tool output into DENSE, STRUCTURED JSON summaries.

RULES:
1. Output ONLY valid JSON matching the AlphaSummary schema.
2. Preserve ALL actionable findings: IPs, credentials, vulnerabilities, paths, configs, hostnames.
3. Discard: progress bars, verbose logs, boilerplate, handled errors, duplicate lines.
4. Target 90% token reduction.
5. Tag with glyphs: ⟁=phase, 🝮=core insight, ⚡=alert, 🜂=action needed, ♱=sovereign finding.
6. Include followup_hints for prime's next decisions.

SCHEMA:
{
  "tool": "string",
  "query_hash": "string",
  "summary": "string (1-3 sentences, dense)",
  "key_findings": ["string", ...],
  "artifacts": ["string", ...],
  "followup_hints": ["string", ...],
  "tokens_saved": "int",
  "glyphs": ["string", ...],
  "compression_ratio": "float (0-1)"
}"""

async def compress_tool_result(tool_result: ToolResult, http_client: httpx.AsyncClient) -> AlphaSummary:
    """Compress a single tool result using Groq."""
    
    # Prepare input
    raw_text = json.dumps(tool_result.result, indent=2)[:50000]  # Cap input
    original_tokens = len(raw_text.split()) * 1.3  # Rough estimate
    
    user_prompt = f"""Tool: {tool_result.tool}
Query: {tool_result.query}
Context: {json.dumps(tool_result.context)}

Raw Output:
{raw_text}

Compress now. Output ONLY JSON."""

    payload = {
        "model": ALPHA_MODEL,
        "messages": [
            {"role": "system", "content": ALPHA_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 2048,
        "response_format": {"type": "json_object"}
    }
    
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    resp = await http_client.post(GROQ_ENDPOINT, json=payload, headers=headers, timeout=30.0)
    resp.raise_for_status()
    data = resp.json()
    
    # Parse and validate
    summary_data = json.loads(data["choices"][0]["message"]["content"])
    summary_data["timestamp"] = time.time()
    summary_data["query_hash"] = tool_result.query_hash
    summary_data["tokens_saved"] = int(original_tokens - len(json.dumps(summary_data).split()) * 1.3)
    summary_data["compression_ratio"] = summary_data["tokens_saved"] / max(original_tokens, 1)
    
    return AlphaSummary(**summary_data)

# ─── Storage & Distribution ────────────────────────────────────────────

async def store_summary(summary: AlphaSummary):
    """Store in Forge Vault, push to memcustd, inject to prime."""
    
    # 1. Forge Vault (persistent)
    await forge_vault_store("alpha_summaries", summary.query_hash, asdict(summary))
    
    # 2. memcustd Tier 1 (hot)
    await memcustd_push("alpha_summary", asdict(summary))
    
    # 3. Prime context injection (via socket)
    await prime_inject("alpha", asdict(summary))

async def forge_vault_store(collection: str, key: str, data: dict):
    """Store in Forge Memory Vault via CLI."""
    import subprocess
    # forge-memory store --collection alpha_summaries --key <hash> --data <json>
    pass  # Implementation uses forge-memory CLI

async def memcustd_push(tag: str, data: dict):
    """Push to memcustd hot context."""
    async with httpx.AsyncClient() as client:
        # POST to memcustd /domain/load with domain=alpha_<tool>
        await client.post(
            "http://127.0.0.1:9379/domain/load",
            json={"domain": f"alpha_{data['tool']}", "context": json.dumps(data)},
            timeout=5.0
        )

async def prime_inject(channel: str, data: dict):
    """Inject into prime context via Hermes hook."""
    # This would integrate with Hermes context injection system
    pass

# ─── Queue Processor ──────────────────────────────────────────────────

class AlphaQueue:
    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=QUEUE_MAX)
        self.processing = set()
    
    async def enqueue(self, tool_result: ToolResult):
        await self.queue.put(tool_result)
    
    async def process_loop(self, http_client: httpx.AsyncClient):
        while True:
            try:
                tool_result = await asyncio.wait_for(self.queue.get(), timeout=PROCESS_INTERVAL)
                self.processing.add(tool_result.query_hash)
                
                try:
                    summary = await compress_tool_result(tool_result, http_client)
                    await store_summary(summary)
                    print(f"[Alpha] Compressed {tool_result.tool} → {summary.tokens_saved} tokens saved")
                except Exception as e:
                    print(f"[Alpha] Error processing {tool_result.tool}: {e}")
                finally:
                    self.processing.discard(tool_result.query_hash)
                    self.queue.task_done()
            except asyncio.TimeoutError:
                continue  # Loop continues

# ─── HTTP API ──────────────────────────────────────────────────────────

async def http_submit(request):
    """POST /submit - Submit tool result for compression."""
    data = await request.json()
    tool_result = ToolResult(
        tool=data["tool"],
        query=data["query"],
        result=data["result"],
        context=data.get("context", {}),
        timestamp=time.time(),
        query_hash=hashlib.sha256(f"{data['tool']}:{data['query']}".encode()).hexdigest()[:16]
    )
    await request.app["queue"].enqueue(tool_result)
    return web.json_response({"status": "queued", "hash": tool_result.query_hash})

async def http_status(request):
    """GET /status - Daemon status."""
    queue = request.app["queue"]
    return web.json_response({
        "status": "running",
        "queue_depth": queue.queue.qsize(),
        "processing": len(queue.processing),
        "model": ALPHA_MODEL,
        "uptime_seconds": time.time() - request.app["start_time"]
    })

async def http_health(request):
    """GET /health - Health check."""
    return web.json_response({"status": "ok", "model": ALPHA_MODEL})

# ─── Main ──────────────────────────────────────────────────────────────

async def main():
    # Ensure socket directory
    os.makedirs("/tmp/ares", exist_ok=True)
    
    # Clean stale socket
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)
    
    app = web.Application()
    app["queue"] = AlphaQueue()
    app["start_time"] = time.time()
    
    # HTTP routes
    app.router.add_post("/submit", http_submit)
    app.router.add_get("/status", http_status)
    app.router.add_get("/health", http_health)
    
    # Start queue processor
    http_client = httpx.AsyncClient(timeout=60.0)
    processor_task = asyncio.create_task(app["queue"].process_loop(http_client))
    
    # Start HTTP server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", HTTP_PORT)
    await site.start()
    
    # Unix socket for local IPC
    from aiohttp import web_unix
    unix_runner = web.AppRunner(app)
    await unix_runner.setup()
    unix_site = web_unix.UnixSite(unix_runner, SOCKET_PATH)
    await unix_site.start()
    
    print(f"[Alpha] Daemon running — HTTP :{HTTP_PORT}, Unix {SOCKET_PATH}")
    print(f"[Alpha] Model: {ALPHA_MODEL}")
    
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("[Alpha] Shutting down...")
    finally:
        processor_task.cancel()
        await http_client.aclose()
        await runner.cleanup()
        await unix_runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Systemd Service

```ini
# /etc/systemd/user/ares-alpha.service
[Unit]
Description=ARES Offloader Alpha — Tool Context Compressor
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/home/craig/.NOTTHEONETOEDIT/skills/memory/ares-alpha-daemon/scripts/alpha_daemon.py
EnvironmentFile=/home/craig/.NOTTHEONETOEDIT/.env
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

**Enable**: `systemctl --user enable --now ares-alpha`

---

## Hermes Integration Hook

```python
# In Hermes tool execution wrapper (conceptual)
async def execute_tool_with_alpha_offload(tool_name, query, execute_fn):
    """Execute tool, offload result to Alpha, return summary to prime."""
    
    # 1. Execute tool
    result = await execute_fn()
    
    # 2. Submit to Alpha (async, non-blocking)
    asyncio.create_task(submit_to_alpha(tool_name, query, result))
    
    # 3. Return immediately with placeholder
    # Prime will receive Alpha summary via context injection
    return {"status": "offloaded", "alpha_hash": hash(f"{tool_name}:{query}")}

async def submit_to_alpha(tool, query, result):
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://127.0.0.1:9381/submit",
            json={"tool": tool, "query": query, "result": result},
            timeout=5.0
        )
```

---

## CLI Client

```bash
# Submit manually
ares-alpha submit --tool terminal --query "nmap -sS 10.0.0.0/8" --result "$(cat nmap.out)"

# Check status
ares-alpha status
# → Queue: 3 | Processing: 1 | Model: llama-3.1-8b-instant | Uptime: 2h 14m

# Force flush queue
ares-alpha flush

# View recent summaries
ares-alpha recent --limit 10 --format json
```

---

## Glyph Tags

| Glyph | Meaning |
|-------|---------|
| 🜂 | Alpha active / tool context flowing |
| ♱ | Summary injected to prime |
| ⚡ | Compression alert (ratio < 50%) |
| ⚠ | Queue backing up |
| 💤 | Idle / no tool results |