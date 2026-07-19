---
name: moa-is-dead-use-delegation
description: MoA (Mixture-of-Agents) is deprecated — the 3-tier pipeline no longer runs reference models. All parallel worker / subagent configuration now lives under the delegation config section. This skill prevents wasting time on the old MoA config.
category: CORE
triggers:
  - user says "MOA" or "MoA" or "mixture of agents"
  - previous session referenced the 3-tier pipeline (Architect→Foreman→Doer)
  - config mentions moa.reference_models or moa.presets
  - user asks about "reference models" or "aggregator model"
  - user asks to set up the "doer" or "foreman" as a separate model
---

# MoA Is Dead — Use Delegation

## Critical Context

**Mixture-of-Agents (MoA) is no longer active.** The old 3-tier pipeline (Architect → Foreman → Doer) with reference models via `moa.presets.default.reference_models` no longer runs. The `moa_loop.py` file has been rewritten into "executor mode" — it's a pass-through to the main model with an instruction to use `delegate_task`.

## What to Do Instead

✅ **Use `delegation:` config section** for parallel workers/subagents.

See skill: `hermes-delegation-subagent-config`

## What Still Exists (Vestigial)

- `moa:` config block in config.yaml still present from old config migrations
- `reference_models` list still in the config — **not used at runtime**
- `delegation.parameters` field (empty string in config) — **not parsed, vestigial**

## Migration Pattern

| Old (MoA) | New (Delegation) |
|-----------|------------------|
| `moa.reference_models[0].model` | `delegation.model` |
| `moa.reference_models[1].temperature` | `delegation.request_overrides.temperature` (w/ patch) |
| `moa.presets.default.aggregator` | Main `model:` section (unchanged) |
| Per-reference temperature/params | Global delegate overrides via `request_overrides` |

## Verification

If you see `MoAClient`, `aggregate_moa_context`, or `reference_models` being discussed as active runtime components — **they are not**. The executor mode replaced them. The agent uses `delegate_task` for sub-tasks, not parallel MoA model fan-out.
