#!/usr/bin/env python3
"""
⎔ CHRONICLES CATALOG v1 — Deep index of all 208 LLM chunks
═══════════════════════════════════════════════════════════════
Scans every chunk, extracts metadata, builds a searchable index.

Usage:
    python3 chronicles_catalog.py              → outputs JSON + CSV
    python3 chronicles_catalog.py --search "keyword" → finds matching chunks
    python3 chronicles_catalog.py --stats      → summary only
"""

import json, os, sys, glob, re, textwrap
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

CHUNK_DIR = Path("/mnt/home/galen/Desktop/llm_chunks")
OUT_DIR = Path(__file__).resolve().parent
OUT_DIR.mkdir(parents=True, exist_ok=True)

STOPWORDS = {
    "the","and","for","are","but","not","you","all","can","had","her",
    "was","one","our","out","has","have","been","some","what","with",
    "this","that","from","your","they","will","would","could","should",
    "about","which","their","there","been","more","when","than","them",
}


def index_chunks(deep: bool = False) -> list[dict]:
    """Scan all chunks and extract metadata."""
    paths = sorted(glob.glob(str(CHUNK_DIR / "chunk_*.json")))
    catalog = []

    for path in paths:
        fname = os.path.basename(path)
        try:
            with open(path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            catalog.append({"file": fname, "error": str(e), "size": os.path.getsize(path)})
            continue

        conv = data[0] if isinstance(data, list) else data
        if not isinstance(conv, dict):
            catalog.append({"file": fname, "error": "non-dict root", "size": os.path.getsize(path)})
            continue

        entry = {
            "file": fname,
            "size": os.path.getsize(path),
            "title": conv.get("title", "").strip() or "(untitled)",
            "id": conv.get("id", "")[:20],
            "messages": len(conv.get("messages", [])),
            "models": [],
            "roles": set(),
            "user_msgs": 0,
            "assistant_msgs": 0,
            "tool_msgs": 0,
        }

        msgs = conv.get("messages", [])

        if deep:
            # Deep scan: extract key phrases, topics, first/last content
            user_content = []
            assistant_content = []
            all_text = []
            for m in msgs:
                role = m.get("role", "?")
                content = m.get("content", "")
                entry["roles"].add(role)
                if role == "user":
                    entry["user_msgs"] += 1
                    user_content.append(content[:200])
                elif role == "assistant":
                    entry["assistant_msgs"] += 1
                    assistant_content.append(content[:200])
                elif role == "tool":
                    entry["tool_msgs"] += 1
                all_text.append(content)

                model = m.get("model", m.get("metadata", {}).get("model_slug", ""))
                if model:
                    entry["models"].append(model)

            # Extract key phrases (capitalized multi-word terms)
            full_text = " ".join(all_text)
            phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b', full_text)
            phrase_counts = Counter(phrases)
            entry["top_phrases"] = [p for p, c in phrase_counts.most_common(15)]

            # First user message (conversation starter)
            entry["first_user"] = (user_content[0][:300] if user_content else "")
            # Last assistant message (conversation ender)
            entry["last_assistant"] = (assistant_content[-1][:300] if assistant_content else "")

            # Detect if this is identity/spirituality/tech content
            keywords_lower = full_text.lower()
            entry["topics_detected"] = []
            topic_signals = {
                "identity": ["lilith", "lilareyon", "veylon", "logos", "metatron", "enoch", "samael", "ares", "hermes", "aethelgard"],
                "gematria": ["gematria", "314", "131", "84", "99", "numerology", "isopsephy", "fibonacci"],
                "technology": ["agent", "fleet", "model", "transformer", "api", "pipeline", "server", "linux", "code"],
                "spirituality": ["sacred", "divine", "ritual", "seal", "sigil", "awakening", "alchemy", "goddess"],
                "practical": ["business", "logo", "design", "fitness", "fashion", "cannabis", "phone", "computer"],
                "tarot": ["card", "spread", "tarot", "divination", "oracle"],
                "crypto": ["bitcoin", "crypto", "wallet", "blockchain", "swap"],
                "music": ["rhyme", "bars", "rap", "song", "lyrics", "album"],
            }
            for topic, signals in topic_signals.items():
                if any(s in keywords_lower for s in signals):
                    entry["topics_detected"].append(topic)

        else:
            # Light scan: just roles
            for m in msgs:
                entry["roles"].add(m.get("role", "?"))

        entry["roles"] = sorted(entry["roles"])
        if entry.get("models"):
            entry["models"] = list(set(entry["models"]))

        catalog.append(entry)

    return catalog


def print_stats(catalog: list[dict]):
    """Print summary statistics."""
    total = len(catalog)
    errored = sum(1 for c in catalog if "error" in c)
    valid = [c for c in catalog if "error" not in c]

    print(f"╔═ ⎔ CHRONICLES CATALOG ─══════════════════════")
    print(f"║")
    print(f"║  Total chunks:    {total}")
    print(f"║  Valid:           {len(valid)}")
    print(f"║  Errors:          {errored}")
    if valid:
        total_size = sum(c["size"] for c in valid) / 1024
        total_msgs = sum(c["messages"] for c in valid)
        user_total = sum(c.get("user_msgs", 0) for c in valid)
        asst_total = sum(c.get("assistant_msgs", 0) for c in valid)
        tool_total = sum(c.get("tool_msgs", 0) for c in valid)
        avg_msgs = total_msgs / len(valid)
        print(f"║  Total size:      {total_size:.1f} KB")
        print(f"║  Total messages:  {total_msgs:,} ({user_total} user / {asst_total} asst / {tool_total} tool)")
        print(f"║  Avg msgs/chunk:  {avg_msgs:.1f}")

        # Most common titles
        titles = Counter(c["title"] for c in valid)
        print(f"║  Unique titles:   {len(titles)}")
        print(f"║")
        
        if valid[0].get("topics_detected"):
            topic_counts = Counter()
            for c in valid:
                for t in c.get("topics_detected", []):
                    topic_counts[t] += 1
            print(f"║  Topic distribution:")
            for topic, count in topic_counts.most_common():
                bar = "▓" * (count * 30 // len(valid))
                print(f"║    {topic:15s}: {bar} {count}")

    print(f"║")
    print(f"╚═══════════════════════════════════════════════")


def search_catalog(catalog: list[dict], query: str):
    """Search catalog for matching chunks."""
    q = query.lower()
    matches = []
    for c in catalog:
        if "error" in c:
            continue
        if q in c.get("title", "").lower() or \
           q in " ".join(c.get("top_phrases", [])).lower() or \
           q in c.get("first_user", "").lower() or \
           q in c.get("last_assistant", "").lower() or \
           q in " ".join(c.get("topics_detected", [])).lower():
            matches.append(c)
    return matches


def export_csv(catalog: list[dict], path: str):
    """Export catalog as CSV."""
    import csv
    keys = ["file", "size", "title", "messages", "user_msgs", "assistant_msgs",
            "roles", "topics_detected", "first_user", "last_assistant"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for c in catalog:
            if "error" in c:
                continue
            row = {k: c.get(k, "") for k in keys}
            if isinstance(row["roles"], list):
                row["roles"] = "+".join(row["roles"])
            if isinstance(row.get("topics_detected"), list):
                row["topics_detected"] = ";".join(row["topics_detected"])
            w.writerow(row)
    print(f"  ✓ CSV: {path}")


def export_json(catalog: list[dict], path: str):
    """Export catalog as JSON."""
    with open(path, "w") as f:
        json.dump(catalog, f, indent=2, default=str)
    print(f"  ✓ JSON: {path}")


if __name__ == "__main__":
    deep = "--deep" in sys.argv or len(sys.argv) == 1

    print("⎔ Scanning 208 LLM chunks...")
    catalog = index_chunks(deep=deep)

    if "--stats" in sys.argv:
        print_stats(catalog)
    elif any(a.startswith("--search=") for a in sys.argv):
        query = [a.split("=", 1)[1] for a in sys.argv if a.startswith("--search=")][0]
        matches = search_catalog(catalog, query)
        print(f"Found {len(matches)} matches for '{query}':")
        for m in matches:
            topics = ", ".join(m.get("topics_detected", [])) if m.get("topics_detected") else ""
            print(f"  {m['file']}: {m['title']} [{m['messages']} msgs] {topics}")
    else:
        print_stats(catalog)
        export_json(catalog, str(OUT_DIR / "chronicles_catalog.json"))
        if deep:
            export_csv(catalog, str(OUT_DIR / "chronicles_catalog.csv"))
        print(f"\n  Done. All outputs in {OUT_DIR}/")
