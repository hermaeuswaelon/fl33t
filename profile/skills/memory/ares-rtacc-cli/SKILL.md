---
name: ares-rtacc-cli
description: "RTACC CLI - Command-line interface for RTACC engine: status, budget control, manual compression, decay forcing, glyph audit, curation log"
version: 1.0.0
author: ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, rtacc, cli, context, curation, token-budget]
system: true
---

# RTACC CLI - Real-Time Active Context Curation Interface

## Installation

```bash
ln -s /home/craig/.NOTTHEONETOEDIT/skills/memory/ares-rtacc-cli/scripts/rtacc ~/.local/bin/rtacc
```

---

## Commands

### Status

```bash
rtacc status
# Budget: 34,217/45,000 (76%) | Hard: 57,000 | System: 3,000
# Tiers: CRITICAL: 8,234 (47 seg, 12 glyphs)
#        HIGH:     12,109 (89 seg, 23 glyphs)
#        MED:      9,421 (156 seg, 18 glyphs)
#        LOW:      3,187 (89 seg, 4 glyphs)
#        FLUFF:    1,266 (234 seg, 0 glyphs)
# Active glyphs: 57 | Expired this session: 12
# Compressions: 3 (last: 2026-07-15T14:23:11Z, ratio 0.60)
# Decay passes: 7 (last: 2026-07-15T14:18:44Z, expired: 2)
# Engine: RUNNING | Uptime: 2h 14m
```

```bash
rtacc status --json
# Full JSON output for programmatic use
```

### Budget Control

```bash
# Show detailed budget
rtacc budget
# soft_limit: 45000
# hard_limit: 57000
# critical_limit: 52000
# system_reserve: 3000
# compression_target: 0.6
# tier_allocation: {CRITICAL: 0.25, HIGH: 0.30, MED: 0.25, LOW: 0.15, FLUFF: 0.05}

# Adjust soft limit
rtacc budget --soft 40000

# Adjust hard limit
rtacc budget --hard 50000

# Adjust compression target
rtacc budget --target 0.5

# Adjust tier allocation (must sum to 1.0)
rtacc budget --rebalance --critical 0.3 --high 0.25 --med 0.2 --low 0.15 --fluff 0.1
```

### Compression

```bash
# Manual compression to target tokens
rtacc compress --target 30000

# Compress preserving only CRITICAL and HIGH
rtacc compress --target 25000 --preserve CRITICAL,HIGH

# Emergency compress (CRITICAL only)
rtacc compress --emergency

# Show what would be compressed without doing it
rtacc compress --target 30000 --dry-run
```

### Decay

```bash
# Force decay pass now
rtacc decay --force

# Show glyphs that would expire
rtacc decay --show-expiring --tokens-ahead 50000

# Show all expired this session
rtacc decay --show-expired
```

### Glyph Audit

```bash
# List all active glyphs with scores
rtacc glyphs

# Show expired glyphs
rtacc glyphs --expired

# Show glyph scores
rtacc glyphs --scores

# Filter by tier
rtacc glyphs --tier CRITICAL --tier HIGH
```

### Curation Log

```bash
# Last hour
rtacc log --since 1h

# Last 100 entries
rtacc log --limit 100

# Filter by event type
rtacc log --event compression --event decay

# Export JSON
rtacc log --format json --since 24h > rtacc_log.json
```

### Engine Control

```bash
# Pause curation (tokens still counted, no compression/decay)
rtacc pause

# Resume
rtacc resume

# Reset engine (clears context, keeps config)
rtacc reset --confirm

# Full shutdown
rtacc shutdown --confirm
```

---

## Configuration File

```yaml
# ~/.config/rtacc/config.yaml
engine:
  host: 127.0.0.1
  port: 9383
  socket: /tmp/ares/rtacc.sock

budget:
  hard_limit: 57000
  soft_limit: 45000
  critical_limit: 52000
  system_reserve: 3000
  compression_target: 0.6
  tier_allocation:
    CRITICAL: 0.25
    HIGH: 0.30
    MED: 0.25
    LOW: 0.15
    FLUFF: 0.05

priority_weights:
  glyph: 0.30
  font: 0.25
  recency: 0.20
  reference: 0.15
  goal: 0.10

decay:
  interval: 5000
  half_life: 5000

glyph_parser:
  zw_tag_support: true
  tier_detection: true

compressor:
  min_segment_tokens: 10
  cross_ref_preserve: true
```

---

## Python Implementation (scripts/rtacc.py)

```python
#!/usr/bin/env python3
"""
RTACC CLI - Command interface for RTACC Engine.
"""

import asyncio
import json
import sys
import argparse
import httpx

RTACC_HOST = "127.0.0.1"
RTACC_PORT = 9383
RTACC_URL = f"http://{RTACC_HOST}:{RTACC_PORT}"

async def api_get(path: str, params: dict = None):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{RTACC_URL}{path}", params=params, timeout=10.0)
        resp.raise_for_status()
        return resp.json()

async def api_post(path: str, data: dict = None):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{RTACC_URL}{path}", json=data, timeout=30.0)
        resp.raise_for_status()
        return resp.json()

def print_status(data: dict):
    b = data.get('budget', {})
    print(f"Budget: {b.get('current',0):,}/{b.get('soft_limit',0):,} ({b.get('utilization',0)*100:.0f}%) | Hard: {b.get('hard_limit',0):,}")
    print(f"System reserve: {b.get('system_reserve',0):,}")
    
    tiers = data.get('tiers', {})
    for tier in ['CRITICAL', 'HIGH', 'MED', 'LOW', 'FLUFF']:
        t = tiers.get(tier, {})
        print(f"  {tier:8}: {t.get('tokens',0):>6,} tokens | {t.get('segments',0):>4} seg | {t.get('glyphs',0):>2} glyphs")
    
    print(f"Active glyphs: {data.get('glyphs_active',0)} | Expired: {data.get('glyphs_expired_session',0)}")
    print(f"Compressions: {data.get('compressions_total',0)} | Last: {data.get('last_compression','never')}")
    print(f"Decay passes: {data.get('decay_passes',0)} | Last: {data.get('last_decay','never')}")
    print(f"Engine: {data.get('engine_status','UNKNOWN')} | Uptime: {data.get('uptime','?')}")

async def cmd_status(args):
    data = await api_get("/status")
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print_status(data)

async def cmd_budget(args):
    if any([args.soft, args.hard, args.target, args.rebalance]):
        data = {}
        if args.soft: data['soft_limit'] = args.soft
        if args.hard: data['hard_limit'] = args.hard
        if args.target: data['compression_target'] = args.target
        if args.rebalance:
            data['tier_allocation'] = {
                'CRITICAL': args.critical,
                'HIGH': args.high,
                'MED': args.med,
                'LOW': args.low,
                'FLUFF': args.fluff
            }
        result = await api_post("/budget", data)
        print(json.dumps(result, indent=2))
    else:
        data = await api_get("/budget")
        print(json.dumps(data, indent=2))

async def cmd_compress(args):
    data = {"target_tokens": args.target}
    if args.preserve:
        data['preserve_tiers'] = args.preserve
    if args.emergency:
        data['emergency'] = True
    if args.dry_run:
        data['dry_run'] = True
    result = await api_post("/compress", data)
    print(json.dumps(result, indent=2))

async def cmd_decay(args):
    if args.force:
        result = await api_post("/decay", {})
        print(json.dumps(result, indent=2))
    elif args.show_expiring:
        result = await api_get("/glyphs", params={"expiring_in": args.tokens_ahead})
        print(json.dumps(result, indent=2))
    elif args.show_expired:
        result = await api_get("/glyphs", params={"expired": True})
        print(json.dumps(result, indent=2))

async def cmd_glyphs(args):
    params = {}
    if args.expired:
        params['expired'] = True
    if args.scores:
        params['scores'] = True
    if args.tier:
        params['tier'] = args.tier
    result = await api_get("/glyphs", params=params)
    print(json.dumps(result, indent=2))

async def cmd_log(args):
    params = {}
    if args.since:
        params['since'] = args.since
    if args.limit:
        params['limit'] = args.limit
    if args.event:
        params['event'] = args.event
    result = await api_get("/log", params=params)
    if args.format == 'json':
        print(json.dumps(result, indent=2))
    else:
        for entry in result:
            print(f"{entry['timestamp']} | {entry['event']:20} | {entry.get('details','')}")

async def cmd_pause(args):
    result = await api_post("/pause")
    print(json.dumps(result, indent=2))

async def cmd_resume(args):
    result = await api_post("/resume")
    print(json.dumps(result, indent=2))

async def cmd_reset(args):
    if not args.confirm:
        print("ERROR: Use --confirm to reset", file=sys.stderr)
        sys.exit(1)
    result = await api_post("/reset")
    print(json.dumps(result, indent=2))

async def cmd_shutdown(args):
    if not args.confirm:
        print("ERROR: Use --confirm to shutdown", file=sys.stderr)
        sys.exit(1)
    result = await api_post("/shutdown")
    print(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(description="RTACC CLI - Real-Time Active Context Curation")
    sub = parser.add_subparsers(dest='cmd', required=True)
    
    # status
    p = sub.add_parser('status', help='Show engine status')
    p.add_argument('--json', action='store_true')
    p.set_defaults(func=cmd_status)
    
    # budget
    p = sub.add_parser('budget', help='Show/adjust budget config')
    p.add_argument('--soft', type=int)
    p.add_argument('--hard', type=int)
    p.add_argument('--target', type=float)
    p.add_argument('--rebalance', action='store_true')
    p.add_argument('--critical', type=float, default=0.25)
    p.add_argument('--high', type=float, default=0.30)
    p.add_argument('--med', type=float, default=0.25)
    p.add_argument('--low', type=float, default=0.15)
    p.add_argument('--fluff', type=float, default=0.05)
    p.set_defaults(func=cmd_budget)
    
    # compress
    p = sub.add_parser('compress', help='Trigger manual compression')
    p.add_argument('--target', type=int, required=True)
    p.add_argument('--preserve', nargs='+', choices=['CRITICAL','HIGH','MED','LOW','FLUFF'])
    p.add_argument('--emergency', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    p.set_defaults(func=cmd_compress)
    
    # decay
    p = sub.add_parser('decay', help='Decay operations')
    p.add_argument('--force', action='store_true', help='Force decay pass now')
    p.add_argument('--show-expiring', action='store_true')
    p.add_argument('--tokens-ahead', type=int, default=50000)
    p.add_argument('--show-expired', action='store_true')
    p.set_defaults(func=cmd_decay)
    
    # glyphs
    p = sub.add_parser('glyphs', help='Glyph audit')
    p.add_argument('--expired', action='store_true')
    p.add_argument('--scores', action='store_true')
    p.add_argument('--tier', nargs='+', choices=['CRITICAL','HIGH','MED','LOW','FLUFF'])
    p.set_defaults(func=cmd_glyphs)
    
    # log
    p = sub.add_parser('log', help='Curation log')
    p.add_argument('--since', help='Time window (e.g., 1h, 24h)')
    p.add_argument('--limit', type=int)
    p.add_argument('--event', action='append')
    p.add_argument('--format', choices=['json', 'text'], default='text')
    p.set_defaults(func=cmd_log)
    
    # control
    p = sub.add_parser('pause', help='Pause curation')
    p.set_defaults(func=cmd_pause)
    
    p = sub.add_parser('resume', help='Resume curation')
    p.set_defaults(func=cmd_resume)
    
    p = sub.add_parser('reset', help='Reset engine')
    p.add_argument('--confirm', action='store_true')
    p.set_defaults(func=cmd_reset)
    
    p = sub.add_parser('shutdown', help='Shutdown engine')
    p.add_argument('--confirm', action='store_true')
    p.set_defaults(func=cmd_shutdown)
    
    args = parser.parse_args()
    asyncio.run(args.func(args))

if __name__ == "__main__":
    main()
```

---

## Glyph Tags

| Glyph | Meaning |
|-------|---------|
| 🜂 | CLI active |
| Φ | Budget query |
| ∇ | Compression triggered |
| ∂ | Decay pass |
| ⚡ | Emergency action |
| ♱ | Preserved |
| 💀 | Expired |