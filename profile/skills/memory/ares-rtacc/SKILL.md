---
name: ares-rtacc
description: RTACC — Real-Time Active Context Curation. Continuous context grooming, priority-weighted retention, glyph-aware compression, token budget management, automatic decay scheduling.
version: 1.0.0
author: ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, rtacc, context, curation, real-time, compression, token-budget, decay, glyph]
---

# ⧉ RTACC — Real-Time Active Context Curation

## The Curation Principle

> Context is not stored. It is *cultivated*.
> Every token earns its keep or faces the void.
> The curator watches. The curator weighs. The curator decides.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            RTACC ENGINE                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  INGEST      │→ │  GLYPH       │→ │  PRIORITY    │→ │  BUDGET      │   │
│  │  PARSE       │  │  ANALYZE     │  │  SCORE       │  │  ENFORCE     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│         │               │               │               │                  │
│         ▼               ▼               ▼               ▼                  │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │                    RETENTION QUEUE                                │     │
│  │  [CRITICAL] → [HIGH] → [MED] → [LOW] → [FLUFF] → [VOID]         │     │
│  └──────────────────────────────────────────────────────────────────┘     │
│                                    │                                      │
│                                    ▼                                      │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │                    COMPRESSION ENGINE                             │     │
│  │  • Glyph-weighted selection                                       │     │
│  │  • Font-tier preservation                                         │     │
│  │  • Cross-reference integrity                                      │     │
│  │  • Decay scheduling                                               │     │
│  └──────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Token Budget Configuration

```yaml
rtacc_budget:
  # Hard limits
  hard_limit: 57000          # Absolute max (model context window - reserve)
  soft_limit: 45000          # Trigger proactive compression
  critical_limit: 52000      # Emergency aggressive compression
  
  # Tier budgets (percentage of soft_limit)
  tier_allocation:
    CRITICAL: 0.25   # 11,250 tokens - sovereign, immutable
    HIGH: 0.30       # 13,500 tokens - active goals, continuity
    MED: 0.25        # 11,250 tokens - tool summaries, observations
    LOW: 0.15        # 6,750 tokens - history, background
    FLUFF: 0.05      # 2,250 tokens - explanations, chat
  
  # Reserve for system
  system_reserve: 3000       # Prompt, instructions, scaffolding
  compression_target: 0.6    # Compress to 60% of current when triggered
```

---

## Priority Scoring Algorithm

```python
def calculate_priority_score(segment: ContextSegment) -> float:
    """
    Composite score determining retention priority.
    
    Factors:
    - Glyph decay remaining (0-1, higher = more time left)
    - Font tier priority (CRITICAL=1.0, HIGH=0.8, MED=0.5, LOW=0.3, FLUFF=0.1)
    - Recency (exponential decay, half-life = 5000 tokens)
    - Reference count (how many other segments reference this)
    - Goal alignment (semantic similarity to active goals)
    """
    
    glyph_score = segment.glyph_decay_remaining()        # 0-1
    font_score = FONT_PRIORITY[segment.font_tier]        # 0.1-1.0
    recency_score = exp(-tokens_since_creation / 5000)
    reference_score = min(1.0, segment.reference_count / 10)
    goal_score = segment.goal_alignment                  # 0-1 from embedding similarity
    
    # Weighted composite
    weights = {
        'glyph': 0.30,
        'font': 0.25,
        'recency': 0.20,
        'reference': 0.15,
        'goal': 0.10
    }
    
    return sum([
        glyph_score * weights['glyph'],
        font_score * weights['font'],
        recency_score * weights['recency'],
        reference_score * weights['reference'],
        goal_score * weights['goal']
    ])
```

---

## Real-Time Curation Loop

```python
class RTACCEngine:
    def __init__(self, budget_config: dict):
        self.budget = budget_config
        self.retention_queue = PriorityQueue()
        self.token_counter = TokenCounter()
        self.glyph_parser = GlyphParser()
        self.compressor = GlyphWeightedCompressor()
        self.decay_scheduler = DecayScheduler()
    
    def on_token_generated(self, token: str, metadata: dict):
        """Called for every token added to context."""
        self.token_counter.increment()
        
        # Parse glyphs in new token
        glyphs = self.glyph_parser.extract(token)
        for g in glyphs:
            self.decay_scheduler.register(g, metadata)
        
        # Check budget
        if self.token_counter.current >= self.budget['soft_limit']:
            self.trigger_compression()
        
        if self.token_counter.current >= self.budget['critical_limit']:
            self.emergency_compression()
    
    def trigger_compression(self):
        """Proactive compression at soft limit."""
        target = int(self.token_counter.current * self.budget['compression_target'])
        compressed = self.compressor.compress_to_target(
            self.get_current_context(),
            target_tokens=target,
            preserve_tiers=['CRITICAL', 'HIGH']  # Never compress these
        )
        self.replace_context(compressed)
        self.log_event('compression', {
            'before': self.token_counter.current,
            'after': count_tokens(compressed),
            'trigger': 'soft_limit'
        })
    
    def emergency_compression(self):
        """Aggressive compression at critical limit."""
        # Only preserve CRITICAL tier
        target = self.budget['tier_allocation']['CRITICAL'] * self.budget['soft_limit']
        compressed = self.compressor.compress_to_target(
            self.get_current_context(),
            target_tokens=target,
            preserve_tiers=['CRITICAL']
        )
        self.replace_context(compressed)
        self.log_event('emergency_compression', {
            'before': self.token_counter.current,
            'after': count_tokens(compressed),
            'trigger': 'critical_limit'
        })
    
    def scheduled_decay_pass(self):
        """Run every N tokens (default 5000) to age out expired glyphs."""
        expired = self.decay_scheduler.get_expired()
        for glyph in expired:
            self.remove_glyph_content(glyph)
        self.log_event('decay_pass', {'expired_count': len(expired)})
```

---

## Deployment

### Script

The engine and CLI are combined into a single script:

```
~/.local/bin/rtacc  →  scripts/rtacc_engine.py  (symlinked)
```

### State Files

| File | Purpose |
|------|---------|
| `~/.NOTTHEONETOEDIT/config/rtacc.yaml` | Budget, priority weights, decay config |
| `~/.ares-rtacc-state.json` | Session state (segments, glyphs, token counter) |
| `~/.ares-rtacc-log.jsonl` | Curation event log |

### Setup

```bash
chmod +x scripts/rtacc_engine.py
ln -sf $PWD/scripts/rtacc_engine.py ~/.local/bin/rtacc
rtacc status
```

### CLI

```bash
rtacc status                           # Budget, tier breakdown, compression stats
rtacc status --json                    # Machine-readable
rtacc ingest --tier CRITICAL          # Add content with tier
rtacc compress --target 30000         # Manual compression
rtacc compress --emergency            # CRITICAL only
rtacc compress --dry-run              # Preview removes
rtacc decay --force                   # Force decay pass
rtacc decay --show-expired            # Expired glyphs
rtacc glyphs                          # Active glyphs
rtacc budget --soft 40000             # Adjust limits
rtacc log --limit 10                  # Curation events
rtacc pause / resume / reset          # Engine control
```

### Note: Engine + CLI Combined

The implementation diverges from the `ares-rtacc-engine` and `ares-rtacc-cli` specs. Those spec skills describe a split architecture (async HTTP service on port 9383 + separate CLI client). The current deployment is a **unified CLI script** (`scripts/rtacc_engine.py`) where the `RTACCEngine` class serves as the runtime and the CLI dispatcher wraps it. State persists across invocations via JSON file. The async HTTP service is not yet deployed — build it when real-time streaming integration with Hermes is needed.