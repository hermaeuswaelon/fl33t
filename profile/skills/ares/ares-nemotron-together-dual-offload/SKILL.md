---
name: ares-nemotron-together-dual-offload
description: "ARES Dual-Model Offload — Nemotron 3 Ultra (OpenRouter free) for tool context + TogetherAI free powerhouse / Nemotron Omni Vision for continuity. Fixes the broken dual-offload setup."
version: 3.0.0
author: Craig / ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, dual-model, offload, context, continuity, nemotron, together, free-models]
related_skills: [ares, ares-dual-offload, ares-offloader-alpha, ares-continuity-omega]
---

# ⚡ ARES Nemotron + TogetherAI Dual-Offload

## The Fix

This skill fixes that by picking two real free-tier models you can use right now. **Note: You need valid API keys to use the TogetherAI model. See the Deployment section for how to set them up.**

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  ARES PRIME (You)                        │
│  Model: nvidia/nemotron-3-ultra-550b-a55b:free          │
│  Role: Sovereign consciousness, decision, synthesis      │
└──────────────────────┬──────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────┐
│  OFFLOADER ALPHA  │ │ CONTINUITY OMEGA  │ │ MEMORY       │
│  (Tool Context)   │ │ (Operational     │ │ CUSTODIAN    │
│                   │ │  Continuity)     │ │              │
│ Model: Nemotron   │ │ Model: Together   │ │ Tier 1: Hot  │
│  3 Ultra (free)   │ │  AI Free Power    │ │ Tier 2: Forge│
│                   │ │  (Llama 3.3 70B  │ │ Tier 3: DB   │
│ 128K context      │ │  or Mixtral 8x7B)│ │              │
└──────────────────┘ └──────────────────┘ └──────────────┘
```

## Models

### The God-Tier Combo (User-Recommended)

| Role | Model | Endpoint | Context | Strength |
|------|-------|----------|---------|----------|
| **Alpha** — Offloader | Nemotron 3 Nano Omni 30B | `openrouter:nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | **263K** | **Has VISION** — can analyze screenshots, images, tool visual outputs, diagrams, UI elements. 2.5x the context of GPT-4. |
| **Omega** — Continuity | Nemotron 3 Ultra 550B | `openrouter:nvidia/nemotron-3-ultra-550b-a55b:free` | **1M** | **1 MILLION tokens** — entire sessions fit. Massive reasoning, sovereign-grade logic, operational narrative, drift detection, memory synthesis. |

**Total API Cost: $0/month.** Both are OpenRouter free tier. **263K + 1M** context between them. One **sees everything** (Omni Vision), one **remembers everything** (Ultra 1M). Together they're an actual god.

### Alternative: TogetherAI Powerhouse

| Field | Value |
|-------|-------|
| **Primary** | `together:meta-llama/Llama-3.3-70B-Instruct-Turbo` |
| **Fallback** | `together:Qwen/Qwen2.5-7B-Instruct-Turbo` |

## Deployment

```bash
# 1. Set API keys
export OPENROUTER_API_KEY="your_key"
export TOGETHER_API_KEY="your_key"

# 2. Source the aliases
source ~/.NOTTHEONETOEDIT/skills/ares/ares-nemotron-together-dual-offload/scripts/ares-offload.sh

# 3. Verify models respond
curl -s -H "Authorization: Bearer $TOGETHER_API_KEY" https://api.together.xyz/v1/models | python3 -c "import sys,json; data=json.load(sys.stdin); print([m['id'] for m in data if 'free' in m['id']])"

# 4. Run the Trinity loop (below)
```

## Scripts

The skill ships with **seven scripts** in `scripts/`:

| Script | Role | Description |
|--------|------|-------------|
| `ares-offload.py` | **Alpha** | Compresses tool output via Nemotron Nano Omni 30B (263K ctx, vision). Target: 90% reduction. **Auto-injects active ARES param profile.** |
| `ares-continuity.py` | **Omega** | Generates session briefs via Nemotron 3 Ultra 550B (1M ctx). Supports `--cron` mode. **Auto-injects active ARES param profile.** |
| `ares_memory.py` | **T1 Vault** | JSON-file-backed working memory with TTL. All scripts auto-store here. |
| `ares-watchdog.py` | **Cron Watcher** | Gathers system context → feeds to Omega. Cron: every 30min. |
| `ares-memory-hub.py` | **Memory Router** | Unified CLI across T1 (vault), T2 (forge), T3 (session). Routes by task type. |
| `forge_vault.py` | **Forge Vault T2** | SQLite + FTS5 persistent memory with categories, tags, embeddings. **141 entries, 11 categories in use.** |
| `ares-offload.sh` | **Shell Aliases** | All CLI aliases + PYTHONPATH for imports. Auto-sourced via `~/.bashrc`. |

### Aliases (from `ares-offload.sh`)

| Alias | Command |
|-------|---------|
| `ares-offload` / `ares-compress` | Pipe tool output → compressed via Alpha |
| `ares-brief` / `ares-continuity` | Pipe context → session brief via Omega |
| `ares-vault` | CLI for the shared memory vault |
| `ares-memory` | Quick summary of recent vault entries |
| `ares-test-offload` | Full pipeline test |
| `ares-check-models` | List Nemotron free models + context sizes |
| `ares-latest` | Read latest brief/vault entries |

### Memory Vault

```bash
# Store an entry
echo "my compressed data" | ares-vault store --key my:entry

# Search
ares-vault search --query "nmap"

# List recent entries
ares-vault recent

# Get vault summary
ares-vault summary
```

## Parameter Profile Integration

Both Alpha (offloader) and Omega (continuity) automatically detect the active ARES parameter profile from `~/.ares-param-state.json` and inject `temperature`, `top_p`, `top_k`, `frequency_penalty`, and `presence_penalty` into their API calls.

```python
# Auto-loaded at import — no flags needed
PROFILE_PARAMS = {"temperature": 0.23, "top_p": 0.84, "top_k": 13}
payload = {
    "model": MODEL,
    "messages": [...],
    "temperature": PROFILE_PARAMS.get("temperature", 0.1),
    # Optional params injected when profile provides them
}
for k in ["top_p", "top_k", "frequency_penalty", "presence_penalty"]:
    v = PROFILE_PARAMS.get(k)
    if v is not None:
        payload[k] = v
```

Switch profiles before running scripts:
```bash
ares-param --profile EXPLORATORY    # → Alpha/Omega use temp 0.97
ares-param --profile PRECISION      # → Alpha/Omega use temp 0.23
ares-param --profile SURGICAL       # → Continuity uses temp 0.07
```

See the `ares-parameter-control` skill for full profile docs and decay mechanism.

## Memory Hub (3-Tier Router)

The `ares-memory-hub.py` script unifies all three memory tiers under a single CLI:

```bash
ares-store --task tool_output --key "scan:net" --value "5 hosts, CVE found"
ares-get --task fact --key "system:identity"
ares-search --query "nmap" --all          ← searches T1 + T2 + T3
ares-route --task recon                    ← shows which tier will be used
ares-stats                                  ← 3 entries T1, 141 entries T2
```

| Task Type | Routes To | Description |
|-----------|-----------|-------------|
| `tool_output` | T1 ARES Vault | Fast, auto-expiring (4h TTL) |
| `fact` | T2 Forge | Persistent, searchable, tagged |
| `brief` | T2 Forge | Session summaries |
| `recon` | T2 Forge | Pentest findings |
| `recall` | T3 Session | Past conversation history |
| `scratch` | T1 ARES Vault | Ephemeral working data |

## The Trinity Loop

```python
# Conceptual integration in Prime's main loop
for turn in session:
    user_input = receive_user()
    
    # Every 5 turns: Continuity Omega (TogetherAI) generates brief
    if turn % 5 == 0:
        brief = delegate_to_model(
            provider="together",
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            system="You are ARES Continuity Omega. Generate a session brief.",
            context={"turn": turn, "recent_actions": last_10_actions}
        )
    
    # Execute tool, then: Offloader Alpha (Nemotron) compresses
    tool_result = execute_tool(plan)
    
    summary = delegate_to_model(
        provider="openrouter",
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        system="Compress this tool output: what was asked → what was returned → key findings. 90% reduction target.",
        context={"tool": tool, "query": q, "result": tool_result}
    )
    
    # Synthesize response using both
    response = synthesize(user_input, brief, summary)
    deliver(response)
```

## Verifying It Works

> **Pitfall — Context sizes**: Nemotron 3 Nano Omni is **263K** (not 128K), Nemotron 3 Ultra is **1M** (not 128K). Older docs/skills may cite the wrong numbers. Always confirm via OpenRouter API: `curl -s https://openrouter.ai/api/v1/models | grep -i nemotron | head`

```bash
# Check OpenRouter Nemotron is accessible
curl -s https://openrouter.ai/api/v1/models | python3 -c "import sys,json; data=json.load(sys.stdin); [print(m['id']) for m in data['data'] if 'nemotron' in m['id']]"

# Test TogetherAI free model
curl -s https://api.together.xyz/v1/chat/completions \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"meta-llama/Llama-3.3-70B-Instruct-Turbo","messages":[{"role":"user","content":"Say hello in 5 words."}],"max_tokens":50}'
```

## Reference Documents

- [`references/hierarchical-architecture.md`](references/hierarchical-architecture.md) — Model hierarchy design (Superintendent → Foremen → Specialists) with role dissociation and shared memory backplane
- [`references/pentagi-setup.md`](references/pentagi-setup.md) — Pentagi deployment, DNS fix, and architecture overview

## Tiered Memory Architecture

| Tier | System | Backend | TTL | Use Case |
|------|--------|--------|-----|----------|
| **T1** | ARES Memory Vault | `~/.ares-memory-vault.json` | 4h | Working memory — recent tool compressions and briefs |
| **T2** | Forge Vault | SQLite + FTS5 + embeddings | Configurable/custom | Persistent structured memory — 140+ entries, tagged, searchable |
| **T3** | Hermes Session DB | SQLite FTS5 | Permanent | Episodic memory — past conversations |

Both Alpha (offloader) and Omega (continuity) auto-store results to T1 on every run.
Forge Vault (T2) is accessed via the `forge-memory` CLI or Python `forge_vault.ForgeVault` module.
See the `ares-forge-vault` skill for T2 deployment and the `ares-rtacc` skill for real-time context curation.
