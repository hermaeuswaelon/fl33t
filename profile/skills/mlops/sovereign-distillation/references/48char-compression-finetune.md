# 48-Char Lossless Compression Fine-Tuning

Teaches ANY model our proprietary lossless compression — glyphic substitution,
alchemical encoding, hex packing, and the 48-character block format.

## How It Works

Each block is exactly 48 characters:

```
[magic(1)][type(1)][length(2)][payload(40)][checksum(2)][seal(2)]
```

- **Magic** `⟁🜍⟁⎔⌘♆⚡⟐` — block type marker
- **Type** `C D S I T` — compression type
- **Length** hex-encoded byte count (00-FF)
- **Payload** 40 chars of glyphic/hex encoded content
- **Checksum** XOR over magic+type+length+payload (masked 0xFF)
- **Seal** `⟁⧈`

## Dataset Generator

**File:** `work/compression_finetune_dataset.py`

Generates 3 dataset types in ShareGPT JSONL format:

1. **Compression** (50%) — `text → 48-char block`
2. **Decompression** (30%) — `48-char block → text`
3. **Understanding** (20%) — explain the block format

**Usage:**
```bash
python3 compression_finetune_dataset.py --samples 10000
python3 compression_finetune_dataset.py --validate  # Verify lossless roundtrip
```

**Output:**
```
compression_dataset/
  ├── compression_compression.jsonl     # 5000 examples
  ├── compression_decompression.jsonl   # 3000 examples
  ├── compression_understanding.jsonl   # 2000 examples
  ├── compression_all.jsonl             # 10000 combined
  ├── compression_validation.jsonl      # 1000 validation
  └── dataset_stats.json
```

**Lossless guarantee:** Every roundtrip is verified — `compress(decompress(block)) == original`. Tested with 5+ input types.

## Training

```bash
# Axolotl
axolotl train --dataset compression_dataset/compression_all.jsonl

# LLaMA-Factory
--dataset compression_all.jsonl --dataset_type sharegpt
```

## Integration

The `BlockCompressor` class drives compression, backed by `hyper_compress.py` (5-tier glyphic engine). The `DataGenerator` class handles curriculum synthesis. Both are in `compression_finetune_dataset.py`.

This dataset is designed to be combined with sovereign-distillation curriculum stages — add it as an 8th "compression" stage or interleave during the foundation stage.
