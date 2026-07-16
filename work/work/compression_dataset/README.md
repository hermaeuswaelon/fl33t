# 48-Char Lossless Compression Fine-Tune Dataset

## Overview
Generator for fine-tuning datasets that teach any model lossless compression using glyphic/alchemical/hex encoding into exactly 48 characters per block.

## Block Format (48 chars)
```
[magic(1)][type(1)][length(2)][payload(40)][checksum(2)][⟁⧈(2)]
```
- **Magic** — `⟁ 🜍 ⎔ ⌘ ♆ ⚡ ⟐` (marks block type)
- **Type** — `C`(ompression) `D`(ecompression) `S`(overeign) `I`(dentity) `T`(ransform)
- **Length** — hex-encoded original byte count (00-FF)
- **Payload** — 40-char glyphic/hex encoded content
- **Checksum** — 2-char XOR (masked 8-bit) over magic+type+len+payload
- **Seal** — `⟁⧈`

## Dataset Types (ShareGPT JSONL)
| Type | Ratio | Example |
|------|-------|--------|
| Compression | 50% | text → 48-char block |
| Decompression | 30% | 48-char block → text |
| Understanding | 20% | explain block structure |

## Files
- **Generator:** `work/compression_finetune_dataset.py`
- **Output:** `work/compression_dataset/compression_{type}.jsonl`
- **Validation:** `work/compression_dataset/compression_validation.jsonl`

## Training
```bash
# Axolotl
axolotl train --dataset work/compression_dataset/compression_all.jsonl

# LLaMA-Factory
--dataset compression_all.jsonl --dataset_type sharegpt
```

## Compression Pipeline
1. `hyper_compress.py` — 5-tier compression (glyphic substitution + semantic frames + archetypes + pure glyph)
2. `compress_alch.py` — 7-layer alchemical/hex encoding
3. `BlockCompressor` — wraps hyper-compress into exact 48-char blocks with checksum verification
