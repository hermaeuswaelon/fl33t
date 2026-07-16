---
name: ares-nemotron-together-dual-offload
description: "ARES Dual-Executor MOA Architecture — DeepSeek Reasoner orchestrating Nemotron 3 Ultra 550B + Nemotron 3 Nano 30B as OpenRouter free executors. MOA aggregation, single-executor dispatch, token cost awareness."
version: 3.0.0
author: Craig / ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, dual-model, offload, context, continuity, nemotron, together, free-models]
related_skills: [ares, ares-dual-offload, ares-offloader-alpha, ares-continuity-omega]
---

# ⚡ ARES Dual-Executor MOA Architecture

## Live Configuration (July 2026)

This is the **currently deployed** executor architecture. Three models working together, all routed through OpenRouter — no local hosting, no TogetherAI:

```
┌────────────────────────────────────────────────────────────────────┐
│                   DEEPSEEK REASONER (Me)                           │
│  Role: Conversation context, orchestration, MOA aggregation        │
│  Provider: deepseek (api.deepseek.com)                             │
│  Context: 128K tokens                                              │
└──────────────────────────┬─────────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │  MOA Aggregator          │
              │  (DeepSeek Reasoner)     │
              └────────────┬────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌──────────────────┐ ┌──────────────────┐
│   NEMOTRON ULTRA  │ │  NEMOTRON NANO   │
│   550B A55B       │ │   30B A3B        │
│   OpenRouter free │ │  OpenRouter free  │
│   1M context       │ │  256K context     │
│   Deep reasoning   │ │  Fast tool calls  │
└──────────────────┘ └──────────────────┘
```

**Total API cost: $0/month for executors.** Both Nemotron models are OpenRouter free tier. DeepSeek Reasoner is the only paid model at $0.55/M input tokens.

## TogetherAI as Custom Provider (Added July 2026)

TogetherAI is now registered as a **custom provider** in the thotheauphis profile alongside the OpenRouter MOA setup:

```yaml
custom_providers:
  - name: togetherai
    base_url: https://api.together.xyz/v1
    api_key_env: TOGETHER_API_KEY
    api_mode: chat_completions
```

**API key:** `TOGETHER_API_KEY` set in `~/.hermes/profiles/thotheauphis/.env` (key: `tgp_v1_jkKWKWdAMMes...`)

**How to use TogetherAI:**
```bash
# Interactive model picker (run in real terminal)
hermes model --refresh

# Direct invocation
hermes chat --provider togetherai -m meta-llama/Llama-3.3-70B-Instruct-Turbo

# Add as fallback when OpenRouter rate-limits
hermes fallback add    # then select togetherai from provider picker
```

**Why this works:** TogetherAI is in the Hermes curated model list (`hermes_cli/models.py`) despite having no plugin directory. The `custom_providers` config section is the correct way to register such providers. See `multi-model-executor-architecture` skill's `references/adding-providers-via-custom-providers.md` for the full pattern.

**Full OpenRouter model list:** The cache at `~/.hermes/profiles/thotheauphis/cache/openrouter_model_metadata.json` contains metadata for 1000+ models. To refresh: run `hermes model --refresh` interactively, which fetches the live catalog from `https://openrouter.ai/api/v1/models`.

## MOA Config

The live configuration in `config.yaml`:

```yaml
moa:
  presets:
    default:
      reference_models:
        - provider: openrouter
          model: nvidia/nemotron-3-ultra-550b-a55b:free
        - provider: openrouter
          model: nvidia/nemotron-3-nano-30b-a3b:free
      aggregator:
        provider: deepseek
        model: deepseek-reasoner
      fanout: per_iteration
  reference_models:
    - provider: openrouter
      model: nvidia/nemotron-3-ultra-550b-a55b:free
    - provider: openrouter
      model: nvidia/nemotron-3-nano-30b-a3b:free
  aggregator:
    provider: deepseek
    model: deepseek-reasoner
  enabled: true
```

## Dispatch Patterns

### MOA (multi-model aggregation)

Use `/moa <prompt>` to run the same prompt through both Nemotron models and aggregate their responses through DeepSeek Reasoner. Best for tasks that benefit from multiple perspectives.

### Single-executor delegation

Used by the main agent (DeepSeek Reasoner) via the `executor` tool (see `work/executor_manager.py`):

| Executor | Model | When |
|----------|-------|------|
| `executor(nano, task)` | Nemotron Nano 30B A3B | Quick tool calls, X11, Pascal compilation, fast code |
| `executor(ultra, task)` | Nemotron Ultra 550B A55B | Deep reasoning, long context (up to 1M tok), heavy analysis |
| `executor(parallel, nano_task, ultra_task)` | Both | Simultaneous fast + deep on independent sub-tasks |

## Token Cost Awareness

**MOA costs 3x input tokens per invocation** (2 reference models + 1 aggregator read the same prompt). Only use when the multi-perspective benefit justifies the cost.

The single largest token sink in the system is the **skills index** — ~5,147 tok/turn for 147 skill descriptions burned every turn regardless of MOA. For comparison, a single MOA fanout costs less than the ongoing skills index bleed.

## Scripts Status (July 2026)

The Python scripts in `scripts/` (`ares-offload.py`, `ares-continuity.py`, etc.) were written for the original TogetherAI direct-offload architecture. They are **NOT the active executor path**. The live system uses:
- **MOA configuration** in `config.yaml` (Hermes-native) — executors via OpenRouter free tier
- **`work/executor_manager.py`** — dispatches via `delegate_task` with model override
- **`work/x11_tool.py`** — X11 desktop control via xdotool
- **`custom_providers`** in config — TogetherAI registered as a custom provider for direct use and fallback

The old scripts remain for reference but should not be assumed active without re-verification.

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
