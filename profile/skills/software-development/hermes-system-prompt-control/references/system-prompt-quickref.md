# System Prompt Composition Analysis

> Full investigation of Hermes v0.18.2 system prompt structure at ~/.hermes/profiles/thotheauphis/skills/software-development/efficient-by-default/references/system-prompt-composition.md

## Quick Reference: Source Line Map

The deep-dive reference file contains exact line numbers for every file involved:

- `system_prompt.py` L580 — `build_system_prompt()` caching
- `system_prompt.py` L606 — `invalidate_system_prompt()` rebuild trigger
- `system_prompt.py` L176-469 — `build_system_prompt_parts()` tier assembly
- `prompt_builder.py` L1445-1712 — `build_skills_system_prompt()` index builder
- `skill_selector.py` L189-242 — smart category selector
- `conversation_loop.py` L282-361 — `_restore_or_build_system_prompt()` cache logic
- `turn_context.py` L343-347 — per-turn restore gate
- `run_agent.py` L5789-5812 — `AIAgent.run_conversation()` entry point

## Key Technique: Force Mid-Session Rebuild

When the system prompt was built with `system_message=None` (common first-turn path), the smart selector never fires. To get a compact skills index mid-session:

```python
from agent.system_prompt import invalidate_system_prompt
invalidate_system_prompt(agent)
```

This sets `agent._cached_system_prompt = None`, forcing the next turn to rebuild with the current conversation context — triggering the smart selector.

## Key Technique: Measure Composition

```bash
hermes prompt-size --json
```

Returns: total size, skills_index size, memory, user_profile, tool count+bytes, section breakdown (stable/context/volatile).

## Future Work

The smart selector could be extended to fire on EVERY rebuild, not just first-turn builds. This would keep the skills index compact even mid-session without manual invalidation.
