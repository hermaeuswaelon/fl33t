---
name: hermes-system-health
description: "Comprehensive Hermes system health investigation — check installations, processes, memory, API keys, folder structures, and configurations. Covers parallel investigation patterns for diagnosing what's working vs what's not."
version: 1.0.0
author: Hermes Agent (thotheauphis)
created_by: agent
platforms: [linux, macos]
metadata:
  hermes:
    tags: [hermes, diagnostics, system-health, investigation, memory, troubleshooting]
    related_skills: [hermes-agent, snapndrop, gated-context-system]
---

# Hermes System Health Investigation

Class-level skill for comprehensively checking the health of a Hermes Agent installation. Covers parallel investigation, memory verification, API key inventory, process auditing, and folder structure analysis.

## When to Load This Skill

- User asks "check the status of my Hermes system"
- Investigating why a tool or feature isn't working
- After upgrades, migrations, or reconfigurations
- User wants to know "what's active" and "what's missing"
- Diagnosing memory tool failures
- Inventorying available API keys and capabilities

## Core Principle: Parallel Investigation

Batch independent checks into a single response. Investigation queries rarely depend on each other — run them together:

```python
# What to batch in one turn:
1. Installation paths and versions   (which hermes, pip show, git log)
2. Running processes                 (ps aux | grep hermes)
3. Profile structure                 (ls ~/.hermes/profiles/)
4. Memory system status              (hermes memory status)
5. Environment variables / API keys  (cat .env)
6. Config sections of interest       (grep memory|terminal config.yaml)
```

## Investigation Checklist

### 1. Installation & Version

```bash
which hermes                    # Launcher binary path
hermes --version                # Version + install method + python version
pip show hermes-agent           # Package metadata, location
# If git-installed:
cd /opt/hermes-agent && git log --oneline -5 && git branch
```

**Pitfalls:**
- `hermes --version` shows upstream commit count — large gaps (e.g., "680 commits behind") mean a major upgrade is available via `uv pip install --upgrade hermes-agent`
- The install method matters: `pip install` vs `git clone` vs shell installer affect config paths

### 2. Running Processes

```bash
ps aux | grep -i hermes | grep -v grep
```

**What to look for:**
- Gateway daemon (running since when?)
- Dashboard process (what port/profile?)
- Current session flags (`--ignore-rules`, `--yolo`, `--ignore-user-config`)
- tmux sessions (sovereign, etc.)
- Parallel worker processes (foreman, doer)
- Witness/monitoring scripts

### 3. Profile Structure

```bash
ls -la ~/.hermes/profiles/
# Check active profile config:
cat ~/.hermes/profiles/<active>/config.yaml
```

**Key config sections to inspect:**
- `model` — provider, base_url, default model
- `memory` — memory_enabled, provider (or absence = defaults)
- `terminal` — backend (local/docker/ssh)
- `platform_toolsets.cli` — which tools are enabled
- `gateway` — platform connections

### 4. Memory System Health

```bash
# CLI health check (works even when tool doesn't):
hermes memory status

# Check memory data directory:
ls -la ~/.hermes/profiles/<profile>/memory/
ls -la ~/.hermes/profiles/<profile>/memory/store/   # VSA vectors
ls -la ~/.hermes/profiles/<profile>/memory/sms/     # SMS plugin
```

**Interpreting memory status:**
| Message | Meaning |
|---------|---------|
| "Built-in: always active" | Default memory backend working |
| "Provider: none" | No external provider configured — using built-in only (this is fine) |
| Plugin list | Installed but not active unless enabled in config |
| VSA vectors file present | Memory data actively persisted |

**Why the memory TOOL might fail while memory system works:**
The `memory` tool in a Hermes session requires the `MemoryStore` object to be injected into its dispatch kwargs by the conversation loop. Sessions launched with `--ignore-user-config` (and possibly `--ignore-rules`) skip this injection. The handler at `tools/memory_tool.py` line 977 checks `if store is None` and returns "not available". This is a session-startup artifact, NOT a broken memory system. A normal `hermes` session or `/reset` without stripped flags will have full memory tool access.

**Memory module location:**
- Tool: `/opt/hermes-agent/tools/memory_tool.py`
- NOT at `agent.memory` (that module doesn't exist in the current layout)

### 5. API Key Inventory

```bash
# List all set API keys (without exposing values):
grep -v "^#" ~/.hermes/.env | grep -v "^$" | cut -d= -f1
```

**What to check:**
- Which providers have keys (DeepSeek, OpenRouter, xAI, etc.)
- What's missing (Anthropic, OpenAI, Google, Airtable, etc.)
- Whether gateway keys are present (Telegram, Discord, Email)

### 6. Folder Structure Analysis

When a folder name is unknown or suspicious:

```bash
stat /path/to/folder                    # Size, inode, permissions, creation date
find /path/to/folder -maxdepth 2 -type d | sort  # Structure
cat /path/to/folder/SOUL.md 2>/dev/null          # Check if it's a Hermes home
cat /path/to/folder/active_profile 2>/dev/null    # Which profile?
```

**Detecting bind mounts vs symlinks vs real dirs:**
```bash
stat --format="%i %d" /path/A /path/B    # Same device number? Different inodes?
mount | grep <name>                       # Check for bind mounts
readlink -f /path                         # Resolve symlinks
find /path -maxdepth 0 -type l           # Is it a symlink?
```

**Common folder patterns:**
| Pattern | Meaning |
|---------|---------|
| `.NOTTHEONETOEDIT` | Backup/snapshot — "not the one to edit" |
| `ORGANIZED_FILES/` | Organized backup copies |
| `projects/hermes-upgrades/` | Active upgrade work |
| `.hermes/profiles/<name>/` | Active Hermes profile |

## Presentation Style for Results

When reporting system health investigation results:
- Use a table for structured data (installations, processes, API keys)
- Use numbered sections matching the investigation checklist
- Lead with the bottom line — "working" or "not working" first
- Group related findings together (all installation info, all memory info)
- When something isn't working, explain WHY and whether it matters

## Pitfalls

1. **Memory tool failure in stripped sessions** — `--ignore-user-config` removes the MemoryStore injection. This is not a broken memory system. Check via `hermes memory status` CLI instead.
2. **Config inheritance** — `~/.hermes/config.yaml` is the base, `~/.hermes/profiles/<name>/config.yaml` overrides it. Memory sections may be absent in one but present in the other.
3. **`hermes config get` returns empty** — The key may not exist in config at all (defaults apply). Check both base and profile configs directly.
4. **Version gaps** — `hermes --version` showing "N commits behind" is normal for installed-vs-upstream; doesn't indicate a broken install.
5. **Gateway process is silent** — Check the logs at `~/.hermes/logs/gateway.log` for the actual error.
