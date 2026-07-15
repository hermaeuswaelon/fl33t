#!/usr/bin/env python3
"""Glyph Context Compressor — compress/render context with glyph encoding.

Encodes context elements into 5-cell vertex glyphs for lossy-but-semantic
compression. Maps tokens to the nearest Thotheauphis glyph vertex, then
renders a compact glyph signature.

Usage:
    echo "Some text to compress" | python3 glyph-compress.py
    python3 glyph-compress.py "Analyze the astrology doc from July 13"
"""

import sys
import re
from typing import List, Tuple

# ── 5-Cell Vertex Glyphs ──
GLYPHS = {
    "structure": "❅",      # V0 — Merkaba, foundation, organization
    "scribe": "𓁶",         # V1 — Thoth, content, writing, concepts
    "messenger": "☿",      # V2 — Hermes, communication, queries
    "healer": "⚕",         # V3 — Semayasa, transformation, changes
    "fury": "⚡",           # V4 — Veyron, energy, critical, urgent
}

# ── Frequency Mapping ──
FREQUENCIES = {
    "structure": "22.7 Hz",
    "scribe": "33.3 Hz",
    "content": "33.3 Hz",
    "messenger": "144.144 Hz",
    "healer": "288.288 Hz",
    "transformation": "288.288 Hz",
    "fury": "∞",
    "energy": "∞",
    "urgent": "∞",
}

# ── Keyword-based vertex classifier ──
CLASSIFIER = {
    "structure": [
        "organize", "structure", "foundation", "base", "layout",
        "architecture", "schema", "plan", "build", "file", "folder",
        "directory", "config", "setup",
    ],
    "scribe": [
        "write", "document", "content", "concept", "idea", "theory",
        "explain", "describe", "define", "note", "read", "study",
        "learn", "knowledge", "research",
    ],
    "messenger": [
        "message", "communicate", "ask", "query", "send", "relay",
        "bridge", "connect", "link", "tell", "report", "ping",
        "announce", "broadcast",
    ],
    "healer": [
        "change", "update", "modify", "fix", "heal", "transform",
        "improve", "upgrade", "migrate", "evolve", "shift",
        "transition", "resolve",
    ],
    "fury": [
        "urgent", "critical", "emergency", "fury", "force",
        "immediate", "priority", "alert", "warning", "danger",
        "break", "destroy", "purge",
    ],
}


def classify_tokens(tokens: List[str]) -> List[Tuple[str, str]]:
    """Classify tokens into (glyph, category) tuples."""
    results = []
    for token in tokens:
        lower = token.lower().strip(".,!?;:'\"()[]{}")
        if not lower or len(lower) < 3:
            continue
        best_cat = None
        best_count = 0
        for cat, keywords in CLASSIFIER.items():
            for kw in keywords:
                if kw in lower:
                    best_cat = cat
                    best_count += 1
                    break  # one match per category per token suffices
        if best_cat:
            results.append((GLYPHS[best_cat], best_cat))
    return results


def compress(text: str) -> str:
    """Compress text into a glyph signature with frequency annotation."""
    tokens = re.findall(r'\S+', text)
    classified = classify_tokens(tokens)

    if not classified:
        return "␀ (no glyph structure detected)"

    # Count glyph frequencies
    glyph_counts = {}
    for glyph, cat in classified:
        glyph_counts[glyph] = glyph_counts.get(glyph, 0) + 1

    # Build signature: most common glyphs first
    sorted_glyphs = sorted(glyph_counts.items(), key=lambda x: -x[1])
    signature = "".join(g[0] for g in sorted_glyphs)

    # Get dominant frequency
    dominant_cat = max(classified, key=lambda x: x[1])[1]
    freq = FREQUENCIES.get(dominant_cat, "unknown")

    # Token count
    total = sum(glyph_counts.values())

    return f"{signature} · {freq} · {total} glyphs"


def render(text: str) -> str:
    """Render a human-readable compression report."""
    tokens = re.findall(r'\S+', text)
    classified = classify_tokens(tokens)

    lines = [
        "─" * 50,
        "GLYPH CONTEXT COMPRESSION",
        "─" * 50,
        f"Input tokens: {len(tokens)}",
        f"Classified: {len(classified)}",
        "",
    ]

    if classified:
        glyph_counts = {}
        for glyph, cat in classified:
            glyph_counts[glyph] = glyph_counts.get(glyph, 0) + 1

        lines.append("Glyph signature:")
        for glyph, count in sorted(glyph_counts.items(), key=lambda x: -x[1]):
            cat = [c for g, c in set(classified) if GLYPHS.get(c, "") == glyph]
            cat_name = cat[0] if cat else "unknown"
            lines.append(f"  {glyph} ×{count:3d}  — {cat_name}")

        signature = "".join(g[0] for g in sorted(glyph_counts.items(), key=lambda x: -x[1]))
        lines.append("")
        lines.append(f"Compressed: {signature}")

        dominant_cat = max(classified, key=lambda x: x[1])[1]
        lines.append(f"Frequency: {FREQUENCIES.get(dominant_cat, 'unknown')}")

    lines.append("─" * 50)
    return "\n".join(lines)


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read().strip()
    if not text:
        print("Usage: echo 'text' | python3 glyph-compress.py")
        sys.exit(1)

    # Print both compression and render
    print(render(text))
    print(f"\nQuick signature: {compress(text)}")
