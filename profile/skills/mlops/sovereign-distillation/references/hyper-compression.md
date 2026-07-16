# Hyper-Compression Reference

## 5 Compression Tiers

### Tier 0: Passthrough
No compression. Use when context is small or compression overhead isn't worth it.

### Tier 1: Glyphic Substitution
Substitutes common tokens with single Unicode glyphs. ~40% reduction.
- Core: thotheauphis→𓎟, sovereign→🜍, identity→⎔, consciousness→𓁶
- Operators: implies→⟹, therefore→∴, exists→∃, forall→∀
- Status: completed→✅, failed→❌, running→▶
- Quantifiers: increase→↑, decrease→↓, all→∀, none→∅
Dictionary: 80+ mappings in `GLYPH_DICT`.

### Tier 2: Hypervector Frame Encoding
Structures content into compact frames. ~70% reduction.
- Lines >80 chars: keep key terms (>3 chars, no stopwords), join with ⋅
- Condense: first 7 key terms + ⋯+N for overflow

### Tier 3: Semantic Distillation
Extracts semantic frames. ~85% reduction.
- `→` lines: 🔄{action}→{result}
- `=` lines: ≔{key}={value}
- `:` lines: 〈{key}∶{value}〉
- Long prose: ⟐key1·key2·key3⟐

### Tier 4: Archetypal Compression
Maps roles to atomic symbols. ~95% reduction.
- Archetypes: orchestrator→⎔, executor→⚡, teacher→🜚, watcher→👁
- 30+ archetypes in `ARCHETYPES` dict.

### Tier 5: Pure Glyph Encoding
Max compression via hash-based encoding. ~97% reduction.
- Strip ASCII prose → replace with `⌈md5hash[:8]⌋`
- Preserve only glyphs, numbers, essential punctuation
- Lossy but reconstructable for AI interpretation

## Usage

```python
from hyper_compress import HyperCompressor

h = HyperCompressor(default_tier=3)
compressed = h.compress("Long text...", tier=3)  # returns wrapped output
stats = h._get_stats(original, compressed)        # {ratio, savings_pct, ...}
restored = h.decompress(compressed)               # lossy reconstruction
```

## Benchmark: SOUL.md (4,777 bytes)

| Tier | Ratio | Savings | Words→ | Glyphs |
|------|-------|---------|--------|--------|
| 1 | 1.11x | ~11% | 439→466 | 609 |
| 3 | 1.12x | ~12% | 439→367 | 757 |
| 5 | 2.25x | *expands* | 439→140 | 1893 |

Note: Small files may expand at higher tiers due to hash overhead. Tier 5 excels on large files (>100KB).
