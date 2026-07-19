# Architectural Preference: Native Defaults, Not Invokable Skills

## The Principle

Systems should be wired at the **infrastructure layer** — core Hermes code, config defaults, plugin registration, or toolset membership — so they activate automatically without manual invocation.

**Preferred:**
- Core code wiring (e.g., `_SMS_ACTIVE = True` in `memory_tool.py`)
- Plugin registration (e.g., `gated_context` plugin → `context_engine` toolset)
- Config defaults (`skills.default`, `platform_toolsets.cli`)
- Built-in tool implementations

**Avoid:**
- Skills that require `/skill <name>` to load
- One-shot setup scripts that must be re-run
- Manual tool/feature toggling each session

## Why

- Reduces friction — systems work on first use
- Eliminates the "I forgot to load the skill" class of failure
- Makes the environment self-describing — a `hermes doctor` or config audit reveals everything

## Testing the Preference

When adding or auditing a capability, ask: "Does this work on a fresh `hermes` session with no `/` commands?" If the answer is no, it violates the native-default principle.

## Exceptions

Skills that provide *specialized* capabilities (not general infrastructure) can remain as loadable skills. Examples: project-specific AGENTS.md, domain-specific research workflows, one-shot data migration procedures.
