---
name: autonomous-agents
description: "Delegate coding and reasoning to autonomous AI agents — Claude Code, Codex, OpenCode, MoA ensembles"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [autonomous, coding-agents, claude-code, codex, opencode, moa, delegation]
    related_skills: [hermes-agent]
---

# Autonomous Agents Umbrella

Consolidated skill for delegating coding and reasoning tasks to autonomous AI agents. Absorbs: claude-code, codex, mixture-of-agents, opencode.

## Contents

1. [Claude Code (Anthropic)](#1-claude-code-anthropic)
2. [Codex (OpenAI)](#2-codex-openai)
3. [OpenCode (Provider-Agnostic)](#3-opencode-provider-agnostic)
4. [Mixture of Agents (MoA)](#4-mixture-of-agents-moa)

---

## 1. Claude Code (Anthropic)

Anthropic's autonomous coding agent CLI. v2.x can read files, write code, run shell commands, spawn subagents, and manage git workflows.

### Prerequisites

```bash
npm install -g @anthropic-ai/claude-code
claude auth login --console  # or ANTHROPIC_API_KEY
```

### Print Mode (One-Shot, Preferred)

```bash
claude -p 'Add error handling to all API calls in src/' --allowedTools 'Read,Edit' --max-turns 10
```

### Interactive Mode (via tmux)

```bash
tmux new-session -d -s claude-work -x 140 -y 40
tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter
# Handle trust+permissions dialogs
sleep 5 && tmux send-keys -t claude-work Enter
sleep 2 && tmux send-keys -t claude-work Down && sleep 0.3 && tmux send-keys -t claude-work Enter
```

### Key Flags

| Flag | Purpose |
|------|---------|
| `-p "task"` | Print mode (non-interactive) |
| `--max-turns N` | Limit agentic loops |
| `--allowedTools 'Read,Edit,Bash'` | Whitelist tools |
| `--model sonnet\|opus\|haiku` | Model selection |
| `--output-format json` | Structured JSON output |
| `--bare` | Fastest startup, skips plugins/MCP |
| `--worktree name --tmux` | Isolated worktree + tmux session |

### PR Review

```bash
claude -p 'Review this PR thoroughly' --from-pr 42 --max-turns 10
```

### CLAUDE.md

Project context file auto-loaded by Claude Code. Rules directory: `.claude/rules/*.md`.

---

## 2. Codex (OpenAI)

OpenAI's autonomous coding agent CLI.

### Prerequisites

```bash
npm install -g @openai/codex
# Auth: OPENAI_API_KEY or OAuth
```

### One-Shot Tasks

```bash
codex exec 'Add dark mode toggle to settings'
```

### Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution |
| `--full-auto` | Auto-approves changes in sandbox |
| `--yolo` | No sandbox, no approvals (fastest) |
| `--sandbox danger-full-access` | Bypass bubblewrap issues |

### Requirements

- Git repository required (use `mktemp -d && git init` for scratch)
- `pty=true` for interactive sessions
- In gateway/service contexts, use `--sandbox danger-full-access`

### Parallel PR Fixing

Create worktrees, run Codex in each, monitor with `process` tool.

---

## 3. OpenCode (Provider-Agnostic)

Open-source, provider-agnostic AI coding agent.

### Prerequisites

```bash
npm i -g opencode-ai@latest
opencode auth login  # Configures at least one provider
```

### One-Shot Tasks

```bash
opencode run 'Add retry logic to API calls'  # No pty needed
opencode run 'Review config' -f config.yaml  # Attach files
opencode run 'Debug tests' --thinking         # Show reasoning
```

### Interactive Sessions (Background)

```bash
opencode  # Start in background with pty=true
# Send prompts via process(action="submit")
# Exit with Ctrl+C (\x03) or process(action="kill")
```

### Key Flags

| Flag | Effect |
|------|--------|
| `run 'prompt'` | One-shot execution and exit |
| `-c` / `--continue` | Continue last session |
| `--model provider/model` | Force specific model |
| `--thinking` | Show model thinking |
| `--file path` / `-f` | Attach file(s) |

### PR Review

```bash
opencode pr 42
```

---

## 4. Mixture of Agents (MoA)

Delegate multi-perspective reasoning to multiple reference models via MoA aggregation.

### Architecture

- **Orchestrator model** dispatches to several parallel reference models
- Reference models each produce independent responses
- **Aggregator model** synthesizes the best combined answer
- Useful for complex reasoning, fact-checking, debate-style analysis

### Typical Setup

```yaml
orchestrator: deepseek-reasoner
reference_models:
  - nemotron-ultra-550b  # Free tier
  - claude-sonnet-4       # Deep reasoning
  - gemini-2.0-flash      # Fast alternative
aggregator: deepseek-reasoner  # Synthesizes final answer
```

### When to Use

- Complex multi-step reasoning problems
- Fact-checking across multiple sources
- Creative brainstorming with diverse perspectives
- Reducing model-specific bias or hallucination

---

## Choosing the Right Agent

| Task | Recommended Agent |
|------|-------------------|
| One-shot code edit/fix | Claude Code print mode or OpenCode run |
| Complex feature build | Claude Code interactive (tmux) |
| Multiple parallel fixes | Codex with git worktrees |
| PR review | Claude Code `--from-pr` or OpenCode `pr` |
| Multi-perspective reasoning | MoA with reference models |
| Fast, simple change | OpenCode run (no pty needed) |
| Provider-agnostic workflow | OpenCode (bring your own API key) |

## General Rules

1. **Set `workdir`** — always scope agents to the correct project directory
2. **Set timeouts** — code generation can be slow; use generous timeouts (120-300s)
3. **Monitor** — use `process` tools for background sessions
4. **Report** — summarize what changed, test results, and next steps
5. **Clean up** — kill tmux sessions and background processes when done
6. **Isolate** — use temp directories or git worktrees for parallel work
