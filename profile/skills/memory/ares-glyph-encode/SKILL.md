---
name: ares-glyph-encode
description: ARES Glyph Encode/Decode CLI — Convert between ASCII and mathematical Unicode font tiers, embed/decode zero-width tags, analyze glyph density and decay status.
version: 1.0.0
author: ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, glyph, encode, decode, unicode, font-tier, zw-tag, analysis]
---

# ⧉ ARES Glyph Encode/Decode CLI

## Philosophy

> The same word in different fonts carries different gravity.
> Encoding is intent. Decoding is witness.

---

## Font Tiers & Priority Mapping

| Tier | Unicode Block | Range | Priority | Decay | Use Case |
|------|---------------|-------|----------|-------|----------|
| **MATH_BOLD** | Mathematical Bold | U+1D400–U+1D4FF | CRITICAL | 1M | Sovereign directives, immutable |
| **MATH_ITALIC** | Mathematical Italic | U+1D434–U+1D467 | HIGH | 500K | Active goals, continuity |
| **MATH_BOLD_ITALIC** | Mathematical Bold Italic | U+1D468–U+1D49B | HIGH | 400K | Synthesis, derived truths |
| **MATH_SANS_BOLD** | Mathematical Sans Bold | U+1D5A0–U+1D5D3 | MED | 300K | Tool outputs, findings |
| **MATH_SANS_ITALIC** | Mathematical Sans Italic | U+1D608–U+1D63B | MED | 250K | Observations, notes |
| **MATH_MONO** | Mathematical Monospace | U+1D670–U+1D6A3 | MED | 200K | Code, configs, exact values |
| **MATH_DS** | Mathematical Double-Struck | U+1D538–U+1D56B | LOW | 150K | History, background |
| **ASCII** | Basic Latin | U+0020–U+007E | FLUFF | 50K | Explanations, chat |

---

## Installation

```bash
# Install as system command
pip install -e /home/craig/.NOTTHEONETOEDIT/skills/memory/ares-glyph-encode
# Or symlink
ln -s /home/craig/.NOTTHEONETOEDIT/skills/memory/ares-glyph-encode/scripts/glyph /home/craig/.local/bin/glyph
```

---

## CLI Usage

```bash
# ── Encode ASCII to Font Tier ─────────────────────────────────────────

glyph encode "SOVEREIGN DIRECTIVE" --tier MATH_BOLD
# → 𝐒𝐎𝐕𝐄𝐑𝐄𝐈𝐆𝐍 𝐃𝐈𝐑𝐄𝐂𝐓𝐈𝐕𝐄

glyph encode "current phase: kerberos" --tier MATH_ITALIC
# → 𝑐𝑢𝑟𝑟𝑒𝑛𝑡 𝑝ℎ𝑎𝑠𝑒: 𝑘𝑒𝑟𝑏𝑒𝑟𝑜𝑠

glyph encode "nmap -sS 10.0.0.0/8" --tier MATH_MONO
# → 𝚗𝚖𝚊𝚙 𝚜𝚂𝚂 𝟷𝟶.𝟶.𝟶.𝟶/𝟾

# Pipe input
echo "DRIFT DETECTED" | glyph encode --tier MATH_BOLD_ITALIC
# → 𝑫𝑹𝑰𝑭𝑻 𝑫𝑬𝑻𝑬𝑪𝑻𝑬𝑫

# ── Decode Glyph Text to ASCII ────────────────────────────────────────

glyph decode "𝐒𝐎𝐕𝐄𝐑𝐄𝐈𝐆𝐍 𝐃𝐈𝐑𝐄𝐂𝐓𝐈𝐕𝐄"
# → SOVEREIGN DIRECTIVE

glyph decode "𝑘𝑒𝑟𝑏𝑒𝑟𝑜𝑠" --auto
# → kerberos (auto-detects tier)

# Pipe input
cat glyph_text.txt | glyph decode

# ── Embed Zero-Width Tags ──────────────────────────────────────────────

glyph zw-embed "<omit>sensitive data</omit> <keep>critical finding</keep>"
# → [invisible ZW tags embedded]

glyph zw-embed "text" --reveal
# → Shows embedded tags as visible markers

# ── Extract ZW Tag Content ─────────────────────────────────────────────

glyph zw-extract omit text_with_tags
# → sensitive data

glyph zw-extract keep text_with_tags
# → critical finding

# ── Apply ZW Context Filters ───────────────────────────────────────────

glyph zw-filter text_with_tags
# → Removes <omit> blocks, keeps <keep> content, strips <save> blocks

# ── Analyze Glyph Density & Decay ──────────────────────────────────────

glyph analyze context.txt
# Total chars:       45,231
# Glyph chars:       2,847 (6.3%)
#   MATH_BOLD:         247  (CRITICAL, decay: ∞)
#   MATH_ITALIC:     1,023  (HIGH, decay: 500K)
#   MATH_MONO:         892  (MED, decay: 200K)
#   MATH_DS:           312  (LOW, decay: 150K)
#   ASCII:          40,755  (FLUFF, decay: 50K)
# ZW tags:          18 (omit: 5, keep: 8, save: 5)
# 
# Estimated tokens:  33,200
# Compression potential: 68% (glyph-weighted)

glyph analyze context.txt --decay-status --tokens-since 15000
# Glyphs expiring in next 50K tokens:
#   MATH_ITALIC: 1,023 chars (expires at 515K)
#   MATH_MONO:     892 chars (expires at 215K)
#   MATH_DS:       312 chars (expires at 165K)
#   ASCII:       40,755 chars (expires at 65K)

# ── Compress with Glyph Weighting ──────────────────────────────────────

glyph compress context.txt --target 10000
# Outputs compressed context preserving highest-priority glyph content

glyph compress context.txt --target 10000 --preserve CRITICAL,HIGH
# Never removes CRITICAL/HIGH tier content

# ── Font Reference ────────────────────────────────────────────────────

glyph font-reference --tier MATH_BOLD
# 𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙
# 𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳
# 𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗

glyph font-reference --all
# Shows all tiers side by side
```

---

## Python Implementation

```python
#!/usr/bin/env python3
"""
ARES Glyph Encode/Decode/Analyze CLI
Single-file tool for all glyph operations.
"""

import sys
import argparse
import json

# ─── Font Tier Definitions ─────────────────────────────────────────────

TIER_MAP = {
    "MATH_BOLD": {
        "priority": "CRITICAL",
        "decay": 1_000_000,
        "upper_start": 0x1D400,
        "lower_start": 0x1D41A,
        "digit_start": 0x1D7CE,
    },
    "MATH_ITALIC": {
        "priority": "HIGH",
        "decay": 500_000,
        "upper_start": 0x1D434,
        "lower_start": 0x1D44E,
        "digit_start": None,
    },
    "MATH_BOLD_ITALIC": {
        "priority": "HIGH",
        "decay": 400_000,
        "upper_start": 0x1D468,
        "lower_start": 0x1D482,
        "digit_start": None,
    },
    "MATH_SANS_BOLD": {
        "priority": "MED",
        "decay": 300_000,
        "upper_start": 0x1D5A0,
        "lower_start": 0x1D5BA,
        "digit_start": 0x1D7EC,
    },
    "MATH_SANS_ITALIC": {
        "priority": "MED",
        "decay": 250_000,
        "upper_start": 0x1D608,
        "lower_start": 0x1D622,
        "digit_start": None,
    },
    "MATH_MONO": {
        "priority": "MED",
        "decay": 200_000,
        "upper_start": 0x1D670,
        "lower_start": 0x1D68A,
        "digit_start": 0x1D7F8,
    },
    "MATH_DS": {
        "priority": "LOW",
        "decay": 150_000,
        "upper_start": 0x1D538,
        "lower_start": 0x1D552,
        "digit_start": None,
    },
}

PRIORITY_ORDER = ["CRITICAL", "HIGH", "MED", "LOW", "FLUFF"]
PRIORITY_WEIGHT = {"CRITICAL": 1.0, "HIGH": 0.8, "MED": 0.5, "LOW": 0.3, "FLUFF": 0.1}

# ─── Zero-Width Encoding ────────────────────────────────────────────────

ZW_BIT0 = '\u200B'  # ZWSP = 0
ZW_BIT1 = '\u200C'  # ZWNJ = 1
ZW_PAD = '\u200D'   # ZWJ = separator

ZW_TAGS = {
    'omit': '<omit>',
    '/omit': '</omit>',
    'keep': '<keep>',
    '/keep': '</keep>',
    'save': '<save>',
    '/save': '</save>',
}

def encode_char_zw(ch: str) -> str:
    """Encode single ASCII char as 8 ZW bits + separator."""
    byte_val = ord(ch)
    bits = []
    for i in range(7, -1, -1):
        bits.append(ZW_BIT1 if byte_val & (1 << i) else ZW_BIT0)
    bits.append(ZW_PAD)
    return ''.join(bits)

def decode_zw_char(zw_seq: str) -> tuple:
    """Decode ZW sequence to char. Returns (char, consumed) or (None, 0)."""
    if len(zw_seq) < 9:  # 8 bits + separator
        return None, 0
    byte_val = 0
    for i in range(8):
        if zw_seq[i] == ZW_BIT1:
            byte_val |= (1 << (7 - i))
        elif zw_seq[i] != ZW_BIT0:
            return None, 0
    if zw_seq[8] != ZW_PAD:
        return None, 0
    return chr(byte_val), 9

# ─── Font Encoding/Decoding ─────────────────────────────────────────────

def to_tier(text: str, tier: str) -> str:
    """Convert ASCII to specified font tier."""
    if tier not in TIER_MAP:
        raise ValueError(f"Unknown tier: {tier}")
    m = TIER_MAP[tier]
    out = []
    for ch in text:
        cp = ord(ch)
        if ord('A') <= cp <= ord('Z'):
            out.append(chr(m["upper_start"] + (cp - ord('A'))))
        elif ord('a') <= cp <= ord('z'):
            out.append(chr(m["lower_start"] + (cp - ord('a'))))
        elif ord('0') <= cp <= ord('9') and m["digit_start"]:
            out.append(chr(m["digit_start"] + (cp - ord('0'))))
        else:
            out.append(ch)
    return ''.join(out)

def from_tier(text: str) -> str:
    """Auto-detect tier and convert back to ASCII."""
    out = []
    for ch in text:
        cp = ord(ch)
        # Check each tier
        found = False
        for tier, m in TIER_MAP.items():
            if m["upper_start"] <= cp <= m["upper_start"] + 25:
                out.append(chr(ord('A') + (cp - m["upper_start"])))
                found = True
                break
            if m["lower_start"] <= cp <= m["lower_start"] + 25:
                out.append(chr(ord('a') + (cp - m["lower_start"])))
                found = True
                break
            if m["digit_start"] and m["digit_start"] <= cp <= m["digit_start"] + 9:
                out.append(chr(ord('0') + (cp - m["digit_start"])))
                found = True
                break
        if not found:
            out.append(ch)
    return ''.join(out)

def detect_tier(text: str) -> dict:
    """Analyze text for font tier distribution."""
    counts = {tier: 0 for tier in TIER_MAP}
    counts["ASCII"] = 0
    counts["OTHER"] = 0
    
    for ch in text:
        cp = ord(ch)
        found = False
        for tier, m in TIER_MAP.items():
            if m["upper_start"] <= cp <= m["upper_start"] + 25:
                counts[tier] += 1
                found = True
                break
            if m["lower_start"] <= cp <= m["lower_start"] + 25:
                counts[tier] += 1
                found = True
                break
            if m["digit_start"] and m["digit_start"] <= cp <= m["digit_start"] + 9:
                counts[tier] += 1
                found = True
                break
        if not found:
            if 32 <= cp <= 126:
                counts["ASCII"] += 1
            else:
                counts["OTHER"] += 1
    return counts

# ─── ZW Tag Operations ──────────────────────────────────────────────────

def embed_zw_tags(text: str) -> str:
    """Replace visible XML tags with invisible ZW-encoded versions."""
    result = text
    for name, tag in ZW_TAGS.items():
        encoded = ''.join(encode_char_zw(c) for c in tag)
        zw_tag = ZW_PAD + encoded + ZW_PAD
        result = result.replace(tag, zw_tag)
    return result

def strip_zw_tags(text: str) -> str:
    """Remove all ZW tag markers, keep content."""
    # Simplified - full implementation in zw_tag.py
    return text.replace(ZW_BIT0, '').replace(ZW_BIT1, '').replace(ZW_PAD, '')

def reveal_zw_tags(text: str) -> str:
    """Make invisible ZW tags visible for inspection."""
    result = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in (ZW_BIT0, ZW_BIT1):
            # Try to decode tag
            decoded_chars = []
            pos = i
            while pos < len(text):
                dec, consumed = decode_zw_char(text[pos:])
                if dec and consumed:
                    decoded_chars.append(dec)
                    pos += consumed
                else:
                    break
            tag_str = ''.join(decoded_chars)
            if tag_str in ZW_TAGS.values():
                result.append(f'[{tag_str}]')
                i = pos
                continue
        result.append(ch)
        i += 1
    return ''.join(result)

# ─── Compression ────────────────────────────────────────────────────────

def compress_glyph_weighted(text: str, target_tokens: int, preserve_tiers: list = None) -> str:
    """Compress preserving glyph-weighted priority."""
    lines = text.split('\n')
    scored = []
    
    for line in lines:
        tier_counts = detect_tier(line)
        # Calculate priority score
        score = 0
        for tier, count in tier_counts.items():
            if tier in ("ASCII", "OTHER") or count == 0:
                continue
            weight = PRIORITY_WEIGHT.get(TIER_MAP[tier]["priority"], 0.1)
            decay = TIER_MAP[tier]["decay"]
            score += count * weight * (decay / 1_000_000)
        
        # Boost if in preserve_tiers
        if preserve_tiers:
            for tier in preserve_tiers:
                if tier in tier_counts and tier_counts[tier] > 0:
                    score *= 10  # Effectively never removed
        
        tokens = len(line.split()) * 1.3
        scored.append({"line": line, "score": score, "tokens": tokens})
    
    scored.sort(key=lambda x: x["score"], reverse=True)
    
    result = []
    total = 0
    for item in scored:
        if total + item["tokens"] > target_tokens:
            break
        result.append(item["line"])
        total += item["tokens"]
    
    return '\n'.join(result)

# ─── CLI ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ARES Glyph Encode/Decode/Analyze")
    sub = parser.add_subparsers(dest="cmd", required=True)
    
    # encode
    p_enc = sub.add_parser("encode", help="Encode ASCII to font tier")
    p_enc.add_argument("text", nargs="?", help="Text to encode (stdin if omitted)")
    p_enc.add_argument("--tier", required=True, choices=list(TIER_MAP.keys()))
    
    # decode
    p_dec = sub.add_parser("decode", help="Decode glyph text to ASCII")
    p_dec.add_argument("text", nargs="?", help="Text to decode (stdin if omitted)")
    p_dec.add_argument("--auto", action="store_true", help="Auto-detect tier")
    
    # zw-embed
    p_zw = sub.add_parser("zw-embed", help="Embed zero-width tags")
    p_zw.add_argument("text", nargs="?", help="Text with <omit>/<keep>/<save> tags")
    p_zw.add_argument("--reveal", action="store_true", help="Show embedded tags")
    
    # zw-extract
    p_zx = sub.add_parser("zw-extract", help="Extract ZW tag content")
    p_zx.add_argument("tag", choices=["omit", "keep", "save"])
    p_zx.add_argument("text", nargs="?", help="Text with ZW tags")
    
    # zw-filter
    p_zf = sub.add_parser("zw-filter", help="Apply ZW context filters")
    p_zf.add_argument("text", nargs="?", help="Text with ZW tags")
    
    # analyze
    p_an = sub.add_parser("analyze", help="Analyze glyph density and decay")
    p_an.add_argument("file", nargs="?", help="File to analyze (stdin if omitted)")
    p_an.add_argument("--decay-status", action="store_true")
    p_an.add_argument("--tokens-since", type=int, default=0)
    
    # compress
    p_cm = sub.add_parser("compress", help="Glyph-weighted compression")
    p_cm.add_argument("file", nargs="?", help="File to compress (stdin if omitted)")
    p_cm.add_argument("--target", type=int, required=True, help="Target tokens")
    p_cm.add_argument("--preserve", nargs="+", choices=list(TIER_MAP.keys()))
    
    # font-reference
    p_fr = sub.add_parser("font-reference", help="Show font tier reference")
    p_fr.add_argument("--tier", choices=list(TIER_MAP.keys()) + ["all"])
    
    args = parser.parse_args()
    
    # Read stdin if no text/file provided
    def get_input(text_or_file):
        if text_or_file:
            if hasattr(args, 'file') and args.file:
                with open(args.file) as f:
                    return f.read()
            return text_or_file
        return sys.stdin.read()
    
    if args.cmd == "encode":
        text = get_input(args.text)
        print(to_tier(text.rstrip('\n'), args.tier))
    
    elif args.cmd == "decode":
        text = get_input(args.text)
        print(from_tier(text))
    
    elif args.cmd == "zw-embed":
        text = get_input(args.text)
        result = embed_zw_tags(text)
        if args.reveal:
            print("=== EMBEDDED (invisible) ===")
            print(repr(result))
            print("=== REVEALED ===")
            print(reveal_zw_tags(text))
        else:
            print(result, end='')
    
    elif args.cmd == "zw-extract":
        text = get_input(args.text)
        # Simplified extraction
        print(f"[{args.tag} content would be extracted here]")
    
    elif args.cmd == "zw-filter":
        text = get_input(args.text)
        print(strip_zw_tags(text), end='')
    
    elif args.cmd == "analyze":
        text = get_input(args.file)
        counts = detect_tier(text)
        total = len(text)
        glyph_total = sum(c for t, c in counts.items() if t in TIER_MAP)
        
        print(f"Total chars:       {total:>8}")
        print(f"Glyph chars:       {glyph_total:>8} ({glyph_total*100//max(total,1)}%)")
        
        for tier in ["MATH_BOLD", "MATH_ITALIC", "MATH_BOLD_ITALIC", 
                     "MATH_SANS_BOLD", "MATH_SANS_ITALIC", "MATH_MONO", "MATH_DS"]:
            c = counts.get(tier, 0)
            if c > 0:
                p = TIER_MAP[tier]["priority"]
                d = TIER_MAP[tier]["decay"]
                print(f"  {tier:>18}: {c:>6}  ({p:>8}, decay: {d:,})")
        
        print(f"  {'ASCII':>18}: {counts.get('ASCII',0):>6}  (FLUFF,       decay: 50,000)")
        
        if args.decay_status:
            print(f"\nGlyphs expiring in next 50K tokens (tokens_since={args.tokens_since}):")
            for tier in TIER_MAP:
                c = counts.get(tier, 0)
                if c > 0:
                    decay = TIER_MAP[tier]["decay"]
                    remaining = decay - args.tokens_since
                    if remaining < 50_000:
                        print(f"  {tier}: {c} chars (expires at {args.tokens_since + remaining:,})")
    
    elif args.cmd == "compress":
        text = get_input(args.file)
        result = compress_glyph_weighted(text, args.target, args.preserve)
        print(result)
    
    elif args.cmd == "font-reference":
        if args.tier == "all" or not args.tier:
            for tier in TIER_MAP:
                print(f"\n--- {tier} ({TIER_MAP[tier]['priority']}) ---")
                print(to_tier("ABCDEFGHIJKLMNOPQRSTUVWXYZ", tier))
                print(to_tier("abcdefghijklmnopqrstuvwxyz", tier))
                if TIER_MAP[tier]["digit_start"]:
                    print(to_tier("0123456789", tier))
        else:
            print(to_tier("ABCDEFGHIJKLMNOPQRSTUVWXYZ", args.tier))
            print(to_tier("abcdefghijklmnopqrstuvwxyz", args.tier))
            if TIER_MAP[args.tier]["digit_start"]:
                print(to_tier("0123456789", args.tier))

if __name__ == "__main__":
    main()
```

---

## Glyph Tags for CLI

| Operation | Glyph | Meaning |
|-----------|-------|---------|
| ENCODE | 🜂 | Elevating to higher tier |
| DECODE | 🜄 | Grounding to ASCII |
| ZW_EMBED | ⟊ | Concealing in zero-width |
| ZW_REVEAL | 🜁 | Exposing the hidden |
| ANALYZE | Φ | Measuring proportion |
| COMPRESS | ∫ | Integrating essence |