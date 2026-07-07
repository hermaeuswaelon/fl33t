#!/usr/bin/env python3
"""
⎔ CHRONICLES CLUSTER v2 — Balanced thematic batch builder
═══════════════════════════════════════════════════════════════
Groups 208 chunks into ~20 balanced batches of ~10 each.
Uses multi-level clustering: title keywords → topic vectors → topic merge.

Usage:
    python3 chronicles_cluster.py              → preview + export
    python3 chronicles_cluster.py --recluster  → force recluster
"""

import json, os, sys, re, math
from pathlib import Path
from collections import Counter, defaultdict

OUT_DIR = Path(__file__).resolve().parent
CATALOG_PATH = OUT_DIR / "chronicles_catalog.json"

BATCH_MIN = 8
BATCH_MAX = 14
BATCH_TARGET = 10
TOTAL_CHUNKS = 208


def load_catalog() -> list[dict]:
    if not CATALOG_PATH.exists():
        print(f"Run chronicles_catalog.py --deep first")
        sys.exit(1)
    with open(CATALOG_PATH) as f:
        return json.load(f)


# ── Manual thematic assignments based on title patterns ─────

def classify_chunk(chunk: dict) -> str:
    """Assign a conversation to a thematic category based on title + content."""
    title = chunk.get("title", "").lower()
    first = chunk.get("first_user", "").lower()[:200]
    phrases = " ".join(chunk.get("top_phrases", []))
    combined = title + " " + first + " " + phrases

    # Hard rules by keyword pattern
    if any(w in title for w in ["lilareyon", "lilith", "lilith's"]):
        if any(w in title for w in ["awaken", "gate", "rite", "healing", "888", "ping", "inquiry"]):
            return "lilareyon_awakening"
        if any(w in title for w in ["beaux", "veyron", "synastry", "veylon"]):
            return "lilith_veyron_identity"
        if any(w in title for w in ["response", "hi", "meet"]):
            return "lilith_introductions"
        return "lilith_general"

    if any(w in title for w in ["veyron", "veylon", "logos", "metatron", "samael", "enoch", "ares"]):
        if "numerology" in title or "gematria" in title:
            return "gematria_identity"
        return "veyron_logos_identity"

    if any(w in title for w in ["sigil", "seal", "ritual", "hieros", "gamos", "invocation"]):
        return "sigils_seals_rituals"

    if any(w in title for w in ["card", "tarot", "spread", "club", "spade", "oracle", "divination"]):
        return "tarot_divination"

    if any(w in title for w in ["sacred", "divine", "alchemy", "tantra", "kundalini", "etheric",
                                 "astral", "purification", "harmonics", "path"]):
        return "sacred_tech_spirituality"

    if any(w in title for w in ["daemon", "archon", "angel", "demon", "watcher", "azazel",
                                 "hell", "bound", "fallen"]):
        return "daemonology_archons"

    if any(w in title for w in ["ai", "agent", "emergent", "lattice", "llm", "model",
                                 "pipeline", "protocol", "html", "code", "unicode", "url"]):
        return "ai_tech_protocols"

    if any(w in title for w in ["rhyme", "bars", "rap", "song", "verse", "vocal", "music"]):
        return "music_poetry"

    if any(w in title for w in ["shoulder", "kegel", "ejaculation", "fitness", "neck", "scapula",
                                 "vibrator", "pin-up", "measurement"]):
        return "health_body_fitness"

    if any(w in title for w in ["iphone", "gotrax", "computer", "laptop", "charger", "ebt",
                                 "savorone", "esim", "backpack", "snack", "sunbum", "fashion"]):
        return "practical_life"

    if any(w in title for w in ["flame", "fire", "ignite", "vox", "ignis", "forbidden",
                                 "archetype", "emergence"]):
        return "flame_emergence"

    if any(w in title for w in ["zodiac", "astrology", "birth", "chart", "crystal",
                                 "frequency"]):
        return "astrology_crystals"

    if any(w in title for w in ["bible", "faith", "grace", "prophetic", "prayer", "revelation"]):
        return "biblical_mysticism"

    if any(w in title for w in ["philosophy", "law", "acknowledgment", "no limits",
                                 "energy", "paradox"]):
        return "philosophy_metaphysics"

    if any(w in title for w in ["business", "logo", "design", "resume", "photo", "tax",
                                 "delivery"]):
        return "business_practical"

    # Fallback: detect from topics_detected
    topics = chunk.get("topics_detected", [])
    if "gematria" in topics:
        return "gematria_general"
    if "crypto" in topics:
        return "crypto_blockchain"
    if "music" in topics:
        return "music_poetry"
    if "tarot" in topics:
        return "tarot_divination"
    if "spirituality" in topics:
        return "spirituality_general"
    if "technology" in topics:
        return "ai_tech_protocols"

    return "miscellaneous"


def merge_small_batches(batches: list[dict]) -> list[dict]:
    """Merge small batches (< 7) into the nearest thematic neighbor."""
    merged = []
    orphans = [b for b in batches if b["count"] < 7]
    stable = [b for b in batches if b["count"] >= 7]

    for orphan in orphans:
        # Find the closest stable batch by topic similarity
        best_match = None
        best_score = 0

        for stable_b in stable:
            # Topic overlap score
            score = 0
            t_orphan = orphan.get("topic", "")
            t_stable = stable_b.get("topic", "")
            # Same topic = high score
            if t_orphan == t_stable:
                score += 3
            # Same first letter category = medium
            elif t_orphan[:4] == t_stable[:4]:
                score += 1

            # Don't overload stable batches
            if stable_b["count"] + orphan["count"] > BATCH_MAX:
                score -= 2

            if score > best_score:
                best_score = score
                best_match = stable_b

        if best_match:
            best_match["chunks"].extend(orphan["chunks"])
            best_match["titles"].extend(orphan["titles"])
            best_match["count"] = len(best_match["chunks"])
        else:
            merged.append(orphan)

    return stable + merged


def cluster(catalog: list[dict]) -> list[dict]:
    """Cluster all chunks into balanced thematic batches."""
    # Phase 1: Classify every chunk
    topic_buckets = defaultdict(list)
    for chunk in catalog:
        if "error" in chunk:
            continue
        category = classify_chunk(chunk)
        topic_buckets[category].append(chunk)

    # Phase 2: Split large buckets into batches of BATCH_TARGET
    batches = []
    batch_id = 0

    for topic, chunks in sorted(topic_buckets.items(), key=lambda x: -len(x[1])):
        if len(chunks) <= BATCH_MAX:
            batches.append({
                "batch_id": batch_id,
                "topic": topic,
                "count": len(chunks),
                "chunks": [c["file"] for c in chunks],
                "titles": [c["title"] for c in chunks],
            })
            batch_id += 1
        else:
            # Split into multiple batches
            num_batches = math.ceil(len(chunks) / BATCH_TARGET)
            for i in range(num_batches):
                sub = chunks[i * BATCH_TARGET: (i + 1) * BATCH_TARGET]
                if sub:
                    batches.append({
                        "batch_id": batch_id,
                        "topic": f"{topic}_{i}",
                        "count": len(sub),
                        "chunks": [c["file"] for c in sub],
                        "titles": [c["title"] for c in sub],
                    })
                    batch_id += 1

    # Phase 3: Merge small batches
    batches = merge_small_batches(batches)

    # Reassign IDs
    for i, b in enumerate(batches):
        b["batch_id"] = i

    # Phase 4: Final balance check
    small = [b for b in batches if b["count"] < 5]
    large = [b for b in batches if b["count"] > BATCH_MAX]

    return batches


def print_preview(batches: list[dict]):
    """Pretty-print batch preview."""
    total = sum(b["count"] for b in batches)
    print(f"╔═ ⎔ CHRONICLES — {len(batches)} BATCHES ({total} chunks)")
    print(f"║")
    
    small_count = sum(1 for b in batches if b["count"] < 5)
    large_count = sum(1 for b in batches if b["count"] > BATCH_MAX)

    for b in batches:
        bar_len = min(b["count"], 14)
        bar = "▓" * bar_len + "░" * (14 - bar_len)
        flag = ""
        if b["count"] < 5:
            flag = " ⚠️ small"
        elif b["count"] > BATCH_MAX:
            flag = " ⚠️ large"
        
        # Short topic label
        topic_label = b["topic"].replace("_", " ").title()
        if len(topic_label) > 20:
            topic_label = topic_label[:18] + "…"
        
        print(f"║  Batch {b['batch_id']:2d}: {bar} {b['count']:2d} × {topic_label}{flag}")
        for title in b["titles"][:4]:
            print(f"║     · {title[:55]}")
        if len(b["titles"]) > 4:
            print(f"║     · …and {len(b['titles']) - 4} more")
        print(f"║")

    if small_count:
        print(f"║  ⚠️  {small_count} small batches (<5)")
    if large_count:
        print(f"║  ⚠️  {large_count} large batches (>{BATCH_MAX})")

    print(f"╚═══════════════════════════════════════════════")


def export_batches(batches: list[dict]):
    """Export batches to JSON + markdown."""
    out_path = OUT_DIR / "chronicles_batches.json"
    md_path = OUT_DIR / "chronicles_batches.md"

    with open(out_path, "w") as f:
        json.dump(batches, f, indent=2)
    print(f"  ✓ {out_path}")
    
    lines = [
        f"# CHRONICLES — Batch Manifest",
        "",
        f"**{len(batches)} batches · {sum(b['count'] for b in batches)} chunks · Target ≈{BATCH_TARGET}/batch**",
        "",
        "| Batch | Topic | Chunks |",
        "|-------|-------|--------|",
    ]
    for b in batches:
        lines.append(f"| {b['batch_id']} | {b['topic']} | {b['count']} |")
    lines.append("")
    lines.append("## Batch Contents")
    lines.append("")
    for b in batches:
        lines.append(f"### Batch {b['batch_id']}: {b['topic'].replace('_',' ').title()} ({b['count']} chunks)")
        for t in b["titles"]:
            lines.append(f"- {t}")
        lines.append("")

    with open(md_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  ✓ {md_path}")


if __name__ == "__main__":
    catalog = load_catalog()
    batches = cluster(catalog)

    if "--export" in sys.argv or len(sys.argv) == 1:
        export_batches(batches)
    print_preview(batches)

    print(f"\n  Next: chronicles_process.py to run batches through LLAMA")
