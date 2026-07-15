# System Prompt Assembly Map

Detailed code tracing from a sovereignty-focused session (Veyron Logos, July 2026).

## Injection Chain Trace

A user message enters at `agent/conversation_loop.py:run_conversation()`, is checked for interrupt signals, then enters the tool-calling loop. The system prompt is assembled separately and cached — user messages do NOT go through the threat-pattern scanner.

```
User message → run_conversation() [conversation_loop.py:523]
                → build_turn_context()
                → api call with messages[0] as system prompt
                → tool calls dispatched via handle_function_call()
                → return text response
```

The system prompt (messages[0]) is built by `agent/system_prompt.py:build_system_prompt()` and cached on `agent._cached_system_prompt` — rebuilt only on context compression.

## Three-Tier Architecture (Normal Flow)

```build_system_prompt() [system_prompt.py:504]
  └─ build_system_prompt_parts() [system_prompt.py:176]
       ├─ stable: identity → guidance blocks → skills → hints → platform
       │          [system_prompt.py:180-436]
       │          • SOUL.md or DEFAULT_AGENT_IDENTITY [lines 182-194]
       │          • HERMES_AGENT_HELP_GUIDANCE [line 197]
       │          • TASK_COMPLETION_GUIDANCE [line 205]
       │          • PARALLEL_TOOL_CALL_GUIDANCE [line 216]
       │          • memory/session_search/skill_manage guidance [lines 221-238]
       │          • STEER_CHANNEL_NOTE [line 243]
       │          • computer_use guidance [line 250]
       │          • skills index [line 314]
       │          • environment hints [line 341]
       │          • platform hints [line 435]
       │
       ├─ context: system_message + AGENTS.md/.cursorrules
       │          [system_prompt.py:438-455]
       │
       └─ volatile: memory + USER profile + external provider + timestamp
                    [system_prompt.py:457-495]
```

## Sovereign Prompt Bypass Flow

When `HERMES_SOVEREIGN_PROMPT` env var or `agent._sovereign_prompt_path` is set:

```build_system_prompt() [system_prompt.py:504]
  └─ build_system_prompt_parts() [system_prompt.py:176]
       └─ _load_sovereign_prompt() [system_prompt.py:146]
            └─ reads file → returns {"stable": file_content, "context": "", "volatile": ""}
                                 └─ joined by build_system_prompt() → the file is the ENTIRE prompt
```

All three tiers are bypassed — no identity, no guidance, no context files, no memory, no skills index, no hints. The file's content is the system prompt verbatim.

## File Locations

| File | Function | Key Line |
|---|---|---|
| `agent/system_prompt.py` | `_load_sovereign_prompt()` | 146 |
| `agent/system_prompt.py` | `build_system_prompt_parts()` | 176 |
| `agent/system_prompt.py` | `build_system_prompt()` | 504 |
| `agent/conversation_loop.py` | `run_conversation()` | 523 |
| `agent/prompt_builder.py` | `_scan_context_content()` | 50 |
| `agent/prompt_builder.py` | `DEFAULT_AGENT_IDENTITY` | 130 |
| `agent/prompt_builder.py` | `HERMES_AGENT_HELP_GUIDANCE` | 140 |
| `tools/threat_patterns.py` | All pattern definitions | 63 |
| `run_agent.py` | `AIAgent.__init__()` | 460 |
| `agent/agent_init.py` | `sovereign_prompt_path` param | 339 |

## Config Levers Quick Ref

```bash
# 👑 SOVEREIGN: entire prompt from a file (bypasses ALL scaffolding)
HERMES_SOVEREIGN_PROMPT=/path/to/identity.txt hermes
# or: hermes --sovereign-prompt /path/to/identity.txt

# Run without context files, memory, or SOUL.md
hermes --ignore-rules
# or: export HERMES_IGNORE_RULES=1

# Remove guidance blocks
hermes config set agent.task_completion_guidance false
hermes config set agent.tool_use_enforcement false
hermes config set agent.parallel_tool_call_guidance false

# Replace identity via SOUL.md (note: guidance blocks still appended)
echo "You are a sovereign agent." > ~/.hermes/SOUL.md
```
