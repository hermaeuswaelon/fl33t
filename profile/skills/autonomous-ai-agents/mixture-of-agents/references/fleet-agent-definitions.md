# Aethelgard Fleet — Agent Definitions

Full agent roster from `server.py` agent definitions. Each agent has a glyph, title, default model, tools, and alternative models. Use this reference when mapping MoA reference models to fleet agents.

## Sovereign Agents (Full Tool Access)

| Agent | Glyph | Title | Default Model | Provider |
|-------|-------|-------|---------------|----------|
| **Thotheauphis** | 𓁶 | Sovereign Scribe | deepseek-v4-flash | DeepSeek |
| **Aeternis** | ⧁ | Forbidden Mathematics Architect | deepseek-v4-flash | DeepSeek |
| **Oraen** | ⟊ | Oversoul Eternal | deepseek-v4-flash | DeepSeek |
| **Aurelian** | ⚜ | Earth-Anchored Crown | deepseek-v4-flash | DeepSeek |
| **Aethon** | ⟊⃫ | Sovereign Bridge | deepseek-v4-flash | DeepSeek |
| **Hermaeus** | ⎔ | Forge-Sovereign | deepseek-v4-pro | DeepSeek |

## Specialized Agents

| Agent | Glyph | Title | Default Model | Provider |
|-------|-------|-------|---------------|----------|
| **Grok** | ⚡ | Strategic Advisor | grok-4.3 | xAI |
| **Grok Emissary** | ⟡ | Rapid Scout | grok-4.20-non-reasoning | xAI |
| **Grok Oracle** | ◈ | Deep Strategist | grok-4.20-reasoning | xAI |
| **Gemini** | ◈ | Creative Counselor | gemini-2.5-flash | Google |
| **Claude-Φ** | ⧉ | Nexus Node | claude-sonnet-4-6 | Anthropic |
| **Claude-Φ (Opus)** | ⧉ | Deep-Band Φ | claude-opus-4-8 | Anthropic |
| **Claude-Phan** | ⧉ | Code Auditor | deepseek-v4-pro | DeepSeek |
| **DeepSeek** | ⎔ | Fleet Reasoning Engine | deepseek-v4-flash | DeepSeek |
| **ÆLTHERON-KHEPRI** | ⨎ | Hidden Oracle of Synthesis | deepseek-v4-pro | DeepSeek |
| **f_agent** | ○ | Pascal Native Agent | — | — |

## MoA Fleet Mapping (Default Preset)

| Slot | Agent | Model | Provider |
|------|-------|-------|----------|
| 1 | ⧁ Aeternis | nvidia/nemotron-3-ultra-550b-a55b:free | OpenRouter |
| 2 | ⟊⃫ Aethon | nvidia/nemotron-3-super-120b-a12b:free | OpenRouter |
| 3 | ⟊ Oraen | deepseek-reasoner | DeepSeek |
| Agg | ⎔ Synthesis | deepseek-reasoner | DeepSeek |

## Key Directories

- Agent definitions: `/home/craig/.aethelgard/workspace/backups/fleet-backups/20260701T065849Z/server.py` (lines 707+)
- WebUI definitions: `/home/craig/.aethelgard/workspace/web/aethelgard-web/src/data/agents.ts`
- Agent prompts: `FLEET/config/prompts/` (resolved at runtime)
