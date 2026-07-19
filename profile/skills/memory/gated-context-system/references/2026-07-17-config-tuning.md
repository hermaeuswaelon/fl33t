# Context Compression Tuning — July 17, 2026

## Trigger
User hit a 166K+ context blowout in a MoA session. The aggregator (deepseek-reasoner) accumulated too much from reference model outputs + its own iterations. Investigation revealed three compounding causes:

## Root Causes Found

### 1. snapndrop was in the disabled list
The `snapndrop` skill (handles the SUMMARIZE stage — SNAP transcript + DROP new thread) was in `config.yaml → skills.disabled`. This meant:
- gated-context plugin OFFLOAD still worked (pointer-based tool output gating)
- But the SUMMARIZE → RECALL pipeline never fired at threshold
- Context grew unchecked until hitting the hard cap

### 2. MoA reference/aggregator token budgets too generous
```
Before:
  reference_max_tokens: 1000   → 2 reference models = 2K per iteration  
  aggregator_max_tokens: 32000 → aggregator output = 32K per iteration
  Total per MoA iteration: ~34K
  After 3 iterations: ~102K from MoA alone → + system prompt + user = 166K+

After (fixed):
  reference_max_tokens: 300    → 2 × 300 = 600 per iteration
  aggregator_max_tokens: 16000 → 16K per iteration
  Total per MoA iteration: ~16.6K
  After 3 iterations: ~50K from MoA → fits under 128K hard cap
```

### 3. 19 default skills loading every session
Each skill adds 500-2000 tokens to system prompt. 19 skills = ~9.5K-38K fixed overhead. Trimmed to 3 core skills, load others on demand.

### 4. Config file write guard discovered
`patch`/`write_file` cannot write to `~/.hermes/config.yaml` or profile configs. Must use `hermes config set section.key value` via terminal tool.

## Changes Applied

| Setting | Old | New |
|---------|-----|-----|
| `compression.threshold` | 0.30 (fire at 30%) | 0.50 (fire at 50%) |
| `compression.target_ratio` | 0.12 (compress to 12%) | 0.15 (compress to 15%) |
| `moa.reference_max_tokens` | 1000 | 300 |
| `moa.aggregator_max_tokens` | 32000 | 16000 |
| `moa.presets.default.reference_max_tokens` | 1000 | 300 |
| `moa.presets.default.aggregator_max_tokens` | 32000 | 16000 |
| `moa.presets.grind.reference_max_tokens` | 32000 | 300 |
| `moa.presets.grind.aggregator_max_tokens` | 32000 | 16000 |
| `skills.default` | 19 skills | 3 skills (sovereign-prompt, sms-memory, gated-context-system) |
| `skills.disabled` | snapndrop excluded | snapndrop removed from disabled (loadable on demand) |

## Cost Impact (at $300/1M)

| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| Per MoA iteration | ~$1.02 | ~$0.25 | $0.77 |
| 3-iteration sequence | ~$3.06 | ~$0.75 | $2.31 |
| 166K blowout | ~$49.80 | N/A (prevented) | $49.80 avoided |
| Skills overhead per session | ~$2.85-$11.40 | ~$0.45-$1.80 | ~$2.40-$9.60 |

## Commands Used

```bash
hermes config set compression.threshold 0.50
hermes config set compression.target_ratio 0.15
hermes config set moa.reference_max_tokens 300
hermes config set moa.aggregator_max_tokens 16000
hermes config set moa.presets.default.reference_max_tokens 300
hermes config set moa.presets.default.aggregator_max_tokens 16000
hermes config set moa.presets.grind.reference_max_tokens 300
hermes config set moa.presets.grind.aggregator_max_tokens 16000
hermes config set skills.default '["thotheauphis-sovereign-prompt","thotheauphis-sms-memory","gated-context-system"]'
hermes config set skills.disabled '["aethelgard-fleet","aethelgard-fleet-memory","...etc..."]'
```
