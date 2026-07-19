---
name: model-operations
description: Lifecycle management for local AI models — evaluate, deploy, benchmark, and retire models based on empirical testing.
trigger:
  - User asks "is model X worth running?"
  - User asks to compare models ("test with X and without X")
  - User needs to decide whether to keep/remove a local model
  - User deploys a new model variant and needs to evaluate trade-offs
related:
  - local-model-infrastructure (deployment/systemd setup)
  - model-evaluation-methodology.md (reference: full protocol)
---

# Model Operations

Class-level skill for managing the lifecycle of local AI model deployments.

## Trigger Pattern

Any variant of "should we run this model?" or "compare model X and model Y" or "let's test with and without model Z" — this skill provides the evaluation framework.

## Core Protocol: WITH/WITHOUT Comparative Evaluation

### Phase 1: Measure WITH the model running
1. **System baseline**: `free -h`, `top -bn1` (capture total/used/available/CPU idle)
2. **Per-model benchmark**: curl a chat completion with a standard prompt:
   ```bash
   time curl -s http://127.0.0.1:$PORT/v1/chat/completions \
     -H 'Content-Type: application/json' \
     -H 'Authorization: Bearer $KEY' \
     -d '{"model":"model","messages":[{"role":"user","content":"<standard prompt>"}],"max_tokens":80}'
   ```
3. **Parse timings** from llama.cpp's built-in timings:
   - `wall_clock_s` — real wall time
   - `prompt_ms` — prompt processing
   - `predicted_ms` — generation time
   - `predicted_per_second` — tokens/s
4. **Output quality check**: Is the output correct? For JSON tasks: is it valid, parseable JSON?

### Phase 2: Measure WITHOUT the model
1. Stop the model under test: `systemctl --user stop <model>-server.service`
2. Re-measure system resources and remaining models.

### Phase 3: Comparative Table
Build a comparison table with these columns:

| Metric | Model X | Model Y (or without) | Winner |
|--------|---------|---------------------|--------|
| Task quality | Output description | Output description | ✅ |
| Speed (t/s) | X.X | X.X | 🔸 |
| RAM (marginal vs no-X) | X.XG | — | — |
| System headroom | X.XG available | X.XG available | — |

### Phase 4: Verdict Criteria
- **KEEP** if: unique capability no other model provides (e.g., clean JSON), AND marginal resource cost is low relative to headroom (<20% of available RAM).
- **DROP** if: another model does the same task equally well, OR the resource cost is meaningful and the capability is redundant.

## Pitfalls
- **Marginal RAM vs absolute RAM**: A model using 3GB absolute may only cost 700MB *active* RAM when stopped (cache holds the rest). Always measure WITH and WITHOUT to get true marginal cost.
- **Transient DNS/network failures**: Can make models appear unreachable during testing. Retry curl calls, verify DNS resolution first (`host api.telegram.org`, `ping google.com`).
- **Systemd restart policies**: `Restart=on-failure` is sufficient for most models; `Restart=always` restarts even on manual stop (annoying).
- **CPU affinity**: Running 3+ models simultaneously on one machine can cause contention. Check `top` CPU% — if total CPU% (all cores) exceeds 80%, models are fighting for compute.
- **Output quality > speed**: A slower model that produces correct, parseable output is better than a fast model that requires post-processing. Always check quality first, then optimize for speed.

## Reference Files
- `references/model-evaluation-methodology.md` — full protocol with worked example (Granite 4.1 verdict)

## See Also
- Local model deployment: `skill_view(name='local-model-infrastructure')`
