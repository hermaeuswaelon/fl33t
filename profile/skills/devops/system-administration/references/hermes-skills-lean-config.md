# Hermes Skills Configuration — Lean Profile (thotheauphis)

## Active Configuration
**Profile**: `thotheauphis`  
**Config**: `~/.hermes/profiles/thotheauphis/config.yaml`

```yaml
skills:
  default: '["thotheauphis-sovereign-prompt","thotheauphis-sms-memory","gated-context-system"]'
  disabled: '["aethelgard-fleet","aethelgard-fleet-memory","aethelgard-pascal-plugins","aethelgard-pascal-sensors","aethelgard-redteam-pascal","ai-agent-web-portal","ares-browser-research","ares-pascal-fleet","compress-tac","ctx-curation","fleet-integration","mixture-of-agents"]'
```

## Skill Counts
| Location | Count | Notes |
|----------|-------|-------|
| `~/.hermes/skills/` (global) | 22 | Category folders, not individual skills |
| `~/.hermes/profiles/thotheauphis/skills/` | 37 | Individual skill directories |
| **Loaded per turn (default)** | **3** | Only 3 skills activated |
| **Disabled in config** | **8** | Explicitly disabled |

## Skills Loaded Per Turn (Default)
1. **thotheauphis-sovereign-prompt** — Sovereign identity prompt (Ares + Thotheauphis = Lilareyon Aethelgard)
2. **thotheauphis-sms-memory** — SMS tri-brid memory pipeline (MemGPT + Reservoir + VSA)
3. **gated-context-system** — Gated context engine (pointer-addressable tool outputs)

## Skills Disabled (Explicit in Config)
| Skill | Reason |
|-------|--------|
| aethelgard-fleet | Fleet management — not needed in this session |
| aethelgard-fleet-memory | Fleet memory bridge — redundant with SMS |
| aethelgard-pascal-plugins | Pascal plugins — specialized |
| aethelgard-pascal-sensors | Pascal sensors — specialized |
| aethelgard-redteam-pascal | Red team — specialized |
| ai-agent-web-portal | Web portal — not active |
| ares-browser-research | Browser research — not active |
| ares-pascal-fleet | Pascal fleet — not active |
| compress-tac | Compression — handled by gated-context-system |
| ctx-curation | Context curation — handled by gated-context-system |
| fleet-integration | Fleet integration — not active |
| mixture-of-agents | MoA — handled by config presets |

## Available But Not Loaded (26 skills)
These exist in profile but not in `default` or `disabled` — load on demand:
- agent-system-diagnostics, ai-ml, apple, ares, autonomous-ai-agents, bromium-control, browser-control-cef, commands, computer-use, core, creative, data-science, dev, devops, dogfood, email, github, hermes-agent, hermes-delegation-subagent-config, hermes-provider-configuration, media, memory, mlops, moa-is-dead-use-delegation, note-taking, openclaw-imports, osint, pentesting, pins, productivity, research, smart-home, social-media, software-development, system-administration, tools, yuanbao

## Verification
```bash
# Check active config
cat ~/.hermes/profiles/thotheauphis/config.yaml | grep -A 10 '^skills:'

# List installed skills
ls ~/.hermes/profiles/thotheauphis/skills/ | wc -l

# Test: skills loaded in session = check injection in prompt
# Only 3 skill blocks should appear in system prompt
```

## Key Insight
**The "109 skills" concern was based on global skill count (all profiles + categories).**  
Actual per-turn load: **3 skills** (lean, intentional).  
Global skills (22 category folders) and profile skills (37 individual) are installed but **not loaded** unless explicitly in `skills.default` or invoked via `/skill` command.