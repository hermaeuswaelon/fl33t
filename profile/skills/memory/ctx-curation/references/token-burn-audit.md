# Token Burn Audit — July 2026 Session
*Full audit of per-turn system prompt overhead and remediation*

---

## Baseline (before remediation)

| Source | Tokens/turn | Daily cost (100 turns) |
|--------|------------:|------------------------|
| Skills index (147 skills) | ~5,147 | ~$0.28 |
| Tool schemas (75 tools) | ~8,750 | ~$0.48 |
| System prompt boilerplate | ~2,000 | ~$0.11 |
| SOUL.md | ~346 | ~$0.02 |
| **Total fixed overhead** | **~16,243** | **~$0.89/turn → ~$89/day** |

---

## Remediation Applied

### 1. Smart Skill Injection (`agent/skill_selector.py`)

**Mechanism:** Per-turn keyword + tool matching → expands ONLY relevant skill categories.

| Match | Categories expanded |
|-------|---------------------|
| code, debug, git, refactor | software-development |
| github, pr, issue, repo | github |
| paper, arxiv, research | research |
| click, mouse, xdotool, X11 | computer-use |
| generate, image, design | creative |
| model, train, inference | mlops |
| scan, network, recon | pentesting |
| ... | ... |

**Rules:** 31 keyword sets × 20 categories + tool-based routing + always/never lists.

**Result:** ~65% reduction → ~1,000–2,000 tok/turn instead of 5,147.

### 2. Priority Categories in Prompt Builder

**Files patched:**
- `agent/prompt_builder.py` — `priority_categories` param + invert logic
- `agent/system_prompt.py` — wires `skill_selector.select_relevant_skill_categories()`
- `agent/coding_context.py` — existing `compact_categories` for coding posture

**Behavior:** `priority_categories` WINS over `compact_categories`. When set, ONLY listed categories get full descriptions; everything else → names-only line.

### 3. Tool Schema Shrinking (planned)

Top offenders:
- `cronjob` schema: 2,396 tok
- `session_search`: 1,985 tok
- `skill_manage`: 1,446 tok
- `terminal`: 952 tok

---

## Verification

```bash
# Fresh verification script (ad-hoc)
python3 -c "
import sys; sys.path.insert(0, '/opt/hermes-agent')
from agent.skill_selector import select_relevant_skill_categories
# Test cases
print(select_relevant_skill_categories('write python script', {'terminal'}))
print(select_relevant_skill_categories('scan network', {'computer_use'}))
print(select_relevant_skill_categories('hello world', set()))
"
```

Expected: small sets (1–4 categories) per query; empty set for generic greetings.

---

## Files Created/Modified

| File | Type | Purpose |
|------|------|---------|
| `/opt/hermes-agent/agent/skill_selector.py` | **NEW** | Context-aware skill category router |
| `/opt/hermes-agent/agent/prompt_builder.py` | PATCH | `priority_categories` parameter + inversion |
| `/opt/hermes-agent/agent/system_prompt.py` | PATCH | Wires selector into prompt assembly |
| `/opt/hermes-agent/agent/coding_context.py` | EXISTING | Already had `compact_categories` for coding posture |

---

## Related Skills

- `ctx-curation` — this skill's dual tool/skill architecture
- `hermes-system-prompt-control` — prompt assembly internals
- `hermes-agent` — CLI/config reference