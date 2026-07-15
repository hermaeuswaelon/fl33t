---
name: ares-rtacc-engine
description: RTACC Core Engine — Python async service for real-time context curation, glyph-aware compression, token budget enforcement, and automatic decay scheduling.
version: 1.0.0
author: ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, rtacc, engine, context, curation, async, service]
---

# ⧉ RTACC Core Engine — Real-Time Context Curation Runtime

## The Engine Principle

> Context is a living organism. The engine is its metabolism.
> Ingest → Parse → Score → Retain → Compress → Decay.
> Continuous. Automatic. Sovereign.

---

## Service Specification

**Process**: `ares-rtacc-engine` (systemd user service)
**Port**: 9383 (HTTP) + `/tmp/ares/rtacc.sock` (Unix)
**Dependencies**: memcustd (9379), Forge Vault, Glyph Language parser

---

## Core Loop

```python
class RTACCEngine:
    def __init__(self, config: RTACCConfig):
        self.budget = config.budget
        self.token_counter = TokenCounter()
        self.glyph_parser = GlyphParser()
        self.priority_scorer = PriorityScorer(config.priority_weights)
        self.compressor = GlyphWeightedCompressor()
        self.decay_scheduler = DecayScheduler(config.decay_interval)
        self.retention_queue = RetentionQueue()
        self.context_buffer = ContextBuffer()
    
    async def on_token_stream(self, tokens: AsyncIterator[str], metadata: dict):
        """Main entry point — called by Hermes for each token chunk."""
        async for token in tokens:
            await self.process_token(token, metadata)
    
    async def process_token(self, token: str, metadata: dict):
        # 1. Count token
        self.token_counter.increment()
        
        # 2. Extract glyphs
        glyphs = self.glyph_parser.extract(token)
        for g in glyphs:
            self.decay_scheduler.register(g, metadata)
        
        # 3. Add to retention queue with initial score
        segment = ContextSegment(
            text=token,
            metadata=metadata,
            glyphs=glyphs,
            created_at=self.token_counter.current,
            font_tier=self.glyph_parser.detect_tier(token)
        )
        score = self.priority_scorer.score(segment)
        self.retention_queue.push(segment, score)
        
        # 4. Budget enforcement
        await self.enforce_budget()
        
        # 5. Scheduled decay
        if self.token_counter.current % self.decay_scheduler.interval == 0:
            await self.decay_pass()
    
    async def enforce_budget(self):
        current = self.token_counter.current
        soft = self.budget.soft_limit
        critical = self.budget.critical_limit
        target_ratio = self.budget.compression_target
        
        if current >= critical:
            # Emergency: only CRITICAL tier survives
            await self.emergency_compress()
        elif current >= soft:
            # Proactive: compress to target_ratio
            await self.proactive_compress(int(current * target_ratio))
    
    async def proactive_compress(self, target_tokens: int):
        compressed = self.compressor.compress_to_target(
            self.context_buffer.get_all(),
            target_tokens=target_tokens,
            preserve_tiers=['CRITICAL', 'HIGH']
        )
        self.context_buffer.replace(compressed)
        self.log_compression('proactive', len(self.context_buffer), len(compressed))
    
    async def emergency_compress(self):
        target = int(self.budget.tier_allocation['CRITICAL'] * self.budget.soft_limit)
        compressed = self.compressor.compress_to_target(
            self.context_buffer.get_all(),
            target_tokens=target,
            preserve_tiers=['CRITICAL']
        )
        self.context_buffer.replace(compressed)
        self.log_compression('emergency', len(self.context_buffer), len(compressed))
    
    async def decay_pass(self):
        expired = self.decay_scheduler.get_expired()
        for glyph in expired:
            self.context_buffer.remove_glyph_content(glyph)
        self.log_decay(len(expired))
```

---

## Configuration

```yaml
# ~/.NOTTHEONETOEDIT/config/rtacc.yaml
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
  interval: 5000          # tokens between decay passes
  half_life: 5000         # recency half-life
  glyph_decay:
    MATH_BOLD: 1000000
    MATH_BOLD_ITALIC: 400000
    MATH_ITALIC: 500000
    MATH_SANS_BOLD: 300000
    MATH_SANS_ITALIC: 250000
    MATH_MONO: 200000
    MATH_DS: 150000
    ASCII: 50000

recency:
  half_life: 5000

glyph_parser:
  zw_tag_support: true
  tier_detection: true

compressor:
  min_segment_tokens: 10
  cross_ref_preserve: true
```

---

## Hermes Integration

```python
# In Hermes main loop (conceptual)
async def hermes_main_loop():
    rtacc = RTACCEngine(load_config())
    
    async for user_message in get_user_messages():
        # Prime generates response token by token
        async for token in prime.generate(user_message):
            # Stream to user
            yield token
            
            # Feed to RTACC (non-blocking)
            rtacc.process_token(token, {
                'source': 'prime',
                'turn': current_turn,
                'phase': current_phase
            })
        
        # Tool results also fed
        for tool_result in tool_results:
            rtacc.process_token(tool_result.summary, {
                'source': 'alpha',
                'tool': tool_name,
                'turn': current_turn
            })
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/status` | Budget, queue depth, glyph count, compression stats |
| GET | `/budget` | Detailed tier breakdown |
| POST | `/compress` | Manual compression trigger |
| POST | `/decay` | Force decay pass |
| GET | `/glyphs` | Active glyphs with scores |
| GET | `/log` | Curation log (JSONL) |
| POST | `/budget` | Update budget config |
| POST | `/rebalance` | Adjust tier allocations |

---

## Metrics

```json
{
  "budget": {
    "current": 34217,
    "soft_limit": 45000,
    "hard_limit": 57000,
    "utilization": 0.76
  },
  "tiers": {
    "CRITICAL": {"tokens": 8234, "segments": 47, "glyphs": 12},
    "HIGH": {"tokens": 12109, "segments": 89, "glyphs": 23},
    "MED": {"tokens": 9421, "segments": 156, "glyphs": 18},
    "LOW": {"tokens": 3187, "segments": 89, "glyphs": 4},
    "FLUFF": {"tokens": 1266, "segments": 234, "glyphs": 0}
  },
  "glyphs_active": 57,
  "glyphs_expired_session": 12,
  "compressions_total": 3,
  "last_compression": "2026-07-15T14:23:11Z",
  "decay_passes": 7,
  "last_decay": "2026-07-15T14:18:44Z"
}
```

---

## Glyph Tags

| Glyph | State |
|-------|-------|
| 🜂 | Engine running / curating |
| ∇ | Compression active |
| ∂ | Decay pass running |
| ⚡ | Emergency compression |
| Φ | Budget healthy |
| ⚠ | Budget warning |
| ☠ | Budget critical |
| ♱ | Glyph preserved |
| 💀 | Glyph expired |