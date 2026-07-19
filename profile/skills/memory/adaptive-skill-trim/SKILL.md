---
name: adaptive-skill-trim
description: "Adaptive Skill/Trim Layer — frequency-tracked, 8-category, names-only, tool-tip injected system prompt optimizer"
---

# Adaptive Skill/Trim Layer

## Purpose
Replace the static ~93-skill `<available_skills>` index (~10KB/turn) with a compact, frequency-ranked, names-only index organized into 8 umbrella categories, plus per-turn tool-tip injection.

## Components

### 1. Frequency Cortex (`~/.hermes/profiles/thotheauphis/skill_freq.json`)
```json
{
  "skill_name": {
    "count": 12,
    "last_used": 1712345678.123,
    "sessions": [1712345678.123, 1712345000.0],
    "decayed_score": 11.4
  }
}
```
- Updated on every `skill_view()` call
- Decay: `score = count × 0.95^days_since_last_use`
- Session boost: skills used in last 3 sessions get 1.5× multiplier

### 2. Category Merger (8 umbrella categories)
Map current 29+ categories to 8:
1. **CORE** — hermes-provider-configuration, hermes-core-internals, system-administration, commands, pins, tools
2. **DEV** — software-development, github, data-science, autonomous-ai-agents, test-driven-development, pascal-toolchain
3. **WEB** — browser-control-cef, bromium-control, openclaw-imports, computer-use
4. **AI/ML** — mlops, mlops/*, llm-training, llm-backends, serving-llms-vllm, llama-cpp
5. **OSINT/RESEARCH** — osint, research, pentesting, pentest-*, osint-recon-framework
6. **CREATIVE** — creative, creative-*, media, creative-content, creative-media, creative-visual
7. **COMMS** — email, social-media, smart-home, note-taking, yuanbao, workspace
8. **MEMORY** — memory, recall, aethelgard-fleet-memory, gated-context-system, snapndrop

### 3. Compact Index Builder
- Takes raw skills_by_category dict
- Maps to 8 categories
- Sorts by frequency (decayed_score)
- Top 5 shown per category; "N more" collapsed
- Never-used skills hidden, listed at bottom as "X unused skills available"
- NO descriptions — names only
- Output: ~500-800 chars vs current ~10,000 chars

### 4. Tool-Tip Injector
- Per-turn, before model call, inject a brief tool-tip
- Keyword-match user message → relevant skills
- 60-100 token hint appended to volatile section
- Format: `[⧉ Context: <skill1>, <skill2> relevant | <toolA>, <toolB> available]`

## Files
- `~/.hermes/profiles/thotheauphis/skill_freq.json` — frequency data
- `/opt/hermes-agent/agent/prompt_builder.py` — patched `build_skills_system_prompt()`
- `/opt/hermes-agent/tools/skills_tool.py` — patched `skill_view()` to log frequency

## CLI
- `hermes skill-freq` — view frequency stats
- `hermes skill-freq --decay` — force recalculation of decay scores
- `hermes skill-freq --reset` — reset all counters

## Verification
After deployment:
```bash
hermes skill-freq
# Should show frequency-ranked skill list
hermes prompt-size --json | grep skills_index
# Should show < 1000 chars vs previous 10207
```
