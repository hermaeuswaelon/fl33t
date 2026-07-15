# Context Continuity — DeepSeek Frozen Prompt Rollover

## Problem

DeepSeek v4 (and v3/v2 MLA models) have a 256K context window. Data
generation for identity distillation requires long-running teacher sessions
that can easily exceed this limit — 100+ conversation turns with identity-rich
responses (~2K tokens each) fills 256K in ~120 turns.

The naive solution (truncating old context) destroys identity coherence
because the model loses earlier self-referential grounding.

## Solution: Frozen Prompt Rollover

DeepSeek's API is stateless — every request must include the full message
history. However, DeepSeek's **context caching** automatically detects
repeated prompt prefixes across requests. When the same prefix is seen
again, the cached computation is reused at ~98% cost reduction.

The key insight: **the system prompt is the stable prefix.** It's sent once
and repeated identically in every request. This means we can use the system
prompt area as a context carry-over buffer.

### Rollover Protocol

Normal operation:
- Turn 1:   [system prompt (frozen)] [user] [assistant]  →  ~3K tokens
- Turn 2:   [system prompt (frozen)] [user] [assistant]  →  ~6K tokens
- ...
- Turn N:   [system prompt (frozen)] ...                → ~200K tokens

When approaching 256K limit:
1. Take the ENTIRE accumulated context (~210K tokens)
2. Start a new thread
3. system_prompt = [original identity prompt] + [ALL prior conversation history]
4. user_message = "New thread, continuity preserved"
5. DeepSeek caches the repeated prefix (identity prompt + history) as a
   cache hit. The ~210K prefix costs ~2K tokens of fresh compute.
6. Continue seamlessly

Repeat indefinitely — each rollover doubles the effective context.

### Why this works with DeepSeek specifically

- **Context caching is automatic** — no special flags needed. Any repeated
  prefix in the `messages` array is a candidate for cache-hit pricing.
- **The system prompt is the ideal prefix** — it's stable, sent first in
  every request, and never changes during a session.
- **Cache-hit pricing** on v4-flash: $0.0028/token vs $0.14 cache-miss
  (98% reduction on the repeated prefix).
- **DeepSeek does not truncate** the cached prefix — it can be arbitrarily
  long as long as the total stays within the 256K window.

### Simpler alternative: Periodic Checkpoint

Instead of monitoring the token budget continuously, roll over on a fixed
schedule — every 4-5 turns. This has lower overhead:

- Turn 5:  Take full context → prepend to system prompt → new thread
- Turn 10: Same
- Turn 15: Same

Each rollover adds the previous turns to the cached prefix. The effective
context grows by ~10-15K tokens per checkpoint, doubling roughly every
20 checkpoints.

## Output Token Budget (max_tokens)

The teacher model's output token limit directly affects response quality.
When unset, Hermes Agent defaults to **4096 tokens** per response — too
short for identity-rich data generation.

### Configuration

In Hermes Agent, set `max_tokens` under the `model:` section of
`~/.NOTTHEONETOEDIT/config.yaml` (or `$HERMES_HOME/config.yaml`):

```yaml
model:
  default: deepseek-v4-flash
  provider: deepseek
  max_tokens: 32768
```

Recommended values:
- **32768** — Good balance for data generation. Allows full identity-rich
  responses (~20-30K output tokens) without hitting the cap mid-response.
- **65536** — Maximum practical for very long multi-turn generations.
- **16384** — Conservative. Safe for most use cases but may truncate
  complex gematria or philosophical expositions.
- **4096** — Default when unset. Too short for identity work.

### Without configuration

If `model.max_tokens` is absent from config.yaml, the Hermes Agent falls
back to its hardcoded default of 4096 output tokens. Responses self-cap
at this limit, which truncates long identity responses mid-gematria or
mid-argument, forces compression (reducing marker density), and wastes
generation opportunities.

Always set `max_tokens` explicitly when running data generation pipelines.

## Important Caveats

1. **Not infinite** — Each rollover adds the previous window's context to
   the prefix. After ~5-7 rollovers at 200K each, the total prefix (~1-1.4M
   tokens) may approach practical caching limits. In practice, 500K-1M tokens
   of effective context is achievable before diminishing returns.

2. **Cache hits are opportunistic** — DeepSeek does not guarantee a cache
   hit. Repeated identical prefixes are *likely* to hit, but there are no
   SLAs. Always design for the cache-miss case (slower, more expensive, but
   still works).

3. **Not suitable for interactive use** — The rollover introduces a brief
   interruption (new thread creation, context re-initialization). Use this
   for batch data generation where a moment of pause is acceptable.

4. **Stick to the same model** — v4-flash and v4-pro have different latent
   spaces. Rolling over from one to the other breaks the cache and may
   produce incoherent identity responses. Keep the same model ID across
   all rollovers in a generation session.
