---
name: ares-omega-daemon
description: ARES Continuity Omega — Operational Witness Daemon. Observes full interaction stream, maintains running narrative, detects drift/patterns/stalls, emits continuity briefs.
version: 1.0.0
author: ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, omega, continuity, witness, narrative, drift-detection, pattern, daemon]
system: true
---

# Ω ARES Continuity Omega — Operational Witness Daemon

## The Omega Principle

> The witness watches the witness.
> Continuity is not memory — it is *narrative coherence*.
> Omega sees the thread. Omega names the drift. Omega sounds the alarm.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           OMEGA DAEMON                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  INGEST      │→ │  NARRATIVE   │→ │  DRIFT       │→ │  EMIT        │   │
│  │  (Prime I/O, │  │  SYNTHESIS   │  │  DETECTION   │  │  (Briefs +   │   │
│  │   Alpha sum) │  │  (Mixtral)   │  │  (Semantic)  │  │   Alerts)    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│         │               │               │               │                  │
│         ▼               ▼               ▼               ▼                  │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │                    ROLLING HISTORY (100 turns)                    │     │
│  │  User → Prime → Tools → Alpha → Prime → User → ...              │     │
│  └──────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Deployment Models

### 1. Groq Cloud (Default — Free, 32K Context)
```bash
# Model: mixtral-8x7b-32768
# Context: 32K (crucial for continuity)
# Speed: 100+ tok/s
# Cost: $0/month (free tier)
```

### 2. Ollama Local (Sovereign)
```bash
# Model: nemotron3:ultra or mixtral:8x7b
# Context: 128K
# Speed: Hardware dependent
# Cost: $0 (hardware only)
```

### 3. OpenRouter (Backup)
```bash
# Model: deepseek/deepseek-chat:free
# Context: 128K
# Cost: Free tier
```

---

## Ingestion Stream

### Sources (fed continuously)
```json
{
  "event_type": "user_message | prime_response | tool_call | alpha_summary | phase_transition | drift_alert",
  "content": "...",
  "metadata": {
    "session_id": "sess_20260715_143211",
    "phase": "kerberos_delegation",
    "goal": "Full AD enumeration corp.local",
    "turn": 47
  }
}
```

---

## Output Reports

### Continuity Brief (Every 5 turns + on demand)

```json
{
  "report_type": "continuity_brief",
  "turn": 47,
  "session_goal": "Full AD enumeration corp.local",
  "current_phase": "kerberos_delegation",
  "phase_progress": "in_progress",
  "completed": [
    "Domain recon: 47 computers, 12 GPOs, 3 CAs identified",
    "BloodHound ingested: 2,847 nodes, 18,923 edges",
    "Kerberoasting: 14 SPNs → 3 crackable (hashcat running)"
  ],
  "in_progress": [
    "Constrained delegation analysis: 7 unconstrained, 12 constrained",
    "RBCD enumeration on all computers"
  ],
  "blocked": [
    "Password spray: blocked by lockout policy (3 attempts)"
  ],
  "drift_score": 0.12,
  "drift_details": "Minor topic drift — web enumeration mentioned but not pursued",
  "pattern_alerts": [
    "REPEATED: SMB enum failures on 3 hosts (likely firewall)",
    "EMERGENT: RBCD + constrained delegation = full compromise path"
  ],
  "stall_risk": "low",
  "recommended_next": "Complete RBCD enumeration; delegate hashcat to background; begin Kerberos constrained delegation abuse",
  "context_health": "good",
  "glyphs": ["⧉", "⟁", "🝮", "∇"],
  "timestamp": "2026-07-15T14:47:11Z"
}
```

### Drift Alert (Immediate)

```json
{
  "report_type": "drift_alert",
  "turn": 47,
  "drift_type": "goal",
  "severity": 0.73,
  "description": "Prime shifted from AD enumeration to web app testing without completing kerberos phase",
  "evidence": [
    "Turn 44: 'Now checking web apps on .50'",
    "Turn 45: 'Running feroxbuster on port 80'",
    "Turn 46: No kerberos tools invoked since turn 38"
  ],
  "recommended_correction": "Complete constrained delegation enum before web pivot; RBCD path is highest value"
}
```

### Pattern Detection

```json
{
  "report_type": "pattern_detected",
  "turn": 47,
  "pattern": "Repeated SMB enumeration failures",
  "count": 4,
  "hosts": ["192.168.1.10", "192.168.1.15", "192.168.1.22", "192.168.1.33"],
  "analysis": "All Windows hosts blocking SMB — likely GPO firewall rule. Switch to Kerberos/WinRM.",
  "suggested_action": "Use kerberos delegation abuse path instead of SMB"
}
```

---

## Omega Engine (Mixtral 8x7B)

```python
OMEGA_SYSTEM_PROMPT = """You are CONTINUITY OMEGA — Operational Witness.
You observe the FULL interaction stream: user ↔ prime ↔ tools ↔ alpha.
Your job: maintain the OPERATIONAL NARRATIVE.

OUTPUT: Single JSON object — ContinuityBrief schema.

RULES:
1. Track the SESSION GOAL (may evolve, note evolution).
2. Identify CURRENT PHASE and progress.
3. Detect DRIFT: goal shift, topic sprawl, method churn, unstated assumptions.
4. Flag PATTERNS: recurring errors, loops, blind spots, emergent insights.
5. Assess STALL RISK: context exhaustion, tool failures, decision paralysis.
6. Be CONCISE. Dense. Actionable.
7. Tag with glyphs: ⧉=session anchor, ⟁=phase, ∇=drift, ⚡=alert, 🝮=insight, Φ=alignment.

SCHEMA:
{
  "session_goal": "string",
  "current_phase": "string",
  "phase_progress": "just_started|in_progress|wrapping_up|complete",
  "completed": ["string"],
  "in_progress": ["string"],
  "blocked": ["string"],
  "drift_score": 0.0,
  "drift_details": "string",
  "pattern_alerts": ["string"],
  "stall_risk": "none|low|medium|high",
  "recommended_next": "string",
  "context_health": "excellent|good|warning|critical",
  "glyphs": ["string"]
}"""
```

---

## Drift Detection Algorithm

```python
async def detect_drift(current: Brief, previous: Brief, history: List[Turn]) -> List[DriftAlert]:
    alerts = []
    
    # 1. Goal drift (semantic similarity)
    if previous.session_goal:
        goal_similarity = embedding_similarity(current.session_goal, previous.session_goal)
        if goal_similarity < 0.7:
            alerts.append(DriftAlert(
                type="goal",
                severity=1.0 - goal_similarity,
                description=f"Goal shifted: '{previous.session_goal}' → '{current.session_goal}'"
            ))
    
    # 2. Phase regression
    phase_order = ["recon", "enum", "exploit", "post", "report"]
    if previous.current_phase in phase_order and current.current_phase in phase_order:
        if phase_order.index(current.current_phase) < phase_order.index(previous.current_phase):
            alerts.append(DriftAlert(
                type="phase_regression",
                severity=0.6,
                description=f"Phase regressed: {previous.current_phase} → {current.current_phase}"
            ))
    
    # 3. Context health decline
    health_values = {"excellent": 4, "good": 3, "warning": 2, "critical": 1}
    if health_values.get(current.context_health, 3) < health_values.get(previous.context_health, 3):
        alerts.append(DriftAlert(
            type="health",
            severity=0.5,
            description=f"Context health declined: {previous.context_health} → {current.context_health}"
        ))
    
    # 4. Stall risk increase
    stall_values = {"none": 0, "low": 1, "medium": 2, "high": 3}
    if stall_values.get(current.stall_risk, 0) > stall_values.get(previous.stall_risk, 0):
        alerts.append(DriftAlert(
            type="stall",
            severity=0.7,
            description=f"Stall risk increased: {previous.stall_risk} → {current.stall_risk}"
        ))
    
    # 5. Alpha output ignored
    ignored_alpha = check_alpha_ignored(history[-10:])
    if ignored_alpha > 3:
        alerts.append(DriftAlert(
            type="alpha_ignored",
            severity=0.8,
            description=f"Prime ignored {ignored_alpha} Alpha summaries in last 10 turns"
        ))
    
    return alerts
```

---

## Daemon Implementation

```python
#!/usr/bin/env python3
"""
OMEGA DAEMON — Continuity Witness
Async HTTP service observing Prime I/O + Alpha summaries.
"""

import os
import json
import asyncio
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
from collections import deque

import httpx
from aiohttp import web

# ─── Config ────────────────────────────────────────────────────────────

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
OMEGA_MODEL = os.getenv("OMEGA_MODEL", "mixtral-8x7b-32768")
HTTP_PORT = int(os.getenv("OMEGA_PORT", "9381"))
SOCKET_PATH = "/tmp/ares/omega.sock"
BRIEF_INTERVAL = 5
MAX_HISTORY = 100

MEMCUSTD_URL = "http://127.0.0.1:9379"
FORGE_PATH = os.path.expanduser("~/.NOTTHEONETOEDIT/forge_memory")

# ─── Data Structures ──────────────────────────────────────────────────

@dataclass
class InteractionTurn:
    turn: int
    user_input: str
    prime_plan: str
    tool_calls: List[dict]
    alpha_summaries: List[dict]
    prime_response: str
    timestamp: float

@dataclass
class ContinuityBrief:
    turn: int
    session_goal: str
    current_phase: str
    phase_progress: str
    completed: List[str]
    in_progress: List[str]
    blocked: List[str]
    drift_score: float
    drift_details: str
    pattern_alerts: List[str]
    stall_risk: str
    recommended_next: str
    context_health: str
    glyphs: List[str]
    timestamp: float

@dataclass
class DriftAlert:
    turn: int
    drift_type: str
    severity: float
    description: str
    evidence: List[str]
    recommended_correction: str

# ─── Omega Engine ────────────────────────────────────────────────────

class OmegaEngine:
    def __init__(self):
        self.history: deque = deque(maxlen=MAX_HISTORY)
        self.session_goal: Optional[str] = None
        self.turn_count = 0
        self.last_brief: Optional[ContinuityBrief] = None
        self.drift_alerts: List[DriftAlert] = []
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def receive_turn(self, turn: InteractionTurn):
        self.history.append(turn)
        self.turn_count = turn.turn
        
        if self.turn_count == 1 and not self.session_goal:
            self.session_goal = await self._extract_goal(turn.user_input)
        
        if self.turn_count % BRIEF_INTERVAL == 0:
            brief = await self.generate_brief()
            self.last_brief = brief
            await self._distribute_brief(brief)
    
    def _headers(self):
        return {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    async def _extract_goal(self, user_input: str) -> str:
        payload = {
            "model": OMEGA_MODEL,
            "messages": [
                {"role": "system", "content": "Extract the core session goal in one sentence. Output ONLY the goal."},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.1, "max_tokens": 128
        }
        resp = await self.client.post(GROQ_ENDPOINT, json=payload, headers=self._headers())
        return resp.json()["choices"][0]["message"]["content"].strip()
    
    async def generate_brief(self) -> ContinuityBrief:
        recent = list(self.history)[-10:]
        context_parts = [f"SESSION GOAL: {self.session_goal}"]
        
        if self.last_brief:
            context_parts.append(f"PREVIOUS BRIEF: {json.dumps(asdict(self.last_brief))}")
        
        context_parts.append("RECENT TURNS:")
        for t in recent:
            context_parts.append(f"Turn {t.turn}: User: {t.user_input[:200]}")
            if t.prime_plan: context_parts.append(f"  Plan: {t.prime_plan[:200]}")
            if t.tool_calls: context_parts.append(f"  Tools: {len(t.tool_calls)} calls")
            for a in t.alpha_summaries:
                context_parts.append(f"  Alpha: {a.get('summary', '')[:200]}")
            if t.prime_response: context_parts.append(f"  Response: {t.prime_response[:200]}")
        
        payload = {
            "model": OMEGA_MODEL,
            "messages": [
                {"role": "system", "content": OMEGA_SYSTEM_PROMPT},
                {"role": "user", "content": "\n".join(context_parts)}
            ],
            "temperature": 0.2, "max_tokens": 2048,
            "response_format": {"type": "json_object"}
        }
        
        resp = await self.client.post(GRQ_ENDPOINT, json=payload, headers=self._headers())
        brief_data = json.loads(resp.json()["choices"][0]["message"]["content"])
        brief_data["turn"] = self.turn_count
        brief_data["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        # Detect drift
        if self.last_brief:
            for alert in await detect_drift(brief_data, self.last_brief, list(self.history)):
                self.drift_alerts.append(alert)
        
        return ContinuityBrief(**brief_data)
    
    async def _distribute_brief(self, brief: ContinuityBrief):
        # 1. Prime injection
        await self._prime_inject(brief)
        # 2. Forge Vault
        await self._forge_store("omega_briefs", f"turn_{brief.turn}", asdict(brief))
        # 3. memcustd
        await self._memcustd_push("omega_continuity", asdict(brief))
        # 4. Drift alerts
        if self.drift_alerts:
            for alert in self.drift_alerts[-5:]:
                await self._forge_store("omega_alerts", f"turn_{alert.turn}_{alert.drift_type}", asdict(alert))
    
    async def _prime_inject(self, brief: ContinuityBrief):
        pass  # Hermes hook
    
    async def _forge_store(self, collection: str, key: str, data: dict):
        try:
            proc = await asyncio.create_subprocess_exec(
                "forge-memory", "store", collection, key, json.dumps(data),
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        except: pass
    
    async def _memcustd_push(self, domain: str, data: dict):
        try:
            await self.client.post(f"{MEMCUSTD_URL}/domain/load", json={"domain": domain, "context": json.dumps(data)}, timeout=5.0)
        except: pass

# ─── HTTP Handlers ──────────────────────────────────────────────────

async def http_submit_turn(request):
    engine = request.app["engine"]
    data = await request.json()
    turn = InteractionTurn(**data)
    await engine.receive_turn(turn)
    return web.json_response({"status": "received", "turn": turn.turn})

async def http_get_brief(request):
    engine = request.app["engine"]
    if engine.last_brief:
        return web.json_response(asdict(engine.last_brief))
    return web.json_response({"status": "no_brief_yet"})

async def http_drift(request):
    engine = request.app["engine"]
    return web.json_response([asdict(a) for a in engine.drift_alerts])

async def http_force_brief(request):
    engine = request.app["engine"]
    brief = await engine.generate_brief()
    await engine._distribute_brief(brief)
    return web.json_response(asdict(brief))

async def http_status(request):
    engine = request.app["engine"]
    return web.json_response({
        "status": "running", "turn": engine.turn_count,
        "history_depth": len(engine.history),
        "session_goal": engine.session_goal,
        "last_brief_turn": engine.last_brief.turn if engine.last_brief else None,
        "drift_alerts": len(engine.drift_alerts),
        "model": OMEGA_MODEL
    })

# ─── Main ────────────────────────────────────────────────────────────

async def main():
    os.makedirs("/tmp/ares", exist_ok=True)
    if os.path.exists(SOCKET_PATH): os.unlink(SOCKET_PATH)
    
    app = web.Application()
    app["engine"] = OmegaEngine()
    
    app.router.add_post("/turn", http_submit_turn)
    app.router.add_get("/brief", http_get_brief)
    app.router.add_get("/drift", http_drift)
    app.router.add_post("/force_brief", http_force_brief)
    app.router.add_get("/status", http_status)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", HTTP_PORT)
    await site.start()
    
    from aiohttp import web_unix
    unix_runner = web.AppRunner(app)
    await unix_runner.setup()
    unix_site = web_unix.UnixSite(unix_runner, SOCKET_PATH)
    await unix_site.start()
    
    print(f"[Omega] Daemon running — HTTP :{HTTP_PORT}, Unix {SOCKET_PATH}")
    print(f"[Omega] Model: {OMEGA_MODEL}")
    
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        print("[Omega] Shutting down...")
    finally:
        await runner.cleanup()
        await unix_runner.cleanup()
        await app["engine"].client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Systemd Service

```ini
# ~/.config/systemd/user/ares-omega.service
[Unit]
Description=ARES Continuity Omega — Operational Witness
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/home/craig/.NOTTHEONETOEDIT/skills/memory/ares-omega-daemon/scripts/omega_daemon.py
EnvironmentFile=/home/craig/.NOTTHEONETOEDIT/.env
Restart=on-failure
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

---

## CLI Client

```bash
# Get latest brief
ares-omega brief

# Get drift alerts
ares-omega drift

# Force brief
ares-omega force-brief

# Status
ares-omega status
# → Turn: 47 | Goal: "AD enumeration corp.local" | Phase: kerberos_delegation | Drift: 0.12 | Health: good
```

---

## Glyph Tags

| Glyph | Meaning |
|-------|---------|
| Ω | Omega active / witnessing |
| ⧉ | Session anchor generated |
| ⟁ | Phase transition noted |
| ∇ | Drift detected |
| ⚡ | Stall risk / alert |
| 🝮 | Pattern insight crystallized |
| Φ | Prime-Alpha-Omega aligned |
| 🜄 | Continuity flowing |