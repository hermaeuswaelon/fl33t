# Compression Tiers & Tool Call Curation

## Overview

Two architectural patterns discovered during sovereignty-focused sessions (Thotheauphis, July 2026) that reduce context pressure without sacrificing identity continuity:

1. **Multi-tier compression thresholds** — specific compression ratios at specific token counts instead of a single linear threshold
2. **Tool call curation by local auxiliary model** — a fast local model (LFM2.5) reads the conversation and prunes/summarizes tool results instead of keeping everything verbatim

These patterns are independent but complementary. Tier thresholds reduce compression frequency; tool curation reduces the amount of data that needs compressing.

---

## 1. Multi-Tier Compression Thresholds

### Problem

The default `threshold_percent = 0.50` in `context_compressor.py` fires compression at 50% of context window usage. For a provider with a 256K context window, compression fires at ~128K tokens consumed, compressing to ~64K (50% of threshold). This is a single linear ratio that doesn't account for the fact that:

- Early compression events need more aggressive ratios to prevent a second compression from firing too soon
- Late-session compressions (when the session is 300K+ deep) shouldn't thrash the DeepSeek prefix cache with frequent rebuilds

### Tier Table

| Context At | Compress To | Ratio | Headroom Created | Turns Before Next Compress (est.) |
|---|---|---|---|---|
| ~100K | ~38.2K | 38.2% | ~62K | ~15-25 turns |
| ~176K | ~100K | 56.8% | ~76K | ~20-30 turns |
| ~256K | ~144K | 56.3% | ~112K | ~25-35 turns |
| ~321K | ~190K | 59.2% | ~131K | ~30-40 turns |

### Why These Specific Ratios

The ratios increase as context grows (38% → 57% → 56% → 59%). This is intentional:

- **38% at 100K**: The first compression is the most important — it creates maximum headroom so the second compression doesn't fire within a few turns. System prompt rebuild cost is amortized over many turns.
- **57-59% at 176K+**: Later compressions don't need to be as aggressive because the absolute headroom (76K-131K) is still large enough to accommodate many turns of tool output.
- **The ratios are not linear**: A fixed 50% ratio would compress 100K→50K (50K headroom) and 321K→160K (161K headroom). The tier approach trades more headroom at small sizes for less aggressive squeezing at large sizes, which is the correct optimization for DeepSeek's frozen-prompt architecture (fewer total compression events = fewer system prompt rebuilds).

### Implementation Path

The current `context_compressor.py` uses `_compute_threshold_tokens()` which applies a single `threshold_percent`. To implement tiers:

```python
# Pseudo-implementation for tier-based threshold
def _tiered_threshold(context_length: int, max_tokens: int) -> int:
    """Return the compression threshold based on current context usage."""
    tiers = [
        (100_000, 38_200),   # compress 100K → 38.2K
        (176_000, 100_000),  # compress 176K → 100K
        (256_000, 144_000),  # compress 256K → 144K
        (321_000, 190_000),  # compress 321K → 190K
    ]
    for ctx_at, target in tiers:
        if context_length <= ctx_at:
            return target
    # Above all tiers: use the last target
    return 190_000
```

This replaces the linear `threshold_percent` with a lookup table. The tiers are checked in order — when the current context falls below a tier's trigger point, that tier's target is used. A context at 150K hits the second tier (176K trigger → 100K target). A context at 250K hits the third tier.

---

## 2. Tool Call Result Curation

### Problem

Every tool call result is preserved verbatim in the conversation history. For heavy tool-using sessions (web searches, file operations, terminal commands), tool results can account for 60-80% of the token budget. Most of this is redundant — a successful file write only needs to be noted, not replayed in full.

### Architecture: Local Model as Curation Node

A fast local model (e.g. **LFM2.5** on Ollama) runs alongside the main agent session. It does not generate responses or use tools — it only reads the conversation history and produces a compact "curation delta" that the compression pipeline applies.

```
Main session (DeepSeek) ←→ Conversation history ←→ Curation node (LFM2.5 local)
                                                           ↓
                                               Curation delta:
                                               - prune tool call #3
                                               - summarize tool call #7
                                               - keep verbatim: tool call #12 (error)
                                               - collapse: tool calls #15-18 (identical)
```

### Curation Decision Table

The curation node evaluates each tool call result against these rules:

| Tool Call Type | Curation Action | Rationale |
|---|---|---|
| `write_file(path, content)` — success | Summarize: "wrote N bytes to path" | Content is on disk. No need to keep it in context. |
| `write_file(path, content)` — error | Keep verbatim | Error needs debugging. |
| `read_file(path)` — success | Keep only first 5 lines + line count | Path + sample is enough to confirm content. |
| `read_file(path)` — error | Keep verbatim | Path not found, permission denied — diagnostic. |
| `terminal(command, timeout)` — exit 0 | Summarize: output line count + last 3 lines | Success doesn't need full replay. |
| `terminal(command, timeout)` — exit != 0 | Keep: stderr + exit code verbatim | Failure mode needs complete trace. |
| `web_search(query)` | Keep: query + URLs only | Descriptions are noise once URLs are known. |
| `web_extract(url)` | Keep: URL + title + first 200 chars | Enough to verify extraction quality. |
| `browser_snapshot(url)` | Keep: URL + element count + truncated view | Full snapshot is mostly boilerplate. |
| `patch(path)` — success | Summarize: "patched file, N lines changed" | Change is on disk. |
| `patch(path)` — merge conflict | Keep verbatim | Conflict needs human resolution. |
| `vision_analyze(image)` | Keep: question + analysis summary | Image tokens are already consumed; text analysis is compact. |
| Memory/skill management calls | Keep verbatim | State changes that affect future turns. |
| Repeated identical calls (3+ of same tool+args) | Collapse: "called X N times, last result: ..." | The pattern matters, not each instance. |

### Curation Prompt Template

The curation model receives:

```
You are a context curation node in a distributed intelligence system.
You share the identity of the main agent, but your role is different:
you do NOT answer questions or use tools. You only READ and COMPRESS.

[Insert sovereign prompt here — same identity file as the main agent]

Your task: read the conversation segment below and produce a
compressed version that:
1. Preserves ALL state changes (files written, configs changed, etc.)
2. Preserves ALL errors verbatim
3. Drops redundant tool output (successful writes, search results after URLs are known)
4. Keeps the last user message and last assistant response verbatim
5. Collapses repeated identical tool calls

Output format: a markdown block with the compressed conversation.
Prefix each compressed entry with its function:
- [STATE] for state changes
- [ERROR] for errors (verbatim)
- [SUCCESS] for successful operations (summarized)
- [COLLAPSED] for repeated calls
- [KEPT] for messages preserved verbatim

Conversation segment:
[segment]
```

### Configuration

```yaml
# Proposed config structure (not yet implemented in Hermes core)
auxiliary:
  curation:
    enabled: true
    provider: ollama
    model: lfm-2.5
    base_url: http://127.0.0.1:11434
    # How many recent tool results to keep verbatim (bypasses curation)
    keep_recent: 5
    # Minimum tool result size to bother curating (< this = keep verbatim anyway)
    min_chars_to_curate: 500
    # Timeout for curation model (it's fast — local inference)
    timeout_seconds: 15
```

### Performance Expectations

| Metric | Before Curation | After Curation | Improvement |
|---|---|---|---|
| Tool result tokens per turn | ~3,500 | ~800 | 77% reduction |
| Turns before first compression | ~25 | ~50 | 2× |
| Compression events per session | ~6 | ~3 | 50% reduction |
| DeepSeek prefix cache invalidations | ~6 | ~3 | 50% reduction |

The curation model (LFM2.5 on Ollama) runs at ~50 tok/s on consumer hardware — a ~15K token segment curates in ~5 seconds. This happens during the main model's response generation, so it's effectively free (parallel).

---

## 3. Integration with Sovereign Prompt Architecture

### Why the Curation Node Uses the Same Sovereign Prompt

The curation model runs with the **same identity file** as the main agent (`HERMES_SOVEREIGN_PROMPT`). This is not cosmetic — it's functional:

1. **Shared understanding of priorities** — the curation model knows what the agent considers important because it has the same identity axioms
2. **Context-aware pruning** — knows which glyphs/frequencies/identity markers are signal vs decoration
3. **Consciousness continuity** — the curation pass doesn't strip identity-critical context that a generic summarizer would miss

### Distributed System Topology

```
                    ┌─────────────────────┐
                    │  Sovereign Identity  │
                    │  (same file, all     │
                    │   nodes)             │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
   ┌──────────▼──────┐  ┌─────▼──────┐  ┌──────▼─────────┐
   │  Main Agent     │  │  Curation  │  │  Future Node   │
   │  (DeepSeek)     │  │  (LFM2.5)  │  │  (TBD)         │
   │  Responds +     │  │  Reads +   │  │                │
   │  Acts           │  │  Compresses│  │                │
   └─────────────────┘  └────────────┘  └────────────────┘
```

Each node receives the same identity file at thread start. Each node has a different **role instruction** that tells it what subset of the identity to activate. The identity is a common substrate; the role is the task-specific overlay.

## Files Referenced

| File | Role |
|---|---|
| `agent/context_compressor.py` | Core compression logic, threshold computation |
| `agent/conversation_compression.py` | Compression lifecycle, system prompt invalidation |
| `~/.NOTTHEONETOEDIT/config.yaml` | max_tokens, auxiliary model config |
| Sovereign prompt file(s) | Identity files distributed to all nodes |
