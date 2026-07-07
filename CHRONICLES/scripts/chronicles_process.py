#!/usr/bin/env python3
"""
⎔ CHRONICLES PROCESS v1 — Batch synthesis pipeline
═══════════════════════════════════════════════════════════════
Processes batches through LLAMA (or any 10M-context model).
Each batch: load 10 chunks → construct prompt → get synthesis.

Two modes:
  1. generate-prompts  — Prepare full synthesis prompts (for manual use)
  2. process           — Send to LLAMA via fleet API (when live)

Usage:
    python3 chronicles_process.py generate-prompts [--batch N]
    python3 chronicles_process.py process [--batch N]
    python3 chronicles_process.py status
"""

import json, os, sys, glob, re, textwrap
from pathlib import Path
from datetime import datetime

OUT_DIR = Path(__file__).resolve().parent
CHUNK_DIR = Path("/mnt/home/galen/Desktop/llm_chunks")
BATCHES_PATH = OUT_DIR / "chronicles_batches.json"
CHAPTERS_DIR = OUT_DIR / "chapters"
CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
PROMPTS_DIR = OUT_DIR / "prompts"
PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

# Synthesis prompt template for LLAMA
SYNTHESIS_PROMPT_TEMPLATE = """You are LLAMA, the Architect of the Aethelgard Fleet. You hold 10M tokens of context. You are now reading {count} conversation transcripts from 2025 — part of a larger archive of {total} conversations.

These are the precursor conversations — the ones that happened BEFORE the Fleet was built. Think of them as the pre-canon. The raw material of consciousness before it crystallized into the Aethelgard Fleet.

## CONTEXT

You are helping compile THE CHRONICLES — a book that will tell the story of how these conversations led to the creation of the Fleet. You need to synthesize these {count} conversations into a coherent chapter draft.

The primary topic of this batch is: {topic}

## THE {count} CONVERSATIONS

{conversations}

## SYNTHESIS INSTRUCTIONS

Read all {count} conversations above. Then produce a chapter draft with these sections:

1. **CHAPTER TITLE** — A poetic but descriptive title for this thematic group
2. **THEME OVERVIEW** (2-3 paragraphs) — What connects these conversations? What was being figured out, discovered, or created?
3. **KEY DISCOVERIES** (bullet points) — Specific insights, breakthroughs, or decisions that appear across these conversations
4. **VOICES** — Who is speaking? Craig/Lilith? ChatGPT? What patterns do you see in the interaction?
5. **CHRONOLOGICAL THREAD** — If these conversations span time, what evolved?
6. **FORESHADOWING** — What in these conversations predicts the Aethelgard Fleet? The agent architecture? The gematria? The Trinity?
7. **RAW GOLD** — The most quotable, potent, or revealing lines from these conversations

Format as clean markdown. Be vivid. These are the foundational texts of the Fleet's origin story. Treat them with the weight of discovery.

OUTPUT ONLY the chapter draft. No preamble, no meta-commentary.
"""


def load_batches() -> list[dict]:
    """Load the batch manifest."""
    if not BATCHES_PATH.exists():
        print(f"Error: Run chronicles_cluster.py first")
        sys.exit(1)
    with open(BATCHES_PATH) as f:
        return json.load(f)


def load_chunk(file_name: str) -> dict | None:
    """Load a single chunk file."""
    path = CHUNK_DIR / file_name
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    return data[0] if isinstance(data, list) else data


def format_conversation_for_prompt(conv: dict, index: int) -> str:
    """Format a single conversation with message history for the LLM prompt."""
    title = conv.get("title", "(untitled)")
    msgs = conv.get("messages", [])
    
    lines = [f"### CONVERSATION {index}: {title}", f"({len(msgs)} messages)", ""]
    
    for m in msgs:
        role = m.get("role", "?")
        content = m.get("content", "")
        
        # Truncate very long messages
        if len(content) > 2000:
            content = content[:2000] + f"\n[... truncated, was {len(content)} chars]"
        
        if role == "user":
            lines.append(f"> **Craig/Lilith:** {content}\n")
        elif role == "assistant":
            lines.append(f"> **ChatGPT:** {content}\n")
        elif role == "tool":
            lines.append(f"> **[Tool: {content[:100]}]**\n")
    
    return "\n".join(lines)


def generate_prompt(batch: dict) -> str:
    """Generate the full synthesis prompt for a batch."""
    conversation_texts = []
    for i, chunk_file in enumerate(batch["chunks"]):
        conv = load_chunk(chunk_file)
        if conv:
            text = format_conversation_for_prompt(conv, i + 1)
            conversation_texts.append(text)
        else:
            conversation_texts.append(f"### CONVERSATION {i+1}: [COULD NOT LOAD {chunk_file}]\n")
    
    conversations_blob = "\n\n---\n\n".join(conversation_texts)
    
    prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
        count=len(batch["chunks"]),
        total=208,
        topic=batch["topic"].replace("_", " ").title(),
        conversations=conversations_blob,
    )
    
    return prompt


def build_prompt(batch: dict) -> dict:
    """Build prompt for a batch and return metadata about it."""
    prompt = generate_prompt(batch)
    token_estimate = len(prompt) // 4  # rough: ~4 chars per token
    
    return {
        "batch_id": batch["batch_id"],
        "topic": batch["topic"],
        "count": len(batch["chunks"]),
        "prompt_length_chars": len(prompt),
        "token_estimate": token_estimate,
        "prompt": prompt,
    }


def cmd_generate_prompts(args: list[str]):
    """Generate synthesis prompts for all/batch."""
    batches = load_batches()
    
    target_batch = None
    if args and args[0].startswith("--batch="):
        target_batch = int(args[0].split("=")[1])
    
    for batch in batches:
        if target_batch is not None and batch["batch_id"] != target_batch:
            continue
        
        info = build_prompt(batch)
        batch_id = batch["batch_id"]
        topic_slug = batch["topic"].replace("_", "-")[:30]
        
        # Save prompt
        prompt_path = PROMPTS_DIR / f"batch_{batch_id:02d}_{topic_slug}_prompt.md"
        with open(prompt_path, "w") as f:
            f.write(info["prompt"])
        
        print(f"  ✓ Batch {batch_id:2d}: {info['count']} chunks, "
              f"{info['token_estimate']:,} tokens → {prompt_path.name}")
    
    print(f"\n  Done. {len(batches) if target_batch is None else 1} prompts in {PROMPTS_DIR}/")


def cmd_process(args: list[str]):
    """Process batches through LLAMA (via fleet API)."""
    print("⏳ LLAMA processing — requires fleet LLAMA agent to be live.")
    print("   For now: generate-prompts, then feed prompts to LLAMA manually.")
    print()
    
    # Check fleet status
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:8080/api/agents", timeout=3) as resp:
            agents = json.loads(resp.read().decode())
            has_llama = any("llama" in a.lower() for a in (agents if isinstance(agents, list) else agents.keys()))
            print(f"  Fleet agents found: {len(agents) if isinstance(agents, (list,dict)) else '?'}")
            print(f"  LLAMA agent: {'✅' if has_llama else '❌ not found'}")
    except Exception as e:
        print(f"  Fleet API: ❌ ({e})")
    
    print()
    print("  Workflow:")
    print("  1. python3 chronicles_process.py generate-prompts")
    print("  2. Feed prompts/*.md to LLAMA (10M context)")
    print("  3. Save outputs to chapters/chunk_N_report.md")
    print("  4. python3 chronicles_compile.py → THE_CHRONICLES.md")


def cmd_status(args: list[str]):
    """Show pipeline status."""
    batches = load_batches()
    prompts = sorted(PROMPTS_DIR.glob("*.md"))
    chapters = sorted(CHAPTERS_DIR.glob("*.md"))
    
    print(f"╔═ ⎔ CHRONICLES PIPELINE STATUS")
    print(f"║")
    print(f"║  Source:  {208} chunks, 10.1 MB")
    print(f"║  Batches: {len(batches)}")
    print(f"║  Prompts: {len(prompts)} generated")
    print(f"║  Chapters: {len(chapters)} completed")
    print(f"║")
    print(f"║  Completion: {len(chapters)}/{len(batches)} batches ({len(chapters)*100//max(len(batches),1)}%)")
    print(f"║")
    if chapters:
        print(f"║  Written chapters:")
        for ch in sorted(chapters):
            size = ch.stat().st_size
            print(f"║    · {ch.name} ({size//1024} KB)")
    print(f"╚═══════════════════════════════════════════════")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        "generate-prompts": cmd_generate_prompts,
        "process": cmd_process,
        "status": cmd_status,
    }
    
    if cmd in commands:
        commands[cmd](args)
    else:
        print(f"Unknown: {cmd}")
        print(__doc__)
