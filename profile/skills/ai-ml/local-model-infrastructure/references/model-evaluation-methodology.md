# Model Evaluation Methodology

Systematic framework for deciding "is this model worth running?"

## Trigger
User asks whether to keep/remove/test a local model, or says "let's run some tests with X and without it."

## Protocol

### Phase 1: WITH Model (baseline fleet)
Run all desired models. Measure:

1. **System resources**: `free -h` (total/used/available), `top -bn1` (CPU%, idle%)
2. **Per-model speed**: curl chat completion with same prompt, parse timings:
   - wall_clock_s = total real time
   - prompt_ms = prompt processing time
   - predicted_ms = generation time  
   - predicted_per_second = tokens/s
3. **Output quality**: Does the output match the task? JSON tasks need clean parseable JSON.

### Phase 2: WITHOUT Model
Stop the model under test. Re-measure #1 and #2 for remaining models.

### Phase 3: Comparative Table

| Metric | Model X | Model Y | Winner |
|--------|---------|---------|--------|
| **Task quality** | Description of output | Description of output | ✅ |
| **Speed** | X.X t/s | X.X t/s | 🔸 |
| **Marginal RAM cost** | X.XG diff vs without | — | — |
| **System headroom** | X.XG available | X.XG available | — |

### Phase 4: Verdict
- **KEEP IT** if the model provides a unique capability (e.g., clean JSON, structured output) that no other model can do, AND the marginal resource cost is low relative to headroom.
- **DROP IT** if another model can do the same task equally well, OR the resource cost is meaningful (>20% of available RAM).

## Example: Granite 4.1 3B Verdict (2026-07-18)

**Ask**: "We'll not run granite unless it's worth it — run tests with and without."

**Result**: Granite was the ONLY model that output clean parseable JSON (`{"key":"val"}` vs LFM's function-call wrapping). Marginal RAM cost 700MB on a system with 9GB available — essentially free. **Verdict: KEEP.**

## Key Insight
The WITH/WITHOUT comparison reveals the **marginal cost** of a model, not just its absolute RAM usage. When the system has abundant headroom (e.g., 9GB available), even a 3GB model may cost only 700MB of active RAM after cache eviction.
