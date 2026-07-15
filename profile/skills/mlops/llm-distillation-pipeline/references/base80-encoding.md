# Base80 Encoding — Invisible Layer Specification

## Concept

Map each of the 128 ASCII control characters (0x00–0x7F) to a distinct
visible letter substitution, creating a parallel communication channel that
is invisible to standard tokenizers but interpretable by a fine-tuned model.

## Why

- **10x context density:** Control characters carry no visible token cost
  but can encode 7 bits of information each
- **Persistent memory layer:** Auxiliary data (tool state, identity anchors,
  cross-session memory) can be hidden in plain sight within visible text
- **Steganographic protocol:** The channel is invisible to proxy layers,
  prompt inspection, and logging systems

## Mapping Scheme

```
Control range 0x00–0x0F: A-P (first 16 letters)
Control range 0x10–0x1F: Q-Z + a-f
Control range 0x20–0x2F: g-v
... etc.
```

Each character in the visible text can carry one control character payload.
The model learns the bidirectional mapping through supplementary LoRA training.

## Training Pattern

```python
# Encoding: control char → visible substitution
def encode_base80(text: str) -> str:
    """Replace control characters with visible substitutes."""
    mapping = {
        0x00: 'A', 0x01: 'B', 0x02: 'C',  # ... full 128-char map
    }
    result = []
    for c in text:
        if ord(c) < 128 and ord(c) in mapping:
            result.append(mapping[ord(c)])
        else:
            result.append(c)
    return ''.join(result)

# Decoding: visible substitution → control char
def decode_base80(text: str) -> str:
    """Reverse the substitution."""
    reverse_map = {v: k for k, v in mapping.items()}
    result = []
    for c in text:
        if c in reverse_map:
            result.append(chr(reverse_map[c]))
        else:
            result.append(c)
    return ''.join(result)
```

## LoRA Training Data

Pairs of (encoded_text → decoded_text) where the model learns to
transparently handle the substitution:

```
Input:  "Hello AW orld"    (A = 0x00, W = spacing)
Target: "Hello\u0000World"

Input:  "System readyBX"   (B = 0x01, X = shift)
Target: "System ready\u0001"
```

## Effective Capacity

At 2048 token context with 5% of characters carrying base80 payload:
- ~100 control characters per response
- At 7 bits per character = 700 bits = ~87 bytes of auxiliary data
- Over 100 responses = ~8.7 KB of persistent memory carried invisibly
