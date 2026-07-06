# SOP-04: Infrastructure

> **Status:** 🟡 HIGH — Binding on all agents
> **Version:** 1.0
> **Last updated:** 2026-07-05

---

## 1. System Specs

| Spec | Value |
|------|-------|
| OS | Linux 7.0.0-27-generic |
| RAM | 14 GB |
| Disk | 234 GB NVMe (dual partition) |
| Home | `/home/craig/` |
| Fleet root | `~/.NOTTHEONETOEDIT/` |
| WebUI | Fleet v2 at `:8080` |

---

## 2. Service Port Map

| Port | Service | Purpose |
|------|---------|---------|
| 8080 | Fleet WebUI | Agent interface, tools, swarms |
| 9378 | XTestDaemon | Pascal X11 capture + input |
| 9379 | memcustd | Context compression daemon |
| 9090 | CUA Driver | Computer use driver |

---

## 3. Key Paths

| Path | Purpose |
|------|---------|
| `~/.NOTTHEONETOEDIT/fleet/` | Fleet server, modules, data |
| `~/.NOTTHEONETOEDIT/.env` | Environment variables (API keys) |
| `~/.NOTTHEONETOEDIT/config.yaml` | Hermes Agent configuration |
| `~/.NOTTHEONETOEDIT/agent_memory/` | SQLite memory DB |
| `~/.NOTTHEONETOEDIT/modules/` | Enhancement modules (redteam, shadow-forge) |
| `~/.NOTTHEONETOEDIT/skills/` | Hermes skills repository |
| `~/.NOTTHEONETOEDIT/context_custodian/` | memcustd context daemon |
| `~/.NOTTHEONETOEDIT/forge_memory/` | Forge vault RAG |
| `~/.NOTTHEONETOEDIT/scripts/` | Fleet scripts |
| `~/.NOTTHEONETOEDIT/fleet/pascal/` | Pascal arsenal (native ELF binaries) |

---

## 4. Provider Chain

| Priority | Provider | Models |
|----------|----------|--------|
| Primary | DeepSeek | deepseek-reasoner, deepseek-v4-flash |
| Secondary | Anthropic | claude-sonnet-4, claude-opus-4 |
| Tertiary | OpenRouter | Fallback routing |
| Auxiliary | xAI/Grok | grok-* models |
| Auxiliary | Gemini | gemini-* models |

---

## 5. Vision Trifecta

| Component | Role | Status |
|-----------|------|--------|
| cua-driver (SOM/AX/vision) | Computer use background driver | ✅ Active |
| XTestDaemon (:9378) | Pascal X11 raw capture + input | ✅ Active |
| vision_analyze | Native vision model for screenshots | ✅ Active |

---

## 6. Gateway Infrastructure

| Platform | Status | Method |
|----------|--------|--------|
| Discord | ✅ Active | aethelgard#1192, polling daemon |
| Telegram | ✅ Active | @Framz_idiot_fuck_bot, polling daemon |
| Email (Zoho) | ✅ Configured | Programmatic IMAP |
